from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class UpperBodyClothingItem(BaseModel):
    """Detailed information about an upper-body clothing item"""
    type: List[Literal[
        'short sleeve top', 'long sleeve top', 'short sleeve outwear', 'long sleeve outwear',
        'vest', 'sweater', 'cape'
    ]] = Field(..., description="Type of upper body clothing item")

    sleeve_length: Optional[Literal['short', 'long', 'sleeveless']] = Field(
        None, description="Sleeve length if applicable"
    )


class LowerBodyClothingItem(BaseModel):
    """Detailed information about a lower-body clothing item"""
    type: Literal['shorts', 'pants', 'skirt'] = Field(
        ..., description="Type of lower body clothing item"
    )


class FullBodyClothingItem(BaseModel):
    """Detailed information about a full-body clothing item"""
    type: Literal[
        'short sleeve dress', 'long sleeve dress', 'vest dress',
        'sling dress', 'jumpsuit'
    ] = Field(..., description="Type of full-body clothing item")

    sleeve_length: Optional[Literal['short', 'long', 'sleeveless']] = Field(
        None, description="Sleeve length if applicable"
    )


class Accessories(BaseModel):
    """Accessories like glasses, hats, and scarves"""
    type: List[Literal['glasses', 'hat', 'glove', 'scarf', 'hood']] = Field(
        ..., description="Type of accessory"
    )


class FullBodyClothingInfo(BaseModel):
    """Comprehensive full-body clothing and accessories information"""
    upper_body: List[UpperBodyClothingItem] = Field(
        default_factory=list,
        description="List of upper body clothing items worn"
    )
    lower_body: List[LowerBodyClothingItem] = Field(
        default_factory=list,
        description="List of lower body clothing items worn"
    )
    full_body: List[FullBodyClothingItem] = Field(
        default_factory=list,
        description="List of full-body clothing items worn"
    )
    accessories: List[Accessories] = Field(
        default_factory=list,
        description="List of accessories worn"
    )