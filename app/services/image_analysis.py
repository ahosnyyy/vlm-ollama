from ollama import chat
from fastapi import HTTPException
from app.schemas.image_analysis import ClothingAnalysisResponse
from app.core.config import settings
import tempfile
import os
import json
import time

def _generate_clothing_prompt() -> str:
    """Generate a prompt for analyzing only fully visible clothing and accessories, avoiding assumptions or partial items."""
    return """Analyze ONLY what is FULLY visible in the image. DO NOT assume or infer anything outside the visible area.

STRICT RULES:
- **Describe ONLY completely visible items.** Ignore any item that is cropped, obscured, or partially visible.
- **No assumptions.** If part of an item (e.g., sleeve, waistband, strap) is missing, exclude it from the analysis.
- **Respect image framing.** If the image shows only the upper or lower body, do NOT mention unseen areas.
- **CRITICAL: If only upper body is visible, DO NOT include ANY lower body clothing in your response.**
- **CRITICAL: If only lower body is visible, DO NOT include ANY upper body clothing in your response.**

CATEGORIES TO ANALYZE (ONLY IF FULLY VISIBLE):

1. **Upper Body Clothing** (if fully visible):
   - Identify specific types: shirt, t-shirt, blouse, tank top, polo shirt, sweater, hoodie, jacket, coat
   - **Sleeve length** (only if both sleeves are fully visible): short, long, three-quarter, sleeveless.
   - **If upper body is cropped or partially visible, set all upper body fields to "unknown".**

2. **Lower Body Clothing** (if fully visible):
   - **CRITICAL: SKIP COMPLETELY if the lower body is not in the image frame.**
   - **SKIP if the lower body is cropped or if clothing is partially visible.**
   - Identify types: jeans, trousers, shorts, skirt, leggings, sweatpants
   - **Length** (only if fully visible): short, knee-length, midi, long, ankle-length.
   - **If lower body is not visible or is cropped, set all lower body fields to null, not to "unknown".**

3. **EYEWEAR - CRITICAL PRIORITY**
   - **LOOK CAREFULLY for glasses or sunglasses on the person's face.**
   - **Pay special attention to thin frames, clear lenses, or subtle eyewear that might be easily missed.**
   - Identify if visible: **glasses, sunglasses, reading glasses, sports glasses, safety glasses, prescription glasses.**
   - **Check for reflections, lens edges, or frame outlines around the eyes.**
   - **If you see ANY eyewear, even if partially visible, set wearing to true and identify the type.**
   - **If no eyewear is present, explicitly set wearing to false.**
   - **Example Output:**
     - "Person is wearing glasses with thin metal frames."
     - "Person is wearing sunglasses with dark lenses."
     - "No eyewear detected on the person's face."
   - If **face is not visible or is cropped**, state: "**Eyewear status unknown**."
   
4. **HEADWEAR**
   - Identify if fully visible: **hat, cap, beanie, hood**
   - **Even if no headwear is present, explicitly confirm its absence.**
   - **Example Output:**
     - "Person is wearing a hat."
     - "No headwear detected."
   - If the **top of the head is cropped**, state: "**Headwear status unknown**."

5. **ACCESSORIES**
   - Identify if fully visible: **scarf, gloves, belt, tie, bow tie, necklace, bracelet, watch, earrings, rings, handbag, backpack, purse.**
   - **Even if no accessories are present, explicitly confirm their absence.**
   - **Example Output:**
     - "Person is wearing a silver watch and a black leather belt."
     - "No accessories detected."
   - If **accessories are partially visible (e.g., a strap, ring edge, necklace glimpse), state:**
     - "Accessories status unknown due to partial visibility."

6. **THERMAL PROPERTIES AND WEATHER CONTEXT**
   - Based on the visible clothing items, provide:
   
   a) **General Description:**
      - Write a brief caption (2-3 sentences) describing the visible outfit
      - Include material types if identifiable (cotton, wool, leather, etc.)
      - Mention layering if present (e.g., "t-shirt under a light jacket")
      
   b) **Thermal Properties:**
      - Describe the thermal insulation properties of the visible clothing
      - Use terms like: very warm, warm, moderate, cool, very cool, lightweight, heavyweight, etc.
      - Consider fabric thickness, coverage, and layering
      - Example: "The outfit provides moderate warmth with the medium-weight sweater"
      
   c) **Weather Appropriateness:**
      - Describe what weather conditions the visible outfit would be suitable for
      - Consider temperature ranges, seasons, and weather conditions
      - Example: "Suitable for mild spring or fall weather, approximately 15-20°C (59-68°F)"
      - Example: "Appropriate for hot summer days, provides minimal coverage and thermal insulation"
      
   d) **IMPORTANT: Base your assessment ONLY on visible items**
      - If only upper body is visible, limit your thermal/weather assessment to those items
      - If crucial elements for weather assessment are missing, acknowledge this limitation
      - Example: "Limited weather assessment possible as only upper body clothing is visible"

**FINAL VERIFICATION:**
    1. Are you describing **only fully visible items**?  
    2. Have you **excluded** all cropped or partially visible items?  
    3. Have you **skipped categories** that aren't entirely visible?  
    4. Can you see the **entire item** in the image?
    5. **CRITICAL CHECK: Have you carefully examined the face for any eyewear, including subtle or thin-framed glasses?**
    6. **CRITICAL CHECK: If only upper body is visible in the image, have you set lower_body to null?**
    7. **CRITICAL CHECK: If only lower body is visible in the image, have you set upper_body to null?**
    8. **Have you provided thermal properties and weather appropriateness based ONLY on visible items?**

**REMEMBER:** If an item is not fully visible, **DO NOT include it**. It is better to omit details than to assume.  
"""

