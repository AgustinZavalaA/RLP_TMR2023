"""
This class should be used to detect if the robot is stuck.
"""
import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping


from mpu9250_jmdev.registers import \
    AK8963_ADDRESS, MPU9050_ADDRESS_68, GFS_1000, AFS_8G, AK8963_BIT_16, AK8963_MODE_C100HZ, MPU9250

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class IMUController(metaclass=Singleton):

    def __init__(self):
        self._imu = None
        self._accel_data = None

    @abstractmethod
    def setup(self) -> None:
        # Initialize MPU9250 sensor
        self._imu = MPU9250(
            address_ak=AK8963_ADDRESS,
            address_mpu_master=MPU9050_ADDRESS_68,
            address_mpu_slave=None,
            bus=1,
            gfs=GFS_1000,
            afs=AFS_8G,
            mfs=AK8963_BIT_16,
            mode=AK8963_MODE_C100HZ)

        self._imu.configure()

    @abstractmethod
    def is_robot_stuck(self) -> bool:
        # Read the accelerometer data
        self._accel_data = self._imu.readAccelerometerMaster()

        # Check if the robot is stuck
        if self._accel_data['x'] < 0.5 and self._accel_data['y'] < 0.5 and self._accel_data['z'] < 0.5:
            return True
        else:
            return False

    @abstractmethod
    def disable(self) -> None:
        if self._imu is not None:
            self._imu.powerDown()


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
