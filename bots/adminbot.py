from datetime import datetime
import logging

from telegram import (
    ChatAction,
)

from bots.telebot import TeleBot

from admin import (
    ADMIN_GROUP_ID,
    ADMIN_LIST,
    ADMIN_DEV,
    TELE_API_TOKEN,
)

from bot_text import (
    ADMIN_TEXT,
    EMOJI,
)

from functions import to_readable_td

logger = logging.getLogger()

class NotEnoughKeywords(ValueError):
    pass
class NotANumber(ValueError):
    @property
    def value(self):
        return self.args[0]
class NoSuchBike(KeyError):
    @property
    def bike_name(self):
        return self.args[0]
class NoSuchUser(KeyError):
    @property
    def username(self):
        return self.args[0]

def keywords_check(keywords, n):
    if len(keywords) < n:
        raise NotEnoughKeywords()

def to_int(n):
    if not n.isnumeric():
        raise NotANumber(n)
    return int(n)

class AdminBot(TeleBot):

    def admin_log(self, update, context, message, photo=None):
        """Send logs to admin chat group"""
        if photo:
            context.bot.send_photo(
                chat_id=ADMIN_GROUP_ID,
                photo=photo,
                caption=message)
        else:
            context.bot.send_message(
                chat_id=ADMIN_GROUP_ID,
                text=message)



    def get_and_check_user(self, username):
        # Used by user commands: addcredit, deduct, setcredit, user, ban, unban
        user_data = self.get_user(username=username)
        if user_data is None:
            raise NoSuchUser(username)
        return user_data

    def get_and_check_bike(self, bike_name):
        # Used by bike commands: setpin, setstatus, forcereturn
        bike = self.get_bike(bike_name)
        if bike is None:
            raise NoSuchBike(bike_name)
        return bike


    def admin_only(func):
        def new_func(self, update, context, *args, **kwargs):
            """Checks whether the user is an admin, and more"""
            username = update.effective_chat.username
            if username is None:
                username = update.message.from_user.username

            if username not in ADMIN_LIST:
                update.message.reply_text("You've found... something unauthorized? "
                                          "Please contact a orc4bikes committee member or an admin for help!")
                return

            try:
                return func(self, update, context, *args, **kwargs)
            except NotEnoughKeywords as e:
                update.message.reply_text(
                    "Sorry, too little info provided."
                    "\nPlease refer to the format and send more info.")
            except NotANumber as e:
                update.message.reply_text(
                    f"Number entered, {e.value}, is not valid!")
            except NoSuchUser as e:
                update.message.reply_text(
                    "Specified user is not found!"
                    f" Please ask @{e.username} to create an account first."
                    "\nNote: Please do NOT add @ before a username, usernames are case sensitive")
            except NoSuchBike as e:
                update.message.reply_text(
                    f"No such bike, {e.bike_name}, exists. Please try again with current /bikes")
            except (KeyError, FileNotFoundError) as e:
                logger.exception(e)
                update.message.reply_text(
                    "Oops, this is embarrasing, an unexpected error has occurred."
                    f" Please raise a ticket with @{ADMIN_DEV}, along with what you sent.")
        return new_func

    @admin_only
    def admin_command(self, update, context):
        update.message.reply_markdown_v2(ADMIN_TEXT)

    def change_credits(self, username, user_data, change, admin_name):
        initial_amt = user_data['credits']
        user_data['credits'] += change
        final_amt = initial_amt + change

        # update user data
        user_data['finance'] = user_data.get('finance',[])
        f_log = {
            'type': 'admin',
            'time': self.now().strftime("%Y/%m/%d, %H:%M:%S"),
            'initial': initial_amt,
            'change': change,
            'final': final_amt
        }
        user_data['finance'].append(f_log)
        self.update_user(user_data)

        finance_log = [
            username,
            self.now().strftime("%Y/%m/%d, %H:%M:%S"),
            initial_amt, change, final_amt,
            admin_name
        ]
        self.update_finance_log(finance_log)

    @admin_only
    def deduct_command(self, update, context):
        """Deduct specific amount from user credits"""
        keywords_check(context.args, 2)
        update.message.reply_chat_action(ChatAction.TYPING)
        username, number = context.args
        user_data = self.get_and_check_user(username)
        number = to_int(number)
        admin_name = update.message.from_user.username
        self.change_credits(username, user_data, -number, admin_name)
        update.message.reply_text(
            f"Deducted successfully! @{username} now has {user_data['credits']} credits.")


    @admin_only
    def addcredit_command(self, update, context):
        """Topup specific amount to user credits"""
        keywords_check(context.args, 2)
        update.message.reply_chat_action(ChatAction.TYPING)
        username, number = context.args
        user_data = self.get_and_check_user(username)
        number = to_int(number)
        self.change_credits(
            username, user_data,
            change=number,
            admin_name=update.message.from_user.username)
        update.message.reply_text(
            f"Top-up successful! @{username} now has {user_data['credits']} credits.")


    @admin_only
    def setcredit_command(self, update, context):
        """Set user credits to specified amount."""
        keywords_check(context.args, 2)
        update.message.reply_chat_action(ChatAction.TYPING)
        username, number = context.args
        user_data = self.get_and_check_user(username)
        initial_amt = user_data['credits']
        number = to_int(number)
        self.change_credits(
            username, user_data,
            change=number - initial_amt,
            admin_name=update.message.from_user.username)
        update.message.reply_text(
            f"Setting was successful! @{username} now has {user_data['credits']} credits.")


    @admin_only
    def user_command(self, update, context):
        keywords_check(context.args, 1)
        update.message.reply_chat_action(ChatAction.TYPING)
        username = context.args[0]
        user_data = self.get_and_check_user(username)

        text = f"@{user_data['username']} has {user_data.get('credits', 0)} credits left.\n"
        if user_data['bike_name']:
            time = datetime.fromisoformat(user_data['status']).strftime("%Y/%m/%d, %H:%M:%S")
            text += f"User has been renting {user_data['bike_name']} since {time}"
        else:
            text += "User is not renting currently."
        update.message.reply_text(text)

    @admin_only
    def setpin_command(self, update, context):
        keywords_check(context.args, 2)
        update.message.reply_chat_action(ChatAction.TYPING)
        bike_name, number = context.args
        bike = self.get_and_check_bike(bike_name)

        if bike['pin'] == number:
            update.message.reply_text(
                f'Old pin is the same as {number}!')
            return

        bike['oldpin'] = bike['pin']
        bike['pin'] = number
        self.update_bike(bike)
        update.message.reply_text(
            f"Pin for {bike_name} updated to {number}!")

    @admin_only
    def orcabikes_command(self, update, context):
        update.message.reply_chat_action(ChatAction.TYPING)
        if len(context.args) == 0:
            bikes_data = self.get_bikes()
            text = '\n'.join(
                (
                    f"{bike['name']} -- {bike['username'] or bike['status'] or EMOJI['tick']}"
                    f" (Pin: {bike['pin']})"
                    f" {EMOJI['msg'] if bike['message'] else ''}"
                )
                for bike in bikes_data)
            text += (
                f"\n\nBikes with {EMOJI['msg']} indicates a custom message is shown to user when they begin rental."
                "\nUse /orcabikes <code>BIKENAME</code> show the message and for more info."
            )
            update.message.reply_html(text)
            return

        bike_name = context.args[0]
        bike = self.get_and_check_bike(bike_name)

        if len(context.args) == 1:
            if not bike['message']:
                text = f"{bike_name} has no message."
            else:
                text = (
                    f"{bike_name}'s message:"
                    f"\n{bike['message']}"
                )

            text += "\n\nSend /orcabikes <code>BIKENAME</code> <code>MESSAGE</code> to update the bike's message!"
            if bike['message']:
                text += "\nSend /orcabikes <code>BIKENAME</code> remove to remove the bike's message."

            update.message.reply_html(text)
            return

        userinput = ' '.join(context.args[1:])
        if userinput == 'remove':
            bike['message'] = None
            self.update_bike(bike)
            update.message.reply_text(
                f"Alrights, no message will be shown when users rent {bike_name}.")
            return

        bike['message'] = userinput
        self.update_bike(bike)
        update.message.reply_text(
            f"{bike_name}'s message successfully updated! Users will now see this message:"
            f"\n{userinput}")


    @admin_only
    def setstatus_command(self, update, context):
        keywords_check(context.args, 1)
        update.message.reply_chat_action(ChatAction.TYPING)
        bike_name, *status = context.args
        bike = self.get_and_check_bike(bike_name)
        status = ' '.join(status) if status != [] else 0

        rented = bike.get('username', "")
        if rented != '':
            update.message.reply_text(f"Bike is rented by {rented}!")
            return

        if status == '0':  # to reset the status to 0
            status = int(status)
        bike['status'] = status
        self.update_bike(bike)
        update.message.reply_text(
            f"Status for {bike_name} updated to {status}!")

    @admin_only
    def logs_command(self, update, context):
        update.message.reply_text(
            f"This feature is temporarily unavailable. Please complain to @{ADMIN_DEV} if you want the feature!")

        # context.bot.send_document(
        #     chat_id=update.effective_chat.id,
        #     document=open('database/logs/rental.csv','rb'),
        #     filename="rental.csv",
        #     caption="Rental logs"
        # )
        # context.bot.send_document(
        #     chat_id=update.effective_chat.id,
        #     document=open('database/logs/report.csv','rb'),
        #     filename="report.csv",
        #     caption="Report logs"
        # )
        # context.bot.send_document(
        #     chat_id=update.effective_chat.id,
        #     document=open('database/logs/finance.csv','rb'),
        #     filename="finance.csv",
        #     caption="Finance logs"
        # )


    @admin_only
    def forcereturn_command(self, update, context):
        keywords_check(context.args, 1)
        update.message.reply_chat_action(ChatAction.TYPING)
        bike_name = context.args[0]
        bike = self.get_and_check_bike(bike_name)

        username = bike.get('username', "")
        if not username:
            update.message.reply_text("Bike not on rent! Please try again.")
            return

        user_data = self.get_and_check_user(username)

        status = user_data['status']
        if not status:
            update.message.reply_text(
                f"Something seems wrong... The bike {bike_name} tagged to user @{username}, but user is not renting???")
        diff = self.now() - datetime.fromisoformat(status)
        readable_diff = to_readable_td(diff)
        d = {
            'start': status,
            'end': self.now().isoformat(),
            'time': readable_diff,
        }
        deduction = self.calc_deduct(diff)

        # update return logs
        bike = self.get_bike(bike_name)
        start_time = datetime.fromisoformat(bike['status']).strftime('%Y/%m/%d, %H:%M:%S')
        end_time = self.now().strftime('%Y/%m/%d, %H:%M:%S')
        self.update_rental_log([bike_name, username, start_time, end_time, deduction])

        # update bike first, because bike uses user_data.bike_name
        bike['status'] = 0
        bike['username'] = ""
        self.update_bike(bike)

        # update user data
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
        super().update_user(user_data)

        admin_username = update.message.from_user.username
        context.bot.send_message(
            chat_id=int(user_data['chat_id']),
            text=f"An admin, @{admin_username} has returned your bike for you! Your total rental time is {readable_diff}.")
        deduction_text = f"{deduction} credits was deducted. Remaining credits: {user_data['credits']}"
        user_text = deduction_text + "\nIf you have any queries, please ask a comm member for help."
        context.bot.send_message(
            chat_id=int(user_data['chat_id']),
            text=user_text)
        # Notify Admin group
        admin_text = (
            "[RENTAL - RETURN]"
            f"\n@{user_data['username']} returned {bike_name} at following time:"
            f"\n{self.now().strftime('%Y/%m/%d, %H:%M:%S')}"
            f"\nThis return was force-returned by @{admin_username}.\n{deduction_text}"
        )
        self.admin_log(update, context, admin_text)


    @admin_only
    def ban_command(self, update, context):
        """Ban a user"""
        keywords_check(context.args, 1)
        update.message.reply_chat_action(ChatAction.TYPING)
        username = context.args[0]
        user_data = self.get_and_check_user(username)

        is_banned = user_data.get('is_ban')
        if is_banned:
            update.message.reply_text(f"@{username} is already banned.")
            return

        user_data['is_ban'] = True
        self.update_user(user_data)
        update.message.reply_text(f"@{username} is now BANNED.")

    @admin_only
    def unban_command(self, update, context):
        """Unban a user"""
        keywords_check(context.args, 1)
        update.message.reply_chat_action(ChatAction.TYPING)
        username = context.args[0]
        user_data = self.get_and_check_user(username)

        is_banned = user_data.get('is_ban')
        if not is_banned:
            update.message.reply_text(f"@{username} is already not banned.")
            return

        user_data['is_ban'] = None
        self.update_user(user_data)
        update.message.reply_text(f"@{username} is now UNBANNED.")

    @admin_only
    def getchatid_command(self, update, context):
        """Hidden Command: Get the current chat ID - useful for setting up admin group"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = getattr(update.effective_chat, 'title', 'N/A')
        
        text = f"Chat ID: `{chat_id}`\n"
        text += f"Chat Type: {chat_type}\n"
        if chat_title != 'N/A':
            text += f"Chat Title: {chat_title}\n"
        text += f"\nUse this ID in your ADMIN_GROUP_ID environment variable."
        
        update.message.reply_markdown(text)

    def initialize(self):
        """Initialze all admin commands"""
        self.addcmd('admin', self.admin_command)

        self.addcmd('user', self.user_command)
        self.addcmd('addcredit', self.addcredit_command)
        self.addcmd('deduct', self.deduct_command)
        self.addcmd('ban', self.ban_command)
        self.addcmd('unban', self.unban_command)
        self.addcmd('setcredit', self.setcredit_command)

        self.addcmd('orcabikes', self.orcabikes_command)
        self.addcmd('setpin', self.setpin_command)
        self.addcmd('setstatus', self.setstatus_command)
        self.addcmd('forcereturn', self.forcereturn_command)

        self.addcmd('logs', self.logs_command)
        self.addcmd('getchatid', self.getchatid_command)

    def main(self):
        super().main()

if __name__ == '__main__':
    logger.info('Running the AdminBot!')
    newbot = AdminBot(TELE_API_TOKEN)
    newbot.main()
