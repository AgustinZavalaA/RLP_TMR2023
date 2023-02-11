import logging as log

import numpy as np


def sum(a: int, b: int) -> int:
    return a + b


def main():
    log.basicConfig(level=log.DEBUG, format='%(levelname)s - %(message)s')

    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")
    log.critical("critical")
    print('Hello World')
    log.info(np.zeros((3, 3)))


if __name__ == '__main__':
    main()
