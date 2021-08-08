import random
import json
import time
import datetime

import requests
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, parsemode

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
/credits - View your current credits

/doggo - Get a random dog!
/neko - Get a random cat!

/rent - This features is still under development
/getpin - This features is still under development
/return - This features is still under development
/availability - This features is still under development
/report - This features is still under development
"""

"""
To be added:
/rent - Rent a bike
/getpin - Get the pin for specific bikes
/return - Return the current bicycle
/availability - List of currently available bikes
/report - Report damages of our bikes
/routes - To add more new routes!
"""

ADMIN_LIST = [
    #devs
    260281460, # yew chong

    #current comm
    253089925, # jin ming
    482226461, # bo yi
    451582425, # gordon
    292257566, # jolene
    
    #old comm
    185995813, # fangxin
    50545125,  # kai en
    248853832, # brendan
    446305048, # jovi
]
ADMIN_TEXT = """List of admin commands:
Please do NOT add @ before a username. Usernames are case sensitive.
/admin `viewcredit username` - View the user's credits
/admin `setcredit username amount` - Set the user's credit to an integer amount.
/admin `topup username amount` - Top up the user's credit by an integer amount.
/admin `deduct username amount` - Deduct the user's credit by an integer amount.
"""


class TeleBot:
    def __init__(self,api_key):
        self.api_key = api_key
        self.updater = Updater(token=api_key, use_context=True)
        self.dispatcher = self.updater.dispatcher

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

    def update_user(self, user_data):
        chat_id = user_data.get('chat_id', None)
        if not chat_id:
            return None
        with open(f'users/{chat_id}.json', 'w') as f:
            json.dump(user_data, f, sort_keys=True, indent=4)
    
    def get_user_table(self):
        with open('users/table.json', 'r') as f:
            table_data = json.load(f)
        return table_data
    
    def update_user_table(self, update_field):
        with open('users/table.json', 'w') as f:
            json.dump(update_field, f, sort_keys=True, indent=4)

    def addnew(self, command, methodname):
        handler = CommandHandler(command,methodname)
        self.dispatcher.add_handler(handler)

    def addmessage(self, filters, methodname):
        handler = MessageHandler(filters, methodname)
        self.dispatcher.add_handler(handler)

    def main(self):
        print('Initializing bot...')
        self.updater.start_polling()
        self.updater.idle()



class OrcaBot(TeleBot):
    def __init__(self,
            api_key, 
            help_text=HELP_TEXT, 
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT):
        super().__init__(api_key)
        self.help_text = help_text
        self.admin_list = admin_list
        self.admin_text = admin_text

    def get_bikes(self):
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        return bikes_data

    def update_bikes(self, bikes_data):
        with open(f'bicycles.json', 'w') as f:
            json.dump(bikes_data, f, sort_keys=True, indent=4)

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

        if update.effective_chat.id > 0:
            table_data = super().get_user_table()
            table_data[update.message.from_user.username] = update.effective_chat.id
            super().update_user_table(table_data)
        
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
            text = self.help_text,
            parse_mode=ParseMode.MARKDOWN)
    
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


    def rent_command(self,update,context):
        """Start a rental service"""
        user_data = super().get_user(update,context)
        status = user_data.get('status',None)
        if status is not None: #rental in progress
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already renting! Please return your current bike first"
            )
        else: 
            user_data['status'] = datetime.datetime.now().isoformat()
            super().update_user(user_data)
            context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"Rental started! Time of rental, {datetime.datetime.now()}")

    def status_command(self,update,context):
        """Check the user rental status"""
        try:
            user_data = super().get_user(update,context)
            status = user_data.get('status',None)
            if status is not None:
                status = datetime.datetime.fromisoformat(status)
                curr = datetime.datetime.now()
                diff = curr - status
                if diff.days:
                    strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
                else:
                    strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
                status_text = f'You have been renting for {strdiff}'
            else: 
                status_text = "You are not renting..."
            context.bot.send_message(chat_id=update.effective_chat.id,
                text=status_text)
        except AssertionError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Error, {e}'
            )
    
    def return_command(self,update,context):
        """Return the current bike"""
        user_data = super().get_user(update,context)
        status = user_data.get('status', None)
        if status is not None: #rental in progress
            diff = datetime.datetime.now() - datetime.datetime.fromisoformat(status)
            if diff.days:
                strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
            else:
                strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
            d = {
                'start': status,
                'end': datetime.datetime.now().isoformat(),
                'time': strdiff,
            }
            log = user_data.get('log',[])
            log.append(d)
            user_data["status"] = None
            user_data["log"] = log
            super().update_user(user_data)
            
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Successfully returned! Your total rental time is {strdiff}"
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting..."
            )

        



    def handle_admin(self, update, context, keywords):
        """Handle the admin commands after /admin"""
        
        try:
            command = keywords.pop(0)
            username = keywords.pop(0)
            # handle usernames
            all_users = self.get_user_table()
            chat_id = all_users.get(username, None)
            with open(f'users/{chat_id}.json', 'r') as f:
                user_data = json.load(f)

            if command == "topup":
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] += int(amount) #ValueError Here
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "deduct":
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] -= int(amount) #ValueError Here
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "setcredit":
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] = int(amount)
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "viewcredit":
                if chat_id is not None:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'User @{user_data["username"]} has : {user_data["credits"]} credits left.')
                else: 
                    self.admin_failed(update,context)
            else:
                self.admin_failed(update,context)

        except IndexError as e: 
            self.admin_failed(update,context)
        except FileNotFoundError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Specified user is not found! Please ask @{username} to create an account first.')
        except ValueError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Amount entered, {amount}, is not a valid amount!')
        except KeyError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Could not find key {e} in dictionary! Please check database again')

        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Failed, error is {e}')

    def admin_failed(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Unrecognized command. Try again. For more info, enter /admin')
    
    def admin_command(self,update,context):
        """Start a rental service
        var commands is a list of strings that the user sends
        e.g. /admin addcredit username amount
        commands => ['addcredit','username','amount']"""
        commands = context.args
        if update.effective_chat.id in self.admin_list:
            update.message.reply_text(str(commands))
            if commands:
                self.handle_admin(update,context,commands)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=self.admin_text,
                    parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text('You are not authorized admin commands!')



    def echo_command(self,update,context):
        update.message.reply_text(update.message.text)

    def initialize(self):
        """Initializes all commands that are required in the bot."""

        self.addnew('start',self.start_command)
        self.addnew('myinfo',self.info_command)
        self.addnew('help', self.help_command)
        self.addnew('routes', self.routes_command)
        self.addnew('doggo', self.doggo_command)
        self.addnew('neko', self.neko_command)
        self.addnew('payment', self.payment_command)
        self.addnew('credits', self.credits_command)
        self.addnew('rent', self.rent_command)
        self.addnew('status', self.status_command)
        self.addnew('return', self.return_command)



        #admin handler
        self.addnew('admin', self.admin_command)

        # This part is a message command
        # self.addmessage(Filters.text & (~Filters.command), self.echo_command)

    def main(self):
        """Main bot function to run"""
        self.initialize()
        super().main()

        




if __name__=="__main__": 
    # DEV part, do not run this
    print('Running the development bot!')
    API_KEY = '1722354435:AAHAFxP6_sIf_P4hdQJ7Y5EsH64PtyWwWo8' #this is old api for orcabikes_bot
    # API_KEY = '1705378721:AAEbSmhxNhAY4s5eqWMSmxdCxkf44O7_nss' #new key for orc4bikes_bot
    newbot = OrcaBot(API_KEY)
    newbot.main()
    

