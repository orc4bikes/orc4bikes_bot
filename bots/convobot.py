from datetime import datetime
import logging

from telegram import (
    ChatAction,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from bots.telebot import TeleBot

from admin import (
    BOT_ENV,
    BOT_PROMO,
)

# Used to fill up text templates (required even when linter shows unused)
from admin import (
    ADMIN_HEAD,
    ADMIN_HEAD_NAME,
    ADMIN_HEAD_MOBILE,
    ADMIN_SAFETY,
    ADMIN_SAFETY_MOBILE,
    ADMIN_SAFETY_NAME,
    ADMIN_TREASURER,
    ADMIN_TREASURER_MOBILE,
    ADMIN_TREASURER_NAME,
    ADMIN_TREASURER_URL,
)

from bot_text import (
    EMOJI,
    ROUTES_LIST,
    ROUTES_PICS,

    TERMS_TEXT_WITH_BUTTONS
)

from functions import to_readable_td

logger = logging.getLogger()

class ConvoBot(TeleBot):

    def routes_command(self, update, context):
        """Lists all curated routes available."""
        keyboard = [
            [
                InlineKeyboardButton("Blue", callback_data='blue'),
                InlineKeyboardButton("Pink", callback_data='pink'),
            ], [
                InlineKeyboardButton("Green", callback_data='green'),
                InlineKeyboardButton("Orange", callback_data='orange'),
            ], [
                InlineKeyboardButton("All", callback_data='all')
            ]
        ]

        text = "Here are some available routes for ya!"
        text += '\n\n' + '\n'.join(ROUTES_LIST.values())
        update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return 51

    def routes_button(self, update, context):
        """Manage buttons pressed with /routes command"""
        query = update.callback_query
        query.answer()
        colour = query.data
        query.edit_message_text(
            f"{query.message.text}\n\n<i>Selected option: {query.data}</i>",
            parse_mode='HTML')

        if colour == 'all':
            for colour, url in ROUTES_PICS.items():
                query.message.reply_photo(
                    photo=url,
                    caption=ROUTES_LIST[colour])
        else:
            query.message.reply_photo(
                photo=ROUTES_PICS[colour],
                caption=ROUTES_LIST[colour])

        query.message.reply_text(
            "To see more routes, send /routes"
            "\nTo start your journey, send /rent")
        return -1

    def payment_command(self, update, context):
        """Payment: Returns available amounts to top up by."""
        update.message.reply_chat_action(ChatAction.TYPING)
        if not self.check_user(update, context):
            return -1
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("$2.00", callback_data='200')],
            [InlineKeyboardButton("$5.00", callback_data='500')],
            [InlineKeyboardButton("$10.00", callback_data='1000')],
            [InlineKeyboardButton("$20.00", callback_data='2000')],
            [InlineKeyboardButton("Cancel", callback_data='CANCEL_PAYMENT')],
        ]
        text = "Please choose a top-up amount."
        if BOT_PROMO:
            text += "\nPROMO: D-d-double credits!"
        update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return 71

    def payment_button(self, update, context):
        """Manage buttons pressed with /payment and /topup command."""
        query = update.callback_query
        query.answer()
        amount = query.data

        if amount == 'CANCEL_PAYMENT':
            query.edit_message_text("Please choose at top-up amount!")
            query.message.reply_text("Payment cancelled!")
            return -1

        amount = int(amount)
        context.user_data['amount'] = amount
        query.edit_message_text(
            f'{query.message.text}\n\n<i>Selected amount: ${amount//100:.2f}</i>',
            parse_mode='HTML')

        text1 = (
            f"[1] PayLah/PayNow to {ADMIN_TREASURER_NAME}, at <code>{ADMIN_TREASURER_MOBILE}</code>."
            #, or shorturl.at/dBLW6'  ## TODO: shorturl not working!!
            "\n[2] Once done, send a screenshot to @orc4bikes_bot!!"
            '\n[3] You will receive "Transaction complete! You now have XXXX credits" for comfirmation'
        )
        if BOT_ENV != 'production':
            text1 += "\n<i>Test environment - Send /skip to skip uploading picture!</i>"

        text2 = (
            "If I don't respond after you send your screenshot, please try to /topup again."
            "\n\nTo stop, send /cancel"
        )

        query.message.reply_html(
            text1,
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Go to PayLah", callback_data='redirect_paylah', url=ADMIN_TREASURER_URL)]
            ]))
        query.message.reply_text(text2)
        return 72

    def payment_pic(self, update, context):
        """After photo is sent, save the photo and ask if would like to retake."""
        query = update.callback_query
        if query:
            query.answer()
            return 72

        devskip = False
        if BOT_ENV != 'production':
            devskip = update.message.text == '/skip'

        if not update.message.photo and not devskip:
            text = (
                f"Upon completion of payment (to <code>{ADMIN_TREASURER_MOBILE}</code>), please send a screenshot to me @orc4bikes_bot!!"
                "\nTo CONFIRM PAYMENT, send /done. To cancel, send /cancel"
                "\n"
                '\nNOTICE: If you do not see "Transaction complete! You now have XXXX credits",'
                " your credits has NOT been topped up."
            )

            update.message.reply_html(text)
            return

        if not update.message.photo:
            photo = self.get_random_pic()
        else:
            photo = update.message.photo[-1].file_id

        context.user_data['photo'] = photo
        text = (
            f"^ This is your PayLah/PayNow confirmation to {ADMIN_TREASURER_NAME} at <code>{ADMIN_TREASURER_MOBILE}</code>."
            "\nIf you are unsatisfied with your image, please send another one."
            "\nTo CONFIRM PAYMENT, send /done. To cancel, send /cancel"
            "\n"
            '\nNOTICE: If you do not see "Transaction complete! You now have XXXX credits",'
            " your credits has NOT been topped up."
        )

        update.message.reply_photo(
            photo=photo,
            caption=text,
            parse_mode='HTML')

        return 72

    def payment_done(self, update, context):
        if not context.user_data['photo'] or not context.user_data['amount']:
            # Not completed with photo
            if context.user_data.get('amount', None) is None:
                # Unable to get amount, restart payment process
                update.message.reply_text(
                    "Sorry, your operation timed out, as we are unable to get your amount currently. "
                    "Please try to /topup again!")
                return -1
            else:
                update.message.reply_text(
                    "Sorry, you have not completed the payment process!"
                    "\nTo continue, follow the instructions above. To stop, send /cancel")
                return None

        photo = context.user_data['photo']
        amount = context.user_data['amount']
        amount = int(float(amount))

        user_data = self.get_user(update, context)
        initial_amount = user_data['credits']
        user_data['credits'] += amount

        # Notify user
        update.message.reply_text(
            f"Transaction complete! You now have {user_data['credits']} credits."
            "\nTo start your journey, /rent now!")

        if BOT_PROMO:  # Promotion period, credits are doubled
            user_data['credits'] += amount
            update.message.reply_text(
                f"Promotion applied! An additional {amount} credits was added to your account."
                f"You now have {user_data['credits']} credits."
                "\nHappy cycling!")

        user_data['finance'] = user_data.get('finance', [])
        f_log = {
            'type': 'payment',
            'time': self.now().strftime("%Y/%m/%d, %H:%M:%S"),
            'initial': initial_amount,
            'change': user_data['credits'] - initial_amount,
            'final': user_data['credits'],
        }
        user_data['finance'].append(f_log)
        user_data['username'] = update.message.from_user.username
        super().update_user(user_data)

        # Notify Admin group
        message = (
            f"[FINANCE - PAYMENT]\n@{user_data['username']} paid ${amount/100:.2f} at "
            f"{self.now().strftime('%Y/%m/%d, %H:%M:%S')}"
        )
        self.admin_log(update, context, message, photo)

        # Update finance log
        finance_log = [
            user_data['username'],
            self.now().strftime("%Y/%m/%d, %H:%M:%S"),
            initial_amount, user_data['credits']-initial_amount, user_data['credits'],
            'orc4bikes_bot'
        ]
        self.update_finance_log(finance_log)

        return -1


    def rent_command(self, update, context):
        """Start to rent a bike.
        Impose 3 checks before rental: Registered, Renting, Credits
        Get bikes in the format of InlineKeyboardMarkup buttons
        Usage: click button to rent
        """
        update.message.reply_chat_action(ChatAction.TYPING)
        # Impose checks on user before starting
        if not self.check_user(update, context):
            return -1
        context.user_data.clear()
        user_data = super().get_user(update, context)
        status = user_data.get('status', None)
        if status is not None:  # Rental in progress
            update.message.reply_text(
                "You are already renting! Please /return your current bike first.")
            return -1
        if user_data.get('credits', 0) < 1:  # Insufficient credits
            text = (
                f"You cannot rent, as you don't have enough credits! Current credits: {user_data['credits']}"
                "\nUse /history to check your previous transactions, or /topup to top up now!"
            )
            update.message.reply_text(text)
            return -1

        # Pass all checks, can rent. Get bikes
        bikes_data = self.get_bikes()
        avail, not_avail = [], []
        for bike in bikes_data:
            if not bike['status']:
                avail.append(bike)
            else:
                not_avail.append(bike)

        avail_text = '\n'.join(f"{b['name']} {EMOJI['tick']}" for b in avail)
        not_avail_text = '\n'.join(f"{b['name']} {EMOJI['cross']} -- {'on rent' if b['username'] else b['status']}" for b in not_avail)
        action_text = "Click below to start renting now!" if avail else "Sorry, no bikes are available..."
        text = '\n\n'.join(["<b>Bicycles:</b>", avail_text, not_avail_text, action_text])

        avail_bikes = [bike['name'] for bike in bikes_data if not bike['status']]
        keyboard = [[InlineKeyboardButton(f"Rent {bike}", callback_data=bike)] for bike in avail_bikes]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data='stoprent')])

        update.message.reply_html(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return 11

    def rent_button(self, update, context):
        """Manage buttons pressed with /rent command"""
        query = update.callback_query
        query.answer()
        bike_name = query.data

        if bike_name == 'stoprent':
            query.edit_message_text(text="Rental has been cancelled! Send /rent to refresh the available bikes.")
            return -1

        bike_data = self.get_bike(bike_name)
        if bike_data is None:  # Bike doesn't exist
            query.message.reply_text(
                f"No such bike {bike_name} found. Please indicate which bike you would like to rent.")
            return -1

        # Bike exists
        if bike_data['status'] != 0:  # Bike is not available
            query.message.reply_text(
                f"Sorry, {bike_name} is not available. Please indicate which bike you would like to rent.")
            return -1

        query.edit_message_text(
            f"{query.message.text_html}\n\n<i>Selected bike: {bike_name}</i>",
            parse_mode='HTML')

        if bike_data['message']:
            query.message.reply_text(bike_data['message'])

        context.user_data['bike_name'] = bike_name
        text = TERMS_TEXT_WITH_BUTTONS.format(**globals())
        keyboard = [            [InlineKeyboardButton("Accept", callback_data='TERMS_YES')],
            [InlineKeyboardButton("Decline", callback_data='TERMS_NO')]        ]

        query.message.reply_text(
            text, parse_mode='HTML',            reply_markup=InlineKeyboardMarkup(keyboard)) 
        return 12

    def terms_button(self, update, context):
        """After accepting terms, ask for photo."""
        query = update.callback_query
        query.answer()
        answer = query.data
        query.message.reply_chat_action(ChatAction.TYPING)

        if answer != 'TERMS_YES':
            query.message.reply_text(
                "Terms of use has not been accepted. Cancelling rental now.")
            query.edit_message_text(
                f"{query.message.text_html}\n\n<i>To rent, please accept the terms above.</i>",
                parse_mode='HTML')
            return -1

        query.edit_message_text(
            f"{query.message.text_html}\n\n<i>You have accepted the terms.</i>",
            parse_mode='HTML')


        text = (
            "Please send a picture of the bike you will be renting! Photo must include the BIKE and LOCK."
            "\n"
            "\nTo cancel, send /cancel"
        )
        if BOT_ENV != 'production':
            text += "\n<i>Test environment - Send /skip to skip uploading picture!</i>"

        query.message.reply_html(text)
        return 13

    def rent_pic(self, update, context):
        """After photo is sent, save the photo and ask if would like to retake"""
        update.message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

        devskip = False
        if BOT_ENV != 'production':
            devskip = update.message.text == '/skip'

        if not update.message.photo and not devskip:
            text = (
                "Please send a picture of the bike you will be renting! Photo must include the BIKE and LOCK."
                # , As shown in the sample photo.'
                "\n"
                "\nTo CONFIRM RENTAL, send /done.\nTo cancel, send /cancel"
            )
            update.message.reply_text(text)
            """
            # SEND SAMPLE PHOTO HERE!!
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sample photo not available at the moment... Please still send a photo though!!"
            )
            """
            return
        if not update.message.photo:
            photo = self.get_random_pic()
        else:
            photo = update.message.photo[-1].file_id

        context.user_data['photo'] = photo
        text = ("^ This is your image. If you are unsatisfied with your image, please send another one."
                "\nTo CONFIRM RENTAL, send /done. To cancel, send /cancel")
        
        update.message.reply_photo(
            photo=photo,
            caption=text)

    def rent_done(self, update, context):
        update.message.reply_chat_action(ChatAction.TYPING)
        if not context.user_data['photo'] or not context.user_data['bike_name']:
            if context.user_data.get('bike_name', None) is None:  # Unable to get bike_name, restart rental process
                update.message.reply_text(
                    "Sorry, your operation timed out, as we are unable to get your bike name currently. "
                    "Please try to /rent again!")
                return -1
            else:
                update.message.reply_text(
                    "Sorry, you have not completed the rental process!"
                    "\nTo continue, follow the instructions above. To stop, send /cancel")
                return None

        # Completed with photo
        bike_name = context.user_data['bike_name']

        user_data = self.get_user(update, context)
        curr_time = self.now().isoformat()
        user_data['status'] = curr_time
        user_data['bike_name'] = bike_name
        user_data['username'] = update.message.from_user.username
        super().update_user(user_data)

        bike = self.get_bike(bike_name)
        bike['username'] = user_data['username']
        bike['status'] = curr_time
        self.update_bike(bike)

        # Notify user
        update.message.reply_text(
            f"Rental started! Time of rental, {self.now().strftime('%Y/%m/%d, %H:%M:%S')}"
            "\nUse /getpin to unlock bike.")

        # Notify Admin group
        message = (
            f"[RENTAL - RENT]"
            f"\n@{user_data['username']} rented {bike_name} at {self.now().strftime('%Y/%m/%d, %H:%M:%S')}"
        )
        self.admin_log(update, context, message, context.user_data['photo'])
        return -1


    def return_command(self, update, context):
        """Return the current bike"""
        update.message.reply_chat_action(ChatAction.TYPING)
        if not self.check_user(update, context):
            return -1
        context.user_data.clear()
        user_data = super().get_user(update, context)
        status = user_data.get('status', None)

        if status is None:  # Rental in progress
            update.message.reply_text("You are not renting...")
            return -1

        text = (
            "Please send a photo for proof of return! Photo must include the BIKE and LOCK."
            "\nPicture must be a photo, not a file..."
            "\nTo continue rental, send /cancel"
        )
        if BOT_ENV != 'production':
            text += "\n<i>Test environment - Send /skip to skip uploading picture!</i>"

        update.message.reply_text(text, parse_mode='HTML')
        return 91

    def return_pic(self, update, context):
        """After photo is sent, save the photo and ask for others"""
        update.message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        devskip = False
        if BOT_ENV != 'production':
            devskip = update.message.text == '/skip'

        if not update.message.photo and not devskip:
            update.message.reply_text(
                "Please send a photo for proof of return!\nTo continue rental, send /cancel")
            return 91

        if not update.message.photo:
            photo = self.get_random_pic()
        else:
            photo = update.message.photo[-1].file_id

        context.user_data['photo'] = photo
        text = (
            "^ This is your image. If you are unsatisfied with your image, please send another one."
            "\nTo return the bike, send /done. To continue rental, send /cancel"
        )
        update.message.reply_photo(
            photo=photo,
            caption=text)

    def return_done(self, update, context):
        update.message.reply_chat_action(ChatAction.TYPING)
        user_data = super().get_user(update, context)
        status = user_data.get('status', None)
        if context.user_data['photo']:
            diff = self.now() - datetime.fromisoformat(status)
            readable_diff = to_readable_td(diff)
            d = {
                'start': status,
                'end': self.now().isoformat(),
                'time': readable_diff
            }

            deduction = self.calc_deduct(diff)

            # Update return logs
            username = user_data['username']
            bike_name = user_data['bike_name']
            bike_data = self.get_bike(bike_name)
            start_time = datetime.fromisoformat(bike_data['status']).strftime('%Y/%m/%d, %H:%M:%S')
            end_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
            self.update_rental_log([bike_name, username, start_time, end_time, deduction])

            # Update bike first, because bike uses user_data.bike_name
            bike_data['status'] = 0
            bike_data['username'] = ""
            self.update_bike(bike_data)

            # Update user data
            log = user_data.get('log', [])
            log.append(d)
            f_log = {
                'type': 'rental',
                'time': self.now().strftime("%Y/%m/%d, %H:%M:%S"),
                'credits': user_data['credits'],
                'spent': deduction,
                'remaining': user_data['credits'] - deduction
            }
            user_data['status'] = None
            user_data['log'] = log
            user_data['bike_name'] = ''
            user_data['credits'] -= deduction
            user_data['finance'] = user_data.get('finance', [])
            user_data['finance'].append(f_log)
            user_data['username'] = update.message.from_user.username
            super().update_user(user_data)


            update.message.reply_text(
                f"Successfully returned! Your total rental time is {readable_diff}.")

            deduction_text = f"{deduction} credits was deducted. Remaining credits: {user_data['credits']}"
            user_text = deduction_text + "\n\nTo top-up your credits, send /topup"
            user_text += "\nTo start a new journey, send /rent"
            update.message.reply_text(user_text)
            # Notify Admin group

            admin_text = (
                "[RENTAL - RETURN]"
                f"\n@{update.message.from_user.username} returned {bike_name} at following time:"
                f"\n{self.now().strftime('%Y/%m/%d, %H:%M:%S')}"
                f"\n{deduction_text}"
            )

            self.admin_log(update, context, admin_text, context.user_data['photo'])
            context.user_data.clear()
            return -1
        else:
            update.message.reply_text("Sorry, please send a photo.")
            return 91

    def return_cancel(self, update, context):
        update.message.reply_text(
            "Return is cancelled. Enjoy your ride!")
        context.user_data.clear()
        return -1

    def report_command(self, update, context):
        """Starts a report conversation"""
        context.user_data.clear()
        update.message.reply_text(
            "Please send a short description of the report you would like to make! \nTo stop, send /cancel")
        return 81

    def report_desc(self, update, context):
        """After description is sent, save the description and ask for pics"""
        context.user_data['desc'] = update.message.text  # Update desc
        text = (
            "Please attach a picture as well!"
            "\nPicture must be a photo, not a file..."
            "\nTo stop, send /cancel"
        )
        if BOT_ENV != 'production':
            text += "\n<i>Test environment - Send /skip to skip uploading picture!</i>"
        update.message.reply_html(text)
        return 82

    def report_pic(self, update, context):
        """After photo is sent, save the photo and ask for others"""
        update.message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        devskip = False
        if BOT_ENV != 'production':
            devskip = update.message.text == '/skip'

        if not update.message.photo and not devskip:
            update.message.reply_text("Please send a picture!")
            return

        if not update.message.photo:
            photo = self.get_random_pic()
        else:
            photo = update.message.photo[-1].file_id

        context.user_data['photo'] = photo
        text = (
            "Your report is:"
            f"\n{context.user_data['desc']}"
            "\n"
            "\nTo update your report or image, feel free to send another one."
            "\nTo submit, send /done. To stop, send /cancel"
        )
        update.message.reply_photo(
            photo=photo,
            caption=text)
        return 83

    def report_anything(self, update, context):
        """Change either the photo or the message"""
        if update.message.text:
            desc = update.message.text
            context.user_data['desc'] = desc
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            context.user_data['photo'] = photo

        text = (
            "Your report is:"
            f"\n{context.user_data.get('desc', '')}"
            "\n"
            "\nTo update your report or image, feel free to send another one."
            "\nTo submit, send /done. To stop, send /cancel"
        )

        update.message.reply_photo(
            photo=photo,
            caption=text)
        return 83

    def report_done(self, update, context):
        if context.user_data['photo'] and context.user_data['desc']:
            text = (
                "You have successfully sent a report! A comm member will respond in typically 3-5 working days..."
                "\n"
                "\nTo start a journey, send /rent"
                "\nTo see available bikes, send /bikes"
            )
            update.message.reply_text(text)
            # Update admin group
            admin_username = update.message.from_user.username
            admin_text = f"[REPORT]\n@{admin_username} sent the following report:\n{context.user_data['desc']}"
            self.admin_log(update, context, admin_text, context.user_data['photo'])

            # Update report logs
            curr_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
            self.update_report_log([admin_username, curr_time, context.user_data['desc']])
            context.user_data.clear()
            return -1
        else:
            update.message.reply_text(
                "Sorry, please send both a description and a photo.")

    def report_cancel(self, update, context):
        update.message.reply_text(
            "Report cancelled! Make sure to update us if you spot anything suspicious...")
        context.user_data.clear()
        return -1

    def cancel_command(self, update, context):
        """Used for conversation handlers"""
        update.message.reply_text("Operation successfully cancelled!")
        context.user_data.clear()
        return -1

    def all_handlers(self):
        my_handler = ConversationHandler(
            entry_points = [
                CommandHandler('rent', self.rent_command),
                CommandHandler('routes', self.routes_command),
                CommandHandler('payment', self.payment_command),
                CommandHandler('topup', self.payment_command),
                CommandHandler('return', self.return_command),
                CommandHandler('report', self.report_command),
                CommandHandler('feedback', self.whichevent),
            ],
            states = {
                # 1-X: Rental
                11: [
                    CallbackQueryHandler(self.rent_button),
                    CommandHandler('done', callback=self.rent_done),
                ],
                12: [
                    CallbackQueryHandler(self.terms_button),
                    CommandHandler('done', callback=self.rent_done),
                ],
                13: [
                    MessageHandler(filters=~Filters.command, callback=self.rent_pic),
                    CommandHandler('skip', self.rent_pic),
                    CommandHandler('done', callback=self.rent_done),
                ],

                # 5-X: Routes
                51: [
                    CallbackQueryHandler(self.routes_button),
                    MessageHandler(filters=Filters.text | Filters.command, callback=lambda x, y:-1),
                ],

                # 7-X: Payment
                71: [
                    CallbackQueryHandler(self.payment_button),
                    CommandHandler('done', callback=self.payment_done),
                ],
                72: [
                    CallbackQueryHandler(self.payment_pic),
                    MessageHandler(filters=Filters.photo & ~Filters.command, callback=self.payment_pic),
                    CommandHandler('skip', self.payment_pic),
                    CommandHandler('done', callback=self.payment_done),
                ],

                # 8-X: Reports
                81: [
                    MessageHandler(filters=Filters.text & ~Filters.command, callback=self.report_desc),
                    CommandHandler('done', callback=self.report_done),
                ],
                82: [
                    MessageHandler(filters=Filters.photo & ~Filters.command, callback=self.report_pic),
                    CommandHandler('skip', self.report_pic),
                    CommandHandler('done', callback=self.report_done),
                ],
                83: [
                    MessageHandler(filters=(Filters.text | Filters.photo) & ~Filters.command, callback=self.report_anything),
                    CommandHandler('done', callback=self.report_done),
                ],

                # 9-X: Returns
                91: [
                    MessageHandler(~Filters.command, callback=self.return_pic),
                    CommandHandler('skip', self.return_pic),
                    CommandHandler('done', callback=self.return_done)
                ],

                101: [CallbackQueryHandler(self.whichevent_button)],
                102: [MessageHandler(filters=Filters.text, callback=self.eventrank)],
                103: [CallbackQueryHandler(self.eventlength_button)],
                104: [CallbackQueryHandler(self.eventdifficulty_button)],
                105: [CallbackQueryHandler(self.eventpace_button)],
                106: [MessageHandler(filters=Filters.text, callback=self.bikeservice)],
                107: [MessageHandler(filters=Filters.text, callback=self.placetogo)],
                108: [MessageHandler(filters=Filters.text, callback=self.other)],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel_command),
                # Add entry points, to re-enter the Convo
                CommandHandler('rent', self.rent_command),
                CommandHandler('routes', self.routes_command),
                CommandHandler('payment', self.payment_command),
                CommandHandler('topup', self.payment_command),
                CommandHandler('return', self.return_command),
                CommandHandler('report', self.report_command),
            ],
        )
        return my_handler

    def initialize(self):
        """Initializes all ConversationHandlers for the bot"""
        self.addnew(self.all_handlers())
