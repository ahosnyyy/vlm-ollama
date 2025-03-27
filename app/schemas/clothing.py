from typing import Optional, Literal, List
from pydantic import BaseModel, Field

class UpperBodyClothingItem(BaseModel):
    type: Optional[Literal[
        "shirt", "t-shirt", "blouse", "tank top", "polo shirt", 
        "sweater", "hoodie", "jacket", "coat", "dress", "jumpsuit", "overalls"
    ]] = "unknown"
    sleeve_length: Optional[Literal[
        "short", "long", "three-quarter", "sleeveless", "unknown"
    ]] = "unknown"

# Lower Body Clothing Schema
class LowerBodyClothingItem(BaseModel):
    type: Optional[Literal[
        "jeans", "trousers", "shorts", "skirt", "leggings", "sweatpants"
    ]] = "unknown"
    length: Optional[Literal["short", "knee-length", "ankle-length", "unknown"]] = "unknown"

# Eyewear Schema
class EyewearItem(BaseModel):
    wearing: bool = False
    type: Optional[Literal[
        "glasses", "sunglasses", "reading glasses", "sports glasses", 
        "prescription glasses", "safety glasses", "unknown"
    ]] = "unknown"
    frame_style: Optional[Literal[
        "thin", "thick", "rimless", "semi-rimless", "wire", "plastic", "unknown"
    ]] = "unknown"

# Headwear Schema
class HeadwearItem(BaseModel):
    wearing: bool
    type: Optional[Literal["hat", "cap", "beanie", "hood", "unknown"]] = "unknown"

# Accessories Schema
class AccessoriesItem(BaseModel):
    wearing: bool
    type: Optional[Literal[
        "scarf", "gloves", "belt", "necklace", "earrings", "watch", "bracelet", "unknown"
    ]] = "unknown"

# Main Schema for Full Clothing Detection
class FullBodyClothingInfo(BaseModel):
    upper_body: Optional[UpperBodyClothingItem] = None
    lower_body: Optional[LowerBodyClothingItem] = None
    eyewear: Optional[EyewearItem] = None
    headwear: Optional[HeadwearItem] = None
    accessories: Optional[AccessoriesItem] = None
