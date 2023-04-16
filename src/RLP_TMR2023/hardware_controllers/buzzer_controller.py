import enum
import logging
import platform
import threading
import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Type, Mapping, Optional

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.getLogger(__name__).warning("RPi.GPIO not found, using mock buzzer controller")

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


@dataclass
class Note:
    """
    This class represents a note to be played by the buzzer
    """
    frequency: int
    duration: float
    set_frequency: Optional[int] = None


class Melody(enum.Enum):
    """
    This enum contains the melodies that can be played by the buzzer
    """
    CAN_FOUND = enum.auto()
    ABOUT_TO_COLLIDE = enum.auto()
    STEPROBOT_IS_STUCK = enum.auto()
    MIAUMIAUMIAU = enum.auto()
    AXOLOTE_EATING = enum.auto()
    KNOCK_THE_DOOR = enum.auto()


class BuzzerController(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self._melodies: dict[Melody, list[Note]] = {
            Melody.CAN_FOUND: [
                Note(30, 0.1),
                Note(0, 0.1),
                Note(70, 0.1),
                Note(80, 0.1),
                Note(90, 0.2),
            ],
            Melody.ABOUT_TO_COLLIDE: [
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
                Note(10, 0.07),
                Note(0, 0.07),
            ],
            Melody.STEPROBOT_IS_STUCK: [
                Note(99, 0.2),
                Note(0, 0.2),
                Note(99, 0.2),
                Note(0, 0.2),
                Note(99, 0.2),
                Note(0, 0.2),
                Note(99, 0.2),
                Note(0, 0.2),
                Note(99, 0.2),
                Note(0, 0.2),
                Note(99, 0.2),
                Note(0, 0.2),
            ],
            Melody.MIAUMIAUMIAU: [
                Note(1, 0.5),
                Note(0, 0.5),
                Note(10, 0.5),
                Note(0, 0.5),
                Note(20, 0.5),
                Note(0, 0.5),
            ],
            Melody.AXOLOTE_EATING: [
                Note(20,0.3,700),
                Note(0,0.1,),
                Note(40,0.2,700),
                Note(0,0.1,),
                Note(20,0.4,700),
                Note(0,0.1,),
            ],
            Melody.KNOCK_THE_DOOR: [
                Note(20,0.1,1000),
                Note(0,0.2),
                Note(40,0.1,1000),
                Note(0,0.7),
                Note(20,0.1,1000),
                Note(0,0.7),
                Note(20,0.1,1000),
                Note(0,0.7),
                Note(20,0.1,1000),
                Note(0,0.1),
                Note(20,0.1,1000),
                Note(0,0.5),
                Note(20,0.1,1000),
                Note(0,0.5),
            ]
        }

    @abstractmethod
    def setup(self) -> None:
        pass

    # TODO: remember to make this method async or multiprocessing (SUPER IMPORTANT) as it will be called from the
    #  main thread and it does not need to be blocking
    @abstractmethod
    def _background_play(self, melody: Melody) -> None:
        pass

    def play(self, melody: Melody) -> None:
        """
        This method plays a tone with the given frequency and duration, calls the _background_play method as it is a
        blocking method
        :param melody: the melody to play
        """
        threading.Thread(
            target=self._background_play,
            args=(melody,),
            daemon=True).start()

    @abstractmethod
    def disable(self) -> None:
        pass


class BuzzerControllerMock(BuzzerController):
    """
    This class is a mock for the BuzzerController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton BuzzerControllerMock")

    def setup(self) -> None:
        logger.info("BuzzerControllerMock.setup() called")

    def _background_play(self, melody: Melody) -> None:
        logger.info(f"Playing melody {melody.name}")
        for note in self._melodies[melody]:
            logger.info(f"Playing a tone with frequency {note.frequency} and duration {note.duration}")
            time.sleep(note.duration)
        logger.info("Done playing the melody")

    def disable(self) -> None:
        logger.info("Disabling buzzer")


class BuzzerControllerRaspberry(BuzzerController):
    def setup(self) -> None:
        self._buzzer_pin = 38
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._buzzer_pin, GPIO.OUT)

        self._initial_frequency = 2000
        self._current_frequency = self._initial_frequency

        self._buzzer = GPIO.PWM(self._buzzer_pin, self._initial_frequency)
        self._buzzer.start(0)

    def _background_play(self, melody: Melody) -> None:
        for note in self._melodies[melody]:
            if note.set_frequency is not None:
                self._current_frequency = note.set_frequency
                self._buzzer.ChangeFrequency(self._current_frequency)
            elif self._current_frequency != self._initial_frequency:
                self._current_frequency = self._initial_frequency
                self._buzzer.ChangeFrequency(self._current_frequency)
            self._buzzer.ChangeDutyCycle(note.frequency)
            time.sleep(note.duration)
        self._buzzer.ChangeDutyCycle(0)

    def disable(self) -> None:
        self._buzzer.stop()
        GPIO.cleanup()


def buzzer_controller_factory(architecture: str) -> BuzzerController:
    """
    This function returns the correct buzzer controller for the current platform
    :return: the correct buzzer controller for the current platform
    """
    constructors: Mapping[str, Type[BuzzerController]] = {
        "x86_64": BuzzerControllerMock,
        "AMD64": BuzzerControllerMock,
        "aarch64": BuzzerControllerRaspberry,
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.INFO)
    buzzer_controller = buzzer_controller_factory(platform.machine())
    buzzer_controller.setup()

    try:
        while True:
            print("Select a melody to play:")
            for i, melody in enumerate(Melody, 1):
                print(f"{i} -> {melody.name}")
            melody = Melody(int(input()))
            buzzer_controller.play(melody)
    except KeyboardInterrupt:
        buzzer_controller.disable()


if __name__ == "__main__":
    main()
