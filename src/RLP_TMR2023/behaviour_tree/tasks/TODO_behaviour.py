import logging

import py_trees.common

logger = logging.getLogger(__name__)


class TODOBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bypass: bool = True) -> None:
        super().__init__(name=name)
        self._bypass = bypass
        logger.critical(f"'{name}' subtree is not implemented")

    def update(self) -> py_trees.common.Status:
        if self._bypass:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
