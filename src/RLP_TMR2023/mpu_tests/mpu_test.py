# Delete when we don't need it anymore
import logging
import time
from abc import abstractmethod
import platform
import numpy as np
from typing import Type, Mapping

from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import \
    MPU9050_ADDRESS_68, GFS_1000, AFS_8G, AK8963_BIT_16, AK8963_MODE_C100HZ

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class IMUController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def is_robot_stuck(self) -> bool:
        pass

    def disable(self) -> None:
        pass


class IMUControllerMock(IMUController):
    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton IMUControllerMock")

    def setup(self) -> None:
        logger.info("IMUControllerMock.setup() called")

    def is_robot_stuck(self) -> bool:
        logger.info("IMUControllerMock.is_robot_stuck() called")
        return False

        # return False

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

    def setup(self) -> None:
        # logger.info("IMUControllerRaspberry.setup() called")
        self.mpu.configure()

    def is_robot_stuck(self) -> bool:
        # logger.info("IMUControllerRaspberry.is_robot_stuck() called")
        # create a function that returns true if the robot is stuck
        gyro_data = np.array([])
        accel_data = np.array([])

        gyro = self.mpu.readGyroscopeMaster()
        accel = self.mpu.readAccelerometerMaster()

        for i in range(0, 100):
            # IDK why mypy asks for add the np.array() to the np.append() function
            gyro_data = np.append(gyro_data, gyro)
            accel_data = np.append(accel_data, accel)

        gyro_iqr = np.percentile(gyro_data, 75) - np.percentile(gyro_data, 25)
        gyro_std_dev = np.std(gyro_data)

        accel_iqr = np.percentile(accel_data, 75) - np.percentile(accel_data, 25)
        accel_std_dev = np.std(accel_data)

        print(f"{gyro_iqr} {gyro_std_dev} {accel_iqr} {accel_std_dev}")

        if gyro_iqr > 5 and gyro_std_dev > 2:
            return False
        else:
            return True

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


while True:
    logging.basicConfig(level=logging.DEBUG)
    imu_controller = imu_controller_factory(platform.machine())
    imu_controller.setup()
    print(imu_controller.is_robot_stuck())
    time.sleep(1)
