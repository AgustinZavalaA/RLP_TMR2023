import enum
import logging

import py_trees.common
import py_trees.console

from RLP_TMR2023.common_types.common_types import Detection, BoundingBox

logger = logging.getLogger(__name__)

"""
En este ejemplo vamos a crear un arbol que simule cuando el robot ve una lata y se tiene que alinear
con ella para poder recogerla.
"""


class CameraDetectionToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Detection_to_BB")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("detection", access=py_trees.common.Access.WRITE)

    def update(self):
        self.blackboard.detection = Detection(
            category="can",
            score=0.9,
            bounding_box=BoundingBox(
                x=-100,
                y=-100,
                width=200,
                height=200
            ),
            frame_height=1,
            frame_width=1,
            approx_size=1
        )
        logging.info("Detection to BB")
        return py_trees.common.Status.SUCCESS


def get_data_gathering_subtree() -> py_trees.behaviour.Behaviour:
    data_gathering = py_trees.composites.Sequence(name="Data Gathering", memory=False)
    data_gathering.add_child(CameraDetectionToBB())
    return data_gathering


def get_tasks_subtree() -> py_trees.behaviour.Behaviour:
    tasks = py_trees.composites.Selector(name="Tasks", memory=False)
    tasks.add_child(create_can_viewing_sequence())
    return tasks


class ConditionType(enum.Enum):
    IN_CENTER = enum.auto()
    ON_RIGHT = enum.auto()
    ON_LEFT = enum.auto()


def condition_can(blackboard, condition_type: ConditionType) -> bool:
    if condition_type == ConditionType.IN_CENTER:
        return_value = blackboard.detection.bounding_box.x + blackboard.detection.bounding_box.width / 2 == 0
    elif condition_type == ConditionType.ON_RIGHT:
        return_value = blackboard.detection.bounding_box.x + blackboard.detection.bounding_box.width / 2 > 0
    else:
        return_value = blackboard.detection.bounding_box.x + blackboard.detection.bounding_box.width / 2 < 0

    return bool(return_value)


def create_can_viewing_sequence() -> py_trees.behaviour.Behaviour:
    can_viewing_sequence = py_trees.composites.Selector(name="Can Viewing Selector", memory=False)

    # check if the can is in the center of the camera
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can in the center of the camera?",
        condition=lambda blackboard: condition_can(blackboard, ConditionType.IN_CENTER),
        blackboard_keys={"detection"},
        child=py_trees.behaviours.Periodic(name="Can in center", n=2)
    ))

    # check if the can is on the right side of the camera
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can on the right side of the camera?",
        condition=lambda blackboard: condition_can(blackboard, ConditionType.ON_RIGHT),
        blackboard_keys={"detection"},
        child=py_trees.behaviours.Success(name="Can on right side")
    ))

    # check if the can is on the left side of the camera
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can on the left side of the camera?",
        condition=lambda blackboard: condition_can(blackboard, ConditionType.ON_LEFT),
        blackboard_keys={"detection"},
        child=py_trees.behaviours.Success(name="Can on left side")
    ))

    # fallback
    can_viewing_sequence.add_child(py_trees.behaviours.Failure(name="Logic error"))

    return can_viewing_sequence


def create_root() -> py_trees.behaviour.Behaviour:
    # root = py_trees.composites.Sequence(name="Viewing Can Example", memory=False)
    root = py_trees.composites.Parallel(name="Resilient CLaDOS BT",
                                        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                                            synchronise=True
                                        ))
    root.add_child(get_data_gathering_subtree())

    root.add_child(get_tasks_subtree())

    return root


def main():
    logging.basicConfig(level=logging.DEBUG)
    behaviour_tree = create_root()
    print(py_trees.display.ascii_tree(behaviour_tree))
    print(py_trees.display.unicode_tree(behaviour_tree))

    while True:
        try:
            behaviour_tree.tick_once()
            print(py_trees.display.ascii_tree(behaviour_tree, show_status=True))
            py_trees.console.read_single_keypress()
        except KeyboardInterrupt:
            py_trees.display.render_dot_tree(behaviour_tree,
                                             target_directory="bt_images",
                                             with_blackboard_variables=True)
            break


if __name__ == '__main__':
    main()
