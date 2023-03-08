import logging

import py_trees.common
import py_trees.console

from RLP_TMR2023.behaviour_tree.data_recollection.distance import DistanceToBB
from RLP_TMR2023.behaviour_tree.tasks.crash_subtree import create_crash_subtree

logger = logging.getLogger(__name__)


def get_data_recollection_subtree() -> py_trees.behaviour.Behaviour:
    data_gathering = py_trees.composites.Sequence(name="Data Gathering", memory=False)

    # Here is where you add every data recollection node
    data_gathering.add_child(DistanceToBB())

    return data_gathering


def get_tasks_subtree() -> py_trees.behaviour.Behaviour:
    tasks = py_trees.composites.Selector(name="Tasks", memory=False)

    # Here is where you add the behavior of CLaDOS
    tasks.add_child(create_crash_subtree())

    return tasks


def create_root() -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Parallel(name="Resilient CLaDOS BT",
                                        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                                            synchronise=True
                                        ))
    root.add_child(get_data_recollection_subtree())

    root.add_child(get_tasks_subtree())

    return root
