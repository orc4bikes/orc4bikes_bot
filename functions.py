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

DEDUCT_RATE = 20 # deduct 1 credit every 60 seconds or part thereof

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
    
    def get_user_table(self):
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

class FunBot(TeleBot):
    def __init__(self,
        api_key):
        super().__init__(api_key)
            #fun stuff
    def animal_command(
        self, update, context, 
        pic_url='', key=0,
        error_text=None,
        secondary_url='',
        secondary_key=''
        ):
        """Basic command for animals!"""
        try:
            assert(pic_url)
            url = requests.get(pic_url).json()[key]
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                caption = random.choice(CHEER_LIST),
                photo = url,
                )
            
        except AssertionError:
            # empty url given
            animals = update.message.text.split(' ')[0][1:] + 's'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Hmm, I can't seem to find any {animals}... Maybe they're all asleep?"
            )
        except:
            # first url does not work
            try:
                # try secondary url
                assert(secondary_url)
                url = requests.get(secondary_url).json()[secondary_key]
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    caption = random.choice(CHEER_LIST),
                    photo = url,
                    )
            except:
                # both urls do not work
                if error_text is None:
                    animals = update.message.text.split(' ')[0][1:] + 's'
                    error_text = f'Sorry, all the {animals} are out cycling! Please try again when they come home :)'
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_text
                )

    def doggo_command(self,update,context):
        """Shows you a few cute dogs!"""
        url = 'https://random.dog/woof.json'
        key = 'url'
        url2 = 'http://shibe.online/api/shibes'
        key2 = 0
        error_text='Sorry, all the dogs are out playing... Please try again later!'

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            secondary_url=url2, secondary_key=key2)
    
    def neko_command(self,update,context):
        """Shows you a few cute cats!"""
        url = 'https://aws.random.cat/meow'
        key = 'file'
        url2 = 'https://shibe.online/api/cats'
        key2 = 0
        error_text='Sorry, all the cats are asleep... Please try again later!'

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            secondary_url=url2, secondary_key=key2)
       
    def foxy_command(self,update,context):
        """Shows you a few cute foxes!"""
        url = 'https://randomfox.ca/floof/'
        key = 'image'
        error_text="Sorry, all the foxes are asleep... Please try again later!"

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            )

    def shibe_command(self,update,context):
        """Shows you a few cute shibe!"""
        url = 'http://shibe.online/api/shibes'
        key = 0
        error_text="Sorry, doge is doge... Please try again later!"

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            )
    
    def birb_command(self,update,context):
        """Shows you a few cute birbs!"""
        url = 'http://shibe.online/api/birds'
        key = 0
        error_text="Sorry, the birbs flew away... Please try again later!"

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            )
    
    def kitty_command(self,update,context):
        """Shows you a few cute kittens!"""
        url = 'http://shibe.online/api/cats'
        key = 0
        error_text="Sorry, all the cats are asleep... Please try again later!"

        self.animal_command(
            update,context,
            pic_url=url, key=key,
            error_text=error_text,
            )

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



