import os, sys

from telegram import BotCommand
from telegram.ext import Updater

# Hack to import from directory one level up, because this script is not in root directory of module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.admin import TELE_API_TOKEN
from src.bot_text import BOT_COMMANDS


def update_desc():
    """Update descriptions of the commands of the bot."""
    commands = [
        BotCommand(x[0], x[1].strip())
        for x in map(lambda x: x.split(' ', maxsplit=1), BOT_COMMANDS.strip().splitlines())
    ]
    updater.bot.set_my_commands(commands)

def wrapper(context):
    update_desc()
    os._exit(0)  # Can't find another way to prevent SystemExit from being caught

if __name__ == '__main__':
    updater = Updater(token=TELE_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    updater.job_queue.run_once(wrapper, 0)
    updater.start_polling()
    updater.idle()
