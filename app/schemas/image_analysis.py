from pydantic import BaseModel
from .clothing import FullBodyClothingInfo

class ClothingAnalysisResponse(BaseModel):
    """Response model for clothing analysis"""
    clothing_info: FullBodyClothingInfo
