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
from funbot import FunBot
from adminbot import AdminBot

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


class OrcaBot(AdminBot, FunBot, TeleBot):
    def __init__(self,
            api_key,
            admin_group_id=DEV_ADMIN_GROUP_ID,
            help_text=HELP_TEXT,
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT,
            deduct_rate=DEDUCT_RATE
            ):
        print('running OrcaBot')
        super().__init__(api_key)
        self.help_text = help_text
        self.admin_group_id = admin_group_id
        self.admin_list = admin_list
        self.admin_text = admin_text
        self.deduct_rate = deduct_rate

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
        text += "\nFor more info, send /help"

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
        self.random_command(update,context) #random for placeholder
        """
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            caption = "instructions here",
            photo = "url to photo here"
            )
        """        

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
                text="Server timeout... Here are some routes for your consideration\n"
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
            text = "Here are some available routes for ya!\n\n" + '\n'.join(ROUTES_LIST.values()),
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

    def history_command(self,update,context):
        """Shows past 10 transaction history"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        data = user_data.get('finance',[])[-10:] # get the last 10 transactions
        if data:
            text=f"Your past {len(data)} transaction history are as follows:\n\n"
            for i,line in enumerate(data,1):
                if line['type']=='admin':
                    text+=f'{i}: An admin {"added" if line["change"]>=0 else "deducted"} {line["change"]} credits on {line["time"]}. You now have {line["final"]} credits.\n'
                elif line['type']=='rental':
                    text+=f'{i}: You rented a bike on {line["time"]}, and spent {line["spent"]} credits.\n'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You haven't cycled with us before :( Send /bikes to start renting now!"
            )

    def credits_command(self,update,context):
        """Show your current available credits"""
        user_data = super().get_user(update,context)
        if user_data is None:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
        credits = user_data.get("credits", 0)
        text = f'Your remaining credits is: {credits}.'
        if credits < 10:
            text+=' Please top up soon!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
        )

    def calc_deduct(self,time_diff):
        deduction = time_diff.seconds // self.deduct_rate + int(time_diff.seconds%self.deduct_rate > 0)
        deduction += time_diff.days * 86400 / self.deduct_rate
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
                elif user_data.get('credits', 0) < 1: #not enough credits
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"You cannot rent, as you do not have enough credits! Current credits: {user_data.get('credits')}"
                    )
                    return
                else:
                    curr_time = self.now().isoformat()
                    user_data['status'] = curr_time
                    user_data['bike_name'] = bike_name
                    super().update_user(user_data)

                    bikes_data[bike_name]['username'] = user_data.get('username')
                    bikes_data[bike_name]['status'] = curr_time
                    self.update_bikes(bikes_data)

                    # Notify user
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Rental started! Time of rental, {self.now().strftime('%m/%d/%Y, %H:%M:%S')}")

                    # Notify Admin group
                    message=f'[RENTAL - RENT] \n@{user_data["username"]} rented {bike_name} at {self.now().strftime("%m/%d/%Y, %H:%M:%S")}'
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
                curr = self.now()
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
            print(f'Error occured at {self.now()}. Error is \n{e}')

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

    def return_pic(self,update,context):
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
            username = user_data.get('username')
            bike_name = user_data['bike_name']
            bikes_data = self.get_bikes()
            start_time = bikes_data[bike_name]['status']
            end_time = self.now().isoformat()
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
            user_data['credits'] -= deduction
            user_data['finance'] = user_data.get('finance',[])
            f_log = {
                'type':'rental',
                'time':self.now().strftime("%m/%d/%Y, %H:%M:%S"),
                'credits':user_data.get('credits'),
                'spent': deduction,
                'remaining': user_data.get('credits') - deduction
            }
            user_data['finance'].append(f_log)
            super().update_user(user_data)



            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Successfully returned! Your total rental time is {strdiff}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{deduction} was deducted from your credits. Your remaining credit is {user_data['credits']}"
            )
            # Notify Admin group
            admin_text=f'[RENTAL - RETURN] \n@{update.message.from_user.username} returned {bike_name} at following time:\n{self.now().strftime("%m/%d/%Y, %H:%M:%S")}'
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
                query.edit_message_text(text="Send /bikes to refresh the available bikes!")
                return
            self.rent_command(update,context,bike_name=bike_name)
            query.edit_message_text(text="Renting in progress...")
        except Exception as e:
            print('error with button renting, error is:\n',e)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Server timed out error..."
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
        not_avail = "\n".join(f'{b["name"]} {EMOJI["cross"]} -- {"on rent" if b.get("username") else b["status"]}'  for b in not_avail )
        text = f'Bicycles:\n{avail}'
        text+= '\n\n' if avail else ''
        text+= f'{not_avail}'
        text+='\n\nClick below to start renting now!' if avail else '\n\nSorry, no bikes are not unavaialble...'
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

    def report_desc(self, update,context):
        """After description is sent, save the description and ask for pics"""
        desc = update.message.text
        context.user_data['desc'] = desc
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please attach a picture as well! \nPicture must be a photo, not a file...  \nTo stop, send /cancel"
        )
        return 12

    def report_pic(self,update,context):
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

    def report_anything(self, update,context):
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
            admin_text=f'[REPORT] \n@{update.message.from_user.username or update.message.from_user.first_name} sent the following report:\n{context.user_data["desc"]}'
            self.admin_log(update,context, admin_text, context.user_data['photo'])

            #update report logs
            curr_time = self.now().isoformat()
            self.update_report_log([update.message.from_user.username or update.message.from_user.first_name, curr_time, context.user_data["desc"]])
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

    def ohno_command(self,update,context):
        text = random.choice([
            "OH NO!",
            "Oh no indeed...",
            "Oh no"])
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)

    def initialize(self):
        """Initializes all commands that are required in the bot."""

        self.addcmd('ohno',self.ohno_command)
        self.addcmd('start',self.start_command)
        self.addcmd('help', self.help_command)
        self.addcmd('guide', self.guide_command)
        self.addcmd('routes', self.routes_command)
        self.addcmd('history', self.history_command)
        
        self.addcmd('payment', self.payment_command)
        self.addcmd('rent', self.rent_command)
        self.addcmd('status', self.status_command)
        # self.addcmd('return', self.return_command) #deprecated, moved to return_handler
        self.addcmd('getpin', self.getpin_command)
        self.addcmd('bikes', self.bikes_command)

        # This part is for convo handlers
        self.addnew(CallbackQueryHandler(self.all_buttons))
        self.addnew(self.report_handler())
        self.addnew(self.return_handler())

        # This part for dummy commands, so that it recognizes commands
        self.addcmd('report', lambda x,y:0) #dummy commmand
        self.addcmd('return', lambda x,y:0) #dummy commmand
        self.addcmd('done', lambda x,y:0) #dummy commmand
        #self.addcmd('cancel', lambda x,y:0) #dummy commmand

        #running python script in bot
        TeleBot.initialize(self)

        #admin handler
        AdminBot.initialize(self)

        # Fun stuff 
        FunBot.initialize(self)

        # Lastly, Filters all unknown commands, put this last!!
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
    

