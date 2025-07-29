"""
ImageObjectInput.py
-------------------
Defines the input data model for object-level image processing requests.
Used by image-processing-service to send metadata and cropped image to text-processing-service.
"""

from pydantic import BaseModel
from typing import Dict


class ImageObjectInput(BaseModel):
    """
    DTO representing a single detected object input from the image-processing-service.

    Attributes
    ----------
    metadata : dict
        Dictionary containing object detection metadata such as coordinates, 
        labels, or model confidence.
    image : str
        Base64-encoded string of the cropped object image.
    """
    metadata: Dict
    image: str

