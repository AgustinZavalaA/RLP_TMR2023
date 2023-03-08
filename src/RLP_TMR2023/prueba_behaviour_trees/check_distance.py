import enum
import logging

import py_trees.common
import py_trees.console

logger = logging.getLogger(__name__)

class CanViewingToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Can distance to BB")
        #self.blackboard = self.attach_blackboard_client(name=self.name)
        #self.blackboard.register_key("distance", access=py_trees.common.Access.WRITE)
        logger.info("Can distance to BB")
        return py_trees.common.Status.SUCCESS

class Distances(enum.Enum):
    CLOSE = enum.auto()
    FAR = enum.auto()
    GOOD = enum.auto()

def get_can_distance_gathering() -> py_trees.behaviour.Behaviour:
    can_distance = py_trees.composites.Sequence(name="Can distance", memory=False)
    can_distance.add_child(CanViewingToBB())
    return can_distance

def get_actions_subtree() -> py_trees.behaviour.Behaviour:
    actions = py_trees.composites.Selector(name="Actions", memory=False)
    actions.add_child(create_can_distance())
    return actions

# Falta blackboard variable
def can_distance(distance: Distances) -> py_trees.behaviour.Behaviour:
    if distance == Distances.CLOSE:
        return return_value
    elif distance == Distances.FAR:
        return return_value
    else:
        return return_value
    
    return return_value

def create_can_distance() -> py_trees.behaviour.Behaviour:
    can_viewing_sequence = py_trees.composites.Selector(name="Posibble scenarios", memory=False)
    can_distance.add_child(py_trees.decorators.EternalGuard(
        name="Is the can to close?",
        condition=lambda blackboard: condition_can(blackboard, Distances.CLOSE),
        # lefts the blackboard variable
        child=py_trees.behaviours.Success(name="Close")
    ))
    can_distance.add_child(py_trees.decorators.EternalGuard(
        name="Is the can far?",
        condition=lambda blackboard: condition_can(blackboard, Distances.FAR),
        #lefts blackboard variable
        child=py_trees.behaviours.Success(name="Far")
    ))
    can_distance.add_child(py_trees.decorators.EternalGuard(
        name="Is the can in a good distance?",
        condition=lambda blackboard: condition_can(blackboard, Distances.GOOD),
        # lefts blackboard variable
        child=py_trees.behaviours.Success(name="Good")
    ))
    
    can_distance.add_child(py_trees.behaviours.Failure(name="Can't see the can boss"))
    
    return can_distance


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