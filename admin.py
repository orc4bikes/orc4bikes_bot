import os

ADMIN_LIST = [
    # Your admins chat_id here
]

# API token from telegram, to be retrieved from @botfather
DEV_API_KEY = os.environ.get('DEV_API_KEY') # API token for development purposes, to run in functions.py
API_KEY = os.environ.get('API_KEY') # API token for production

# Chat ID for administrative purposes, a copy of rental logs will be sent here
DEV_ADMIN_GROUP_ID = os.environ.get('DEV_ADMIN_GROUP_ID') # group chat_id for development purposes
ADMIN_GROUP_ID = os.environ.get('ADMIN_GROUP_ID') # group chatchat_id for production
