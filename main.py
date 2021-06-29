import random
#import os
import requests
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import ConversationHandler

#import logging


API_KEY = '1722354435:AAHAFxP6_sIf_P4hdQJ7Y5EsH64PtyWwWo8'

routes_list = ["From RC4 B1 to Utown",
               "From RC4 Level 1 to Utown",
               "From RC4 to Clementi",
               "From RC4 to Utown (Sheltered)",
               "From RC4 to RC4",
               ]
cheer_list = ["","Cheer up!",
              "Ganbatte!",
              "Hwaiting!",
              "Jiayou!",
              "You got this!",
              ]

updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)

def start_command(update,context):
    """Initializes the bot"""
    text =  'Hello '+update.message.from_user.first_name+', this is your Orcabikes friendly neighbourhood bot :)'
    text += "\nFor more info, send /help"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

start_handler = CommandHandler('start', start_command)
dispatcher.add_handler(start_handler)

def help_command(update,context):
    """Show a list of possible commands"""
    text = """List of commands:
/start - Initializes the bot
/help - Get all available commands
/routes - Get Orcabikes routes
/doggo - Get a random dog!
/neko - Get a random cat!
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = text)

help_handler = CommandHandler('help', help_command)
dispatcher.add_handler(help_handler)

def routes_command(update,context):
    """Returns all routes from the list of routes"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Here are some available routes for you!"
        )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='\n'.join(routes_list)
        )
routes_handler = CommandHandler('routes', routes_command)
dispatcher.add_handler(routes_handler)


def doggo_command(update,context):
    """Shows you a few cute dogs!"""
    url = requests.get('https://random.dog/woof.json').json()['url']
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        caption = random.choice(cheer_list),
        photo = url
        )
    
def neko_command(update,context):
    """Shows you a few cute cats!"""
    url = requests.get('https://aws.random.cat/meow').json()['file']
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        caption = random.choice(cheer_list),
        photo = url
        )

doggo_handler = CommandHandler('doggo',doggo_command)
dispatcher.add_handler(doggo_handler)

neko_handler = CommandHandler('neko',neko_command)
dispatcher.add_handler(neko_handler)


updater.start_polling()
#print('started')
#updater.idle()



"""
### OLD CODE FOR REFERENCE
def echo(update, context):
    chat_id = update.message.chat.id
    text = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

def history(update, context):
    text = 'Here is question history\n'+'\n'.join(context.chat_data['history']) if context.chat_data.get('history') else 'There is no history!'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    
history_handler = CommandHandler('history',history)
dispatcher.add_handler(history_handler)



def ask(update, context):
    chat_id = update.message.chat.id
    query = update.message.text

    if not context.chat_data.get('history'):
        context.chat_data['history'] = [query.replace('/ask ','')]
    else:
        context.chat_data['history'].append(query.replace('/ask ',''))

    text = "Thank you for asking! Honestly, I don't know..."
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


ask_handler = CommandHandler('ask', ask)
dispatcher.add_handler(ask_handler)

"""
