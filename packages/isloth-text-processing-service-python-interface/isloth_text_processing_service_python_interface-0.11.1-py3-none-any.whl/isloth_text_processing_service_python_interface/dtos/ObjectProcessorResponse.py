"""
ObjectProcessingResult.py
--------------------------
Defines the shared output schema for object processing results across services.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ObjectProcessorResult(BaseModel):
    """
    Represents the result of processing a visual object using the BLIP model and product helper logic.

    Attributes
    ----------
    description : str
        Caption generated for the image object using the BLIP model.

    matched_products : List[Dict[str, Any]]
        List of products matched based on the caption and product catalog.
    """
    description: str = Field(..., min_length=1)
    matched_products: List[Dict[str, Any]]
