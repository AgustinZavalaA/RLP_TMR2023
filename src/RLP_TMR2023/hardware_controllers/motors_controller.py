import enum
import logging as log
import platform
import time
from abc import abstractmethod

from RLP_TMR2023.hardware_controllers.singleton import Singleton

try:
    import RPi.GPIO as GPIO
except ImportError:
    log.warning("RPi.GPIO not installed, using mock instead")


# TODO: probably change the name of this enum
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
        log.warning("Instantiating Singleton MotorsControllerMock")

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
        # TODO: change these hardcoded values to a config file
        # Motor 1
        self.pin_pwm_motor_1_output = 12
        self.pin_dir_motor_1_input = (13, 15)
        self.pwm_motor_1: GPIO.PWM = None
        # Motor 2
        self.pin_pwm_motor_2_input = 35
        self.pin_dir_motor_2_input = (16, 18)
        self.pwm_motor_2: GPIO.PWM = None

    def setup(self) -> None:
        GPIO.setmode(GPIO.BOARD)

        # Set all the motor direction pins as output
        for pin in self.pin_dir_motor_1_input + self.pin_dir_motor_2_input:
            GPIO.setup(pin, GPIO.OUT)

        # Set all the motor pwm pins as output
        GPIO.setup(self.pin_pwm_motor_1_output, GPIO.OUT)
        GPIO.setup(self.pin_pwm_motor_2_input, GPIO.OUT)

        # Initialize pwm objects to 100Hz (100 % duty cycle)
        self.pwm_motor_1 = GPIO.PWM(self.pin_pwm_motor_1_output, 100)
        self.pwm_motor_2 = GPIO.PWM(self.pin_pwm_motor_2_input, 100)

        duty_cycle = 0  # set dc variable to 0 for 0%
        self.pwm_motor_1.start(duty_cycle)  # Start PWM with 0% duty cycle
        self.pwm_motor_2.start(duty_cycle)

    def stop(self) -> None:
        duty_cycle = 1
        self.pwm_motor_1.ChangeDutyCycle(duty_cycle)
        self.pwm_motor_2.ChangeDutyCycle(duty_cycle)

        for pin in self.pin_dir_motor_1_input + self.pin_dir_motor_2_input:
            GPIO.output(pin, GPIO.LOW)

    def move(self, motor_side: MotorSide, speed: int, direction: MotorDirection) -> None:
        in_pin1 = GPIO.LOW
        in_pin2 = GPIO.HIGH

        if direction == MotorDirection.FORWARD:
            in_pin1 = GPIO.HIGH
            in_pin2 = GPIO.LOW

        if motor_side == MotorSide.LEFT:
            GPIO.output(self.pin_dir_motor_1_input[0], in_pin1)
            GPIO.output(self.pin_dir_motor_1_input[1], in_pin2)
            self.pwm_motor_1.ChangeDutyCycle(speed)
        else:
            GPIO.output(self.pin_dir_motor_2_input[0], in_pin1)
            GPIO.output(self.pin_dir_motor_2_input[1], in_pin2)
            self.pwm_motor_2.ChangeDutyCycle(speed)

    def disable(self) -> None:
        self.stop()
        self.pwm_motor_1.stop()  # stop PWM object
        self.pwm_motor_2.stop()  # stop PWM object
        # TODO this should only be called when the program is exiting (maybe in main.py)
        GPIO.cleanup()  # resets GPIO ports used back to input mode


def motors_controller_factory(architecture: str) -> MotorsControllers:
    constructors = {
        'x86_64': MotorsControllerMock,
        'armv7l': MotorsControllerRaspberry,
    }
    return constructors[architecture]()


def main() -> None:
    log.basicConfig(level=log.DEBUG)
    motors = motors_controller_factory(platform.machine())
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
