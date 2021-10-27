import random
import json # use json to store bicycles.json and user data
import csv # use csv to store logs of rental
import datetime

from os import (path, mkdir)

import requests
import re

from bot_text import (
    START_MESSAGE,
    BAN_MESSAGE,
)

from admin import DEV_API_KEY

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


class TeleBot:

    """
    Base Telegram bot for other classes to inherit 
    Provides data manipulation methods here
    
    """
    GMT = 8
    USER_PATH = 'database/users'

    def __init__(self,api_key):
        self.api_key = api_key
        self.updater = Updater(token=api_key, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def now(self,gmt=None):
        if gmt is None:
            gmt = self.GMT
        return datetime.datetime.utcnow() + datetime.timedelta(hours=gmt)

    def log_exception(self, e, text=""):
        if text: 
            print(text)
        print(f'Error occured at {self.now()}. Error is \n{e}')

    def calc_deduct(self,time_diff):
        """
        Calculate credits deductable given a time period
        This is a dummy command, that should be implemented in the main bot!
        """
        return 0

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

    def get_user(self,update=None,context=None,username=None, userpath=None)  -> dict or None:
        if userpath is None:
            userpath = self.USER_PATH
        if username is not None:
            chat_id = self.get_user_table().get(username)
            if chat_id is None:
                return None
        else:
            chat_id = update.effective_chat.id
        try:
            if not path.exists(userpath):
                mkdir('database/users')
                userpath = 'database/users'
            with open(f'{userpath}/{chat_id}.json', 'r') as f:
                user_data = json.load(f)
        except FileNotFoundError: # User doesn't exist!
            user_data = None
        return user_data

    def update_user(self, user_data):
        chat_id = user_data.get('chat_id', None)
        if not chat_id:
            return None
        if not path.exists(self.USER_PATH):
            mkdir(self.USER_PATH)
        with open(f'{self.USER_PATH}/{chat_id}.json', 'w') as f:
            json.dump(user_data, f, sort_keys=True, indent=4)
    
    def get_user_table(self, userpath=None) -> dict:
        if userpath is None:
            userpath = self.USER_PATH
        table_data = dict()
        try:
            with open(f'{userpath}/table.json', 'r') as f:
                table_data = json.load(f)
        except FileNotFoundError:
            self.update_user_table({})
        return table_data
    
    def update_user_table(self, update_field, userpath=None):
        if userpath is None:
            userpath = self.USER_PATH
        with open(f'{userpath}/table.json', 'w') as f:
            json.dump(update_field, f, sort_keys=True, indent=4)

    def get_bikes(self) -> dict:
        with open('database/bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        return bikes_data

    def update_bikes(self, bikes_data) -> None:
        with open('database/bicycles.json', 'w') as f:
            json.dump(bikes_data, f, sort_keys=True, indent=4)

    def update_rental_log(self, update_list):
        """Updates rental logs with headers:
           bike,username,start_time,end_time"""
        if not path.exists('database/logs'):
            mkdir('database/logs')
        with open('database/logs/rental.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(update_list)

    def update_report_log(self, update_list):
        """Updates report logs with headers:
           username,time,report"""
        if not path.exists('database/logs'):
            mkdir('database/logs')
        with open('database/logs/report.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(update_list)

    def update_finance_log(self, update_list):
        """Updates finance logs with headers:
           username,time,initial_amt,change_amt,final_amt"""
        if not path.exists('database/logs'):
            mkdir('database/logs')
        with open('database/logs/finance.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(update_list)

    def addnew(self,handler):
        self.dispatcher.add_handler(handler)

    def addcmd(self, command, methodname):
        handler = CommandHandler(command, methodname)
        self.addnew(handler)

    def addmsg(self, filters, methodname):
        handler = MessageHandler(filters, methodname)
        self.addnew(handler)

    def initialize(self):
        pass

    def main(self):
        print('Initializing bot...')
        self.initialize()
        self.updater.start_polling()
        self.updater.idle()



if __name__=="__main__":
    print('Running the TeleBot!')
    newbot = TeleBot(DEV_API_KEY)
    newbot.main()
    
