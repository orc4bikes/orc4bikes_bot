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
    EMOJI
)

from telebot import TeleBot

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


class AdminBot(TeleBot):
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

    def admin_command(self,update,context,keywords,command=''):
        """Admin command handler, actual one in OrcaBot"""
        print("Run OrcaBot for admin commands!!")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Run OrcaBot for admin commands!!"
        )

    def admin_log(self, update, context, message, photo=None):
        if photo:
            context.bot.send_photo(
                chat_id=self.admin_group_id,
                photo=photo,
                caption=message
            )
        else:
            context.bot.send_message(
                chat_id=self.admin_group_id,
                text=message
            )

    def admin_check(self,update,context):
        """Checks whether the user is an admin"""
        if update.effective_chat.id in self.admin_list:
            return True
        update.message.reply_text('You\'ve found... something unauthorized? Please contact a orc4bikes commmittee member or an admin for help!')
        return False

    def admin_command(self,update,context):
        try:
            commands = context.args
            if self.admin_check(update,context):
                if commands:
                    self.handle_admin(update,context,commands)
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=self.admin_text,
                        parse_mode="MarkdownV2")
        except Exception as e:
            self.log_exception(e,"Error with admin_command")

    def topup_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='topup')
        except AssertionError:
            pass

    def deduct_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='deduct')
        except AssertionError:
            pass

    def setcredit_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='setcredit')
        except AssertionError:
            pass

    def user_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='user')
        except AssertionError:
            pass

    def setpin_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='setpin')
        except AssertionError:
            pass

    def setstatus_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='setstatus')
        except AssertionError:
            pass

    def logs_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='logs')
        except AssertionError:
            pass

    def forcereturn_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='forcereturn')
        except AssertionError:
            pass

    def ban_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='ban')
        except AssertionError:
            pass

    def unban_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,command='unban')
        except AssertionError:
            pass

    def py_command(self,update,context):
        def reply(item):
            item=str(item)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=item
        )
        def accounts():
            from os import listdir
            from os.path import isfile, join
            files = [f for f in listdir('users/') if isfile(join('users/', f))]
            files = [json.load(open(f'users/{file}')) for file in files]
            return files
        
        code = update.message.text[4:].strip()
        try:
            if code == '':
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='You can run python with this command.\
                        \nUse reply(item) to ask bot to send a message with reply as "item".\
                        \nUse accounts() to access all accounts as a list.'
                )
            else:
                exec(code)
        except Exception as e:
            self.log_exception(e,"Error with py_command")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, this command is not valid."
            )
            print(e)

    def initialize(self):
        self.addcmd('admin',self.admin_command)
        self.addcmd('topup',self.topup_command)
        self.addcmd('deduct',self.deduct_command)
        self.addcmd('setcredit',self.setcredit_command)
        self.addcmd('user',self.user_command)
        self.addcmd('setpin',self.setpin_command)
        self.addcmd('setstatus',self.setstatus_command)
        self.addcmd('logs',self.logs_command)
        self.addcmd('forcereturn',self.forcereturn_command)
        self.addcmd('ban',self.ban_command)
        self.addcmd('unban',self.unban_command)
        self.addcmd('py',self.py_command)

    def main(self):
        self.initialize()
        super().main()