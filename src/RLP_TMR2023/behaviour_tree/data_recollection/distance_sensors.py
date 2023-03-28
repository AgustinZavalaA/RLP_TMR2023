import platform

import py_trees.common

from RLP_TMR2023.hardware_controllers.distance_sensors_controller import distance_sensors_controller_factory, \
    all_sensors_strategy


class DistanceSensorsToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Distance Sensors To BB")
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key("is_robot_about_to_collide", access=py_trees.common.Access.WRITE)

        self._distance_sensor = distance_sensors_controller_factory(platform.machine())

    def update(self):
        self._blackboard.is_robot_about_to_collide = self._distance_sensor.is_about_to_collide(all_sensors_strategy)

        return py_trees.common.Status.SUCCESS
