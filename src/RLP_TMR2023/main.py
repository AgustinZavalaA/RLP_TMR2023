import logging
import platform

import py_trees.common
import py_trees.console

from RLP_TMR2023.behaviour_tree.root import create_root
from hardware_controllers import camera_controller
from hardware_controllers import motors_controller
from hardware_controllers.motors_controller import motors_controller_factory

logging.basicConfig(level=logging.DEBUG, format="%(module)s:%(funcName)s - %(levelname)s - %(message)s")


def main():
    # log.basicConfig(level=log.DEBUG, format='%(levelname)s - %(message)s')
    #
    # log.debug("debug")
    # log.info("info")
    # log.warning("warning")
    # log.error("error")
    # log.critical("critical")
    # print('Hello World')
    # log.info(np.zeros((3, 3)))
    motors_controller.main()
    pass


def main2():
    camera_controller.main()


def main_bt():
    # Initialization of controllers
    motors = motors_controller_factory(platform.machine())
    motors.setup()

    behaviour_tree = create_root()
    print(py_trees.display.ascii_tree(behaviour_tree))

    while True:
        try:
            behaviour_tree.tick_once()
            print(py_trees.display.ascii_tree(behaviour_tree, show_status=True))
            py_trees.console.read_single_keypress()
        except KeyboardInterrupt:
            py_trees.display.render_dot_tree(behaviour_tree,
                                             target_directory="bt_images",
                                             with_blackboard_variables=True)
            break

    motors.disable()


if __name__ == '__main__':
    # main()
    # main2()
    main_bt()
