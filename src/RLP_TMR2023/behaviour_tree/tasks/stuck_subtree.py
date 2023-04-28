import platform
import time

import py_trees.common

from RLP_TMR2023.behaviour_tree.tasks.move_wait_threads_subtree import MotorMovement, \
    MotorInstruction, ExecuteMotorInstructions
from RLP_TMR2023.constants import bt_values
from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorSide, MotorDirection


class StuckRecovery(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Dash dance")
        self._motors = motors_controller_factory(platform.machine())
        self._initial_time = None

    def update(self):
        if self._initial_time is None:
            self._initial_time = time.perf_counter()

        if time.perf_counter() - self._initial_time < bt_values.STUCK_BACK_OFF_TIME_SECONDS:
            self._motors.move(MotorSide.LEFT, bt_values.STUCK_BACK_OFF_SPEED, MotorDirection.BACKWARD)
            self._motors.move(MotorSide.RIGHT, bt_values.STUCK_BACK_OFF_TIME_SECONDS, MotorDirection.BACKWARD)
            return py_trees.common.Status.RUNNING
        else:
            return py_trees.common.Status.SUCCESS

    def terminate(self, new_status: py_trees.common.Status) -> None:
        self._initial_time = None


def create_back_and_forth_subtree() -> py_trees.behaviour.Behaviour:
    motor_instructions = [
        MotorInstruction(MotorMovement.BACKWARD, bt_values.STUCK_BACK_OFF_SPEED,
                         bt_values.STUCK_BACK_OFF_TIME_SECONDS),
        MotorInstruction(MotorMovement.FORWARD, bt_values.STUCK_ADVANCE_SPEED,
                         bt_values.STUCK_ADVANCE_TIME_SECONDS),
    ]

    back_and_forth_subtree = ExecuteMotorInstructions(motor_instructions, "Back and forth subtree")

    return back_and_forth_subtree


def create_stuck_subtree() -> py_trees.behaviour.Behaviour:
    stuck_subtree = py_trees.composites.Selector("Stuck subtree", memory=False)

    stuck_subtree.add_child(
        py_trees.decorators.EternalGuard(
            name="Stuck in the sand?",
            child=create_back_and_forth_subtree(),
            condition=lambda blackboard: blackboard.is_robot_stuck,
            blackboard_keys={"is_robot_stuck"},
        ))

    return stuck_subtree
