from datetime import datetime, timedelta
from decimal import Decimal
import logging

from telegram.ext import (
    CallbackQueryHandler,
    Filters,
)

from bots.telebot import TeleBot
from bots.funbot import FunBot
from bots.adminbot import AdminBot
from bots.userbot import UserBot
from bots.convobot import ConvoBot

from admin import (
    DEV_ADMIN_GROUP_ID,
    ADMIN_LIST,
    TELE_API_TOKEN,
)

from bot_text import (
    HELP_TEXT,
    ADMIN_TEXT,
    TERMS_TEXT,
)

from functions import to_readable_td

logger = logging.getLogger()

class Orc4bikesBot(ConvoBot, AdminBot, UserBot, FunBot, TeleBot):
    DEDUCT_RATE = 20  # deduct 1 credit every 20 seconds or part thereof

    def __init__(
            self,
            api_key,
            admin_group_id=DEV_ADMIN_GROUP_ID,
            help_text=HELP_TEXT,
            admin_list=ADMIN_LIST,
            admin_text=ADMIN_TEXT,
            deduct_rate=DEDUCT_RATE,
            terms_text=TERMS_TEXT,
            promo=False):
        logger.info("running Orc4bikesBot now")
        super().__init__(api_key)
        self.help_text = help_text
        self.admin_group_id = admin_group_id
        self.admin_list = admin_list
        self.admin_text = admin_text
        self.deduct_rate = deduct_rate
        self.terms_text = terms_text
        self.promo = promo

    def calc_deduct(self, time_diff):
        """Calculate credits deductable given a time period."""
        deduction = time_diff.seconds // self.deduct_rate + int(time_diff.seconds % self.deduct_rate > 0)
        deduction += time_diff.days * 86400 / self.deduct_rate
        return Decimal(deduction)

    def echo_command(self, update, context):
        update.message.reply_text(update.message.text)

    def convo_outside_command(self, update, context):
        """Inform user when update occurs outside of a ConversationHandler."""
        update.message.reply_text("This command was a little out of place...")
        context.user_data.clear()
        return -1

    def dummy_command(self, update, context):
        update.message.reply_text("This feature will be added soon! Where art thou, bikes...?")

    def unrecognized_command(self, update, context):
        """Inform user when command is unrecognized."""
        update.message.reply_text("Unrecognized command. Send /help for available commands.")

    def unrecognized_buttons(self, update, context):
        """Edit query so the user knows button is not accepted."""
        query = update.callback_query
        query.answer()
        text = query.message.text
        text += "\n\nSorry, this button has expired. Please send the previous command again."
        query.edit_message_text(text)

    def reminder(self, context):
        """Callback Reminder for return, every hour"""
        bikes_data = self.get_bikes()
        for bike_data in bikes_data:
            username = bike_data['username']
            if not username:
                continue

            chat_id = self.get_user_id(username)
            user_data = self.get_user(username=username)
            status = user_data['status']
            start = datetime.fromisoformat(status)
            curr = self.now()
            diff = curr - start
            readable_diff = to_readable_td(diff)
            status_text = f"You have been renting {user_data['bike_name']} for {readable_diff}."
            deduction = self.calc_deduct(diff)
            status_text += (
                f"\n\nCREDITS:"
                f"\nCurrent: {user_data['credits']}"
                f"\nThis trip: {deduction}"
                f"\nProjected final: {user_data['credits'] - deduction}"
            )
            context.bot.send_message(
                chat_id=chat_id,
                text=status_text)
            context.bot.send_message(
                chat_id=chat_id,
                text="Please remember to /return your bike! Check your bike status with /status.")

    def scheduler(self):
        """Scheduler for reminder to be run"""
        job_queue = self.updater.job_queue
        logger.debug('getting daily queue')

        job_queue.run_repeating(
            callback=self.reminder,
            interval=timedelta(hours=1))

    def initialize(self):
        """Initializes all CommandHandlers, MessageHandlers,
        and job_queues that are required in the bot.
        """
        # Initialize parent classes first
        TeleBot.initialize(self)   # Base Telegram Bot
        UserBot.initialize(self)   # All user commands
        ConvoBot.initialize(self)  # All conversation handlers
        AdminBot.initialize(self)  # All admin commands
        FunBot.initialize(self)    # Fun commands

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

if __name__ == '__main__':
    newbot = Orc4bikesBot(TELE_API_TOKEN, admin_group_id=DEV_ADMIN_GROUP_ID)
    newbot.main()
