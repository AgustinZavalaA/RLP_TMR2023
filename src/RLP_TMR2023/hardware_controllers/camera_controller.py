import logging
import platform
from abc import abstractmethod
from importlib.resources import path
from typing import Optional, Mapping, Type

import cv2
import numpy as np
import numpy.typing as npt
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

from RLP_TMR2023 import tf_models
from RLP_TMR2023.constants import object_detection_values
from RLP_TMR2023.hardware_controllers.singleton import Singleton
from RLP_TMR2023.image_processing.tf_object_detection import get_detections

logger = logging.getLogger(__name__)


def get_default_model() -> str:
    with path(tf_models, object_detection_values.TF_MODEL) as model_path:
        return str(model_path)


class CameraController(metaclass=Singleton):
    def __init__(self) -> None:
        self._cap: Optional[cv2.VideoCapture] = None
        self._camera_width: Optional[int] = None
        self._camera_height: Optional[int] = None
        self._model = get_default_model()
        self._camera_id = object_detection_values.CAMERA_ID
        self._number_threads = object_detection_values.NUMBER_THREADS
        self._enable_edgetpu = object_detection_values.ENABLE_EDGETPU
        self._is_mock = False

        self.detector: Optional[vision.ObjectDetector] = None

    def setup(self) -> None:
        # Start capturing video input from the camera
        self._cap = cv2.VideoCapture(self._camera_id)
        print(type(self._cap))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._camera_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._camera_height)

        # Initialize the object detection model
        base_options = core.BaseOptions(
            file_name=self._model, use_coral=self._enable_edgetpu, num_threads=self._number_threads)
        detection_options = processor.DetectionOptions(
            max_results=object_detection_values.MAX_RESULTS, score_threshold=object_detection_values.SCORE_THRESHOLD)
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)
        print(type(self.detector))

    def get_current_frame(self) -> Optional[npt.NDArray[np.uint8]]:
        if self._cap is None:
            logger.error("CameraController is not initialized")
            return None
        success, image = self._cap.read()
        if not success:
            logger.error("Failed to read image from camera")
            return None

        image = cv2.flip(image, 1)
        if self._is_mock:
            cv2.imshow('current frame', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise KeyboardInterrupt
        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image: npt.NDArray[np.uint8] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return rgb_image

    @abstractmethod
    def disable(self) -> None:
        if self._cap is not None:
            self._cap.release()
        cv2.destroyAllWindows()

    def show_image(self) -> None:
        pass


class CameraControllerMock(CameraController):
    """
    This class is a mock for the CameraController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        self._camera_width = object_detection_values.CAMERA_WIDTH_MOCK
        self._camera_height = object_detection_values.CAMERA_HEIGHT_MOCK
        logger.info("Instantiating Singleton CameraControllerMock")

    def setup(self) -> None:
        logger.info("CameraControllerMock.setup() called")
        self._is_mock = True
        super().setup()

    def disable(self) -> None:
        logger.info("Disabling camera")
        super().disable()


class CameraControllerRaspberry(CameraController):
    def __init__(self):
        super().__init__()
        self._camera_width = object_detection_values.CAMERA_WIDTH_MOCK
        self._camera_height = object_detection_values.CAMERA_HEIGHT_MOCK

    def disable(self) -> None:
        logger.info("Disabling camera")
        super().disable()


def camera_controller_factory(architecture: str) -> CameraController:
    constructors: Mapping[str, Type[CameraController]] = {
        "x86_64": CameraControllerMock,
        "aarch64": CameraControllerRaspberry,
        "AMD64": CameraControllerMock,
    }

    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.DEBUG)
    camera = camera_controller_factory(platform.machine())
    camera.setup()
    try:
        while True:
            current_image = camera.get_current_frame()
            if current_image is None:
                continue
            detections = get_detections(current_image, camera.detector)
            print(detections)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
