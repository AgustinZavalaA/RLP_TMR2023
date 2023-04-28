import logging
import platform

from RLP_TMR2023.hardware_controllers.buzzer_controller import buzzer_controller_factory, Melody
from RLP_TMR2023.hardware_controllers.distance_sensors_controller import distance_sensors_controller_factory, \
    any_sensor_strategy

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    buzzer = buzzer_controller_factory(platform.machine())
    ultrasonic = distance_sensors_controller_factory(platform.machine())
    buzzer.setup()
    ultrasonic.setup()

    try:
        while True:
            if ultrasonic.is_about_to_collide(any_sensor_strategy):
                buzzer.play(Melody.AXOLOTE_EATING)
    except:
        buzzer.disable()
        ultrasonic.disable()


if __name__ == "__main__":
    main()
