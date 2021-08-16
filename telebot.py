import random
import json # use json to store bicycles.json and user data
import csv # use csv to store logs of rental
import datetime

import requests
import re

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
    def __init__(self,api_key):
        self.api_key = api_key
        self.updater = Updater(token=api_key, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def get_user(self,update,context)  -> dict or None:
        chat_id = update.effective_chat.id
        try:
            with open(f'users/{chat_id}.json', 'r') as f:
                user_data = json.load(f)
        except FileNotFoundError:
            # User doesn't exist!
            user_data = None
        return user_data

    def update_user(self, user_data):
        chat_id = user_data.get('chat_id', None)
        if not chat_id:
            return None
        with open(f'users/{chat_id}.json', 'w') as f:
            json.dump(user_data, f, sort_keys=True, indent=4)
    
    def get_user_table(self) -> dict:
        table_data = dict()
        try:
            with open('users/table.json', 'r') as f:
                table_data = json.load(f)
        except FileNotFoundError:
            self.update_user_table({})
        return table_data
    
    def update_user_table(self, update_field):
        with open('users/table.json', 'w') as f:
            json.dump(update_field, f, sort_keys=True, indent=4)

    def get_bikes(self) -> dict:
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        return bikes_data

    def update_bikes(self, bikes_data) -> None:
        with open('bicycles.json', 'w') as f:
            json.dump(bikes_data, f, sort_keys=True, indent=4)

    def update_rental_log(self, update_list):
        with open('logs/rental.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(update_list)

    def update_report_log(self, update_list):
        with open('logs/report.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(update_list)

    def addnew(self,handler):
        self.dispatcher.add_handler(handler)

    def addcmd(self, command, methodname):
        handler = CommandHandler(command,methodname)
        self.addnew(handler)

    def addmsg(self, filters, methodname):
        handler = MessageHandler(filters, methodname)
        self.addnew(handler)

    def main(self):
        print('Initializing bot...')
        self.updater.start_polling()
        self.updater.idle()