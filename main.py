import logging
import os
import sys

from admin import (
    ADMIN_GROUP_ID,
    TELE_API_TOKEN
)
from Orc4bikesBot import Orc4bikesBot

if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(filename)s: [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)



    newbot = Orc4bikesBot(TELE_API_TOKEN, admin_group_id=ADMIN_GROUP_ID, promo=False)
    newbot.main()
