"""
This class should be used to detect the array of distances of the robot from an obstacle.
"""
import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class DistanceSensorsController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def is_about_to_collide(self) -> bool:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass


class DistanceSensorsControllerMock(DistanceSensorsController):
    """
    This class is a mock for the DistanceSensorsController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton DistanceSensorsControllerMock")

    def setup(self) -> None:
        logger.info("DistanceSensorsControllerMock.setup() called")

    def is_about_to_collide(self) -> bool:
        logger.info("Sensing distance")
        return False

    def disable(self) -> None:
        logger.info("DistanceSensorsControllerMock.disable() called")


# TODO implement this class
# class DistanceSensorsControllerRaspberry(DistanceSensorsController):

def distance_sensors_controller_factory(architecture: str) -> DistanceSensorsController:
    """
    This function is used to return the correct DistanceSensorsController class depending on the platform
    :return: the correct DistanceSensorsController class
    """
    constructors: Mapping[str, Type[DistanceSensorsController]] = {
        "x86_64": DistanceSensorsControllerMock,
        "AMD64": DistanceSensorsControllerMock,
        # "aarch64": DistanceSensorsControllerMockRaspberry, #TODO: implement this class
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.INFO)
    distance_sensors = distance_sensors_controller_factory(platform.machine())
    distance_sensors.setup()
    try:
        while True:
            print(distance_sensors.is_about_to_collide())
            time.sleep(0.2)
    except KeyboardInterrupt:
        distance_sensors.disable()
        logger.info("Exiting program")


if __name__ == '__main__':
    main()
