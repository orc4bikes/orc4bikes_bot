from functions import *

API_KEY = '1722354435:AAHAFxP6_sIf_P4hdQJ7Y5EsH64PtyWwWo8' #this is old api for orcabikes_bot
# API_KEY = '1705378721:AAEbSmhxNhAY4s5eqWMSmxdCxkf44O7_nss' #new key for orc4bikes_bot
ADMIN_GROUP_ID = -580241456  # dev log group to be updated to new group
# ADMIN_GROUP_ID = -572304795 # Actual group id

if __name__=="__main__": 
    # DEV part, do not run this
    newbot = OrcaBot(API_KEY, admin_group_id=ADMIN_GROUP_ID)
    newbot.main()
