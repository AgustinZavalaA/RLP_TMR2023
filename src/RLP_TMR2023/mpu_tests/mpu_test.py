# Delete when we don't need it anymore
import logging
import time
from abc import abstractmethod
import platform
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

    # TODO change datatype latter to bool
    @abstractmethod
    def is_robot_stuck(self) -> None:
        pass

    def disable(self) -> None:
        pass


class IMUControllerMock(IMUController):
    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton IMUControllerMock")

    def setup(self) -> None:
        logger.info("IMUControllerMock.setup() called")

    # TODO change datatype latter to bool
    def is_robot_stuck(self) -> None:
        logger.info("IMUControllerMock.is_robot_stuck() called")

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

    def is_robot_stuck(self) -> None:
        # logger.info("IMUControllerRaspberry.is_robot_stuck() called")
        # create a function that returns true if the robot is stuck
        gyro = self.mpu.readGyroscopeMaster()
        print(gyro)
        accel = self.mpu.readAccelerometerMaster()
        print(accel)

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
    imu_controller.is_robot_stuck()

    # print("|.....MPU9250 in 0x68 Address.....|")
    # print("Accelerometer", mpu.readAccelerometerMaster())
    # print("Gyroscope", mpu.readGyroscopeMaster())
    # print("Magnetometer", mpu.readMagnetometerMaster())
    # print("Temperature", mpu.readTemperatureMaster())
    # print("\n")

    time.sleep(1)