class OrcaBot(AdminBot, FunBot, TeleBot):
    def __init__(self,
            api_key, 
            admin_group_id=DEV_ADMIN_GROUP_ID,
            help_text=HELP_TEXT, 
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT,
            deduct_rate=DEDUCT_RATE
            ):
        super().__init__(api_key)
        self.help_text = help_text
        self.admin_group_id = admin_group_id
        self.admin_list = admin_list
        self.admin_text = admin_text
        self.deduct_rate = deduct_rate
        

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
        
    
    def help_command(self,update,context):
        """Show a list of possible commands"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = self.help_text,
            parse_mode=ParseMode.MARKDOWN)
    
    def routes_button(self,update,context):
        query = update.callback_query
        query.answer()
        colour = query.data
        try:
            if colour=='all':
                for colour, url in ROUTES_PICS.items():
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=url,
                        caption=ROUTES_LIST[colour],
                    )
            else:
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=ROUTES_PICS[colour],
                    caption=ROUTES_LIST[colour],
                )
        except Exception as e:
            print('error with routes, error is:\n',e)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Server timed out with error... Here are some routes for your consideration\n"
                       + '\n'.join(ROUTES_LIST.values())
                )
        query.edit_message_text(text=f"Selected option: {query.data}")

    def routes_command(self,update,context):
        """Returns all routes from the list of routes"""
        keyboard = [
            [
                InlineKeyboardButton("Blue", callback_data='blue'),
                InlineKeyboardButton("Pink", callback_data='pink'),
            ],
            [
                InlineKeyboardButton("Green", callback_data='green'),
                InlineKeyboardButton("Orange", callback_data='orange'),
            ],
            [
                InlineKeyboardButton("All", callback_data='all')
            ]
        ]

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "Here are some available routes for ya!",
            reply_markup=InlineKeyboardMarkup(keyboard)
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

    def rent_command(self,update,context,bike_name=None):
        """Start a rental service"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        if context.args is not None and len(context.args) < 1:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please indicate which bike you would like to rent\nE.g. /rent orc1bike\
                    \nAlternatively, you can click on any available bike below to start renting!"
            )
            self.bikes_command(update,context)
            return 
        if context.args:
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

                    bikes_data[bike_name]['username'] = user_data.get('username')
                    bikes_data[bike_name]['status'] = curr_time
                    self.update_bikes(bikes_data)
                        
                    # Notify user
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, 
                        text=f"Rental started! Time of rental, {datetime.datetime.now()}")

                    # Notify Admin group
                    message=f'[RENTAL - RENT] \n@{user_data["username"]} rented {bike_name} at {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
                    self.admin_log(update,context,message)
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
                status_text = f'You have been renting {user_data["bike_name"]} for {strdiff}. '
                deduction = diff.seconds // self.deduct_rate + int(diff.seconds%self.deduct_rate > 0)
                status_text += f'\nYour current credits:  {user_data.get("credits")} \nThis trip will cost:  {deduction}\nProjected credits after rental:  {user_data.get("credits") - deduction}'
            else: 
                status_text = "You are not renting..."
                self.credits_command(update,context)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=status_text)
        except AssertionError as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Error, {e}'
            )
        except Exception as e:
            pass
    
    def return_command(self,update,context):
        """Return the current bike"""
        user_data = super().get_user(update,context)
        if user_data is None:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
            return -1
        status = user_data.get('status', None)
        if status is not None: #rental in progress
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please send a photo for proof of return! \nPicture must be a photo, not a file... \nTo continue rental, send /cancel" 
            )
            return 91
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting..."
            )
            return -1
    
    def return_pic(self,update, context):
        """After photo is sent, save the photo and ask for others"""
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo
            text="^ This is your image. If you are unsatisfied with your image, please send another one. \nTo return the bike, send /done. To continue rental, send /cancel"
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=context.user_data["photo"],
                caption=text
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please send a photo for proof of return! \nTo continue rental, send /cancel"
            )
        return 91
        
    def return_done(self,update,context):
        user_data= super().get_user(update,context)
        status= user_data.get('status',None)
        if context.user_data.get('photo'):
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
            
            #update return logs
            username = user_data.get('username')
            bike_name = user_data['bike_name'] 
            bikes_data = self.get_bikes()
            start_time = bikes_data[bike_name]['status']
            end_time = datetime.datetime.now().isoformat()
            self.update_rental_log([bike_name,username,start_time,end_time,])

            #update bike first, because bike uses user_data.bike_name 
            bikes_data[bike_name]['status'] = 0
            bikes_data[bike_name]['username'] = ""
            self.update_bikes(bikes_data)

            #update user data
            log = user_data.get('log',[])
            log.append(d)
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
            admin_text=f'[RENTAL - RETURN] \n@{update.message.from_user.username} returned {bike_name} at following time:\n{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
            self.admin_log(update,context, admin_text, context.user_data['photo'])
            context.user_data.clear()
            return -1   
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, please send a photo."
            )
            return 91

    def return_cancel(self,update,context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Return is cancelled. Enjoy your ride!"
        )
        context.user_data.clear()
        return -1

    def return_handler(self):
        my_handler=ConversationHandler(
            entry_points=[CommandHandler('return', self.return_command)],
            states={
                91:[
                    MessageHandler(~Filters.command, callback=self.return_pic),
                ]
            },
            fallbacks=[
                CommandHandler('cancel',self.return_cancel),
                CommandHandler('done', self.return_done),
                ]
        )
        return my_handler

    def getpin_command(self,update,context):
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        bike_name = user_data.get('bike_name', None)
        if not bike_name:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting... Start a rental to get the pin for a bike!"
            )
        else:
            bike_data = self.get_bikes()
            pin = bike_data[bike_name]['pin']
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Your bike pin is {pin}! Please do not share this pin...'
            )
        
    def rent_button(self,update,context):
        query = update.callback_query
        query.answer()
        bike_name = query.data
        try:
            if bike_name == 'stoprent':
                query.edit_message_text(text=f"Send /bikes to refresh the available bikes!")
                return
            self.rent_command(update,context,bike_name=bike_name)
            query.edit_message_text(text=f"Renting in progress...")
        except Exception as e:
            print('error with button renting, error is:\n',e)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Server timed out error..."
                )

    def bikes_command(self,update,context):
        with open('bicycles.json', 'r') as f:
            bikes_data = json.load(f)
        avail, not_avail = list(), list()
        for bike in bikes_data.values():
            if bike.get('status') == 0:
                avail.append(bike)
            else:
                not_avail.append(bike)

        avail = "\n".join( b["name"]+' '+EMOJI["tick"] for b in avail )
        not_avail = "\n".join(b["name"]+' '+EMOJI["cross"] for b in not_avail )
        text = f'Bicycles:\n{avail}'
        text+= '\n\n' if avail else ''
        text+= f'{not_avail}'
        text+='\n\nClick below to start renting now!' if avail else '\n\nSorry, all bikes are on rent...'
        avail_bikes = [bike["name"] for bike in bikes_data.values() if bike.get('status') == 0]
        keyboard = list([[InlineKeyboardButton('Rent ' + bike, callback_data=bike)] for bike in avail_bikes])
        keyboard.append([InlineKeyboardButton('Cancel', callback_data='stoprent')])
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)  
        )

    def report_command(self,update,context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please send a short description of the report you would like to make! \nTo stop, send /cancel" 
        )
        return 11

    def report_desc(self, update, context):
        """After description is sent, save the description and ask for pics"""
        desc = update.message.text
        context.user_data['desc'] = desc
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please attach a picture as well! \nPicture must be a photo, not a file...  \nTo stop, send /cancel"
        )
        return 12

    def report_pic(self,update, context):
        """After photo is sent, save the photo and ask for others"""
        photo = update.message.photo[-1].file_id
        context.user_data['photo'] = photo
        text=f'Your report is: \n{context.user_data["desc"]}\n\n' 
        text+="To update your report or image, feel free to send another one. \nTo submit, send /done. To stop, send /cancel"
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=context.user_data["photo"],
            caption=text
        )
        return 13

    def report_anything(self, update, context):
        if update.message.text:
            desc = update.message.text
            context.user_data['desc'] = desc
        elif update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo

        text=f'Your report is: \n{context.user_data["desc"]}\n\n' 
        text+="To update your report or image, feel free to send another one. \nTo submit, send /done. To stop, send /cancel"
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=context.user_data.get("photo"),
            caption=text
        )
        return 13

    def report_done(self,update,context):
        if context.user_data.get('photo') and context.user_data.get('desc'):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You have successfully sent a report! A comm member will respond in typically 3-5 working days..."
            )
            #update admin group
            admin_text=f'[REPORT] \n@{update.message.from_user.username} sent the following report:\n{context.user_data["desc"]}'
            self.admin_log(update,context, admin_text, context.user_data['photo'])

            #update report logs
            curr_time = datetime.datetime.now().isoformat()
            self.update_report_log([update.message.from_user.username, curr_time, context.user_data["desc"]])
            context.user_data.clear()
            return -1   
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, please send both a description and a photo."
            )

    def report_cancel(self,update,context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Report cancelled! Make sure to update us if you spot anything suspicious..."
        )
        context.user_data.clear()
        return -1

    def report_handler(self):
        my_handler=ConversationHandler(
            entry_points=[CommandHandler('report', self.report_command)],
            states={
                11:[
                    MessageHandler(filters=Filters.text & ~Filters.command, callback=self.report_desc),

                    ],
                12:[
                    MessageHandler(filters=Filters.photo & ~Filters.command, callback=self.report_pic),
                    
                    ],
                13:[
                    MessageHandler(filters=(Filters.text | Filters.photo) & ~Filters.command, callback=self.report_anything),
                    
                    ],
            },
            fallbacks=[
                CommandHandler('cancel',self.report_cancel),
                CommandHandler('done', self.report_done),
                ]
        )
        return my_handler

        pass


    def handle_admin(self, update, context, keywords):
        """Handle the admin commands after /admin"""  
        try:
            command = keywords.pop(0)
            username = keywords.pop(0)
            # handle usernames
            all_users = self.get_user_table()
            chat_id = all_users.get(username, None)

            if command == "topup":
                with open(f'users/{chat_id}.json', 'r') as f:
                    user_data = json.load(f)
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] += int(amount) #ValueError Here
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "deduct":
                with open(f'users/{chat_id}.json', 'r') as f:
                    user_data = json.load(f)
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] -= int(amount) #ValueError Here
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "setcredit":
                with open(f'users/{chat_id}.json', 'r') as f:
                    user_data = json.load(f)
                amount = keywords.pop(0)
                if chat_id is not None:
                    user_data['credits'] = int(amount)
                    self.update_user(user_data)
                else: 
                    self.admin_failed(update,context)

            elif command == "viewcredit":
                with open(f'users/{chat_id}.json', 'r') as f:
                    user_data = json.load(f)
                if chat_id is not None:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'@{user_data["username"]} has : {user_data["credits"]} credits left.')
                else: 
                    self.admin_failed(update,context)
            elif command =="setpin":
                newpin = keywords.pop(0)
                bikes_data = self.get_bikes()
                bike_name  = username
                bike = bikes_data.get(bike_name, None)
                if bike is not None:
                    if bike['pin']!=newpin:
                        bikes_data[bike_name]['oldpin'] = bike['pin']
                        bikes_data[bike_name]['pin'] = newpin
                        self.update_bikes(bikes_data)
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"Pin for {bike_name} updated to {newpin}!"
                        )
                    else:
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f'Old pin is the same as {newpin}!'
                        )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'No such bike, {bike}, exists. Please try again with current /bikes'
                    )

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

    def unrecognized_command(self,update,context):
        update.message.reply_text('Unrecognized command. Do you need /help...?')

    def all_buttons(self,update,context):
        """Manages all inline query buttons, as there can only be one wrapper"""
        data = update.callback_query.data
        if data in self.get_bikes().keys() or data=='stoprent':
            self.rent_button(update,context)
        elif data in ROUTES_PICS.keys() or data=='all':
            self.routes_button(update,context)
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An unknown error occurred... What did you do?!"
            )

    def initialize(self):
        """Initializes all commands that are required in the bot."""

        self.addcmd('start',self.start_command)
        self.addcmd('help', self.help_command)
        self.addcmd('routes', self.routes_command)
        
        self.addcmd('payment', self.payment_command)
        # self.addcmd('credits', self.credits_command) #deprecated, use /status to access credits   
        self.addcmd('rent', self.rent_command)
        self.addcmd('status', self.status_command)
        # self.addcmd('return', self.return_command) #deprecated, moved to return_handler
        self.addcmd('getpin', self.getpin_command)
        self.addcmd('bikes', self.bikes_command)

        #admin handler
        self.addcmd('admin', self.admin_command)


        self.addnew(CallbackQueryHandler(self.all_buttons))

        # This part is for convo commands
        self.addnew(self.report_handler())
        self.addnew(self.return_handler())

        # This part for dummy commands, so that it recognizes commands
        self.addcmd('report', lambda x,y:0) #dummy commmand
        self.addcmd('return', lambda x,y:0) #dummy commmand
        self.addcmd('done', lambda x,y:0) #dummy commmand
        #self.addcmd('cancel', lambda x,y:0) #dummy commmand


        # Fun stuff 
        #self.addcmd('quote', self.quote_command)   #doesnt work on web...
        self.addcmd('doggo', self.doggo_command)
        self.addcmd('neko', self.neko_command)
        self.addcmd('kitty', self.kitty_command)
        self.addcmd('birb', self.birb_command)
        self.addcmd('shibe', self.shibe_command)
        self.addcmd('foxy', self.foxy_command)  
        self.addcmd('random', self.random_command) 

        self.addcmd('animal',self.animal_command)

        self.addcmd('pika', self.pika_command) #pika sticker

        

        # This part is a message command

        # Filters all unknown commands, put this last!!
        self.addmsg(Filters.command, self.unrecognized_command)


    def main(self):
        """Main bot function to run"""
        self.initialize()
        super().main()

        




if __name__=="__main__": 
    # DEV part, do not run this
    print('Running the development bot!')
    newbot = OrcaBot(DEV_API_KEY, admin_group_id=DEV_ADMIN_GROUP_ID)
    newbot.main()
    

