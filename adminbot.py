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

    def handle_admin(self, update, context, keywords, command=''):
        """Handle the admin commands after /admin"""
        try:
            if not command:
                command=keywords.pop(0)

            if command in ['setpin','setstatus']: #bike commands
                bike_name  = keywords.pop(0) # set the bike_name as name
                bikes_data = self.get_bikes()
                bike = bikes_data.get(bike_name, None)
                if bike is None:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'No such bike, {bike}, exists. Please try again with current /bikes'
                    )
                    return

            elif command in ['topup','deduct','setcredit','user']: # user commands
                username = keywords.pop(0) #set the username as name
                all_users = self.get_user_table()
                chat_id = all_users.get(username, None)
                if chat_id is not None:
                    with open(f'users/{chat_id}.json', 'r') as f:
                        user_data = json.load(f)
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'Specified user is not found! Please ask @{username} to create an account first.')
                    return
            else: # stats and logs commands
                pass

            if command == "topup":
                """Topup specific amount to user credits"""
                number = keywords.pop(0)
                user_data['credits'] = user_data.get('credits', 0)
                initial_amt = user_data.get('credits', 0)
                user_data['credits'] += int(number)
                final_amt = user_data.get('credits')

                #update user data
                user_data['finance'] = user_data.get('finance',[])
                f_log = {
                    'type':'admin',
                    'time':self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': int(number),
                    'final': final_amt
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    initial_amt, int(number), final_amt
                ]
                self.update_finance_log(finance_log)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Top-up successful! @{username} now has {user_data["credits"]} credits.'
                )

            elif command == "deduct":
                """Deduct specific amount from user credits"""
                number = keywords.pop(0)
                user_data['credits'] = user_data.get('credits', 0)
                initial_amt = user_data.get('credits', 0)
                user_data['credits'] -= int(number)
                final_amt = user_data.get('credits')

                #update user data
                user_data['finance'] = user_data.get('finance',[])
                f_log = {
                    'type':'admin',
                    'time':self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': -int(number),
                    'final': final_amt
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    initial_amt, -int(number), final_amt
                ]
                self.update_finance_log(finance_log)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Deducted successfully! @{username} now has {user_data["credits"]} credits.'
                )

            elif command == "setcredit":
                """Set user credits to specified amount."""
                number = keywords.pop(0)
                user_data['credits'] = user_data.get('credits', 0)
                initial_amt = user_data.get('credits', 0)
                change_amt = int(number) - initial_amt
                user_data['credits'] = int(number)

                #update user data
                user_data['finance'] = user_data.get('finance',[])
                f_log = {
                    'type':'admin',
                    'time':self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': change_amt,
                    'final': int(number)
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    initial_amt, change_amt, int(number)
                ]
                self.update_finance_log(finance_log)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Setting was successful! @{username} now has {user_data["credits"]} credits.'
                )

            elif command == "user":
                text=f'@{user_data["username"]} has {user_data.get("credits",0)} credits left.\n'
                text+=f'User has been renting {user_data["bike_name"]} since {user_data["status"]}' if user_data.get("bike_name") else "User is not renting currently."
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)

            elif command == "setpin":
                number = keywords.pop(0)
                if bike['pin']!=number:
                    bikes_data[bike_name]['oldpin'] = bike['pin']
                    bikes_data[bike_name]['pin'] = number
                    self.update_bikes(bikes_data)
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Pin for {bike_name} updated to {number}!"
                    )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'Old pin is the same as {number}!'
                    )
            elif command == "setstatus":
                if not keywords:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Please send a status update!"
                    )
                    return
                status = ' '.join(keywords)
                rented = bike.get('username',"")
                if rented == "":
                    if status.isnumeric(): #to reset the status to 0
                        status=int(status)
                    bikes_data[bike_name]['status'] = status
                    self.update_bikes(bikes_data)
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Status for {bike_name} updated to {status}!"
                    )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'Bike is rented by {rented}!'
                    )


            elif "bike" in command:
                bikes_data = self.get_bikes()
                text= '\n'.join(f'Bike {bike["name"]}  --  {bike["username"] or bike["status"] or EMOJI["tick"]}' for bike in bikes_data.values())
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)

            elif command == "logs":
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('logs/rental.csv','rb'),
                    filename="rental.csv",
                    caption="Rental logs"
                )
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('logs/report.csv','rb'),
                    filename="report.csv",
                    caption="Report logs"
                )
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('logs/finance.csv','rb'),
                    filename="finance.csv",
                    caption="Finance logs"
                )


            else: # unrecognized command...
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Unrecognized command. Try again. For more info, enter /admin')


        except IndexError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Sorry, too little info provided.\nPlease send more info after /{command}"
                )
        except ValueError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Number entered, {number}, is not valid!')
        except KeyError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Could not find key {e} in dictionary! Please check database again')
        except FileNotFoundError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Hmm, file not found... Please raise a ticket with @fluffballz, along with what you sent.')
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Failed, error is {e}\nPlease raise a ticket with @fluffballz, along with what you sent')

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
            print(e)

    def topup_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'topup')
        except AssertionError:
            pass

    def deduct_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'deduct')
        except AssertionError:
            pass

    def setcredit_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'setcredit')
        except AssertionError:
            pass

    def user_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'user')
        except AssertionError:
            pass

    def setpin_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'setpin')
        except AssertionError:
            pass

    def setstatus_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'setstatus')
        except AssertionError:
            pass

    def logs_command(self,update,context):
        try:
            assert(self.admin_check(update,context))
            keywords = context.args
            self.handle_admin(update,context,keywords,'logs')
        except AssertionError:
            pass

    def initialize(self):
        self.addcmd('admin',self.admin_command)
        self.addcmd('topup',self.topup_command)
        self.addcmd('deduct',self.deduct_command)
        self.addcmd('setcredit',self.setcredit_command)
        self.addcmd('user',self.user_command)
        self.addcmd('setpin',self.setpin_command)
        self.addcmd('setstatus',self.setstatus_command)
        self.addcmd('logs',self.logs_command)

    def main(self):
        self.initialize()
        super().main()