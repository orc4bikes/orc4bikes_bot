import logging

from Orc4bikesBot import Orc4bikesBot

if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(filename)s: [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    newbot = Orc4bikesBot()
    logger.info("Running Orc4bikesBot now")
    newbot.main()
