from Orc4bikesBot import Orc4bikesBot
from admin import (
    ADMIN_GROUP_ID,
    API_KEY
    )

if __name__=="__main__":
    newbot = Orc4bikesBot(API_KEY, admin_group_id=ADMIN_GROUP_ID, promo=True)
    newbot.main()