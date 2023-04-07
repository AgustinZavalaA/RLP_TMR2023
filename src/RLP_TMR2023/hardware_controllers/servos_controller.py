import enum
import logging
import platform
from abc import abstractmethod
from typing import Type, Mapping

from board import SCL, SDA
import busio

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)

class ServoPair(enum.Enum):
    ARM = (0, 1)
    CLAW = (2, 3)
    TRAY = (4, 5)


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
                ServoStatus.EXPANDED: 90,  # TODO: obtain this value from a config file
                ServoStatus.RETRACTED: 0,
            },
            ServoPair.CLAW: {
                ServoStatus.EXPANDED: 30,
                ServoStatus.RETRACTED: 0,
            },
            ServoPair.TRAY: {
                ServoStatus.EXPANDED: 60,
                ServoStatus.RETRACTED: 0,
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
        self._servos_status = {
            ServoPair.ARM: ServoStatus.RETRACTED,
            ServoPair.CLAW: ServoStatus.RETRACTED,
            ServoPair.TRAY: ServoStatus.RETRACTED,
        }
        self._servos_values = {
            ServoPair.ARM: {
                ServoStatus.EXPANDED: 90,  # TODO: obtain this value from a config file
                ServoStatus.RETRACTED: 0,

            },
            ServoPair.CLAW: {
                ServoStatus.EXPANDED: 30,
                ServoStatus.RETRACTED: 0,
            },
            ServoPair.TRAY: {
                ServoStatus.EXPANDED: 60,
                ServoStatus.RETRACTED: 0,
            },
        }

    def setup(self) -> None:
        self.i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50



        # verify that the servos are in the correct position
        for servo_pair, _ in self._servos_status.items():
            self.move(servo_pair, ServoStatus.RETRACTED, bypass_check=True)


    def toggle(self, servo_pair: ServoPair) -> None:
        s1 = servo.Servo(self.pca.channels[ServoPair.value[0]])
        s2 = servo.Servo(self.pca.channels[ServoPair.value[1]])
        if self._servos_status[servo_pair] == ServoStatus.RETRACTED:
            s1.angle, s2.angle = self._servos_values[servo_pair][self._servos_status[servo_pair]]
            self._servos_status[servo_pair] = ServoStatus.EXPANDED
        else:
            s1.angle, s2.angle = self._servos_values[servo_pair][self._servos_status[servo_pair]]
            self._servos_status[servo_pair] = ServoStatus.RETRACTED

    def move(self, servo_pair: ServoPair, status: ServoStatus, bypass_check: bool = False) -> None:
        s1 = servo.Servo(self.pca.channels[ServoPair.value[0]])
        s2 = servo.Servo(self.pca.channels[ServoPair.value[1]])
        if not bypass_check and self._servos_status[servo_pair] == status:
            s1.angle, s2.angle = self._servos_values[servo_pair][self._servos_status[servo_pair]]
            return
        self._servos_status[servo_pair] = status


    def disable(self) -> None:
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
