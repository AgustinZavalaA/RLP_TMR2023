"""
This class should be used to detect the array of distances of the robot from an obstacle.
"""
import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping, Callable

import smbus

from RLP_TMR2023.constants import ultrasonic_values
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
        self._max_distance = ultrasonic_values.MAX_DISTANCE

    def setup(self) -> None:
        self._addr = ultrasonic_values.I2C_ADDR
        self._i2c_bus = smbus.SMBus(ultrasonic_values.I2C_BUS)

    def is_about_to_collide(self, strategy: Callable[[tuple[int, int, int], int], bool]) -> bool:
        if self._i2c_bus is None:
            raise RuntimeError("The distance sensors controller has not been setup yet")
        # read the first 3 bytes that are not 255
        sensor_data_list: list[int] = []
        try:
            while len(sensor_data_list) < 3:
                data = self._i2c_bus.read_byte_data(self._addr, 0)
            if data != 255:
                sensor_data_list.append(data)
            sensor_data = (sensor_data_list[0], sensor_data_list[1], sensor_data_list[2])  # just for type hinting
            last_sensor_data = sensor_data
        except:
            sensor_data = (254,254,254)
        logger.info(f"Sensor data: {sensor_data}")
        return strategy(sensor_data, self._max_distance)

    def disable(self) -> None:
        """ This method is used to disable the distance sensors
        """
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
            print(distance_sensors.is_about_to_collide(any_sensor_strategy))
            time.sleep(.2)
    except KeyboardInterrupt:
        distance_sensors.disable()
        logger.info("Program stopped by user.")


if __name__ == '__main__':
    main()
