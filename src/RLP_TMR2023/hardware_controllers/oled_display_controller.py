import logging
import platform
import time
from abc import abstractmethod
from typing import Type, Mapping
from dataclasses import dataclass
from importlib.resources import  path

logger = logging.getLogger(__name__)

try:
    import busio
    from board import SCL, SDA
    import adafruit_ssd1306
except ImportError:
    logger.warning("Could not import busio, board, adafruit_ssd1306. This is expected when running on a computer")

from RLP_TMR2023.hardware_controllers.singleton import Singleton
from RLP_TMR2023.hardware_controllers import fonts


@dataclass
class DisplayMessage:
    state: str = ""
    substate: str = ""
    message: str = ""
    debug: str = ""
    
def get_default_font() -> str:
    with path(fonts, "font5x8.bin") as font_path:
        return str(font_path)


class OLEDDisplayController(metaclass=Singleton):
    def __init__(self):
        self._display_message = DisplayMessage()

    @abstractmethod
    def setup(self) -> None:
        pass

    def update_message(self, state: str = None, substate: str = None, message: str = None, debug: str = None) -> None:
        if state is not None:
            self._display_message.state = state
        if substate is not None:
            self._display_message.substate = substate
        if message is not None:
            self._display_message.message = message
        if debug is not None:
            self._display_message.debug = debug
            
        self._display()
            

    @abstractmethod
    def _display(self) -> None:
        pass


    def clear(self) -> None:
        self.update_message(state="", substate="", message="", debug="")

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

    def _display(self) -> None:
        logger.info(f"Displaying text: {self._display_message}")

    def disable(self) -> None:
        logger.info("Disabling OLEDDisplayControllerMock")


class OLEDDisplayControllerRaspberry(OLEDDisplayController):
    def setup(self) -> None:
        i2c = busio.I2C(SCL, SDA)
        self._oled_display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        self._font = get_default_font()

        self.clear()

    def _display(self) -> None:
        self._oled_display.fill(0)
        self._oled_display.text(self._display_message.state, 0, 0, 1, font_name=self._font)
        self._oled_display.text(self._display_message.substate, 0, 8, 1, font_name=self._font)
        self._oled_display.text(self._display_message.message, 0, 16, 1, font_name=self._font)
        self._oled_display.text(self._display_message.debug, 0, 24, 1, font_name=self._font)
        self._oled_display.show()

    def disable(self) -> None:
        self.update_message(state="", substate="", message="", debug="")


def oled_display_controller_factory(architecture: str) -> OLEDDisplayController:
    constructors: Mapping[str, Type[OLEDDisplayController]] = {
        "x86_64": OLEDDisplayControllerMock,
        "AMD64": OLEDDisplayControllerMock,
        "aarch64": OLEDDisplayControllerRaspberry
    }
    return constructors[architecture]()


def main():
    logging.basicConfig(level=logging.DEBUG)
    display = oled_display_controller_factory(platform.machine())
    display.setup()
    display.update_message(state="Hello World!")
    time.sleep(1)
    display.update_message(substate="How are you?")
    time.sleep(1)
    display.clear()
    time.sleep(1)
    display.update_message(message="I'm fine, thanks!")
    time.sleep(1)
    display.update_message(debug="HOLIS")
    time.sleep(1)
    display.disable()


if __name__ == "__main__":
    main()
