import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping

from RLP_TMR2023.hardware_controllers.singleton import Singleton

logger = logging.getLogger(__name__)


class OLEDDisplayController(metaclass=Singleton):
    def __init__(self):
        self._text = ""

    @abstractmethod
    def setup(self) -> None:
        pass

    def _save_text(self, text: str) -> None:
        self._text = text

    @abstractmethod
    def display(self, text: str) -> None:
        pass

    def append(self, text: str) -> None:
        self.display(self._text + text)

    def clear(self) -> None:
        self.display("")

    @abstractmethod
    def disable(self) -> None:
        pass


class OLEDDisplayControllerMock(OLEDDisplayController):
    """
    This class is a mock for the OLEDDisplayController class, it is used when the program is running on a computer
    """

    def __init__(self):
        super().__init__()
        logger.info("Instantiating Singleton OLEDDisplayControllerMock")

    def setup(self) -> None:
        logger.info("OLEDDisplayControllerMock.setup() called")

    def display(self, text: str) -> None:
        self._save_text(text)
        logger.info(f"Displaying text: {text}")

    def disable(self) -> None:
        logger.info("Disabling OLEDDisplayControllerMock")


# TODO: Add a class for the real OLEDDisplayController
# class OLEDDisplayControllerRaspberry(OLEDDisplayController):

def oled_display_controller_factory(architecture: str) -> OLEDDisplayController:
    constructors: Mapping[str, Type[OLEDDisplayController]] = {
        "x86_64": OLEDDisplayControllerMock,
        "AMD64": OLEDDisplayControllerMock,
        # TODO: "aarch64": add the real OLEDDisplayControllerRaspberry
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.INFO)
    display = oled_display_controller_factory(platform.machine())
    display.setup()
    display.display("Hello World!")
    time.sleep(0.5)
    display.append(" How are you?")
    time.sleep(0.5)
    display.clear()
    time.sleep(0.5)
    display.append("I'm fine, thanks!")
    time.sleep(0.5)
    display.disable()


if __name__ == "__main__":
    main()
