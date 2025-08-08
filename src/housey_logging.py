import logging


def configure():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: [%(module)s.%(funcName)s:%(lineno)d]: %(message)s',
        filename='./config/going_live.log',
        level=logging.INFO
    )

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: [%(module)s.%(funcName)s:%(lineno)d]: %(message)s')
    )
    logging.getLogger().addHandler(console)

