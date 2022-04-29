from admin import (
    DEV_ADMIN_GROUP_ID,
    ADMIN_LIST,
    DEV_API_KEY,
)

from bot_text import (
    ROUTES_LIST,
    ROUTES_PICS,
    CHEER_LIST,
    HELP_TEXT,
    ADMIN_TEXT,
    START_MESSAGE,
    EMOJI,
    GUIDE_PIC
)

from telebot import TeleBot

import random
import json
import csv
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

import logging
logger = logging.getLogger()

class UserBot(TeleBot):
    def __init__(self,
            api_key,
            admin_group_id=DEV_ADMIN_GROUP_ID,
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT,
        ):
        self.admin_group_id = admin_group_id
        self.admin_list = admin_list
        self.admin_text = admin_text
        super().__init__(api_key)


    def start_command(self,update,context):
        """
        Initializes the bot
        This is where we initialize a new user
        If the user is not created, a new entry is created
        in the database with primary key as chat_id
        """
        user_data = super().get_user(update,context)
        if user_data is not None:
            text = f'Welcome back, {update.message.from_user.first_name}! '
        else:
            chat_id = update.effective_chat.id
            if chat_id>0:
                user_data = {'chat_id': chat_id,
                            'first_name': update.message.from_user.first_name,
                            'last_name' : update.message.from_user.last_name,
                            'username':   update.message.from_user.username,
                            'credits': 0,
                            'finance':[],
                            'log':[],
                            'bike_name':'',
                            'status':None,
                            }
                super().update_user(user_data)
            else:
                context.bot.send_message(
                    chat_id=chat_id,
                    text=f'Hi @{update.message.from_user.username}, please start the bot privately, and not in groups!!'
                )
                return

            text = f'Hello, {update.message.from_user.first_name}! '
        text+='This is your orc4bikes friendly neighbourhood bot :)'
        text += "\n"
        text += "\nFor available commands, send /help"
        text += "\nTo use our bikes, /topup now!"

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)

        if update.effective_chat.id > 0:
            username=update.message.from_user.username
            if username: 
                super().update_user_id(username, update.effective_chat.id)

    def help_command(self,update,context):
        """Show a list of possible commands"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = self.help_text,
            parse_mode=ParseMode.MARKDOWN)

    def guide_command(self,update,context):
        """Shows you guide to renting bike"""
        try:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = "Here's the guide! Do you want to /rent ?",
                photo = GUIDE_PIC,
            )
        except Exception as e:
            logger.exception(e)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, /guide currently not available... please try again!",
            )

    def history_command(self,update,context):
        """Shows past 10 transaction history"""
        if not self.check_user(update,context):
            return -1
        user_data = super().get_user(update,context)
        data = user_data.get('finance',[])[-10:] # get the last 10 transactions
        if data:
            text=f"Your past {len(data)} transaction history are as follows:\n\n"
            for i,line in enumerate(data,1):
                if line['type']=='admin':
                    text+=f'--: An admin {"added" if line["change"]>=0 else "deducted"} {line["change"]} credits on {line["time"]}. You now have {line["final"]} credits.\n'
                elif line['type']=='payment':
                    text+=f'--: You topped up {line["change"]} credits on {line["time"]}. You now have {line["final"]} credits.\n'
                elif line['type']=='rental':
                    text+=f'--: You rented a bike on {line["time"]}, and spent {line["spent"]} credits. You now have {line["remaining"]} credits.\n'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You haven't cycled with us before :( Send /rent to start renting now!"
            )

    def bikes_command(self,update,context):
        """Show all available bikes. Used in /rent"""
        bikes_data = self.get_bikes()
        avail, not_avail = list(), list()
        for bike in bikes_data:
            if not bike.get('status'):
                avail.append(bike)
            else:
                not_avail.append(bike)

        avail = "\n".join( b["name"]+' '+EMOJI["tick"] for b in avail )
        not_avail = "\n".join(f'{b["name"]} {EMOJI["cross"]} -- {"on rent" if b.get("username") else b["status"]}'  for b in not_avail )
        text = f'Bicycles:\n{avail}'
        text+= '\n\n' if avail else ''
        text+= f'{not_avail}'
        text+= "\n\nTo start your journey, send /rent"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )

    def status_command(self,update,context):
        """Check the user rental status and current credits"""
        if not self.check_user(update,context):
            return -1
        user_data = super().get_user(update,context)

        status = user_data.get('status',None)
        if status is not None:
            status = datetime.datetime.fromisoformat(status)
            curr = self.now()
            diff = curr - status
            if diff.days:
                strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
            else:
                strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
            status_text = f'You have been renting {user_data["bike_name"]} for {strdiff}. '
            deduction = self.calc_deduct(diff)
            status_text += f'\n\nCREDITS:\nCurrent:  {user_data.get("credits")} \nThis trip:  {deduction}\nProjected final:  {user_data.get("credits") - deduction}'
        else:
            creds = user_data.get("credits", 0)
            status_text = f'You are not renting... \n\nYou have {creds} credits left. Would you like to /topup? '
            if creds < 100:
                status_text+='Please top up soon!'
        status_text+= "\n\nFor more details, send /history"
        status_text+= "\nTo start your journey, send /rent"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=status_text)

    def getpin_command(self,update,context):
        """Gets pin of current renting bike.
        Not available if not renting"""
        if not self.check_user(update,context):
            return -1
        user_data = super().get_user(update,context)
        bike_name = user_data.get('bike_name', None)
        if not bike_name:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting... Start /rent to get the pin for a bike!"
            )
        else:
            bike_data = self.get_bike(bike_name)
            pin = bike_data['pin']
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Your bike pin is {pin}! Please do not share this pin... Can\'t unlock? Please contact one of the admins!'
            )

    def initialize(self):
        """Initializes all user commands"""
        # User related commands
        self.addcmd('start',self.start_command)
        self.addcmd('help', self.help_command)
        self.addcmd('guide', self.guide_command)
        self.addcmd('history', self.history_command)

        # Bike related commands
        self.addcmd('bikes', self.bikes_command)
        self.addcmd('status', self.status_command)
        self.addcmd('getpin', self.getpin_command)
