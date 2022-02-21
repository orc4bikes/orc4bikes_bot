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
import json
import csv
import datetime
from decimal import Decimal

import requests
import re

import os

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

from zipfile import ZipFile
from pathlib import Path

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

    def zip_command(self,update,context):
        """Zips all files and send to user"""
        with ZipFile('all.zip', 'w') as zipf:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Zipping your files..."
            )
            zipf.write('logs/rental.csv')
            zipf.write('logs/finance.csv')
            zipf.write('logs/report.csv')
            zipf.write('users/table.json')

        # with ZipFile('all.zip', 'r') as zipf:
        context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=Path('all.zip'),
            filename="all.zip",
            caption="All files are zipped here"
        )

    def admin_command(self,update,context,keywords,command=''):
        """Admin command handler, actual one in Orc4bikesBot"""
        print("Run Orc4bikesBot for admin commands!!")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Run Orc4bikesBot for admin commands!!"
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
        if self.admin_check(update,context):
            return
        def reply(item):
            item=str(item)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=item
        )
        def accounts(username=""):
            from os import listdir
            from os.path import isfile, join
            files = [f for f in listdir('database/users/') if isfile(join('users/', f))]
            files = [json.load(open(f'database/users/{file}')) for file in files]
            if username != "":
                files = [file for file in files if file.get("username") == username][0]
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
                text=f"Sorry, this command is not valid. Error is {e}"
            )
            print(e)

    def handle_admin(self, update, context, keywords, command=''):
        """Handle the admin commands after /admin"""
        try:
            if not command:
                command=keywords.pop(0)

            if command in ['setpin','setstatus','forcereturn']: #bike commands
                bike_name  = keywords.pop(0) # set the bike_name as name
                bike = self.get_bike(bike_name)
                if bike is None:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'No such bike, {bike}, exists. Please try again with current /bikes'
                    )
                    return

            elif command in ['topup','deduct','setcredit','user','ban','unban']: # user commands
                username = keywords.pop(0) #set the username as name
                user_data = self.get_user(username=username)
                if user_data is None:
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
                    'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': int(number),
                    'final': final_amt
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    initial_amt, int(number), final_amt,
                    update.message.from_user.username
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
                user_data['credits'] -= Decimal(int(number))
                final_amt = user_data.get('credits')

                #update user data
                user_data['finance'] = user_data.get('finance',[])
                f_log = {
                    'type':'admin',
                    'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': -int(number),
                    'final': final_amt
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    initial_amt, -int(number), final_amt,
                    update.message.from_user.username
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
                    'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'initial':initial_amt,
                    'change': change_amt,
                    'final': int(number)
                }
                user_data['finance'].append(f_log)
                self.update_user(user_data)

                finance_log=[
                    username,
                    self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    initial_amt, change_amt, int(number),
                    update.message.from_user.username
                ]
                self.update_finance_log(finance_log)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Setting was successful! @{username} now has {user_data["credits"]} credits.'
                )

            elif command == "user":
                text=f'@{user_data["username"]} has {user_data.get("credits",0)} credits left.\n'
                text+=f'User has been renting {user_data["bike_name"]} since {datetime.datetime.fromisoformat(user_data["status"]).strftime("%Y/%m/%d, %H:%M:%S")}' if user_data.get("bike_name") else "User is not renting currently."
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)

            elif command == "ban":
                """Ban a user"""
                is_ban = user_data.get('is_ban')
                if not is_ban:
                    user_data['is_ban'] = True
                    self.update_user(user_data)
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'@{username} is now BANNED.'
                    )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'@{username} was already banned.'
                    )

            elif command == "unban":
                """Unban a user"""
                is_ban = user_data.get('is_ban')
                if is_ban:
                    user_data['is_ban'] = None
                    self.update_user(user_data)
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'@{username} is now UNBANNED.'
                    )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'@{username} was not banned'
                    )

            elif command == "forcereturn":
                username = bike.get('username',"")
                if not username:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Bike not on rent! Please try again"
                    )
                    return
                    
                user_data = self.get_user(username=username)
                status = user_data.get('status')
                if not status:
                    return context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Something seems wrong... The bike {bike_name} tagged to user @{username}, but user is not renting???"
                    )
                diff = self.now() - datetime.datetime.fromisoformat(status)
                if diff.days:
                    strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
                else:
                    strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
                d = {
                    'start': status,
                    'end': self.now().isoformat(),
                    'time': strdiff,
                }
                deduction = self.calc_deduct(diff)

                #update return logs
                bike = self.get_bike(bike_name)
                start_time = datetime.datetime.fromisoformat(bike['status']).strftime('%Y/%m/%d, %H:%M:%S')
                end_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
                self.update_rental_log([bike_name,username,start_time,end_time,deduction])

                #update bike first, because bike uses user_data.bike_name
                bike['status'] = 0
                bike['username'] = ""
                self.update_bike(bike)

                #update user data
                log = user_data.get('log',[])
                log.append(d)
                user_data["status"] = None
                user_data["log"] = log
                user_data['bike_name'] = ''
                user_data['credits'] -= deduction
                user_data['finance'] = user_data.get('finance',[])
                f_log = {
                    'type':'rental',
                    'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'credits':user_data.get('credits'),
                    'spent': deduction,
                    'remaining': user_data.get('credits') - deduction
                }
                user_data['finance'].append(f_log)
                super().update_user(user_data)

                admin_username = update.message.from_user.username
                context.bot.send_message(
                    chat_id=int(user_data.get('chat_id')),
                    text=f"An admin, @{admin_username} has returned your bike for you! Your total rental time is {strdiff}."
                )
                deduction_text = f"{deduction} credits was deducted. Remaining credits: {user_data['credits']}"
                user_text = deduction_text + '\nIf you have any queries, please ask a comm member for help.'
                context.bot.send_message(
                    chat_id=int(user_data.get('chat_id')),
                    text=user_text
                )
                # Notify Admin group
                admin_text=f'[RENTAL - RETURN] \n@{update.message.from_user.username} returned {bike_name} at following time:\n{self.now().strftime("%Y/%m/%d, %H:%M:%S")}'
                admin_text+=f'\nThis return was force-returned by @{admin_username}.'
                admin_text+='\n'+deduction_text
                self.admin_log(update,context, admin_text)
                

            elif command == "setpin":
                number = keywords.pop(0)
                if bike['pin']!=number:
                    bike['oldpin'] = bike['pin']
                    bike['pin'] = number
                    self.update_bike(bike)
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
                    status = 0
                status = ' '.join(keywords)
                rented = bike.get('username',"")
                if rented == "":
                    if status == '0': #to reset the status to 0
                        status=int(status)
                    bike['status'] = status
                    self.update_bike(bike)
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
                text= '\n'.join(f'{bike["name"]}  --  {bike["username"] or bike["status"] or EMOJI["tick"]} (Pin: {bike["pin"]})' for bike in bikes_data)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)

            elif command == "logs":
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('database/logs/rental.csv','rb'),
                    filename="rental.csv",
                    caption="Rental logs"
                )
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('database/logs/report.csv','rb'),
                    filename="report.csv",
                    caption="Report logs"
                )
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=open('database/logs/finance.csv','rb'),
                    filename="finance.csv",
                    caption="Finance logs"
                )


            else: # unrecognized command...
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Unrecognized command. Try again. For more info, enter /admin')


        except IndexError as e:
            self.log_exception(e,"Error with handle_admin")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Sorry, too little info provided.\nPlease send more info after /{command}"
                )
        except ValueError as e:
            self.log_exception(e,"Error with handle_admin")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Number entered, {number}, is not valid!')
        except KeyError as e:
            self.log_exception(e,"Error with handle_admin")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Could not find key {e} in dictionary! Please check database again')
        except FileNotFoundError as e:
            self.log_exception(e,"Error with handle_admin")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Hmm, file not found... Please raise a ticket with @fluffballz, along with what you sent.')
        except Exception as e:
            self.log_exception(e,"Error with handle_admin")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Failed, error is {e}\nPlease raise a ticket with @fluffballz, along with what you sent')

    def initialize(self):
        """Initialze all admin commands"""
        self.addcmd('zip',self.zip_command)
        self.addcmd('admin',self.admin_command)
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
        super().main()

if __name__=="__main__":
    print('Running the AdminBot!')
    newbot = AdminBot(DEV_API_KEY)
    newbot.main()
