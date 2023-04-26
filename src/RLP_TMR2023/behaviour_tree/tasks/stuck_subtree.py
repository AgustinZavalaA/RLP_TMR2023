import time
import platform
import py_trees.common

from RLP_TMR2023.constants import bt_values
from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory


class StuckPrevention(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Move forward")
        self._motors = motors_controller_factory(platform.machine())
        self._stuck_time = None

    def update(self):
        if self._stuck_time is None:
            self._stuck_time = time.perf_counter()

        if time.perf_counter() - self._stuck_time < bt_values.STUCK_TIME_LIMIT:
            pass
