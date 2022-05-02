import logging
import random
import requests
from requests.exceptions import RequestException
from simplejson.errors import JSONDecodeError

from telegram import (
    ChatAction,
)

from bots.telebot import TeleBot

from bot_text import (
    CHEER_LIST,
    FUN_TEXT,
    OHNO_LIST,
    FUN_URLS,
)

logger = logging.getLogger()

class FunBot(TeleBot):
    def __init__(self, api_key):
        super().__init__(api_key)

    def fun_command(self, update, context):
        """Show user list of fun commands."""
        update.message.reply_text(FUN_TEXT)

    def get_pic_url(self, l):
        """Repeated tries a list of URLs"""
        while len(l) != 0:
            url, key = l.pop(0)
            try:
                img_url = requests.get(url).json()[key]
                return img_url
            except (RequestException, JSONDecodeError) as e:
                logger.exception(e)
        return None

    def chat_action(action):
        def decorator(func):
            def new_func(self, update, context, *args, **kwargs):
                update.message.reply_chat_action(action)
                return func(self, update, context, *args, **kwargs)
            return new_func
        return decorator


    def send_user(
            self, update, context, *,
            pic_url,
            caption,
            error_text):
        """Replies user with either a photo or an error message"""
        if not pic_url:
            update.message.reply_text(error_text)
            return

        update.message.reply_photo(
            photo=pic_url,
            caption=caption)

    @chat_action(ChatAction.TYPING)
    def doggo_command(self, update, context):
        """Shows you a few cute dogs!"""
        pic_url = self.get_pic_url(FUN_URLS['dog'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, all the dogs are out playing... Please try again later!")

    @chat_action(ChatAction.TYPING)
    def shibe_command(self, update, context):
        """Shows you a few cute shibe!"""
        pic_url = self.get_pic_url(FUN_URLS['shibe'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, doge is doge... Please try again later!")

    @chat_action(ChatAction.TYPING)
    def neko_command(self, update, context):
        """Shows you a few cute cats!"""
        pic_url = self.get_pic_url(FUN_URLS['neko'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, all the cats are asleep... Please try again later!")

    @chat_action(ChatAction.TYPING)
    def kitty_command(self, update, context):
        """Shows you a few cute kittens!"""
        pic_url = self.get_pic_url(FUN_URLS['cat'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, all the cats are asleep... Please try again later!")

    @chat_action(ChatAction.TYPING)
    def foxy_command(self, update, context):
        """Shows you a few cute foxes!"""
        pic_url = self.get_pic_url(FUN_URLS['fox'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, all the foxes are asleep... Please try again later!")

    @chat_action(ChatAction.TYPING)
    def birb_command(self, update, context):
        """Shows you a few cute birbs!"""
        pic_url = self.get_pic_url(FUN_URLS['bird'])
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Sorry, the birbs flew away... Please try again later!")

    def get_random_pic(self):
        return self.get_pic_url(random.choice(list(FUN_URLS.values())))

    @chat_action(ChatAction.TYPING)
    def random_command(self, update, context):
        """Sends a random animal!"""
        pic_url = self.get_random_pic()
        self.send_user(
            update, context,
            pic_url=pic_url,
            caption=random.choice(CHEER_LIST),
            error_text="Hmm, I can't seem to find any animals... Maybe they're all asleep?")

    @chat_action(ChatAction.CHOOSE_STICKER)
    def pika_command(self, update, context):
        """Sends a pikachu sticker"""
        if random.random() < 0.1:
            update.message.reply_text("Pika... boo? 🙂")
            return
        PIKA_LIST = [
            'pikachu',
            'pikachu2',
            'PikachuDetective',
            'pikachu6',
            'pikach',
            'pikach_memes',
        ]
        pikas = []
        for pika in PIKA_LIST:
            pikas.extend(context.bot.get_sticker_set(pika).stickers)
        pikas.extend(context.bot.get_sticker_set('uwumon').stickers[:20])
        pika = random.choice(pikas)
        update.message.reply_sticker(sticker=pika)

    def quote_command(self, update, context):
        """Sends an inspirational quote"""
        try:
            url = requests.get('https://type.fit/api/quotes').json()
        except RequestException as e:
            logger.exception(e)
            update.message.reply_text(random.choice(CHEER_LIST))
        else:
            url = random.choice(url)
            update.message.reply_text(
                f'"{url["text"]}" - {url["author"]}')

    @chat_action(ChatAction.CHOOSE_STICKER)
    def brawl_command(self, update, context):
        """Sends a brawl stars sticker"""
        brawls = context.bot.get_sticker_set('BrawlStarsbyHerolias')
        brawl = random.choice(brawls.stickers)
        update.message.reply_sticker(sticker=brawl)

    @chat_action(ChatAction.CHOOSE_STICKER)
    def bangday_command(self, update, context):
        """Sends a bang don sticker"""
        bangdongs = context.bot.get_sticker_set('happybangday')
        bangdong = random.choice(bangdongs.stickers)
        update.message.reply_sticker(sticker=bangdong)

    def ohno_command(self, update, context):
        """Sends a version of "Oh no"..."""
        text = random.choice(OHNO_LIST)
        update.message.reply_text(text)
        raise ZeroDivisionError  # This function is now for testing

    def initialize(self):
        self.addcmd('fun', self.fun_command)
        self.addcmd('doggo', self.doggo_command)
        self.addcmd('neko', self.neko_command)
        self.addcmd('kitty', self.kitty_command)
        self.addcmd('birb', self.birb_command)
        self.addcmd('shibe', self.shibe_command)
        self.addcmd('foxy', self.foxy_command)
        self.addcmd('random', self.random_command)

        self.addcmd('pika', self.pika_command)             # pika sticker
        self.addcmd('brawl', self.brawl_command)           # brawl sticker
        self.addcmd('happybangday', self.bangday_command)  # bangday sticker

        self.addcmd('ohno', self.ohno_command)

        #self.addcmd('quote', self.quote_command)          # doesnt work on web...
