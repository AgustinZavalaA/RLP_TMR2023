import platform

from RLP_TMR2023.hardware_controllers.singleton import Singleton
from abc import abstractmethod
from RLP_TMR2023.constants import object_detection_values
import logging
from tensorflow_lite_support.python.task.processor.proto.detections_pb2 import DetectionResult
import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
from importlib.resources import path
from RLP_TMR2023 import tf_models
from RLP_TMR2023.example_tflite import utils
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

@dataclass
class Detection:
    category: str
    score: float
    bounding_box: BoundingBox

def get_default_model() -> str:
    with path(tf_models, object_detection_values.TF_MODEL) as model_path:
        return str(model_path)


class CameraController(metaclass=Singleton):
    def __init__(self) -> None:
        self._model = get_default_model()
        self._camera_id = object_detection_values.CAMERA_ID
        self._number_threads = object_detection_values.NUMBER_THREADS
        self._enable_edgetpu = object_detection_values.ENABLE_EDGETPU

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def detect_objects(self) -> list[DetectionResult]:
        pass

    @abstractmethod
    def disable(self) -> None:
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
        # Start capturing video input from the camera
        self._cap = cv2.VideoCapture(self._camera_id)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._camera_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._camera_height)

        # Initialize the object detection model
        base_options = core.BaseOptions(
            file_name=self._model, use_coral=self._enable_edgetpu, num_threads=self._number_threads)
        detection_options = processor.DetectionOptions(
            max_results=3, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options)
        self._detector = vision.ObjectDetector.create_from_options(options)

    def detect_objects(self) -> list[Detection]:
        logger.info("Detecting objects")
        success, image = self._cap.read()
        if not success:
            logger.error("Failed to read image from camera")
            return

        image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)

        # Run object detection estimation using the model.
        detection_result = self._detector.detect(input_tensor)

        # Draw keypoints and edges on input image
        image = utils.visualize(image, detection_result)

        cv2.imshow('object_detector', image)

        detections = [
            Detection(
                category=d.categories[0].category_name,
                score=d.categories[0].score,
                bounding_box=BoundingBox(
                    x=d.bounding_box.origin_x,
                    y=d.bounding_box.origin_y,
                    width=d.bounding_box.width,
                    height=d.bounding_box.height,
                ),
            )
            for d in detection_result.detections
        ]

        logger.info(f"Detection result: {detection_result.detections}")
        logger.info(f"Detection result 2: {detections}")
        return detections

    def disable(self) -> None:
        logger.info("Disabling camera")
        self._cap.release()
        cv2.destroyAllWindows()


def camera_controller_factory(platform: str) -> CameraController:
    # TODO change this to return CameraControllerRaspberryPi() when running on the raspberry pi
    return CameraControllerMock()


def main():
    logging.basicConfig(level=logging.DEBUG)
    camera = camera_controller_factory(platform.machine())
    camera.setup()
    while True:
        camera.detect_objects()
        if cv2.waitKey(5) & 0xFF == 27:
            break
    camera.disable()


if __name__ == '__main__':
    main()
