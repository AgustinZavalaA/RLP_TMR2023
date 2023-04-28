from dataclasses import dataclass
from typing import Optional


@dataclass
class BoundingBox:
    """
    Bounding box of an object detected by the model
    """
    x: int
    y: int
    width: int
    height: int


@dataclass
class Detection:
    category: str
    score: float
    bounding_box: BoundingBox
    frame_width: int
    frame_height: int
    approx_size: Optional[int]


@dataclass
class Centroid:
    x: int
    y: int
