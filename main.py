import logging as log

def main():
    log.basicConfig(level=log.DEBUG, format='%(levelname)s - %(message)s')

    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")
    log.critical("critical")
    print('Hello World')


if __name__ == '__main__':
    main()
