import enum
import logging
import platform
import threading
from abc import abstractmethod
from typing import Type, Mapping

import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

from RLP_TMR2023.constants import servos_values
from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class ServoPair(enum.Enum):
    ARM = servos_values.ARM_PINS
    CLAW = servos_values.CLAW_PINS
    TRAY = servos_values.TRAY_PINS


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
        self._servos_values = {
            ServoPair.ARM: {
                ServoStatus.EXPANDED: servos_values.ARM_EXPANDED_DEGREES,
                ServoStatus.RETRACTED: servos_values.ARM_RETRACTED_DEGREES
            },
            ServoPair.CLAW: {
                ServoStatus.EXPANDED: servos_values.CLAW_EXPANDED_DEGREES,
                ServoStatus.RETRACTED: servos_values.CLAW_RETRACTED_DEGREES
            },
            ServoPair.TRAY: {
                ServoStatus.EXPANDED: servos_values.TRAY_EXPANDED_DEGREES,
                ServoStatus.RETRACTED: servos_values.TRAY_RETRACTED_DEGREES
            },
        }

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def toggle(self, servo_pair: ServoPair) -> None:
        pass

    @abstractmethod
    def move(self, servo_pair: ServoPair, status: ServoStatus) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass

    @staticmethod
    def _move_servo(servo: servo.Servo, angle: int) -> None:
        servo.angle = angle


class ServosControllerMock(ServosController):
    """
    This class is a mock for the ServosController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton ServosControllerMock")

    def setup(self) -> None:
        # verify that the servos are in the correct position
        for servo_pair, _ in self._servos_status.items():
            self.move(servo_pair, ServoStatus.RETRACTED, bypass_check=True)

        logger.info("ServosControllerMock.setup() called")

    def toggle(self, servo_pair: ServoPair) -> None:
        if self._servos_status[servo_pair] == ServoStatus.RETRACTED:
            self._servos_status[servo_pair] = ServoStatus.EXPANDED
        else:
            self._servos_status[servo_pair] = ServoStatus.RETRACTED
        logger.info(f"moving to {self._servos_values[servo_pair][self._servos_status[servo_pair]]}")
        logger.info(
            f"Servo {servo_pair.name} moved to {self._servos_values[servo_pair][self._servos_status[servo_pair]]}°"
            f" is now {self._servos_status[servo_pair].name}")

    def move(self, servo_pair: ServoPair, status: ServoStatus, bypass_check: bool = False) -> None:
        # Check if the servo is already in the correct position
        if not bypass_check and self._servos_status[servo_pair] == status:
            logger.info(f"Servo {servo_pair.name} is already in the correct position")
            return
        # Change the status of the servo
        self._servos_status[servo_pair] = status
        logger.info(
            f"Servo {servo_pair.name} moved to {self._servos_values[servo_pair][self._servos_status[servo_pair]]}°"
            f" is now {self._servos_status[servo_pair].name}")

    def disable(self) -> None:
        logger.info("ServosControllerMock.disable() called")


class ServosControllerRaspberry(ServosController):
    def __init__(self):
        super().__init__()
        self._pca = None
        self._i2c = None
        self._servos_status = {
            ServoPair.ARM: ServoStatus.RETRACTED,
            ServoPair.CLAW: ServoStatus.RETRACTED,
            ServoPair.TRAY: ServoStatus.RETRACTED,
        }

    def setup(self) -> None:
        self._i2c = busio.I2C(SCL, SDA)
        self._pca = PCA9685(self._i2c)
        self._pca.frequency = servos_values.PCA9685_FREQUENCY

        # verify that the servos are in the correct position
        for servo_pair, _ in self._servos_status.items():
            self.move(servo_pair, ServoStatus.RETRACTED, bypass_check=True)

    def toggle(self, servo_pair: ServoPair) -> None:
        if self._servos_status[servo_pair] == ServoStatus.RETRACTED:
            status = ServoStatus.EXPANDED
        else:
            status = ServoStatus.RETRACTED

        self.move(servo_pair, status)

    def move(self, servo_pair: ServoPair, status: ServoStatus, bypass_check: bool = False) -> None:
        if not bypass_check and self._servos_status[servo_pair] == status:
            return
        s1, s2 = self._get_servos(servo_pair)
        angle_1 = self._servos_values[servo_pair][self._servos_status[servo_pair]]
        angle_2 = 180 - angle_1
        t1 = threading.Thread(target=self._move_servo, args=(s1, angle_1))
        t2 = threading.Thread(target=self._move_servo, args=(s2, angle_2))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print(angle_1, angle_2)  # TODO: remove all prints in this file
        print(self._servos_status[servo_pair].name)
        self._servos_status[servo_pair] = status

    def _get_servos(self, servo_pair: ServoPair) -> tuple[servo.Servo, servo.Servo]:
        if self._pca is None:
            raise RuntimeError("ServosControllerRaspberry.setup() must be called before using the servos")
        s1 = servo.Servo(self._pca.channels[servo_pair.value[0]])
        s2 = servo.Servo(self._pca.channels[servo_pair.value[1]])
        return s1, s2

    def disable(self) -> None:
        """ Servos don't need to be disabled on the Raspberry Pi """
        pass


def servos_controller_factory(architecture: str) -> ServosController:
    """
    This function is used to return the correct ServosController class depending on the platform
    :return: the correct ServosController class
    """
    constructors: Mapping[str, Type[ServosController]] = {
        "x86_64": ServosControllerMock,
        "AMD64": ServosControllerMock,
        "aarch64": ServosControllerRaspberry,
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
