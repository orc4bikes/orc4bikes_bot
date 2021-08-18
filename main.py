from functions import OrcaBot
from admin import (
    ADMIN_GROUP_ID, 
    API_KEY 
    )

if __name__=="__main__": 
    # DEV part, do not run this
    newbot = OrcaBot(API_KEY, admin_group_id=ADMIN_GROUP_ID)
    newbot.main()
    