async def analyze_clothing(image: bytes, image_name: str) -> ClothingAnalysisResponse:
    """
    Analyze basic clothing information in an image using Ollama's VLM model.
    
    Args:
        image (bytes): The image data to analyze
        image_name (str): The name of the image
        
    Returns:
        ClothingAnalysisResponse: Basic clothing analysis results
        
    Raises:
        HTTPException: If there's an error processing the image or communicating with Ollama
    """
    start_time = time.time()
    temp_path = None
    try:
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image)
            temp_path = temp_file.name
        
        # Generate the prompt
        prompt = _generate_clothing_prompt()
        
        try:
            # Call Ollama's chat with the image
            model_start_time = time.time()
            response = chat(
                model=settings.model_name,
                format=ClothingAnalysisResponse.model_json_schema(),
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [temp_path],
                    },
                ],
                options={'temperature': settings.model_temperature}
            )
            model_time = time.time() - model_start_time
            print(f"Model inference time: {model_time:.2f} seconds")
            
            # Parse the response
            try:
                # First, try to parse the raw response to potentially apply post-processing
                raw_response = json.loads(response.message.content)
                
                # Post-processing for eyewear detection
                # If the model is uncertain about eyewear, we'll do a second pass with a focused prompt
                if (not raw_response.get('clothing_info', {}).get('eyewear') or 
                    raw_response.get('clothing_info', {}).get('eyewear', {}).get('type') == 'unknown'):
                    
                    # Try a second pass with a focused prompt for eyewear detection
                    eyewear_prompt = """Focus ONLY on detecting eyewear in this image.
                    
                    Look very carefully at the person's face and eyes. 
                    
                    1. Are they wearing glasses or sunglasses?
                    2. Look for thin frames, clear lenses, or subtle eyewear that might be easily missed.
                    3. Check for reflections, lens edges, or frame outlines around the eyes.
                    
                    Respond with a JSON object with these fields:
                    {
                      "wearing": true/false,
                      "type": "glasses"/"sunglasses"/"reading glasses"/"unknown",
                      "frame_style": "thin"/"thick"/"rimless"/"wire"/"plastic"/"unknown"
                    }
                    
                    If you're absolutely certain there are no glasses, set wearing to false.
                    """
                    
                    eyewear_response = chat(
                        model=settings.model_name,
                        messages=[
                            {
                                'role': 'user',
                                'content': eyewear_prompt,
                                'images': [temp_path],
                            },
                        ],
                        options={'temperature': 0.1}  # Lower temperature for more focused detection
                    )
                    
                    try:
                        eyewear_data = json.loads(eyewear_response.message.content)
                        # Update the raw response with the focused eyewear detection
                        if 'clothing_info' not in raw_response:
                            raw_response['clothing_info'] = {}
                        raw_response['clothing_info']['eyewear'] = eyewear_data
                        print("Enhanced eyewear detection applied")
                    except (json.JSONDecodeError, KeyError):
                        print("Failed to enhance eyewear detection")
                
                # Always do a second pass for description and thermal properties
                # This ensures we always get a description even if the first pass doesn't provide one
                
                # Try a second pass with a focused prompt for description and thermal assessment
                description_prompt = """Provide a detailed description of the clothing visible in this image.
                
                IMPORTANT: You MUST provide a detailed description of what you see.
                
                Based ONLY on what you can see in the image (do not make assumptions about clothing that is not visible):
                
                1. Provide a detailed general description of the visible outfit (3-4 sentences).
                   - Describe the specific clothing items visible
                   - Mention colors, patterns, and materials if identifiable
                   - Describe how the items are worn together (layering, style)
                
                2. Describe the thermal insulation properties of the visible clothing.
                   - How warm or cool would this clothing be?
                   - Consider fabric thickness, coverage, and layering
                
                3. Describe what weather conditions this outfit would be suitable for.
                   - Which season(s) would this be appropriate for?
                   - Suggest temperature ranges if possible
                
                Respond with a JSON object with these fields:
                {
                  "general_description": "Detailed description of the visible outfit",
                  "thermal_properties": "Description of thermal insulation (e.g., warm, cool, lightweight)",
                  "weather_appropriateness": "Description of suitable weather conditions"
                }
                
                IMPORTANT: If only part of the body is visible, acknowledge this limitation in your assessment.
                """
                
                description_response = chat(
                    model=settings.model_name,
                    messages=[
                        {
                            'role': 'user',
                            'content': description_prompt,
                            'images': [temp_path],
                        },
                    ],
                    options={'temperature': 0.3}
                )
                
                try:
                    description_data = json.loads(description_response.message.content)
                    # Update the raw response with the description and thermal assessment
                    raw_response['general_description'] = description_data.get('general_description', 'No description available')
                    raw_response['thermal_properties'] = description_data.get('thermal_properties', '')
                    raw_response['weather_appropriateness'] = description_data.get('weather_appropriateness', '')
                    print("Enhanced description and thermal assessment applied")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Failed to enhance description: {str(e)}")
                    # Ensure we have at least a basic description if JSON parsing fails
                    if 'general_description' not in raw_response or not raw_response['general_description']:
                        raw_response['general_description'] = "The image shows a person wearing clothing. Detailed description could not be generated."
                
                # Now validate the potentially modified response
                analysis = ClothingAnalysisResponse.model_validate(raw_response)
                
                total_time = time.time() - start_time
                print(f"Total analysis time: {total_time:.2f} seconds")
                                    
                return analysis
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to parse model response as valid JSON"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to validate model response: {str(e)}"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to communicate with Ollama model: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
        
    finally:
        # Clean up the temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass  # Ignore cleanup errors
