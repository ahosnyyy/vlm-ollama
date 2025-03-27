from pydantic import BaseModel, Field
from .clothing import FullBodyClothingInfo
from typing import Optional

class ClothingAnalysisResponse(BaseModel):
    """Response model for clothing analysis"""
    clothing_info: FullBodyClothingInfo
    general_description: str = Field(
        ..., 
        description="General description of the outfit including thermal properties and weather appropriateness"
    )
    thermal_properties: str = Field(
        ..., 
        description="Description of the thermal insulation properties of the clothing (e.g., 'warm', 'cool', 'lightweight')"
    )
    weather_appropriateness: str = Field(
        ..., 
        description="Description of what weather conditions the outfit would be suitable for"
    )
