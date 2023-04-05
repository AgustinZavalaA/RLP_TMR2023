import logging

import py_trees.common
import py_trees.console

from RLP_TMR2023.behaviour_tree.data_recollection.camera import CameraToBB
from RLP_TMR2023.behaviour_tree.data_recollection.distance_sensors import DistanceSensorsToBB
from RLP_TMR2023.behaviour_tree.data_recollection.imu_stuck import IMUToBB
from RLP_TMR2023.behaviour_tree.tasks.TODO_behaviour import TODOBehaviour
from RLP_TMR2023.behaviour_tree.tasks.crash_subtree import create_crash_subtree
from RLP_TMR2023.behaviour_tree.tasks.looking_for_can_subtree import create_look_for_can_subtree

logger = logging.getLogger(__name__)


class SetBBInitialValueNone(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, keys: list[str]):
        super().__init__(name=name)
        self.keys = keys
        self.blackboard = self.attach_blackboard_client(name=name)
        for key in self.keys:
            self.blackboard.register_key(key=key, access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        for key in self.keys:
            self.blackboard.set(key, None)
        return py_trees.common.Status.SUCCESS


def get_data_recollection_subtree() -> py_trees.behaviour.Behaviour:
    data_gathering = py_trees.composites.Sequence(name="Data Gathering", memory=False)

    # Here is where you add every data recollection node
    data_gathering.add_children([
        DistanceSensorsToBB(),
        IMUToBB(),
        CameraToBB(),
        py_trees.decorators.OneShot(
            name="Init values to None",
            child=SetBBInitialValueNone("Init values to None", keys=["detection",
                                                                     "waiting_start_time",
                                                                     "moving_start_time"]),
            policy=py_trees.common.OneShotPolicy.ON_COMPLETION),
    ])

    return data_gathering


def get_tasks_subtree() -> py_trees.behaviour.Behaviour:
    tasks = py_trees.composites.Selector(name="Tasks", memory=False)

    # Here is where you add the behavior of CLaDOS
    tasks.add_child(create_crash_subtree())

    # TODO: do the next subtrees
    tasks.add_children([
        TODOBehaviour("About to enter the water", bypass=False),
        TODOBehaviour("Is stuck in the sand", bypass=False),
        TODOBehaviour("Has enough cans in tray or been more than x minutes", bypass=False),
        create_look_for_can_subtree(),
        TODOBehaviour("Looking for can"),
        TODOBehaviour("Robot Lost"),
    ])

    return tasks


def create_root() -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Parallel(name="Resilient CLaDOS BT",
                                        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                                            synchronise=True
                                        ))
    root.add_child(get_data_recollection_subtree())

    root.add_child(get_tasks_subtree())

    return root
