import argparse
import cProfile
import logging
import platform
import pstats

import py_trees.common
import py_trees.console

from RLP_TMR2023.behaviour_tree.root import create_root, get_data_recollection_subtree
from RLP_TMR2023.hardware_controllers.camera_controller import camera_controller_factory
from RLP_TMR2023.hardware_controllers.distance_sensors_controller import distance_sensors_controller_factory
from RLP_TMR2023.hardware_controllers.imu_controller import imu_controller_factory
from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory
from RLP_TMR2023.hardware_controllers.oled_display_controller import oled_display_controller_factory
from RLP_TMR2023.hardware_controllers.servos_controller import servos_controller_factory

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(module)s:%(funcName)s - %(message)s")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Attach debugger to bt", action="store_true")
    parser.add_argument("--release", help="Disable all logging", action="store_true")
    parser.add_argument("--render-tree", help="Render tree to svg and exit", action="store_true")
    parser.add_argument("--profile", help="Profile the data recollection subtree", action="store_true")
    parser.add_argument("--interactive", help="Interactive mode", action="store_true")
    args = parser.parse_args()
    return args


def initialize_controllers() -> None:
    # Initialization of controllers
    motors = motors_controller_factory(platform.machine())
    motors.setup()
    camera = camera_controller_factory(platform.machine())
    camera.setup()
    distance_sensor = distance_sensors_controller_factory(platform.machine())
    distance_sensor.setup()
    imu = imu_controller_factory(platform.machine())
    imu.setup()
    oled_display = oled_display_controller_factory(platform.machine())
    oled_display.setup()
    servos = servos_controller_factory(platform.machine())
    servos.setup()


def disable_controllers() -> None:
    # Initialization of controllers
    motors = motors_controller_factory(platform.machine())
    motors.disable()
    camera = camera_controller_factory(platform.machine())
    camera.disable()
    distance_sensor = distance_sensors_controller_factory(platform.machine())
    distance_sensor.disable()
    imu = imu_controller_factory(platform.machine())
    imu.disable()
    oled_display = oled_display_controller_factory(platform.machine())
    oled_display.disable()
    servos = servos_controller_factory(platform.machine())
    servos.disable()


def profile_data_recollection_subtree() -> None:
    data_recollection = get_data_recollection_subtree()
    with cProfile.Profile() as pr:
        data_recollection.tick_once()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
    stats.dump_stats("data_recollection.prof")


def run_behaviour_tree(args: argparse.Namespace):
    root = create_root()
    print(py_trees.display.ascii_tree(root))

    if args.profile:
        profile_data_recollection_subtree()
        return

    if args.render_tree:
        py_trees.display.render_dot_tree(root,
                                         target_directory="bt_images",
                                         with_blackboard_variables=True)
        return

    behaviour_tree = py_trees.trees.BehaviourTree(root)
    if args.debug:
        behaviour_tree.visitors.append(py_trees.visitors.DisplaySnapshotVisitor(
            display_blackboard=True,
            # display_activity_stream=True,
            display_only_visited_behaviours=True,
        ))

    while True:
        try:
            behaviour_tree.tick()
            # print(py_trees.display.ascii_tree(root, show_status=True))
            if args.interactive:
                py_trees.console.read_single_keypress()
        except KeyboardInterrupt:
            break


def main():
    args = parse_arguments()
    if args.release:
        logging.disable(logging.CRITICAL)

    initialize_controllers()
    run_behaviour_tree(args)
    disable_controllers()


if __name__ == '__main__':
    main()
