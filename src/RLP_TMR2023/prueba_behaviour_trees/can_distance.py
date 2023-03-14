import enum
import logging
from typing import Any

import py_trees.common
import py_trees.console
from py_trees import common

from RLP_TMR2023.prueba_behaviour_trees.main_prueba import condition_can

logger = logging.getLogger(__name__)


class CanViewingToBB(py_trees.behaviour.Behaviour):

    def __init__(self):
        super().__init__(name="Can distance to BB")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("distance", access=py_trees.common.Access.WRITE)
        logger.info("Can distance to BB")

    def update(self) -> common.Status:
        self.blackboard.detection = "ghettos"
        return py_trees.common.Status.SUCCESS
        pass


# TODO
class Distances(enum.Enum):
    CLOSE = enum.auto()
    FAR = enum.auto()
    GOOD = enum.auto()


def get_can_distance_gathering() -> py_trees.behaviour.Behaviour:
    can_distance_bb = py_trees.composites.Sequence(name="Can distance", memory=False)
    can_distance_bb.add_child(CanViewingToBB())
    return can_distance_bb


def get_actions_subtree() -> py_trees.behaviour.Behaviour:
    actions = py_trees.composites.Selector(name="Actions", memory=False)
    actions.add_child(create_can_distance())
    return actions


# def can_distance(blackboard, distance: Distances) -> Distances:
#
#    if distance == Distances.CLOSE:
#        return_value = distance
#    elif distance == Distances.FAR:
#        return_value = distance
#    else:
#        return_value = distance

#    return return_value


def create_can_distance() -> py_trees.behaviour.Behaviour | Any:
    can_viewing_sequence = py_trees.composites.Selector(name="Possible scenarios", memory=False)
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can to close?",
        condition=lambda blackboard: Distances.CLOSE,
        blackboard_keys={"distance"},
        child=py_trees.behaviours.Success(name="Close")
    ))
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can far?",
        condition=lambda blackboard: Distances.FAR,
        blackboard_keys={"distance"},
        child=py_trees.behaviours.Success(name="Far")
    ))
    can_viewing_sequence.add_child(py_trees.decorators.EternalGuard(
        name="Is the can in a good distance?",
        condition=lambda blackboard: Distances.GOOD,
        blackboard_keys={"distance"},
        child=py_trees.behaviours.Success(name="Good")
    ))

    can_viewing_sequence.add_child(py_trees.behaviours.Failure(name="Can't see the can boss"))

    return can_viewing_sequence


def create_root() -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Selector(name="Close or far", memory=False)

    root.add_child(get_can_distance_gathering())
    root.add_child(get_actions_subtree())
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


if __name__ == "__main__":
    main()
