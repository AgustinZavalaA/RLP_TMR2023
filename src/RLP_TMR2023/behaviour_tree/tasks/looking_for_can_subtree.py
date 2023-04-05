import math
import platform

import cv2
import py_trees.common

from RLP_TMR2023.behaviour_tree.tasks.TODO_behaviour import TODOBehaviour
from RLP_TMR2023.constants.cv_values import black_can_lower_hsv, black_can_upper_hsv, black_can_kernel_size
from RLP_TMR2023.hardware_controllers.camera_controller import camera_controller_factory
from RLP_TMR2023.image_processing.hsv_filter import hsv_filter
from RLP_TMR2023.image_processing.tf_object_detection import get_detections


class CheckIfThereIsDetection(py_trees.behaviour.Behaviour):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.READ)

    def update(self) -> py_trees.common.Status:
        if self.blackboard.detection is not None:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class SearchForCanWithTF(py_trees.behaviour.Behaviour):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="current_frame", access=py_trees.common.Access.READ)

        self.camera_controller = camera_controller_factory(platform.machine())

    def update(self) -> py_trees.common.Status:
        detections = get_detections(self.blackboard.current_frame, self.camera_controller.detector)

        if detections:
            can_detections = [detection for detection in detections if detection.category.find("can") != -1]
            if can_detections:
                best_detection = max(can_detections, key=lambda detection: detection.score)
                self.blackboard.detection = best_detection
        return py_trees.common.Status.SUCCESS


class SearchForCanWithCV(py_trees.behaviour.Behaviour):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="current_frame", access=py_trees.common.Access.READ)

        self.camera_controller = camera_controller_factory(platform.machine())

    def distance(self, x: int, y: int) -> float:
        curr_x = self.blackboard.detection.bounding_box.x
        curr_y = self.blackboard.detection.bounding_box.y
        return math.sqrt((x - curr_x) ** 2 + (y - curr_y) ** 2)

    def update(self) -> py_trees.common.Status:
        img_w, img_h = self.blackboard.current_frame.shape[1], self.blackboard.current_frame.shape[0]
        x, y = img_w // 2 + self.blackboard.detection.bounding_box.x, img_h // 2 + self.blackboard.detection.bounding_box.x
        w, h = self.blackboard.detection.bounding_box.width, self.blackboard.detection.bounding_box.height

        extended_factor = 0.5
        x = int(x - w * extended_factor) if x - w * extended_factor > 0 else 0
        y = int(y - h * extended_factor) if y - h * extended_factor > 0 else 0
        w = int(w * (1 + extended_factor)) if x + w * (1 + extended_factor) < img_w else img_w
        h = int(h * (1 + extended_factor)) if y + h * (1 + extended_factor) < img_h else img_h

        roi_img = self.blackboard.current_frame[y:y + h, x:x + w]

        roi_img_bgr = cv2.cvtColor(roi_img, cv2.COLOR_RGB2BGR)

        filtered_roi = hsv_filter(roi_img_bgr, black_can_lower_hsv, black_can_upper_hsv, black_can_kernel_size)

        contours, _ = cv2.findContours(filtered_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        centroids = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            rect = cv2.boundingRect(contour)
            c_w, c_h = abs(rect[2] - rect[0]), abs(rect[3] - rect[1])
            if c_w in range(int(w * 0.9), int(w * 1.1)) and c_h in range(int(h * 0.9), int(h * 1.1)):
                centroids.append((cx, cy))

        best_centroid = min(centroids,
                            key=lambda centroid: self.distance(centroid[0], centroid[1])) if centroids else None

        if best_centroid is None:
            self.blackboard.detection = None
            cv2.destroyWindow("roi")
            cv2.destroyWindow("roi_thresh")
        else:
            self.blackboard.detection.bounding_box.x = best_centroid[0] - w // 2
            self.blackboard.detection.bounding_box.y = best_centroid[1] - h // 2

            cv2.imshow("roi", roi_img_bgr)
            cv2.imshow("roi_thresh", filtered_roi)
            cv2.waitKey(1)

        return py_trees.common.Status.SUCCESS


def create_look_for_can_subtree() -> py_trees.composites.Selector:
    subtree_root = py_trees.composites.Selector(name="Look for can subtree", memory=False)

    can_found = py_trees.composites.Sequence(name="Can found", memory=False)
    can_found_guard = py_trees.decorators.EternalGuard(
        name="is not scanning the arena?",
        child=can_found,
        condition=lambda blackboard: blackboard.waiting_start_time is None or blackboard.moving_start_time is None,
        blackboard_keys={"waiting_start_time", "moving_start_time"},
    )

    get_detection = py_trees.composites.Selector(name="Get Detection", memory=False)
    can_found.add_children([
        get_detection,
        TODOBehaviour("calcoffset and move motors"),
    ])

    search_for_can_tf = py_trees.composites.Sequence(name="Search for can with TF", memory=False)
    get_detection.add_children([
        py_trees.decorators.EternalGuard(
            name="exists detection?",
            child=SearchForCanWithCV("Calculate detection with computer vision"),
            condition=lambda blackboard: blackboard.detection is not None,
            blackboard_keys={"detection"},
        ),
        search_for_can_tf,
    ])

    search_for_can_tf.add_children([
        SearchForCanWithTF("Search for can with TF"),
        CheckIfThereIsDetection("Is there a detection?"),
    ])

    subtree_root.add_children([
        can_found_guard,
        TODOBehaviour("Scan arena"),
    ])
    return subtree_root
