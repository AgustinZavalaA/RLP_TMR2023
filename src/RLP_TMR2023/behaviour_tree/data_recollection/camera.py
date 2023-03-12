import platform

import py_trees.common

from RLP_TMR2023.hardware_controllers.camera_controller import camera_controller_factory


class CameraToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Camera To BB")
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key("current_frame", access=py_trees.common.Access.WRITE)

        self._camera = camera_controller_factory(platform.machine())

    def update(self):
        self._blackboard.current_frame = self._camera.detect_objects()

        return py_trees.common.Status.SUCCESS
