from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.image_analysis import ClothingAnalysisResponse
from app.services.image_analysis import analyze_clothing

router = APIRouter()

@router.post("/analyze", response_model=ClothingAnalysisResponse)
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to analyze an image using VLM model.
    Accepts an image file and returns a detailed description of its contents.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image = await file.read()
        result = await analyze_clothing(image, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))