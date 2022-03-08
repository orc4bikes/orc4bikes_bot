import random
import json
import csv
import datetime
from decimal import Decimal

import os
from os import (path, mkdir)

import requests
import re

from bot_text import (
    START_MESSAGE,
    BAN_MESSAGE,
)

from admin import DEV_API_KEY

import database.controller as db

LOGGING_URL = os.environ.get('LOGGING_URL')

import logging
logger = logging.getLogger()
logger.warn("botty")



from telegram import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ParseMode, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    CallbackContext,
    CallbackQueryHandler,
    TypeHandler,
)

from warnings import filterwarnings
# See https://tinyurl.com/yuh2jzp3
filterwarnings(action="ignore", message=r".*CallbackQueryHandler")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        super().default(obj)  # Let the json module throw the error

def float_to_decimal(obj):
    """DynamoDB require Decimal in place of float"""
    return json.loads(json.dumps(obj, cls=DecimalEncoder), parse_float=Decimal)

def decimal_to_float(obj):
    return json.loads(json.dumps(obj, cls=DecimalEncoder))

class TeleBot:
    """
    Base Telegram bot for other classes to inherit 
    Provides data manipulation methods here
    
    """
    GMT = 8
    def __init__(self,api_key):
        self.api_key = api_key
        self.updater = Updater(token=api_key, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def now(self,gmt=None):
        if gmt is None:
            gmt = self.GMT
        return datetime.datetime.utcnow() + datetime.timedelta(hours=gmt)

    # def log_exception(self, e, text=""):
    #     if text: 
    #         print(text)
    #     print(f'Error occured at {self.now()}. Error is \n{e}')

    def calc_deduct(self,time_diff):
        """
        Calculate credits deductable given a time period
        This is a dummy command, that should be implemented in the main bot!
        """
        return Decimal(0)

    def check_user(self,update,context):
        """Check if user is registered, and not banned"""
        user_data = self.get_user(update,context)
        if user_data is None:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
            return False
        if user_data.get('is_ban'):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=BAN_MESSAGE
                )
            return False
        return True

    def get_user(self,update=None,context=None,username=None)  -> dict or None:
        """Gets the user data"""
        if username is not None:
            chat_id = self.get_user_id(username)
            if chat_id is None:
                return None
        else:
            chat_id = update.effective_chat.id
        user_data = db.get_user_data(chat_id)
        return user_data

    def update_user(self, user_data):
        chat_id = user_data.get('chat_id', None)
        if not chat_id:
            return None
        try:
            db.set_user_data(chat_id, user_data)
        except Exception as e:
            logger.exception(e)
    
    def get_user_id(self, username='') -> int:
        # table_data = dict()
        if not username:
            return None
        return db.get_username(username)
    
    def update_user_id(self, username, chat_id):
        db.set_username(username, chat_id)

    def get_bikes(self) -> dict:
        return db.get_all_bikes()
    
    def get_bike(self, bike_name) -> dict:
        return db.get_bike_data(bike_name)

    def update_bikes(self, bikes_data) -> None:
        raise FileNotFoundError

    def update_bike(self, bike_data) -> None:
        bike_name = bike_data.get('name')
        if not bike_name:
            return
        db.set_bike_data(bike_name, bike_data)

    def update_rental_log(self, update_list):
        """Updates rental logs with headers:
           bike,username,start_time,end_time"""

        data = decimal_to_float(update_list)
        requests.post(f"{LOGGING_URL}?file=rental", json=data)

    def update_report_log(self, update_list):
        """Updates report logs with headers:
           username,time,report"""
        data = decimal_to_float(update_list)
        requests.post(f"{LOGGING_URL}?file=report", json=data)

    def update_finance_log(self, update_list):
        """Updates finance logs with headers:
           username,time,initial_amt,change_amt,final_amt"""
        data = decimal_to_float(update_list)
        requests.post(f"{LOGGING_URL}?file=finance", json=data)

    def addnew(self,handler):
        self.dispatcher.add_handler(handler)

    def addcmd(self, command, methodname):
        handler = CommandHandler(command,methodname)
        self.addnew(handler)

    def addmsg(self, filters, methodname):
        handler = MessageHandler(filters, methodname)
        self.addnew(handler)
        

    def err(self, update, context):
        """Error handler callback for dispatcher"""
        error = context.error
        logger.exception(error)
        if update is not None and update.effective_user is not None:
            context.bot.send_message(update.effective_user.id,
                "I'm sorry, an error has occurred. The devs have been alerted!"
            )

    def initialize(self):
        self.updater.dispatcher.add_error_handler(self.err)

    def main(self):
        logger.info('Initializing bot...')
        self.initialize()
        self.updater.start_polling()
        self.updater.idle()



if __name__=="__main__":
    logger.info('Running the TeleBot!')
    newbot = TeleBot(DEV_API_KEY)
    newbot.main()
    
