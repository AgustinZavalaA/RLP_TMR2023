import platform

import py_trees.common

from RLP_TMR2023.hardware_controllers.imu_controller import imu_controller_factory


class IMUToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="IMU To BB")
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key("is_robot_stuck", access=py_trees.common.Access.WRITE)

        self._imu = imu_controller_factory(platform.machine())

    def update(self):
        self._blackboard.is_robot_stuck = self._imu.is_robot_stuck()

        return py_trees.common.Status.SUCCESS
