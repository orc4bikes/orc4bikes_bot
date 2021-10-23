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
    TERMS_TEXT,
    START_MESSAGE,
    EMOJI,
    GUIDE_PIC,
)

from telebot import TeleBot
from funbot import FunBot
from adminbot import AdminBot
from convobot import ConvoBot

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


class OrcaBot(ConvoBot, AdminBot, FunBot, TeleBot):
    DEDUCT_RATE = 20 # deduct 1 credit every 20 seconds or part thereof

    def __init__(self,
            api_key,
            admin_group_id=DEV_ADMIN_GROUP_ID,
            help_text=HELP_TEXT,
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT,
            deduct_rate=DEDUCT_RATE,
            terms_text=TERMS_TEXT,
            promo = False,
            ):
        print('running OrcaBot', super().now())
        super().__init__(api_key)
        self.help_text = help_text
        self.admin_group_id = admin_group_id
        self.admin_list = admin_list
        self.admin_text = admin_text
        self.deduct_rate = deduct_rate
        self.terms_text = terms_text
        self.promo = promo

    def calc_deduct(self,time_diff):
        """Calculate credits deductable given a time period"""
        deduction = time_diff.seconds // self.deduct_rate + int(time_diff.seconds%self.deduct_rate > 0)
        deduction += time_diff.days * 86400 / self.deduct_rate
        return deduction

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
                text='''
                You are on Santa's naughty list... What have you done?!
                If you believe this is a mistake, contact @meltingice7 or @Fusion_mix25'''
                )
            return False
        return True

    def start_command(self,update,context):
        """Initializes the bot
            This is where we initialize a new user
            If the user is not created, a new json is created
            with json name as chatid.json"""
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
            table_data = super().get_user_table()
            username=update.message.from_user.username
            if username:
                table_data[username] = update.effective_chat.id
            super().update_user_table(table_data)

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
            self.log_exception(e,"Error with guide_command")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, /guide currently not available... please try again!",
            )

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
            bike_data = self.get_bikes()
            pin = bike_data[bike_name]['pin']
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Your bike pin is {pin}! Please do not share this pin... Cant unlock? Pls /report or contact @awwwsome_by or @Meltingice7'
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
                elif line['type']=='rental':
                    text+=f'--: You rented a bike on {line["time"]}, and spent {line["spent"]} credits.\n'
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
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        avail, not_avail = list(), list()
        for bike in bikes_data.values():
            if bike.get('status') == 0:
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
        try:
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
                status_text = f'You are not renting... \n\nYou have {creds} credits left. Would you like to /topup?'
                if creds < 100:
                    status_text+='Please top up soon!'
            status_text+= "\n\nFor more details, send /history"
            status_text+= "\nTo start your journey, send /rent"
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=status_text)
        except Exception as e:
            self.log_exception(e,"Error with status_command")

    def echo_command(self,update,context):
        update.message.reply_text(update.message.text)

    def convo_outside_command(self,update,context):
        """Used outside of ConversationHandler"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="This command was a little out of place..."
        )
        context.user_data.clear()
        return -1

    def dummy_command(self,update,context):
        update.message.reply_text('This feature will be added soon! Where art thou, bikes...?')

    def unrecognized_command(self,update,context):
        """Let the user know this command is unrecognized"""
        update.message.reply_text('Unrecognized command. Send /help for available commands.')

    def unrecognized_buttons(self,update,context):
        """Edit the query so the user knows button is not accepted."""
        try:
            query = update.callback_query
            query.answer()
            text = query.message.text
            text+= '\n\nSorry, this button has expired. Please send the previous command again'
            query.edit_message_text(text)
        except Exception as e:
            self.log_exception(e,"Error with unrecognized_buttons")

    def reminder(self,context):
        """Reminder for return, every hour"""
        bikes_data = self.get_bikes()
        for bike_name, bike_data in bikes_data.items():
            username = bike_data.get('username')
            if username:
                chat_id = self.get_user_table().get(username)
                user_data = self.get_user(username=username)
                status = user_data.get('status')
                start = datetime.datetime.fromisoformat(status)
                curr = self.now()
                diff = curr - start
                if diff.days:
                    strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
                else:
                    strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
                status_text = f'You have been renting {user_data["bike_name"]} for {strdiff}. '
                deduction = self.calc_deduct(diff)
                status_text += f'\n\nCREDITS:\nCurrent:  {user_data.get("credits")} \nThis trip:  {deduction}\nProjected final:  {user_data.get("credits") - deduction}'
                context.bot.send_message(
                    chat_id=chat_id,
                    text=status_text)
                context.bot.send_message(
                    chat_id=chat_id,
                    text="Please remember to /return your bike! Check your bike status with /status"
                )

    def scheduler(self):
        """Scheduler for reminder to be run"""
        j = self.updater.job_queue
        print('getting daily queue')
        for hour in range(24):
            j.run_daily(
                self.reminder,
                days=(0, 1, 2, 3, 4, 5, 6),
                time=datetime.time(hour=hour, minute=0, second=0))
            if hour%12==2:
                j.run_daily( #Update admin group
                    lambda context: context.bot.send_message(
                        chat_id=self.admin_group_id,
                        text=f'Bot is working at {self.now().strftime("%H:%M:%S")}'
                    ),
                    days=(0, 1, 2, 3, 4, 5, 6),
                    time=datetime.time(hour=hour, minute=0, second=2))
            j.run_daily( #Update Jin Ming
                lambda context: context.bot.send_message(
                    chat_id=253089925,
                    text=f'Bot is working at {self.now().strftime("%H:%M:%S")}'
                ),
                days=(0, 1, 2, 3, 4, 5, 6),
                time=datetime.time(hour=hour, minute=0, second=2))

    def initialize(self):
        """Initializes all CommandHandlers, MessageHandlers, and job_queues that are required in the bot."""
        # Super initialize
        TeleBot.initialize(self)
        ConvoBot.initialize(self)
        AdminBot.initialize(self)
        # Fun bot
        FunBot.initialize(self)

        # User related commands
        self.addcmd('start',self.start_command)
        self.addcmd('help', self.help_command)
        self.addcmd('guide', self.guide_command)
        # self.addcmd('routes', self.routes_command)
        self.addcmd('history', self.history_command)

        # Bike related commands
        self.addcmd('bikes', self.bikes_command)
        self.addcmd('status', self.status_command)
        self.addcmd('getpin', self.getpin_command)

        # Check if user sends converation commands outside of ConversationHandler (ConvoBot)
        self.addcmd('cancel', self.convo_outside_command)
        self.addcmd('done', self.convo_outside_command)

        # Lastly, Filters all unknown commands, and remove unrecognized queries
        self.addmsg(Filters.command, self.unrecognized_command)
        self.addnew(CallbackQueryHandler(self.unrecognized_buttons))

        # For scheduling messages
        self.scheduler()

    def main(self):
        """Main bot function to run"""
        TeleBot.main(self)

if __name__=="__main__":
    newbot = OrcaBot(DEV_API_KEY, admin_group_id=DEV_ADMIN_GROUP_ID)
    newbot.main()
