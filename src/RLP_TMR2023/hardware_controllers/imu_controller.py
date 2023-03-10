"""
This class should be used to detect if the robot is stuck.
"""
import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class IMUController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def is_robot_stuck(self) -> bool:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass


class IMUControllerMock(IMUController):
    """
    This class is a mock for the IMUController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton IMUControllerMock")

    def setup(self) -> None:
        logger.info("IMUControllerMock.setup() called")

    def is_robot_stuck(self) -> bool:
        logger.info("IMUControllerMock.is_robot_stuck() called")
        return False

    def disable(self) -> None:
        logger.info("IMUControllerMock.disable() called")


# TODO: implement this class
# class IMUControllerRaspberry(IMUController):
def imu_controller_factory(architecture: str) -> IMUController:
    """
    This function is used to return the correct IMUController class depending on the platform
    :return: the correct IMUController class
    """
    constructors: Mapping[str, Type[IMUController]] = {
        "x86_64": IMUControllerMock,
        "AMD64": IMUControllerMock,
        # "aarch64": IMUControllerMockRaspberry, #TODO: implement this class
    }
    return constructors[architecture]()


def main():
    """
    This function is used to test the IMUController class
    """
    logging.basicConfig(level=logging.DEBUG)
    imu_controller = imu_controller_factory(platform.machine())
    imu_controller.setup()
    try:
        while True:
            print(f"is_robot_stuck: {imu_controller.is_robot_stuck()}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        imu_controller.disable()
        logger.info("Program stopped by user")


if __name__ == "__main__":
    main()
