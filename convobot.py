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
    EMOJI,
    PAYMENT_URL
)

from telebot import TeleBot

import random
import json
import csv
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

class ConvoBot(TeleBot):
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

        text = "Here are some available routes for ya!\n\n" + '\n'.join(ROUTES_LIST.values())
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
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
                text = "To see more routes, send /routes"
                text+= "\nTo start your journey, send /rent"
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
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
        if not self.check_user(update,context):
            return -1
        context.user_data.clear()
        user_data = super().get_user(update,context)
        keyboard = [
            [InlineKeyboardButton("$2.00", callback_data='200'),],

            [InlineKeyboardButton("$5.00", callback_data='500'),],
            [InlineKeyboardButton("$10.00", callback_data='1000'),],
            [InlineKeyboardButton("$20.00", callback_data='2000'),],
            [InlineKeyboardButton("Cancel", callback_data='CANCEL_PAYMENT')],
        ]
        text = "Please choose a top-up amount."
        if self.promo:
            text+= "\nPROMO: D-d-double credits!"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
            reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return 71

    def payment_button(self,update,context):
        """Manage buttons pressed with /payment and /topup command"""
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
                text1 = f'[1] PayLah/PayNow to Lau Jin Ming, at 98561839'
                text1+= '\n[2] Once done, send a screenshot to @orc4bikes_bot!!'
                text1+= '\n[3] You will receive "Transaction complete! You now have XXXX credits" for comfirmation'

                text2 = 'If I don\'t respond after you send your screenshot, please try to /topup again.'
                text2+= '\n\nTo stop, send /cancel'
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text1,
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Go to PayLah", callback_data='redirect_paylah', url=PAYMENT_URL)]
                    ]),
                )
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text2
                )
                return 72
        except Exception as e:
            self.log_exception(e,"Error with payment_button")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, topup is currently unavailable... Please try to /topup again, or contact a orc4bikes comm member to assist you!"
                )
            return -1

    def payment_pic(self,update,context):
        """After photo is sent, save the photo and ask if would like to retake"""
        query = update.callback_query
        query.answer()
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

                # Notify user
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Transaction complete! You now have {user_data.get('credits')} credits.\nTo start your journey, /rent now!")

                if self.promo: #Promotion period, credits are doubled
                    user_data['credits'] += amount
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Promotion applied! An additional {amount} credits was added to your account. You now have {user_data.get('credits')} credits.\nHappy cycling!")

                super().update_user(user_data)

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
                    text="Sorry, your operation timed out, as we are unable to get your amount currently. Please try to /topup again!"
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
        if not self.check_user(update,context):
            return -1
        context.user_data.clear()
        user_data = super().get_user(update,context)
        status = user_data.get('status', None)
        if status is not None: # Rental in progress
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already renting! Please /return your current bike first"
            )
            return -1
        elif user_data.get('credits', 0) < 1: # Insufficient credits
            text = f"You cannot rent, as you don't have enough credits! Current credits: {user_data.get('credits')}"
            text+= '\nUse /history to check your previous transactions, or /topup to top up now!'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
            )
            return -1

        # Pass all checks, can rent. Get bikes
        bikes_data = self.get_bikes()
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
                    text=f"Rental started! Time of rental, {self.now().strftime('%Y/%m/%d, %H:%M:%S')}\nUse /getpin to unlock bike.")

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
                text="Sorry, an error occurred... Please retry to /rent the bike!"
            )
            return -1

    def return_command(self,update,context):
        """Return the current bike"""
        if not self.check_user(update,context):
            return -1
        context.user_data.clear()
        user_data = super().get_user(update,context)
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
                text="Please send a photo for proof of return! Photo must include the BIKE and LOCK. \nPicture must be a photo, not a file... \nTo continue rental, send /cancel"
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
            deduction_text+= "\n\nTo top-up your credits, send /topup"
            deduction_text+= "\nTo start a new journey, send /rent"
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
        """Starts a report conversation"""
        context.user_data.clear()
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
            text = "You have successfully sent a report! A comm member will respond in typically 3-5 working days..."
            text+= '\n\nTo start a journey, send /rent'
            text+= '\nTo see available bikes, send /bikes'
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
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
                CommandHandler('topup',self.payment_command),
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
                    CallbackQueryHandler(self.payment_pic),
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
                CommandHandler('topup',self.payment_command),
                CommandHandler('return', self.return_command),
                CommandHandler('report', self.report_command)
                ],
        )
        return my_handler

    def initialize(self):
        """
        Initializes all ConversationHandlers for the bot
        """        
        self.addnew(self.all_handlers())