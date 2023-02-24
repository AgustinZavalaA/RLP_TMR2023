import logging
from hardware_controllers import motors_controller
from hardware_controllers import camera_controller

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


if __name__ == '__main__':
    # main()
    main2()
