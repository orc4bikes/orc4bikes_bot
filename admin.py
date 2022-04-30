import os

ADMIN_LIST = [
    # Your admins' chat_id here
    int(s) for s in os.environ.get('ADMIN_LIST','').strip().split(',')
]

# API token from telegram, to be retrieved from @botfather
TELE_API_TOKEN = os.environ.get('TELE_API_TOKEN') # API token for production

# Chat ID for administrative purposes, a copy of rental logs will be sent here
DEV_ADMIN_GROUP_ID = os.environ.get('DEV_ADMIN_GROUP_ID') # group chat_id for development purposes
ADMIN_GROUP_ID = os.environ.get('ADMIN_GROUP_ID') # group chatchat_id for production
