from RLP_TMR2023.HardwareControllers.ProbandoSingleton import prueb_motor_falso_factory


def sum(a: int, b: int) -> int:
    return a + b


def tst_singletons() -> None:
    # p = PruebaMotorFalso()
    # p.setup(5)
    #
    # p.increment()
    # p.increment()
    # # print(p.get_number_of_turns())
    #
    # p2 = PruebaMotorFalso()
    # p2.increment()
    # # print(p2.get_number_of_turns())
    #
    # p3 = PruebaMotorFalso()
    # # print(p3.get_number_of_turns())
    pass


def probando_factory_con_singleton() -> None:
    # p = prueb_motor_falso_factory(platform.machine())
    # p.setup(5)
    # p.increment()
    # p.increment()
    #
    # p.get_number_of_turns()
    #
    # p2 = prueb_motor_falso_factory(platform.machine())
    # p2.increment()
    # p2.get_number_of_turns()
    p = prueb_motor_falso_factory("armv7l")
    p.setup(5)
    p.increment()
    p.increment()

    print(p.get_number_of_turns())

    p2 = prueb_motor_falso_factory("armv7l")
    p2.increment()
    print(p2.get_number_of_turns())


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

    # test_singletons()
    probando_factory_con_singleton()


if __name__ == '__main__':
    main()
