from bot_text import (
    ROUTES_LIST,
    ROUTES_PICS,
    CHEER_LIST,
    HELP_TEXT,
    FUN_TEXT,
    ADMIN_TEXT,
    START_MESSAGE,
    EMOJI,
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


class FunBot(TeleBot):
    def __init__(self,
        api_key):
        super().__init__(api_key)
            #fun stuff

    def fun_command(self,update,context):
        """Shows you guide to renting bike"""
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = FUN_TEXT,
            )

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
            self.log_exception(e,"Error with quote_command")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=random.choice(CHEER_LIST)
            )

    def pika_command(self,update,context):
        """Sends a pikachu sticker"""
        try:
            if random.random() < 0.01:
                return context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Pika... boo? 🙂"
                )
            pika_list = [
                'pikachu',
                'pikachu2',
                'PikachuDetective',
                'pikachu6',
                'pikach',
                'pikach_memes'
                ]
            pikas = []
            for pika in pika_list:
                pikas.extend(context.bot.get_sticker_set(pika).stickers)
            pikas.extend(context.bot.get_sticker_set('uwumon').stickers[:20])
            pika = random.choice(pikas)
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=pika
            )
        except Exception as e:
            self.log_exception(e,"Error with pika_command")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Pika... boo? 🙂"
            )

    def brawl_command(self,update,context):
        """Sends a brawl stars sticker"""
        try:
            brawls = context.bot.get_sticker_set('BrawlStarsbyHerolias')
            brawl = random.choice(brawls.stickers)
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=brawl
            )
        except Exception as e:
            self.log_exception(e,"Error with brawl_command")

    def bangday_command(self,update,context):
        """Sends a bang don sticker"""
        try:
            bangdongs = context.bot.get_sticker_set('happybangday')
            bangdong = random.choice(bangdongs.stickers)
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=bangdong
            )
        except Exception as e:
            self.log_exception(e,"Error with bangday_command")

    def ohno_command(self,update,context):
        """Sends a version of "Oh no"..."""
        text = random.choice([
            "OH NO!",
            "Oh no indeed...",
            "Oh no",
            "Ah, that is not ideal",
            "This is a pleasant surprise without the pleasant",
            "Goodness gracious me!",
            "Oh noes",
            "Das not good",
            "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaah",
            "How could this happen?!",
            "This calls for an 'Oh no'.",
            "F in the chat",
            "What did you do!?",
            "Seriously...",
            "ono",
            "FSKSJFLKSDJFH",
            "My condolences",
            "Rest in peace good sir",
            "ohhh myyy gawwwd",
            "OMG!",
            "oh no",
            "oh no...?",
            "Bless you",
            "Are you sure you didn't mean 'Oh yes'?",
            "This is truly a disaster",
            "...",
            ])
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)

    def initialize(self):
        self.addcmd('fun', self.fun_command)
        self.addcmd('doggo', self.doggo_command)
        self.addcmd('neko', self.neko_command)
        self.addcmd('kitty', self.kitty_command)
        self.addcmd('birb', self.birb_command)
        self.addcmd('shibe', self.shibe_command)
        self.addcmd('foxy', self.foxy_command)  
        self.addcmd('random', self.random_command) 

        self.addcmd('animal',self.animal_command)

        self.addcmd('pika', self.pika_command) #pika sticker
        self.addcmd('brawl', self.brawl_command) #brawl sticker
        self.addcmd('happybangday', self.bangday_command) #bangday sticker

        self.addcmd('ohno',self.ohno_command)

        #self.addcmd('quote', self.quote_command)   #doesnt work on web...

