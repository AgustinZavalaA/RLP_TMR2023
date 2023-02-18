import enum
import logging as log
import time
from abc import abstractmethod

from RLP_TMR2023.HardwareControllers.Singleton import Singleton

try:
    import RPi.GPIO as GPIO
except ImportError:
    log.warning("RPi.GPIO not installed, using mock instead")


# TODO: cambiar nombre de este enum
class MotorSide(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()


class MotorDirection(enum.Enum):
    FORWARD = enum.auto()
    BACKWARD = enum.auto()


class MotorsControllers(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def move(self, motor_side: MotorSide, speed: int, direction: MotorDirection) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass


class MotorsControllerMock(MotorsControllers):
    """
     This class is a mock for the MotorsController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()

    def setup(self) -> None:
        log.warning("MotorsControllerMock.setup() called")

    def stop(self) -> None:
        log.warning("Stopping motors")

    def move(self, motor_side: MotorSide, speed: int, direction: MotorDirection) -> None:
        log.warning(f"Moving {motor_side.name} motors with speed: {speed} and direction {direction.name}")

    def disable(self) -> None:
        log.warning("Disabling motors")


class MotorsControllerRaspberry(MotorsControllers):
    def __init__(self):
        super().__init__()

    def setup(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def move(self, motor_side: MotorSide, speed: int, direction: MotorDirection) -> None:
        pass

    def disable(self) -> None:
        GPIO.cleanup()
        pass


def motors_controller_factory(architecture: str) -> MotorsControllers:
    constructors = {
        'x86_64': MotorsControllerMock,
        'armv7l': MotorsControllerRaspberry,
    }
    return constructors[architecture]()


# class Motors:
#     def __init__(self) -> None:
#         GPIO.setmode(GPIO.BOARD)
#
#         # Motor A
#         self.PWMAIN = 12
#         self.AIN1 = 13
#         self.AIN2 = 15
#         # Motor B
#         self.PWMBIN = 35
#         self.BIN1 = 16
#         self.BIN2 = 18
#
#         GPIO.setup(self.AIN1, GPIO.OUT)
#         GPIO.setup(self.AIN2, GPIO.OUT)
#         GPIO.setup(self.BIN1, GPIO.OUT)
#         GPIO.setup(self.BIN2, GPIO.OUT)
#
#         # Set GPIO pin 12 to output mode.
#         GPIO.setup(self.PWMAIN, GPIO.OUT)
#         # Initialize PWM on pwmPin 100Hz frequency
#         self.pwm_a = GPIO.PWM(self.PWMAIN, 100)
#
#         GPIO.setup(self.PWMBIN, GPIO.OUT)
#         # Initialize PWM on pwmPin 100Hz frequency
#         self.pwm_b = GPIO.PWM(self.PWMBIN, 100)
#
#         dc = 0  # set dc variable to 0 for 0%
#         self.pwm_a.start(dc)  # Start PWM with 0% duty cycle
#         self.pwm_b.start(dc)
#
#     def stop(self) -> None:
#         # GPIO.output(STBY, False)
#         dc = 1
#         self.pwm_a.ChangeDutyCycle(dc)
#         self.pwm_b.ChangeDutyCycle(dc)
#
#         GPIO.output(self.AIN1, GPIO.LOW)
#         GPIO.output(self.AIN2, GPIO.LOW)
#         GPIO.output(self.BIN1, GPIO.LOW)
#         GPIO.output(self.BIN2, GPIO.LOW)
#
#     def move(self, motor: bool, speed: int, direction: bool) -> None:
#         in_pin1 = GPIO.LOW
#         in_pin2 = GPIO.HIGH
#
#         if direction:
#             in_pin1 = GPIO.HIGH
#             in_pin2 = GPIO.LOW
#
#         if motor:
#             GPIO.output(self.AIN1, in_pin1)
#             GPIO.output(self.AIN2, in_pin2)
#             self.pwm_a.ChangeDutyCycle(speed)
#         else:
#             GPIO.output(self.BIN1, in_pin1)
#             GPIO.output(self.BIN2, in_pin2)
#             self.pwm_b.ChangeDutyCycle(speed)
#
#     def disable(self) -> None:
#         self.stop()
#         self.pwm_a.stop()  # stop PWM
#         self.pwm_b.stop()  # stop PWM
#         GPIO.cleanup()  # resets GPIO ports used back to input mode
#
#
def main() -> None:
    log.basicConfig(level=log.DEBUG)
    # motors = motors_controller_factory(platform.machine())
    motors = motors_controller_factory("armv7l")
    motors2 = motors_controller_factory("armv7l")
    print(id(motors) == id(motors2))
    try:
        while True:
            motors.move(MotorSide.RIGHT, 100, MotorDirection.FORWARD)
            motors.move(MotorSide.LEFT, 100, MotorDirection.FORWARD)
            time.sleep(1.2)

            motors.stop()
            time.sleep(1)

            motors.move(MotorSide.RIGHT, 100, MotorDirection.BACKWARD)
            motors.move(MotorSide.LEFT, 100, MotorDirection.BACKWARD)
            time.sleep(1.2)

            motors.stop()
            time.sleep(1)
    except KeyboardInterrupt:
        motors.disable()
        log.warning("Program stopped by user")


if __name__ == "__main__":
    main()
