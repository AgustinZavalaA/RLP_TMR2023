import logging
import time
from abc import abstractmethod
import platform
import numpy as np
import time
import numpy.typing as npt
from typing import Type, Mapping, Callable
from enum import Enum

from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import \
    MPU9050_ADDRESS_68, GFS_1000, AFS_8G, AK8963_BIT_16, AK8963_MODE_C100HZ

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)
NUM_SAMPLES = 25

class DataRecollectedType(Enum):
    GYROSCOPE = 0
    ACCELEROMETER = 1
    

def gyroscope_any_iqr_strategy(full_data: Mapping[DataRecollectedType, npt.NDArray[np.uint8]]) -> bool:
    data = full_data[DataRecollectedType.GYROSCOPE]
    q1, q3 = np.percentile(data, [25, 75], axis=0)
    gyro_iqr = q3 - q1
    return not np.any(gyro_iqr > 5) # TODO: use a config file to set the threshold

def gyroscope_all_iqr_strategy(full_data: Mapping[DataRecollectedType, npt.NDArray[np.uint8]]) -> bool:
    data = full_data[DataRecollectedType.GYROSCOPE]
    q1, q3 = np.percentile(data, [25, 75], axis=0)
    gyro_iqr = q3 - q1
    return np.all(gyro_iqr < 5) # TODO: use a config file to set the threshold

def gyroscope_all_std_strategy(full_data: Mapping[DataRecollectedType, npt.NDArray[np.uint8]]) -> bool:
    data = full_data[DataRecollectedType.GYROSCOPE]
    gyro_std = np.std(data, axis=0)
    return np.all(gyro_std < 1) # TODO: use a config file to set the threshold

class IMUController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def is_robot_stuck(self, strategy: Callable) -> bool:
        pass

    def disable(self) -> None:
        pass


class IMUControllerMock(IMUController):
    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton IMUControllerMock")

    def setup(self) -> None:
        logger.info("IMUControllerMock.setup() called")

    def is_robot_stuck(self, strategy: Callable) -> bool:
        logger.info("IMUControllerMock.is_robot_stuck() called with strategy: " + str(strategy))
        return False

    def disable(self) -> None:
        logger.info("IMUControllerMock.disable() called")


class IMUControllerMockRaspberry(IMUController):
    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton IMUControllerRaspberry")
        self.mpu = MPU9250(
            address_ak=0x68,
            address_mpu_master=MPU9050_ADDRESS_68,
            address_mpu_slave=None,
            bus=1,
            gfs=GFS_1000,
            afs=AFS_8G,
            mfs=AK8963_BIT_16,
            mode=AK8963_MODE_C100HZ
        )
        
        # TODO: implement the static values from a config file
        self.data = {
            DataRecollectedType.GYROSCOPE: np.zeros(shape=(NUM_SAMPLES, 3)),
            DataRecollectedType.ACCELEROMETER: np.zeros(shape=(NUM_SAMPLES, 3))
        }
        self._data_index = 0

    def setup(self) -> None:
        # logger.info("IMUControllerRaspberry.setup() called")
        self.mpu.calibrateMPU6500()
        time.sleep(1)
        self.mpu.configure()

    def is_robot_stuck(self, strategy: Callable) -> bool:
        # create a function that returns true if the robot is stuck

        gyro = self.mpu.readGyroscopeMaster()
        accel = self.mpu.readAccelerometerMaster()
        
        # update current data
        self.data[DataRecollectedType.GYROSCOPE][self._data_index] = gyro
        self.data[DataRecollectedType.ACCELEROMETER][self._data_index] = accel
        self._data_index = (self._data_index + 1) % NUM_SAMPLES # TODO: use a config file to set the size of the array

        return strategy(self.data)

    def disable(self) -> None:
        logger.info("IMUControllerRaspberry.disable() called")
        


def imu_controller_factory(architecture: str) -> IMUController:
    """
    This function is used to return the correct IMUController class depending on the platform
    :return: the correct IMUController class
    """
    constructors: Mapping[str, Type[IMUController]] = {
        "x86_64": IMUControllerMock,
        "AMD64": IMUControllerMock,
        "aarch64": IMUControllerMockRaspberry  # TODO: implement this class
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
            print(f"stuck all iqr gyro: {imu_controller.is_robot_stuck(gyroscope_all_iqr_strategy)}")
            # print(f"stuck any iqr gyro: {imu_controller.is_robot_stuck(gyroscope_any_iqr_strategy)}")
            print(f"stuck all std gyro: {imu_controller.is_robot_stuck(gyroscope_all_std_strategy)}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        imu_controller.disable()
        logger.info("Program stopped by user")


if __name__ == "__main__":
    main()