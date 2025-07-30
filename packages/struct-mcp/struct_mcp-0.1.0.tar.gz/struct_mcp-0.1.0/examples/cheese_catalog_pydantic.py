from typing import List, Optional
from pydantic import BaseModel, Field


class CheeseInventory(BaseModel):
    """Artisanal cheese catalog with provenance tracking"""

    cheese_id: str = Field(description="Unique identifier for each cheese")
    name: str = Field(description="Display name of the cheese")
    stinkiness_level: Optional[int] = Field(description="Stinkiness rating from 1-10")
    emoji: str = Field(description="Visual representation for UI")
    origin_country: Optional[str] = Field(description="Country of origin")
    tasting_notes: Optional[List[str]] = Field(
        description="Expert tasting descriptions"
    )
    is_available: bool = Field(
        description="Currently in stock and available for purchase"
    )
    price_per_pound: Optional[float] = Field(
        description="Current retail price per pound in USD"
    )
