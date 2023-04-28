import logging
from typing import Optional

import cv2
import numpy as np
import numpy.typing as npt
from tflite_support.task import vision

from RLP_TMR2023.common_types.common_types import Detection, BoundingBox
from RLP_TMR2023.image_processing.area_of_can import get_area_of_can

logger = logging.getLogger(__name__)


def get_detections(rgb_image: npt.NDArray[np.uint8], detector: vision.ObjectDetector) -> \
        Optional[list[Detection]]:
    width, height, _ = rgb_image.shape
    # Create a TensorImage object from the RGB image.
    input_tensor = vision.TensorImage.create_from_array(rgb_image)
    # Run object detection estimation using the model.
    detection_result = detector.detect(input_tensor)

    detections = [
        Detection(
            category=d.categories[0].category_name,
            score=d.categories[0].score,
            bounding_box=BoundingBox(
                x=int(d.bounding_box.origin_x) if int(d.bounding_box.origin_x) > 0 else 0,
                y=int(d.bounding_box.origin_y) if int(d.bounding_box.origin_y) > 0 else 0,
                width=int(d.bounding_box.width),
                height=int(d.bounding_box.height),
            ),
            frame_width=width,
            frame_height=height,
            approx_size=get_area_of_can(cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))
        )
        for d in detection_result.detections
    ]

    return detections
