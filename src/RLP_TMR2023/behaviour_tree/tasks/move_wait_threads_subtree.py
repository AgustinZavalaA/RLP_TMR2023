import enum
import logging
import platform
import threading
import time
from dataclasses import dataclass
from typing import Optional

import py_trees.behaviour
from py_trees import common

from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorSide, MotorDirection, \
    MotorsControllers

logger = logging.getLogger(__name__)


class MotorMovement(enum.Enum):
    FORWARD = enum.auto()
    BACKWARD = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    STOP = enum.auto()


@dataclass
class MotorInstruction:
    motor_movement: MotorMovement
    speed: int
    time: float


def execute_motor_instructions(motors: MotorsControllers, motor_instructions: list[MotorInstruction]) -> None:
    motors_directions = {
        MotorMovement.FORWARD: [MotorDirection.FORWARD, MotorDirection.FORWARD],
        MotorMovement.BACKWARD: [MotorDirection.BACKWARD, MotorDirection.BACKWARD],
        MotorMovement.LEFT: [MotorDirection.BACKWARD, MotorDirection.FORWARD],
        MotorMovement.RIGHT: [MotorDirection.FORWARD, MotorDirection.BACKWARD],
        MotorMovement.STOP: [MotorDirection.FORWARD, MotorDirection.FORWARD],
    }
    for instruction in motor_instructions:
        left_direction, right_direction = motors_directions[instruction.motor_movement]
        motors.move(MotorSide.LEFT, instruction.speed, left_direction)
        motors.move(MotorSide.RIGHT, instruction.speed, right_direction)
        time.sleep(instruction.time)


class ExecuteMotorInstructionsClass:
    def __init__(self, motor_instructions: list[MotorInstruction]) -> None:
        self._motor_instructions = motor_instructions
        self._motor_instructions_thread: Optional[threading.Thread] = None
        self._motors = motors_controller_factory(platform.machine())

    def update(self) -> None:
        if self._motor_instructions_thread is not None:
            if not self._motor_instructions_thread.is_alive():
                self._motor_instructions_thread = None
        else:
            self._motor_instructions_thread = threading.Thread(target=execute_motor_instructions,
                                                               args=(self._motors, self._motor_instructions),
                                                               daemon=True)
            self._motor_instructions_thread.start()


class ExecuteMotorInstructions(py_trees.behaviour.Behaviour):
    def __init__(self, motor_instructions: list[MotorInstruction], name: str) -> None:
        super().__init__(name)
        self._motor_instructions = motor_instructions
        self._motor_instructions_thread = None
        self._motors = motors_controller_factory(platform.machine())

    def update(self) -> common.Status:
        if self._motor_instructions_thread:
            if not self._motor_instructions_thread.is_alive():  # type: ignore
                self._motor_instructions_thread = None
                return common.Status.SUCCESS
        else:
            self._motor_instructions_thread = threading.Thread(target=execute_motor_instructions,
                                                               args=(self._motors, self._motor_instructions),
                                                               daemon=True)  # type: ignore
            self._motor_instructions_thread.start()  # type: ignore
        return common.Status.RUNNING


def main():
    logging.basicConfig(level=logging.DEBUG)
    print("Hello World!")
    motor_instructions = [
        MotorInstruction(MotorMovement.FORWARD, 100, 1),
        MotorInstruction(MotorMovement.STOP, 0, 1),
        MotorInstruction(MotorMovement.BACKWARD, 100, 1),
    ]
    executor = ExecuteMotorInstructionsClass(motor_instructions)
    try:
        while True:
            executor.update()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
