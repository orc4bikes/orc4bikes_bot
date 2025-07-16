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
from bots.feedbackbot import FeedbackBot

from src.admin import (
    BOT_DEDUCT_RATE,
)

from src.functions import to_readable_td

logger = logging.getLogger()

class Orc4bikesBot(ConvoBot, AdminBot, UserBot, FeedbackBot, FunBot, TeleBot):

    def calc_deduct(self, time_diff):
        """Calculate credits deductable given a time period."""
        deduction = time_diff.seconds // BOT_DEDUCT_RATE + int(time_diff.seconds % BOT_DEDUCT_RATE > 0)
        deduction += time_diff.days * 86400 / BOT_DEDUCT_RATE
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
        query.edit_message_text(
            f"{query.message.text_html}"
            "\n\n<i>Sorry, this button has expired. Please send the previous command again.</i>",
            parse_mode='HTML')

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
            status_text += "\n\n""Please remember to /return your bike with /return! Check your bike status with /status."
            context.bot.send_message(
                chat_id=chat_id,
                text=status_text)
            # context.bot.send_message(
            #     chat_id=chat_id,
            #     text="")

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
        TeleBot.initialize(self)      # Base Telegram Bot
        UserBot.initialize(self)      # All user commands
        ConvoBot.initialize(self)     # All conversation handlers
        AdminBot.initialize(self)     # All admin commands
        FunBot.initialize(self)       # Fun commands
        FeedbackBot.initialize(self)  # Feedback commands
        self.scheduler()              # Scheduler

        # Check if user sends converation commands outside of ConversationHandler (ConvoBot)
        self.addcmd('cancel', self.convo_outside_command)
        self.addcmd('done', self.convo_outside_command)

        # Lastly, Filters all unknown commands, and remove unrecognized queries
        self.addmsg(Filters.command, self.unrecognized_command)
        self.addnew(CallbackQueryHandler(self.unrecognized_buttons))

    def main(self):
        """Main bot function to run"""
        TeleBot.main(self)

if __name__ == '__main__':
    newbot = Orc4bikesBot()
    newbot.main()
