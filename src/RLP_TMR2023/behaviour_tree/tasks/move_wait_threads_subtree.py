import enum
import logging
import threading
import time
from dataclasses import dataclass

import py_trees.behaviour
from py_trees import common

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


def execute_motor_instructions(motor_instructions: list[MotorInstruction]) -> None:
    for instruction in motor_instructions:
        logger.info(
            f"Moving {instruction.motor_movement.name} for {instruction.time} seconds at {instruction.speed} speed")
        time.sleep(instruction.time)


class ExecuteMotorInstructionsClass:
    def __init__(self, motor_instructions: list[MotorInstruction]) -> None:
        self._motor_instructions = motor_instructions
        self._motor_instructions_thread = None

    def update(self) -> None:
        if self._motor_instructions_thread is not None:
            if not self._motor_instructions_thread.is_alive():
                self._motor_instructions_thread = None
        else:
            self._motor_instructions_thread = threading.Thread(target=execute_motor_instructions,
                                                               args=(self._motor_instructions,),
                                                               daemon=True)
            self._motor_instructions_thread.start()


class ExecuteMotorInstructions(py_trees.behaviour.Behaviour):
    def __init__(self, motor_instructions: list[MotorInstruction], name: str) -> None:
        super().__init__(name)
        self._motor_instructions = motor_instructions
        self._motor_instructions_thread = None

    def update(self) -> common.Status:
        if self._motor_instructions_thread is not None:
            if not self._motor_instructions_thread.is_alive():
                self._motor_instructions_thread = None
                return common.Status.SUCCESS
        else:
            self._motor_instructions_thread = threading.Thread(target=execute_motor_instructions,
                                                               args=(self._motor_instructions,),
                                                               daemon=True)
            self._motor_instructions_thread.start()
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
