import logging
from dataclasses import dataclass
from typing import Optional

import cv2
from tflite_support.task import vision

from RLP_TMR2023.image_processing.visualization import visualize_detections_bounding_rects

logger = logging.getLogger(__name__)


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


def get_detections(cap, detector, camera_width_height, using_mock: bool = False) -> Optional[list[Detection]]:
    if using_mock:
        logger.info("Detecting objects")
    success, image = cap.read()
    if not success:
        logger.error("Failed to read image from camera")
        return None

    image = cv2.flip(image, 1)
    # Convert the image from BGR to RGB as required by the TFLite model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Create a TensorImage object from the RGB image.
    input_tensor = vision.TensorImage.create_from_array(rgb_image)
    # Run object detection estimation using the model.
    detection_result = detector.detect(input_tensor)
    # Draw key points and edges on input image if using mock
    if using_mock:
        image = visualize_detections_bounding_rects(image, detection_result)
        cv2.imshow('current frame', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt

    detections = [
        Detection(
            category=d.categories[0].category_name,
            score=d.categories[0].score,
            bounding_box=BoundingBox(
                x=d.bounding_box.origin_x - camera_width_height[0] / 2,
                y=d.bounding_box.origin_y - camera_width_height[1] / 2,
                width=d.bounding_box.width,
                height=d.bounding_box.height,
            ),
        )
        for d in detection_result.detections
    ]

    if using_mock:
        logger.info(f"Detection result: {detections}")
    return detections
