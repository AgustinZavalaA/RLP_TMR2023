import enum
import logging
import platform
import time

import py_trees.common

from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorDirection, MotorSide

logger = logging.getLogger(__name__)


class MotorMovement(enum.Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4


class MoveBasedOnMovementTime(py_trees.behaviour.Behaviour):
    def __init__(self, motor_movement: MotorMovement, movement_time_seconds: float) -> None:
        super().__init__(name="MoveBasedOnMovementTime")
        self._motor_movement = motor_movement
        self._movement_time_seconds = movement_time_seconds
        self._movement_starting_time = None

        self._motors = motors_controller_factory(platform.machine())

    def initialise(self) -> None:
        self._movement_starting_time = None

    def update(self) -> py_trees.common.Status:
        if self._movement_starting_time is None:
            self._movement_starting_time = time.time()
            logger.info(f"Moving {self._motor_movement.name} for {self._movement_time_seconds} seconds")
            if self._motor_movement == MotorMovement.FORWARD:
                self._motors.move(MotorSide.LEFT, 100, MotorDirection.FORWARD)
                self._motors.move(MotorSide.RIGHT, 100, MotorDirection.FORWARD)
            elif self._motor_movement == MotorMovement.BACKWARD:
                self._motors.move(MotorSide.LEFT, 100, MotorDirection.BACKWARD)
                self._motors.move(MotorSide.RIGHT, 100, MotorDirection.BACKWARD)
            elif self._motor_movement == MotorMovement.LEFT:
                self._motors.move(MotorSide.LEFT, 100, MotorDirection.BACKWARD)
                self._motors.move(MotorSide.RIGHT, 100, MotorDirection.FORWARD)
            elif self._motor_movement == MotorMovement.RIGHT:
                self._motors.move(MotorSide.LEFT, 100, MotorDirection.FORWARD)
                self._motors.move(MotorSide.RIGHT, 100, MotorDirection.BACKWARD)

        time_elapsed = time.time() - self._movement_starting_time
        if time_elapsed < self._movement_time_seconds:
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS


class StopAndWait(py_trees.behaviour.Behaviour):
    def __init__(self, waiting_time_seconds: float) -> None:
        super().__init__(name="StopAndWait")
        self._waiting_time_seconds = waiting_time_seconds
        self._waiting_starting_time = None

        self._motors = motors_controller_factory(platform.machine())

    def initialise(self) -> None:
        self._waiting_starting_time = None

    def update(self) -> py_trees.common.Status:
        if self._waiting_starting_time is None:
            logger.info(f"Waiting for {self._waiting_time_seconds} seconds")
            self._waiting_starting_time = time.time()
            self._motors.stop()

        time_elapsed = time.time() - self._waiting_starting_time
        if time_elapsed < self._waiting_time_seconds:
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS


def create_move_wait_subtree(motor_movement: MotorMovement, movement_time_seconds: float,
                             waiting_time_seconds: float) -> py_trees.behaviour.Behaviour:
    root = py_trees.composites.Sequence(name="MoveWaitSubtree", memory=True)
    root.add_child(MoveBasedOnMovementTime(motor_movement, movement_time_seconds))
    root.add_child(StopAndWait(waiting_time_seconds))

    return root
