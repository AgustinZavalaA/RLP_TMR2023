import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping

import busio
from board import SCL, SDA
import adafruit_ssd1306

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
class OLEDDisplayControllerRaspberry(OLEDDisplayController):
    def setup(self) -> None:
        i2c = busio.I2C(SCL, SDA)
        self._oled_display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        
        self._oled_display.fill(0)
        self._oled_display.show()
        pass

    def display(self, text: str) -> None:
        self._save_text(text)
        
        self._oled_display.fill(0)
        self._oled_display.text(text, 0, 0, 1)
        self._oled_display.show()
        pass

    def disable(self) -> None:
        self.display("")      


def oled_display_controller_factory(architecture: str) -> OLEDDisplayController:
    constructors: Mapping[str, Type[OLEDDisplayController]] = {
        "x86_64": OLEDDisplayControllerMock,
        "AMD64": OLEDDisplayControllerMock,
        "aarch64": OLEDDisplayControllerRaspberry
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
