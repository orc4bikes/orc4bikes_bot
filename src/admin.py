import os
import sys

if os.environ.get('BOT_ENV') is None:
    import dotenv
    dotenv.load_dotenv()
    if os.environ.get('BOT_ENV') is None:
        # logger.critical("No environment variables found. Exiting.")
        sys.exit()

BOT_ENV                = os.environ.get('BOT_ENV')
BOT_PROMO              = os.environ.get('BOT_PROMO').lower() in ('true', '1')
BOT_GMT_OFFSET         = int(os.environ.get('BOT_GMT_OFFSET'))
BOT_DEDUCT_RATE        = int(os.environ.get('BOT_DEDUCT_RATE'))

DB_ACCESS_KEY          = os.environ.get('DB_ACCESS_KEY')
DB_SECRET_KEY          = os.environ.get('DB_SECRET_KEY')
DB_REGION_NAME         = os.environ.get('DB_REGION_NAME')

TELE_API_TOKEN         = os.environ.get('TELE_API_TOKEN')
LOGGING_URL            = os.environ.get('LOGGING_URL')
QR_DATA_FILEPATH       = os.environ.get('QR_DATA_FILEPATH')

ADMIN_GROUP_ID         = os.environ.get('ADMIN_GROUP_ID')      # group chat_id

ADMIN_HEAD             = os.environ.get('ADMIN_HEAD')
ADMIN_HEAD_MOBILE      = os.environ.get('ADMIN_HEAD_MOBILE')
ADMIN_HEAD_NAME        = os.environ.get('ADMIN_HEAD_NAME')
ADMIN_SAFETY           = os.environ.get('ADMIN_SAFETY')
ADMIN_SAFETY_MOBILE    = os.environ.get('ADMIN_SAFETY_MOBILE')
ADMIN_SAFETY_NAME      = os.environ.get('ADMIN_SAFETY_NAME')
ADMIN_TREASURER        = os.environ.get('ADMIN_TREASURER')
ADMIN_TREASURER_MOBILE = os.environ.get('ADMIN_TREASURER_MOBILE')
ADMIN_TREASURER_NAME   = os.environ.get('ADMIN_TREASURER_NAME')
ADMIN_TREASURER_URL    = os.environ.get('ADMIN_TREASURER_URL')
ADMIN_DEV              = os.environ.get('ADMIN_DEV')

ADMIN_LIST             = os.environ.get('ADMIN_LIST').strip().split(',')
