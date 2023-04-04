"""
This class should be used to detect the array of distances of the robot from an obstacle.
"""
import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping, Callable

import smbus

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


def all_sensors_strategy(sensor_values: tuple[int, int, int], max_distance: int) -> bool:
    """
    This function is used to determine if the robot is about to collide with an obstacle.
    It returns True if the robot is about to collide with an obstacle, False otherwise.
    """
    return all(sensor_value < max_distance for sensor_value in sensor_values)


def any_sensor_strategy(sensor_values: tuple[int, int, int], max_distance: int) -> bool:
    """
    This function is used to determine if the robot is about to collide with an obstacle.
    It returns True if the robot is about to collide with an obstacle, False otherwise.
    """
    return any(sensor_value < max_distance for sensor_value in sensor_values)


class DistanceSensorsController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def is_about_to_collide(self, strategy: Callable[[tuple[int, int, int], int], bool]) -> bool:
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

    def is_about_to_collide(self, strategy: Callable[[tuple[int, int, int], int], bool]) -> bool:
        logger.info("Sensing distance")
        return False

    def disable(self) -> None:
        logger.info("DistanceSensorsControllerMock.disable() called")


class DistanceSensorsControllerRaspberry(DistanceSensorsController):
    def __init__(self):
        super().__init__()
        self._i2c_bus = None
        self._addr = None
        self._max_distance = 20  # TODO: get the max distance from the config file

    def setup(self) -> None:
        self._addr = 8  # TODO: get the address from the config file
        self._i2c_bus = smbus.SMBus(1)

    def is_about_to_collide(self, strategy: Callable[[tuple[int, int, int], int], bool]) -> bool:
        dist = smbus.read_byte_data(self._addr, force=None)
        sensor_data = dist.split(' ', 2)
        print(sensor_data)
        return strategy(sensor_data, self._max_distance)

    def disable(self) -> None:
        pass


def distance_sensors_controller_factory(architecture: str) -> DistanceSensorsController:
    """
    This function is used to return the correct DistanceSensorsController class depending on the platform
    :return: the correct DistanceSensorsController class
    """
    constructors: Mapping[str, Type[DistanceSensorsController]] = {
        "x86_64": DistanceSensorsControllerMock,
        "AMD64": DistanceSensorsControllerMock,
        "aarch64": DistanceSensorsControllerRaspberry,
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.INFO)
    distance_sensors = distance_sensors_controller_factory(platform.machine())
    distance_sensors.setup()
    try:
        while True:
            print(distance_sensors.is_about_to_collide(all_sensors_strategy))
            time.sleep(0.2)
    except KeyboardInterrupt:
        distance_sensors.disable()
        logger.info("Exiting program")


if __name__ == '__main__':
    main()
