from dataclasses import dataclass


@dataclass
class BoundingBox:
    """
    Bounding box of an object detected by the model
    All coordinates are relative to the center of the image
    """
    x: float
    y: float
    width: float
    height: float


@dataclass
class Detection:
    category: str
    score: float
    bounding_box: BoundingBox
