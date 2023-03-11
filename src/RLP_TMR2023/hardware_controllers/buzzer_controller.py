import logging
import platform
import threading
import time
from abc import abstractmethod
from typing import Type, Mapping

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class BuzzerController(metaclass=Singleton):
    @abstractmethod
    def setup(self) -> None:
        pass

    # TODO: remember to make this method async or multiprocessing (SUPER IMPORTANT) as it will be called from the
    #  main thread and it does not need to be blocking
    @abstractmethod
    def _background_play(self, frequency: int, duration_seconds: float) -> None:
        pass

    def play(self, frequency: int, duration_seconds: float = 1) -> None:
        """
        This method plays a tone with the given frequency and duration, calls the _background_play method as it is a
        blocking method
        :param frequency: the frequency of the tone
        :param duration_seconds: the duration of the tone in seconds
        """
        thread = threading.Thread(target=self._background_play, args=(frequency, duration_seconds))
        thread.daemon = True
        thread.start()

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

    def _background_play(self, frequency: int, duration: float) -> None:
        logger.info(f"Playing a tone with frequency {frequency} and duration {duration}")
        time.sleep(duration)
        logger.info("Done playing the tone")

    def disable(self) -> None:
        logger.info("Disabling buzzer")


# TODO: add a buzzer controller for the raspberry pi
# class BuzzerControllerRaspberry(BuzzerController):

def buzzer_controller_factory(architecture: str) -> BuzzerController:
    """
    This function returns the correct buzzer controller for the current platform
    :return: the correct buzzer controller for the current platform
    """
    constructors: Mapping[str, Type[BuzzerController]] = {
        "x86_64": BuzzerControllerMock,
        "AMD64": BuzzerControllerMock,
        # TODO: add the raspberry pi constructor
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.INFO)
    buzzer_controller = buzzer_controller_factory(platform.machine())
    buzzer_controller.setup()
    buzzer_controller.play(440, 1)
    time.sleep(0.5)
    buzzer_controller.play(880, 0.5)
    time.sleep(1)
    buzzer_controller.play(1760)
    time.sleep(1.5)
    buzzer_controller.disable()


if __name__ == "__main__":
    main()
