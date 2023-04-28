import logging
import platform
import time

import py_trees.behaviour
from py_trees import common

from RLP_TMR2023.common_types.common_types import Centroid
from RLP_TMR2023.hardware_controllers.buzzer_controller import buzzer_controller_factory
from RLP_TMR2023.hardware_controllers.camera_controller import camera_controller_factory
from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorDirection, MotorSide
from RLP_TMR2023.hardware_controllers.servos_controller import servos_controller_factory, ServoStatus, ServoPair
from RLP_TMR2023.image_processing.calculate_centroid import can_candidates, biggest_rect_strategy
from RLP_TMR2023.image_processing.image_filtering import otsu_filtering
from RLP_TMR2023.image_processing.tf_object_detection import get_detections

logger = logging.getLogger(__name__)


class TFDetection(py_trees.behaviour.Behaviour):
    def __init__(self) -> None:
        super().__init__("TF Detection")
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("detection", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("centroid", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("current_frame", access=py_trees.common.Access.READ)

        self.camera = camera_controller_factory(platform.machine())
        self.buzzer = buzzer_controller_factory(platform.machine())

    def update(self) -> common.Status:
        # make a sound
        # self.buzzer.play(Melody.CAN_FOUND)

        detections = get_detections(self.blackboard.current_frame, self.camera.detector)
        if not detections:
            return py_trees.common.Status.FAILURE
        cans_detections = [d for d in detections if d.category.find("can") != -1]
        if not cans_detections:
            return py_trees.common.Status.FAILURE
        biggest_can = max(cans_detections, key=lambda c: c.approx_size)
        logger.info(f"{biggest_can=}")
        self.blackboard.detection = biggest_can
        x, y, w, h = biggest_can.bounding_box.x, biggest_can.bounding_box.y, \
            biggest_can.bounding_box.width, biggest_can.bounding_box.height
        image_cropped = self.blackboard.current_frame[x:x + w, y:y + h]
        filtered = otsu_filtering(image_cropped)
        bbs_and_centroids = can_candidates(filtered, biggest_rect_strategy)
        centroid = Centroid(biggest_can.bounding_box.x + bbs_and_centroids[0][1][0],
                            biggest_can.bounding_box.y + bbs_and_centroids[0][1][1])
        self.blackboard.centroid = centroid
        logger.info(f"{centroid=}")
        return py_trees.common.Status.SUCCESS


class CenterCan(py_trees.behaviour.Behaviour):
    def __init__(self) -> None:
        super().__init__("Centering Can")
        self.blackboard = self.attach_blackboard_client()

        self.blackboard.register_key("centroid", access=py_trees.common.Access.READ)
        self.blackboard.register_key("detection", access=py_trees.common.Access.READ)

        self.motors = motors_controller_factory(platform.machine())

    def update(self) -> common.Status:
        tolerance_percentage = 0.1
        x_offset = self.blackboard.centroid.x - (self.blackboard.detection.frame_width // 2)
        tolerance = int(self.blackboard.detection.frame_width * tolerance_percentage) // 2

        if x_offset in range(-tolerance, tolerance):
            logger.info("Already in center")
            self.motors.stop()
            return py_trees.common.Status.SUCCESS

        if x_offset > 0:
            self.motors.move(MotorSide.RIGHT, 15, MotorDirection.FORWARD)
            self.motors.move(MotorSide.LEFT, 15, MotorDirection.BACKWARD)
        else:
            self.motors.move(MotorSide.RIGHT, 15, MotorDirection.BACKWARD)
            self.motors.move(MotorSide.LEFT, 15, MotorDirection.FORWARD)
        return py_trees.common.Status.FAILURE


class GetCloseToCan(py_trees.behaviour.Behaviour):
    def __init__(self) -> None:
        super().__init__("Get close to Can")
        self.blackboard = self.attach_blackboard_client()

        self.blackboard.register_key("centroid", access=py_trees.common.Access.READ)
        self.blackboard.register_key("detection", access=py_trees.common.Access.READ)

        self.motors = motors_controller_factory(platform.machine())

    def update(self) -> common.Status:
        tolerance_percentage = 0.1
        cut_line_factor = 0.6
        y_offset = self.blackboard.centroid.y - (self.blackboard.detection.frame_height * cut_line_factor)
        tolerance = int(self.blackboard.detection.frame_height * tolerance_percentage) // 2

        if y_offset in range(-tolerance, tolerance):
            logger.info("At the perfect distance")
            self.motors.stop()
            return py_trees.common.Status.SUCCESS

        if y_offset < 0:
            self.motors.move(MotorSide.RIGHT, 15, MotorDirection.FORWARD)
            self.motors.move(MotorSide.LEFT, 15, MotorDirection.FORWARD)
        else:
            self.motors.move(MotorSide.RIGHT, 15, MotorDirection.BACKWARD)
            self.motors.move(MotorSide.LEFT, 15, MotorDirection.BACKWARD)
        return py_trees.common.Status.FAILURE


class PickCan(py_trees.behaviour.Behaviour):
    def __init__(self) -> None:
        super().__init__("Picking can")
        self.servos = servos_controller_factory(platform.machine())
        self.motors = motors_controller_factory(platform.machine())

    def update(self) -> common.Status:
        self.servos.move(ServoPair.ARM, ServoStatus.EXPANDED)
        self.servos.move(ServoPair.CLAW, ServoStatus.EXPANDED)

        self.motors.move(MotorSide.LEFT, 70, MotorDirection.FORWARD)
        self.motors.move(MotorSide.RIGHT, 70, MotorDirection.FORWARD)
        time.sleep(1)
        self.motors.stop()

        self.servos.move(ServoPair.CLAW, ServoStatus.RETRACTED)
        self.servos.move(ServoPair.ARM, ServoStatus.RETRACTED)

        return py_trees.common.Status.SUCCESS


def create_look_for_can_subtree() -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Sequence("Look for can", memory=False)

    find_can = py_trees.composites.Selector("Find Can", memory=False)
    # add calc offset
    recollect_can = py_trees.composites.Sequence("Recollect can", memory=False)
    recollect_can.add_children([
        CenterCan(),
        GetCloseToCan(),
        PickCan()
    ])

    root.add_children([find_can, recollect_can])

    find_can.add_children([
        # py_trees.decorators.EternalGuard(
        #     "Is TF detection None?",
        #     TFDetection(),
        #     condition=lambda blackboard: blackboard.detection is None,
        #     blackboard_keys={"detection"}
        # )
        TFDetection()
    ])

    return root
