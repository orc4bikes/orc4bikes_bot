import random
import json
import time
import datetime

import requests
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, parsemode

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

DEDUCT_RATE = 20 # deduct 1 credit every 60 seconds or part thereof

ADMIN_GROUP_ID = -580241456

ROUTES_LIST = ["Orange: From RC4 Level 1 to Fine Foods",
               "Pink: From Fine Foods to Octobox (SRC L1)",
               "Green: From RC4 B1 to Fine Foods",
               "Blue: From RC4 B1 to Fine Foods (Wet Weather route)",
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
/shibe - Get a random shiba!
/neko - Get a random cat!
/kitty - Get a random kitten!
/foxy - Get a random fox!
/birb - Get a random bird!
/pika - A wild pikachu appeared!

/rent - This feature is still under development
/getpin - This feature is still under development
/status - This feature is still under development
/return - This feature is still under development
/bikes - This feature is still under development
/report - This feature is still under development
"""

"""
To be added:
/rent - Rent a bike
/getpin - Get the pin for specific bikes
/return - Return the current bicycle
/bikes - List of currently available bikes
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
    1018419264,# yuya
    42444844,  # nic tan
    197473636, # nic ang
    
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

START_MESSAGE = "Please /start me privately to access this service!"


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
            self.kitty_command(update,context)
            return
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, all the cats are asleep... Please try again later!")
        
    def foxy_command(self,update,context):
        """Shows you a few cute foxes!"""
        try:
            url = requests.get('https://randomfox.ca/floof/').json()['image']
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                #reply_markup=InlineKeyboardMarkup(buttons)
                )
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, all the foxes are asleep... Please try again later!")

    def shibe_command(self,update,context):
        """Shows you a few cute shibe!"""
        try:
            url = requests.get('http://shibe.online/api/shibes').json()[0]
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                #reply_markup=InlineKeyboardMarkup(buttons)
                )
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, all the shibe are asleep... Please try again later!")
    
    def birb_command(self,update,context):
        """Shows you a few cute shibe!"""
        try:
            url = requests.get('https://shibe.online/api/birds').json()[0]
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                #reply_markup=InlineKeyboardMarkup(buttons)
                )
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, all the birbs are asleep... Please try again later!")
    
    def kitty_command(self,update,context):
        """Shows you a few cute shibe!"""
        try:
            url = requests.get('https://shibe.online/api/cats').json()[0]
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

    def random_command(self,update,context):
        """Sends a random animal!"""
        command_list = [
                        self.doggo_command,
                        self.neko_command,
                        self.kitty_command,
                        self.foxy_command,
                        self.birb_command,
                        self.shibe_command]
        random.choice(command_list)(update,context)
    
    def quote_command(self,update,context):
        """Sends an inspirational quote"""
        try:
            url = requests.get('https://type.fit/api/quotes').json()
            print(url)
            url = random.choice(url)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'"{url["text"]}" - {url["author"]}'
            )
        except Exception as e:
            print(e)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=random.choice(CHEER_LIST)
            )

    def pika_command(self,update,context):
        """Sends an inspirational quote"""
        try:
            pikas1 = context.bot.get_sticker_set('pikachu').stickers
            pikas2 = context.bot.get_sticker_set('pikachu2').stickers
            pikas3 = context.bot.get_sticker_set('PikachuDetective').stickers
            pikas4 = context.bot.get_sticker_set('pikachu6').stickers
            pikas5 = context.bot.get_sticker_set('pikach').stickers
            pikas6 = context.bot.get_sticker_set('pikach_memes').stickers
            pikas = pikas1+pikas2+pikas3+pikas4+pikas5+pikas6
            pika = random.choice(pikas)
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=pika
            )
        except Exception as e:
            print(e, 'error at', datetime.datetime.now())

    def brawl_command(self,update,context):
        """Sends an inspirational quote"""
        try:
            brawls = context.bot.get_sticker_set('BrawlStarsbyHerolias')
            brawl = random.choice(brawls.stickers)
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=brawl
            )
        except Exception as e:
            print(e, 'error at', datetime.datetime.now())



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
        self.deduct_rate = DEDUCT_RATE

    def get_bikes(self):
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        return bikes_data

    def update_bikes(self, bikes_data):
        with open('bicycles.json', 'w') as f:
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
            if chat_id>0:
                user_data = {'chat_id': chat_id,
                            'first_name': update.message.from_user.first_name,
                            'last_name' : update.message.from_user.last_name,
                            'username':   update.message.from_user.username,
                            'credits': 0,
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
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
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
        try:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo="https://www.dropbox.com/s/5vmd1yhaslceii0/photo_2021-08-12_23-40-06.jpg",
                text='\n'.join(ROUTES_LIST)
            )
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Server timed out with error {e}... Here are some routes for your consideration\n\
                      " + '\n'.join(ROUTES_LIST)
                )

    def payment_command(self,update,context):
        """Payment using Stripe API
           Currently not ready yet, will work on it soon"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "Payment methods will be available soon!"
            )

    def credits_command(self,update,context):
        """Show your current available credits"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        credits =  user_data["credits"]
        text = f'Your remaining credits is: {credits}.'
        if credits < 10:
            text+=' Please top up soon!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
        )

    def deduct_credits(self,update,context,time_diff):
        user_data = super().get_user(update,context)
        deduction = time_diff.seconds // self.deduct_rate + int(time_diff.seconds%self.deduct_rate > 0)
        user_data['credits'] -= deduction
        super().update_user(user_data)
        return deduction

    def rent_command(self,update,context):
        """Start a rental service"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        if len(context.args) < 1:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please indicate which bike you would like to rent"
            )
            self.bikes_command(update,context)
            return 
        else: 
            bike_name = context.args[0]
        bikes_data = self.get_bikes()
        if bikes_data.get(bike_name,None):
            if bikes_data[bike_name]["status"] == 0:
                user_data = super().get_user(update,context)
                status = user_data.get('status',None)
                if status is not None: #rental in progress
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="You are already renting! Please return your current bike first"
                    )
                    return
                elif user_data.get('credits') < 1: #not enough credits
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, 
                        text=f"You cannot rent, as you do not have enough credits! Current credits: {user_data.get('credits')}"
                    )
                    return
                else: 
                    curr_time = datetime.datetime.now().isoformat()
                    user_data['status'] = curr_time
                    user_data['bike_name'] = bike_name
                    super().update_user(user_data)

                    bikes_data[bike_name]['status'] = curr_time
                    self.update_bikes(bikes_data)
                        
                    # Notify user
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, 
                        text=f"Rental started! Time of rental, {datetime.datetime.now()}")

                    # Notify Admin group
                    context.bot.send_message(
                        chat_id=ADMIN_GROUP_ID,
                        text=f'@{user_data["username"]} rented {bike_name} at {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
                    )
                    return
            else: #bike is not available
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Sorry, {bike_name} is not available. Please indicate which bike you would like to rent.')
                self.bikes_command(update,context)
                return
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'No such bike {bike_name} found. Please indicate which bike you would like to rent.')
            self.bikes_command(update,context)
            return
            

    def status_command(self,update,context):
        """Check the user rental status"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        try:
            status = user_data.get('status',None)
            if status is not None:
                status = datetime.datetime.fromisoformat(status)
                curr = datetime.datetime.now()
                diff = curr - status
                if diff.days:
                    strdiff = f"{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds"
                else:
                    strdiff = f'{diff.seconds//3600} hours, {(diff.seconds%3600)//60} minutes, and {diff.seconds%3600%60} seconds'
                status_text = f'You have been renting {user_data["bike_name"]} for {strdiff}.'
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
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
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
            
            #update bike first, because bike uses user_data.bike_name
            bike_name = user_data['bike_name']  
            bikes_data = self.get_bikes()
            bikes_data[bike_name]['status'] = 0
            self.update_bikes(bikes_data)

            user_data["status"] = None
            user_data["log"] = log
            user_data['bike_name'] = ''
            super().update_user(user_data)

            deduction = self.deduct_credits(update,context,diff)

            
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Successfully returned! Your total rental time is {strdiff}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{deduction} was deducted from your credits. Your remaining credit is {user_data['credits']-deduction}"
            )
            # Notify Admin group
            context.bot.send_message(
                chat_id=ADMIN_GROUP_ID,
                text=f'@{user_data["username"]} returned {bike_name} at {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting..."
            )

    def getpin_command(self,update,context):
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        pass
        
    def bikes_command(self,update,context):
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        avail, not_avail = list(), list()
        for bike in bikes_data.values():
            if bike.get('status') == 0:
                avail.append(bike)
            else:
                not_avail.append(bike)

        avail = "\n".join( b["name"] for b in avail )
        not_avail = "\n".join(b["name"] for b in not_avail )
        text = f'Currently available:\n{avail}\n\n'
        text+= f'On loan:\n{not_avail}'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)  

    def report_command(self,update,context):
        pass


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
            text='Unrecognized command. Try again. For more info, enter /admin')
    
    def admin_command(self,update,context):
        """Start a rental service
        var commands is a list of strings that the user sends
        e.g. /admin addcredit username amount
        commands => ['addcredit','username','amount']"""
        commands = context.args
        if update.effective_chat.id in self.admin_list:
            # update.message.reply_text(str(commands))
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

    def dummy_command(self,update,context):
        update.message.reply_text('This feature will be added soon! Where art thou, bikes...?')

    def initialize(self):
        """Initializes all commands that are required in the bot."""

        self.addnew('start',self.start_command)
        self.addnew('myinfo',self.info_command)
        self.addnew('help', self.help_command)
        self.addnew('routes', self.routes_command)
        self.addnew('doggo', self.doggo_command)
        self.addnew('neko', self.neko_command)
        self.addnew('kitty', self.kitty_command)
        self.addnew('birb', self.birb_command)
        self.addnew('shibe', self.shibe_command)
        self.addnew('foxy', self.foxy_command)  
        self.addnew('random', self.random_command)  
        #self.addnew('quote', self.quote_command)   #doesnt work on web...
        self.addnew('pika', self.pika_command)
        self.addnew('payment', self.payment_command)
        self.addnew('credits', self.credits_command)
        self.addnew('rent', self.rent_command) #self.rent_command)
        self.addnew('status', self.status_command) #self.status_command)
        self.addnew('return', self.return_command) #self.return_command)
        self.addnew('getpin', self.dummy_command) #self.getpin_command)
        self.addnew('bikes', self.bikes_command) #self.bikes_command)
        self.addnew('report', self.dummy_command) #self.report_command)

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
    

