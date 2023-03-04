import platform

import py_trees.common

from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory, MotorSide, MotorDirection


class CrashPrevention(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Go back")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("distance", access=py_trees.common.Access.READ)
        self.motors = motors_controller_factory(platform.machine())

    def update(self):
        self.motors.move(MotorSide.LEFT, 100, MotorDirection.BACKWARD)
        self.motors.move(MotorSide.RIGHT, 100, MotorDirection.BACKWARD)
        return py_trees.common.Status.SUCCESS


class GoForward(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Go forward")
        self.motors = motors_controller_factory(platform.machine())

    def update(self):
        self.motors.move(MotorSide.LEFT, 100, MotorDirection.FORWARD)
        self.motors.move(MotorSide.RIGHT, 100, MotorDirection.FORWARD)
        return py_trees.common.Status.SUCCESS


def create_crash_subtree() -> py_trees.behaviour.Behaviour:
    distance_threshold = 15
    crash_subtree = py_trees.composites.Selector("Crash subtree", memory=False)

    crash_subtree.add_child(py_trees.decorators.EternalGuard(name="About to crash?",
                                                             child=CrashPrevention(),
                                                             condition=lambda
                                                                 blackboard: blackboard.distance < distance_threshold,
                                                             blackboard_keys={"distance"},
                                                             ))

    crash_subtree.add_child(GoForward())

    return crash_subtree
