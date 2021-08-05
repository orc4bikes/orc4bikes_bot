import random
import json

import requests
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

ROUTES_LIST = ["From RC4 B1 to Utown",
               "From RC4 Level 1 to Utown",
               "From RC4 to Clementi",
               "From RC4 to Utown (Sheltered)",
               "From RC4 to RC4",
               ]
CHEER_LIST = ["","Cheer up!",
              "Ganbatte!",
              "Hwaiting!",
              "Jiayou!",
              "You got this!",
              ]
HELP_TEXT = """List of commands:
/start - Initializes the bot
/help - Get all available commands
/routes - Get orc4bikes routes
/doggo - Get a random dog!
/neko - Get a random cat!

To be added:
/credits - See my credits
/rent - Rent a bike
/getpin - Get the pin for specific bikes
/return - Return the current bicycle
/availability - List of currently available bikes
/report - Report damages of our bikes
/routes - To add more new routes!
"""


class TeleBot:
    def __init__(self,api_key):
        self.api_key = api_key
        self.updater = Updater(token=api_key, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def update_user(self, user_data):
        chat_id = user_data.get('chat_id', None)
        if not chat_id:
            return None
        with open(f'users/{chat_id}.json', 'w') as f:
            json.dump(user_data, f)

    def get_user(self, update, context):
        chat_id = update.effective_chat.id
        try:
            with open(f'users/{chat_id}.json', 'r') as f:
                user_data = json.load(f)
            #print('user exists')
        except FileNotFoundError:
            user_data = None
            #print('no data found')
        return user_data

    def addnew(self, command, methodname):
        handler = CommandHandler(command,methodname)
        self.dispatcher.add_handler(handler)

    def main(self):
        print('Initializing bot...')
        self.updater.start_polling()
        self.updater.idle()

class OrcaBot(TeleBot):
    def __init__(self,api_key):
        super().__init__(api_key)
        self.help_text = HELP_TEXT

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
            user_data = {'chat_id': chat_id,
                         'first_name': update.message.from_user.first_name,
                         'last_name' : update.message.from_user.last_name,
                         'username':   update.message.from_user.username,
                         'credits': 0,
                        }
            super().update_user(user_data)
                
            text =  f'Hello, {update.message.from_user.first_name}! '
        text+='This is your orc4bikes friendly neighbourhood bot :)'
        text += "\nFor more info, send /help"
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)
        
    def info_command(self, update, context):
        """This is for debugging purposes"""
        user_data = super().get_user(update, context)
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text=str(user_data)
            )
    
    def help_command(self,update,context):
        """Show a list of possible commands"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = self.help_text)
    
    def routes_command(self,update,context):
        """Returns all routes from the list of routes"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "Here are some available routes for you!"
            )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='\n'.join(ROUTES_LIST)
            )



    #fun stuff
    def doggo_command(self,update,context):
        """Shows you a few cute dogs!"""
        try:
            url = requests.get('https://random.dog/woof.json').json()['url']
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                #reply_markup=InlineKeyboardMarkup(buttons)
                )
        except:
            context.bot.send_message(
                chat_id = update.effective_chat.id,
                text="Sorry, all the dogs are out playing... Please try again later!")
    
    def neko_command(self,update,context):
        """Shows you a few cute cats!"""
        try:
            url = requests.get('https://aws.random.cat/meow').json()['file']
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                #reply_markup=InlineKeyboardMarkup(buttons)
                )
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, all the cats are asleep... Please try again later!")
    
    def payment_command(self,update,context):
        """Payment using Stripe API
           Currently not ready yet, will work on it soon"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "Payment methods will be available soon!"
            )

    def credits_command(self,update,context):
        """Show your current available credits"""
        user_data = super().get_user(update,context)
        credits =  user_data["credits"]
        text = f'Your remaining credits is: {credits}.'
        if credits < 10:
            text+=' Please top up soon!'


        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
        )
        
    def main(self):
        self.addnew('start',self.start_command)
        self.addnew('myinfo',self.info_command)
        self.addnew('help', self.help_command)
        self.addnew('routes', self.routes_command)
        self.addnew('doggo', self.doggo_command)
        self.addnew('neko', self.neko_command)
        self.addnew('payment', self.payment_command)
        self.addnew('credits', self.credits_command)

        super().main()

        
if __name__=="__main__":
    print('Run the main python file!')
