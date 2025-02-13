from ollama import chat
from fastapi import HTTPException
from app.schemas.image_analysis import ClothingAnalysisResponse
from app.core.config import settings
import tempfile
import os
import json

def _generate_clothing_prompt() -> str:
    """Generate a prompt for visible clothing analysis with strict guidelines to avoid assumptions"""
    return """Analyze only the clearly visible clothing and accessories in this image. Follow these strict rules:

1. DO NOT include any item that is partially visible, obscured, or ambiguous. Only fully visible and identifiable items should be reported.

2. List the visible upper body clothing items from this restricted list:
   - short sleeve top, long sleeve top, short sleeve outwear, long sleeve outwear,
     vest, sweater, cape
   Specify the sleeve length only if it is fully visible and unambiguous (short, long, sleeveless).

3. List the visible lower body clothing items from this restricted list:
   - shorts, pants, skirt
   Do not infer or assume the presence of these items if they are not entirely visible.

4. List the visible full-body clothing items from this restricted list:
   - short sleeve dress, long sleeve dress, vest dress, sling dress, jumpsuit
   Specify the sleeve length only if it is fully visible and unambiguous (short, long, sleeveless).

5. List visible accessories from this restricted list:
   - glasses, hat, glove, scarf, hood
   Only include accessories that are entirely visible and clearly identifiable.
   

Do not infer or assume the existence of any clothing or accessory that is not fully visible. Provide only details of items that meet these strict criteria.
You could get layered clothing as well.
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
            
            # Parse the response
            try:
                analysis = ClothingAnalysisResponse.model_validate_json(response.message.content)
                
                # Save raw response to JSON file in the output directory
                json_output_path = os.path.join('c:/Users/ahosny/Documents/Projects/vlm-app/fashionpedia', os.path.splitext(image_name)[0] + '.json')
                with open(json_output_path, 'w') as f:
                    json.dump(json.loads(response.message.content), f, indent=2)
                                    
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
