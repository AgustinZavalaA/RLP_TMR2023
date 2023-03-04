import py_trees.common


class DistanceToBB(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Distance To BB")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("distance", access=py_trees.common.Access.WRITE)

        # TODO remove this
        self.actual_index = 0
        self.mock_values = [
            10, 20, 30, 5, 12, 13
        ]

    def update(self):
        self.blackboard.distance = self.mock_values[self.actual_index]
        self.actual_index += 1
        if self.actual_index >= len(self.mock_values):
            self.actual_index = 0

        return py_trees.common.Status.SUCCESS
