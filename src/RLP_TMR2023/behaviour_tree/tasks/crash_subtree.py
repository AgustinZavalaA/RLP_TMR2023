import platform
import time

import py_trees.common

from RLP_TMR2023.constants import bt_values
from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorSide, MotorDirection


class CrashPrevention(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Go back")
        self._motors = motors_controller_factory(platform.machine())
        self._initial_time = None

    def update(self):
        if self._initial_time is None:
            self._initial_time = time.perf_counter()

        if time.perf_counter() - self._initial_time < bt_values.COLLISION_BACK_OFF_TIME_SECONDS:
            self._motors.move(MotorSide.LEFT, bt_values.COLLISION_BACK_OFF_SPEED, MotorDirection.BACKWARD)
            self._motors.move(MotorSide.RIGHT, bt_values.COLLISION_BACK_OFF_SPEED, MotorDirection.BACKWARD)
            return py_trees.common.Status.RUNNING
        else:
            return py_trees.common.Status.SUCCESS

    def terminate(self, new_status: py_trees.common.Status) -> None:
        self._initial_time = None


def create_crash_subtree() -> py_trees.behaviour.Behaviour:
    crash_subtree = py_trees.composites.Selector("Crash subtree", memory=False)

    crash_subtree.add_child(
        py_trees.decorators.EternalGuard(
            name="About to crash?",
            child=CrashPrevention(),
            condition=lambda blackboard: blackboard.is_robot_about_to_collide,
            blackboard_keys={"is_robot_about_to_collide"},
        ))

    return crash_subtree
