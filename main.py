import logging


import os
import sys


if __name__=="__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(filename)s: [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if os.environ.get("BOT_ENV") == None:
        import dotenv
        dotenv.load_dotenv()
        if os.environ.get("BOT_ENV") == None:
            logger.critical("No environment variables found. Exiting.")
            sys.exit()

    from Orc4bikesBot import Orc4bikesBot
    from admin import (
        ADMIN_GROUP_ID,
        TELE_API_TOKEN
        )

    newbot = Orc4bikesBot(TELE_API_TOKEN, admin_group_id=ADMIN_GROUP_ID, promo=False)
    newbot.main()
