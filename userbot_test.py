import unittest, io, sys, os, shutil, json, filecmp, tempfile

from unittest.mock import Mock, patch, PropertyMock

from telegram import ParseMode
from bot_text import START_MESSAGE, HELP_TEXT
from userbot import UserBot
from telebot import TeleBot
import datetime as dt
DEV_API_KEY = "1722354435:AAHRUa4Pph4zjYgNe8PzfsIX1KLzwSJk7Ow"

class TestUserbotMethods(unittest.TestCase):

    USER_DATA = {"user" : "data", "is_ban": False, "chat_id": 00000}
    TABLE_DATA = {"John Doe" : 12345, "testboi": 999999}

    userbot = UserBot(DEV_API_KEY)

    @patch.object(TeleBot, "get_user")
    @patch.object(TeleBot, "update_user")
    @patch.object(TeleBot, "get_user_table")
    @patch.object(TeleBot, "update_user_table")
    def test_start_command(self, mock_update_table, mock_get_table, mock_update, mock_get):
        sample_text = 'This is your orc4bikes friendly neighbourhood bot :)'
        sample_text += "\n"
        sample_text += "\nFor available commands, send /help"
        sample_text += "\nTo use our bikes, /topup now!"

        '''user_data not none, chat id > 0, username not none'''
        mock_get.return_value = "nonNone"
        table = {"John Doe" : 00000, "testboi": 999999}
        mock_get_table.return_value = table
        update = Mock()
        context = Mock()
        update.message.from_user.first_name = "John"
        update.message.from_user.username = "John Doe"
        update.effective_chat.id = 12345
        self.userbot.start_command(update, context)
        test_text = 'Welcome back, John! '
        test_text += sample_text
        context.bot.send_message.assert_called_once_with(chat_id=12345, text=test_text)
        self.assertEqual(table, self.TABLE_DATA)
        mock_update_table.assert_called_once_with(table)
        mock_update_table.reset_mock()

        '''user_data not none, chat id > 0, username none'''
        table = {"John Doe" : 00000, "testboi": 999999}
        mock_get_table.return_value = table
        context = Mock()
        update.message.from_user.username = None
        self.userbot.start_command(update, context)
        test_text = 'Welcome back, John! '
        test_text += sample_text
        context.bot.send_message.assert_called_once_with(chat_id=12345, text=test_text)
        self.assertEqual(table, {"John Doe" : 00000, "testboi": 999999})
        mock_update_table.assert_called_once_with({"John Doe" : 00000, "testboi": 999999})
        mock_update_table.reset_mock()
        mock_get_table.reset_mock()

        '''user_data not none, chat id < 0'''
        table = {"John Doe" : 00000, "testboi": 999999}
        mock_get_table.return_value = table
        update.effective_chat.id = -12
        context = Mock()
        update.message.from_user.username = None
        self.userbot.start_command(update, context)
        test_text = 'Welcome back, John! '
        test_text += sample_text
        context.bot.send_message.assert_called_once_with(chat_id=-12, text=test_text)
        self.assertEqual(table, {"John Doe" : 00000, "testboi": 999999})
        mock_update_table.assert_not_called()
        mock_get_table.assert_not_called()

        '''user_data none, chat id > 0'''
        mock_get.return_value = None
        table = {"testboi": 999999}
        test_data = {'chat_id': 12345,
                            'first_name': "John",
                            'last_name' : "Doe",
                            'username':   "John Doe",
                            'credits': 0,
                            'finance':[],
                            'log':[],
                            'bike_name':'',
                            'status':None,
                            }
        mock_get_table.return_value = table
        update = Mock()
        context = Mock()
        update.message.from_user.first_name = "John"
        update.message.from_user.last_name = "Doe"
        update.message.from_user.username = "John Doe"
        update.effective_chat.id = 12345
        self.userbot.start_command(update, context)
        test_text = 'Hello, John! '
        test_text += sample_text
        context.bot.send_message.assert_called_once_with(chat_id=12345, text=test_text)
        self.assertEqual(table, self.TABLE_DATA)
        mock_update_table.reset_mock()
        mock_get_table.reset_mock()
        mock_update.reset_mock()

        '''user_data none, chat id < 0'''
        table = {"testboi": 999999}
        update.effective_chat.id = 0
        mock_get_table.return_value = table
        context = Mock()
        update.message.from_user.username = "John Doe"
        self.userbot.start_command(update, context)
        test_text = 'Hi @John Doe, please start the bot privately, and not in groups!!'
        context.bot.send_message.assert_called_once_with(chat_id=0, text=test_text)
        mock_update.assert_not_called()
        mock_update_table.assert_not_called()
        mock_get_table.assert_not_called()

'''
    def test_help_command(self):
        update = Mock()
        update.effective_chat.id = 12
        context = Mock()
        self.userbot.help_command(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12,
            text = HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN)
            '''


if __name__ == '__main__':
    unittest.main()