import logging

import py_trees.behaviour
from py_trees import common

logger = logging.getLogger(__name__)


class TFDetection(py_trees.behaviour.Behaviour):
    def __init__(self) -> None:
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("detection", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("centroid", access=py_trees.common.Access.WRITE)

    def update(self) -> common.Status:
        pass


def create_look_for_can_subtree() -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Sequence("Look for can", memory=False)

    find_can = py_trees.composites.Selector("Find Can", memory=False)
    # add calc offset

    root.add_children([find_can])

    find_can.add_children([
        py_trees.decorators.EternalGuard(
            "Is TF detection None?",
            TFDetection(),
            condition=lambda blackboard: blackboard.detection is None

        )
    ])

    return root
