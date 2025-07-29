"""
ImageDetectionResult.py
------------------------
Defines shared data models representing results from object detection.
"""

from pydantic import BaseModel, Field
from typing import List


class BoundingBox(BaseModel):
    """
    Represents a single detected bounding box from object detection.

    Attributes
    ----------
    label : str
        The class label (e.g., "person", "car").
    confidence : float
        The detection confidence score.
    bbox : List[float]
        The bounding box coordinates [x1, y1, x2, y2].
    """
    label: str = Field(..., min_length=1)
    confidence: float
    # [x1, y1, x2, y2]
    bbox: List[float] 


class ImageProcessorResult(BaseModel):
    """
    Represents a full detection result from the image processing service.

    Attributes
    ----------
    image_id : str
        Unique identifier for the image.
    boxes : List[BoundingBox]
        List of all detected bounding boxes.
    annotated_image_path : str
        Path to the locally saved image with visual bounding boxes.
    """
    image_id: str = Field(..., min_length=1)
    boxes: List[BoundingBox]
    annotated_image_path: str
