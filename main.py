from functions import *
import sys, datetime
from admin import (
    ADMIN_GROUP_ID, 
    API_KEY 
    )

if __name__=="__main__": 
    print('Bot Starting...', datetime.datetime.now())
    newbot = OrcaBot(API_KEY, admin_group_id=ADMIN_GROUP_ID)
    newbot.main()
    
