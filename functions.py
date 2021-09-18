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

    def getpin_command(self,update,context):
        """Gets pin of current renting bike.
        Not available if not renting"""
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
                text="You haven't cycled with us before :( Send /bikes to start renting now!"
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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )

    def status_command(self,update,context):
        """Check the user rental status and current credits"""
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
                deduction = self.calc_deduct(diff)
                status_text += f'\n\nCREDITS:\nCurrent:  {user_data.get("credits")} \nThis trip:  {deduction}\nProjected final:  {user_data.get("credits") - deduction}'
            else:
                creds = user_data.get("credits", 0)
                status_text = f'You are not renting... \n\nYou have {creds} credits left. '
                if creds < 100:
                    status_text+='Please top up soon!'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=status_text)
        except Exception as e:
            self.log_exception(e,"Error with status_command")

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
        return 51

    def routes_button(self,update,context):
        """Manage buttons pressed with /routes command"""
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
            self.log_exception(e,"Error with routes_button")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Server timeout... Here are some routes for your consideration\n"
                       + '\n'.join(ROUTES_LIST.values())
                )
        query.edit_message_text(text=f"Selected option: {query.data}")
        return -1

    def payment_command(self,update,context):
        """Payment:
        Returns available amounts to top up by"""
        user_data = super().get_user(update,context)
        if user_data is None:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
            return -1
        keyboard = [
            [InlineKeyboardButton("$5.00", callback_data='500'),],
            [InlineKeyboardButton("$10.00", callback_data='1000'),],
            [InlineKeyboardButton("$20.00", callback_data='2000'),],
            [InlineKeyboardButton("Cancel", callback_data='CANCEL_PAYMENT')],
        ]
        text = "Please choose a top-up amount."
        if self.promo:
            text+= "\nPromotion: double credits!"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
            reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return 71

    def payment_button(self,update,context):
        """Manage buttons pressed with /payment command"""
        query = update.callback_query
        query.answer()
        amount = query.data
        try:
            if amount=='CANCEL_PAYMENT':
                query.edit_message_text('Please choose at top-up amount!')
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Payment cancelled!"
                )
                return -1
            else:
                amount = int(amount)
                context.user_data['amount'] = amount
                query.edit_message_text(f'Selected amount: ${amount//100:.2f}')
                text = 'Please PayLah/PayNow to Lau Jin Ming, at: \n98561839'
                text+= '\nOnce done, please send a screenshot to me @orc4bikes_bot!!'
                text+= '\n\nIf I do not respond after you send the screenshot, please wait for 10 seconds. If I am still not responding, please restart /payment again.'
                text+= '\nNOTICE: If you do not see "Transaction complete! You now have XXXX credits", your credits has NOT been topped up. To stop, send /cancel'
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
                )
                return 72
        except Exception as e:
            self.log_exception(e,"Error with payment_button")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, payment is currently unavailable... Please try /payment again, or contact a orc4bikes comm member to assist you!"
                )
            return -1

    def payment_pic(self,update,context):
        """After photo is sent, save the photo and ask if would like to retake"""
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo
            text = '^ This is your PayLah/PayNow confirmation to Lau Jin Ming, at 98561839.'
            text+= '\nIf you are unsatisfied with your image, please send another one. \nTo CONFIRM PAYMENT, send /done. To cancel, send /cancel'
            text+= '\n\nNOTICE: If you do not see "Transaction complete! You now have XXXX credits", your credits has NOT been topped up.'
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=context.user_data["photo"],
                caption=text
            )
        else:
            text = 'Upon completion of payment (to 98561839), please send a screenshot to me @orc4bikes_bot!!'
            text+= '\nTo CONFIRM PAYMENT, send /done. To cancel, send /cancel'
            text+= '\n\nNOTICE: If you do not see "Transaction complete! You now have XXXX credits", your credits has NOT been topped up.'
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                text=text
            )
        return 72

    def payment_done(self,update,context):
        try:
            if context.user_data.get('photo') and context.user_data.get('amount'): #Completed with photo
                photo = context.user_data.get('photo')
                amount = context.user_data.get('amount')
                amount = int(float(amount))

                user_data = self.get_user(update,context)
                initial_amount = user_data.get('credits')
                user_data['credits'] += amount
                super().update_user(user_data)

                # Notify user
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Transaction complete! You now have {user_data.get('credits')} credits")

                if self.promo: #Promotion period, credits are doubled
                    user_data['credits'] += amount
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Promotion applied! An additional {amount} credits was added to your account. Happy cycling!")

                # Notify Admin group
                message=f'[FINANCE - PAYMENT] \n@{user_data["username"]} paid ${amount/100:.2f} at {self.now().strftime("%Y/%m/%d, %H:%M:%S")}'
                self.admin_log(update,context,message,photo)

                # Update finance log
                finance_log=[
                    user_data.get('username'),
                    self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    initial_amount, user_data.get('credits')-initial_amount, user_data.get('credits'),
                    'orc4bikes_bot'
                ]
                self.update_finance_log(finance_log)

                return -1

            elif context.user_data.get('amount',None) is None: # Unable to get amount, restart payment process
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, your operation timed out, as we are unable to get your amount currently. Please try to make /payment again!"
                )
                return -1
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, you have not completed the payment process! \nTo continue, follow the instructions above. To stop, send /cancel"
                )
                return None
        except Exception as e:
            self.log_exception(e,"Error with payment_done")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, an error occurred... Please retry to make a /payemnt!"
            )
            return -1

    def rent_command(self,update,context):
        """Start to rent a bike.
        Impose 3 checks before rental: Registered, Renting, Credits
        Get bikes in the format of InlineKeyboardMarkup buttons
        Usage: click button to rent"""
        #Impose checks on user before starting
        user_data = super().get_user(update,context)
        if user_data is None: # User is not registered
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=START_MESSAGE
                )
            return -1
        status = user_data.get('status', None)
        if status is not None: # Rental in progress
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already renting! Please return your current bike first"
            )
            return -1
        elif user_data.get('credits', 0) < 1: # Insufficient credits
            text = f"You cannot rent, as you don't have enough credits! Current credits: {user_data.get('credits')}"
            text+= '\nUse /history to check your previous transactions, or /payment to top up now!'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
            )
            return -1

        # Pass all checks, can rent. Get bikes
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
        return 11

    def rent_button(self,update,context):
        """Manage buttons pressed with /rent command"""
        query = update.callback_query
        query.answer()
        bike_name = query.data
        bikes_data = self.get_bikes()
        try:
            if bike_name == 'stoprent':
                query.edit_message_text(text="Rental has been cancelled! Send /rent to refresh the available bikes.")
                return -1
            bike_data = bikes_data.get(bike_name,None)
            if bike_data is None: # Bike doesn't exist
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'No such bike {bike_name} found. Please indicate which bike you would like to rent.')
                return -1
            # Bike exists
            if bike_data["status"] != 0: # Bike is not available
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Sorry, {bike_name} is not available. Please indicate which bike you would like to rent.')
                return -1
            else: # Bike is available
                if bike_name == "fold_blue":
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Dear user, we are aware that the Blue Foldable has a dent. No report is needed to be made, thank you!"
                    )
                query.edit_message_text(text=f'Selected bike: {bike_name}')
                context.user_data['bike_name'] = bike_name
                text=self.terms_text
                keyboard = list()
                keyboard.append([InlineKeyboardButton('Accept', callback_data='TERMS_YES')])
                keyboard.append([InlineKeyboardButton('Decline', callback_data='TERMS_NO')])
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return 12
        except Exception as e:
            self.log_exception(e,"Error with rent_button")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, the server seemed to have disconencted... Please try again!"
                )
            return -1

    def terms_button(self,update,context):
        """After accepting terms, ask for photo."""
        query = update.callback_query
        query.answer()
        answer = query.data
        try:
            if answer=='TERMS_YES':
                query.edit_message_text(text=f"{self.terms_text}\n\nYou have accepted the terms.")
                text = 'Please send a picture of the bike you will be renting! Photo must include the BIKE and LOCK.'
                text+= '\n\nTo cancel, send /cancel'
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)
                return 13
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Terms of use has not been accepted. Cancelling rental now."
                )
                query.edit_message_text(text=f"{self.terms_text}\n\nTo rent, please accept the terms above.")
                return -1
        except Exception as e:
            self.log_exception(e,"Error with terms_button")

    def rent_pic(self,update,context):
        """After photo is sent, save the photo and ask if would like to retake"""
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo
            text="^ This is your image. If you are unsatisfied with your image, please send another one. \nTo CONFIRM RENTAL, send /done. To cancel, send /cancel"
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=context.user_data["photo"],
                caption=text
            )
        else:
            text = 'Please send a picture of the bike you will be renting! Photo must include the BIKE and LOCK.' # , As shown in the sample photo.'
            text+= '\n\nTo CONFIRM RENTAL, send /done. \nTo cancel, send /cancel'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text)
            """
            # SEND SAMPLE PHOTO HERE!!
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sample photo not available at the moment... Please still send a photo though!!"
            )
            """
        return 13

    def rent_done(self,update,context):
        try:
            if context.user_data.get('photo') and context.user_data.get('bike_name'): #Completed with photo
                bike_name = context.user_data.get('bike_name')

                user_data = self.get_user(update,context)
                curr_time = self.now().isoformat()
                user_data['status'] = curr_time
                user_data['bike_name'] = bike_name
                super().update_user(user_data)

                bikes_data = self.get_bikes()
                bikes_data[bike_name]['username'] = user_data.get('username')
                bikes_data[bike_name]['status'] = curr_time
                self.update_bikes(bikes_data)

                # Notify user
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Rental started! Time of rental, {self.now().strftime('%Y/%m/%d, %H:%M:%S')}")

                # Notify Admin group
                message=f'[RENTAL - RENT] \n@{user_data["username"]} rented {bike_name} at {self.now().strftime("%Y/%m/%d, %H:%M:%S")}'
                self.admin_log(update,context,message,context.user_data['photo'])
                return -1

            elif context.user_data.get('bike_name',None) is None: # Unable to get bike_name, restart rental process
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, your operation timed out, as we are unable to get your bike name currently. Please try to /rent again!"
                )
                return -1
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, you have not completed the rental process! \nTo continue, follow the instructions above. To stop, send /cancel"
                )
                return None
        except Exception as e:
            self.log_exception(e,"Error with rent_done")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, an error occurred... Please retry renting the bike!"
            )
            return -1

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
        if status is None: #rental in progress
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not renting..."
            )
            return -1
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please send a photo for proof of return! \nPicture must be a photo, not a file... \nTo continue rental, send /cancel"
            )
            return 91

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
            start_time = datetime.datetime.fromisoformat(bikes_data[bike_name]['status']).strftime('%Y/%m/%d, %H:%M:%S')
            end_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
            self.update_rental_log([bike_name,username,start_time,end_time,deduction])

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
                'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
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

            deduction_text = f"{deduction} credits was deducted. Remaining credits: {user_data['credits']}"
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=deduction_text
            )
            # Notify Admin group
            admin_text=f'[RENTAL - RETURN] \n@{update.message.from_user.username} returned {bike_name} at following time:\n{self.now().strftime("%Y/%m/%d, %H:%M:%S")}'
            admin_text+='\n'+deduction_text
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

    def report_command(self,update,context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please send a short description of the report you would like to make! \nTo stop, send /cancel"
        )
        return 81

    def report_desc(self, update,context):
        """After description is sent, save the description and ask for pics"""
        desc = update.message.text
        context.user_data['desc'] = desc
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please attach a picture as well! \nPicture must be a photo, not a file...  \nTo stop, send /cancel"
        )
        return 82

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
        return 83

    def report_anything(self, update,context):
        """Change either the photo or the message"""
        if update.message.text:
            desc = update.message.text
            context.user_data['desc'] = desc
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo

        text=f'Your report is: \n{context.user_data.get("desc", "")}\n\n'
        text+="To update your report or image, feel free to send another one. \nTo submit, send /done. To stop, send /cancel"

        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=context.user_data.get("photo"),
            caption=text
        )
        return 83

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
            curr_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
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

    def cancel_command(self,update,context):
        """Used for conversation handlers"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Operation successfully cancelled!"
        )
        context.user_data.clear()
        return -1

    def all_handlers(self):
        my_handler = ConversationHandler(
            entry_points = [
                CommandHandler('rent', self.rent_command),
                CommandHandler('routes',self.routes_command),
                CommandHandler('payment',self.payment_command),
                CommandHandler('return', self.return_command),
                CommandHandler('report', self.report_command)
            ],
            states = {
                # 1-X: Rental
                11:[
                    CallbackQueryHandler(self.rent_button),
                    CommandHandler('done',callback=self.rent_done),
                ],
                12:[
                    CallbackQueryHandler(self.terms_button),
                    CommandHandler('done',callback=self.rent_done),
                ],
                13:[
                    MessageHandler(filters=~Filters.command, callback=self.rent_pic),
                    CommandHandler('done',callback=self.rent_done),
                ],

                # 5-X: Routes
                51:[
                    CallbackQueryHandler(self.routes_button),
                    MessageHandler(filters=Filters.text | Filters.command, callback=lambda x,y:-1),
                ],

                # 7-X: Payment
                71:[
                    CallbackQueryHandler(self.payment_button),
                    CommandHandler('done',callback=self.payment_done),
                ],
                72:[
                    MessageHandler(filters=Filters.photo & ~Filters.command, callback=self.payment_pic),
                    CommandHandler('done',callback=self.payment_done),
                ],

                # 8-X: Reports
                81:[
                    MessageHandler(filters=Filters.text & ~Filters.command, callback=self.report_desc),
                    CommandHandler('done',callback=self.report_done),
                ],
                82:[
                    MessageHandler(filters=Filters.photo & ~Filters.command, callback=self.report_pic),
                    CommandHandler('done',callback=self.report_done),
                ],
                83:[
                    MessageHandler(filters=(Filters.text | Filters.photo) & ~Filters.command, callback=self.report_anything),
                    CommandHandler('done',callback=self.report_done),
                ],

                # 9-X: Returns
                91:[
                    MessageHandler(~Filters.command, callback=self.return_pic),
                    CommandHandler('done',callback=self.return_done)
                ],
            },
            fallbacks = [
                CommandHandler('cancel',self.cancel_command),
                # Add entry points, to re-enter the Convo
                CommandHandler('rent', self.rent_command),
                CommandHandler('routes',self.routes_command),
                CommandHandler('payment',self.payment_command),
                CommandHandler('return', self.return_command),
                CommandHandler('report', self.report_command)
                ],
        )
        return my_handler

    def echo_command(self,update,context):
        update.message.reply_text(update.message.text)

    def dummy_command(self,update,context):
        update.message.reply_text('This feature will be added soon! Where art thou, bikes...?')

    def unrecognized_command(self,update,context):
        """Let the user know this command is unrecognized"""
        update.message.reply_text('Unrecognized command. Do you need /help...?')

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
        AdminBot.initialize(self)
        FunBot.initialize(self)

        # User related commands
        self.addcmd('start',self.start_command)
        self.addcmd('help', self.help_command)
        self.addcmd('guide', self.guide_command)
        # self.addcmd('routes', self.routes_command)
        self.addcmd('history', self.history_command)

        # Bike related commands
        self.addcmd('bikes', self.bikes_command)
        #self.addcmd('payment', self.payment_command)
        self.addcmd('status', self.status_command)
        self.addcmd('getpin', self.getpin_command)

        # This part is for convo handlers
        self.addnew(self.all_handlers())

        # Lastly, Filters all unknown commands, and remove unrecognized queries
        self.addmsg(Filters.command, self.unrecognized_command)
        self.addnew(CallbackQueryHandler(self.unrecognized_buttons))

        # For scheduling messages
        self.scheduler()

    def main(self):
        """Main bot function to run"""
        TeleBot.main(self)

    def handle_admin(self, update, context, keywords, command=''):
        """Handle the admin commands after /admin"""
        try:
            if not command:
                command=keywords.pop(0)

            if command in ['setpin','setstatus','forcereturn']: #bike commands
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
                user_data['credits'] -= int(number)
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
                text+=f'User has been renting {user_data["bike_name"]} since {user_data["status"]}' if user_data.get("bike_name") else "User is not renting currently."
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)

            elif command == "forcereturn":
                username = bike.get('username',"")
                if username:
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
                    bikes_data = self.get_bikes()
                    start_time = datetime.datetime.fromisoformat(bikes_data[bike_name]['status']).strftime('%Y/%m/%d, %H:%M:%S')
                    end_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
                    self.update_rental_log([bike_name,username,start_time,end_time,deduction])

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
                        'time':self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'credits':user_data.get('credits'),
                        'spent': deduction,
                        'remaining': user_data.get('credits') - deduction
                    }
                    user_data['finance'].append(f_log)
                    super().update_user(user_data)

                    admin_username = update.message.from_user.username
                    context.bot.send_message(
                        chat_id=user_data.get('chat_id'),
                        text=f"An admin, @{admin_username} has returned your bike for you! Your total rental time is {strdiff}."
                    )
                    deduction_text = f"{deduction} credits was deducted. Remaining credits: {user_data['credits']}"
                    deduction_text+= '\nIf you have any queries, please ask a comm member for help.'
                    context.bot.send_message(
                        chat_id=user_data.get('chat_id'),
                        text=deduction_text
                    )
                    # Notify Admin group
                    admin_text=f'[RENTAL - RETURN] \n@{update.message.from_user.username} returned {bike_name} at following time:\n{self.now().strftime("%Y/%m/%d, %H:%M:%S")}'
                    admin_text+=f'\nThis return was force-returned by @{admin_username}.'
                    admin_text+='\n'+deduction_text
                    self.admin_log(update,context, admin_text)
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Bike not on rent! Please try again"
                    )

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
                text= '\n'.join(f'{bike["name"]}  --  {bike["username"] or bike["status"] or EMOJI["tick"]} (Pin: {bike["pin"]})' for bike in bikes_data.values())
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


if __name__=="__main__":
    newbot = OrcaBot(DEV_API_KEY, admin_group_id=DEV_ADMIN_GROUP_ID)
    newbot.main()