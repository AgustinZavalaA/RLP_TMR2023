import enum
import logging
import platform
from abc import abstractmethod
from typing import Type, Mapping

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class ServoPair(enum.Enum):
    ARM = enum.auto()
    CLAW = enum.auto()
    TRAY = enum.auto()


class ServoStatus(enum.Enum):
    EXPANDED = enum.auto()
    RETRACTED = enum.auto()


class ServosController(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self._servos_status = {
            ServoPair.ARM: ServoStatus.RETRACTED,
            ServoPair.CLAW: ServoStatus.RETRACTED,
            ServoPair.TRAY: ServoStatus.RETRACTED,
        }

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def toggle(self, servo_pair: ServoPair) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass


class ServosControllerMock(ServosController):
    """
    This class is a mock for the ServosController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton ServosControllerMock")

    def setup(self) -> None:
        logger.info("ServosControllerMock.setup() called")

    def toggle(self, servo_pair: ServoPair) -> None:
        if self._servos_status[servo_pair] == ServoStatus.RETRACTED:
            self._servos_status[servo_pair] = ServoStatus.EXPANDED
        else:
            self._servos_status[servo_pair] = ServoStatus.RETRACTED
        logger.info(f"Servo {servo_pair.name} is now {self._servos_status[servo_pair].name}")

    def disable(self) -> None:
        logger.info("ServosControllerMock.disable() called")


# TODO: implement this class
# class ServosControllerRaspberry(ServosController):
# TODO: you remember in setup you have to verify that the servos are in the correct position
# also you can add any other method you need like move in the arduino repository
def servos_controller_factory(architecture: str) -> ServosController:
    """
    This function is used to return the correct ServosController class depending on the platform
    :return: the correct ServosController class
    """
    constructors: Mapping[str, Type[ServosController]] = {
        "x86_64": ServosControllerMock,
        "AMD64": ServosControllerMock,
        # "aarch64": ServosControllerMockRaspberry, #TODO: implement this class
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.DEBUG)
    servos = servos_controller_factory(platform.machine())
    servos.setup()

    for _ in range(2):
        servos.toggle(ServoPair.ARM)
        servos.toggle(ServoPair.CLAW)
        servos.toggle(ServoPair.TRAY)
        logger.info("")

    servos.disable()


if __name__ == "__main__":
    main()
