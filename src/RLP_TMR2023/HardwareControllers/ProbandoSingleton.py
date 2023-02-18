from abc import abstractmethod

from RLP_TMR2023.HardwareControllers.Singleton import Singleton


class PruebaMotorFalso(metaclass=Singleton):
    def __init__(self):
        self.number_of_turns = 0

    @abstractmethod
    def setup(self, x: int):
        pass

    @abstractmethod
    def increment(self):
        pass

    @abstractmethod
    def get_number_of_turns(self) -> int | None:
        pass


# esta clase muestra el texto a terminal
class PruebaMotorFalsoWindows(PruebaMotorFalso):
    def __init__(self):
        super().__init__()

    def setup(self, x: int):
        self.number_of_turns = x
        print(self.number_of_turns)

    def increment(self):
        self.number_of_turns += 1
        print(self.number_of_turns)

    def get_number_of_turns(self) -> None:
        print(self.number_of_turns)


# esta clase es silenciosa, no imprime nada
class PruebaMotorFalsoRaspberry(PruebaMotorFalso):
    def __init__(self):
        super().__init__()

    def setup(self, x: int):
        self.number_of_turns = x

    def increment(self):
        self.number_of_turns += 1

    def get_number_of_turns(self) -> int:
        return self.number_of_turns


def prueb_motor_falso_factory(architecture: str) -> PruebaMotorFalso:
    constructors = {
        'x86_64': PruebaMotorFalsoWindows,
        'armv7l': PruebaMotorFalsoRaspberry,
    }

    return constructors[architecture]()
