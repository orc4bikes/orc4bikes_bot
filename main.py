import logging

from Orc4bikesBot import Orc4bikesBot
from admin import (
    ADMIN_GROUP_ID,
    API_KEY
    )

if __name__=="__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(filename)s: [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    newbot = Orc4bikesBot(API_KEY, admin_group_id=ADMIN_GROUP_ID, promo=True)
    newbot.main()
