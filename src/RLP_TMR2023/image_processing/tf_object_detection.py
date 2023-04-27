import logging
from typing import Optional

import numpy as np
import numpy.typing as npt
from tflite_support.task import vision

from RLP_TMR2023.common_types.common_types import Detection, BoundingBox

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
                x=d.bounding_box.origin_x - width // 2,
                y=d.bounding_box.origin_y - height // 2,
                width=d.bounding_box.width,
                height=d.bounding_box.height,
            ),
        )
        for d in detection_result.detections
    ]

    return detections
