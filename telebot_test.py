import unittest, io, sys, os, shutil, json, filecmp, tempfile

from unittest.mock import Mock, patch
from telebot import TeleBot
import datetime as dt
DEV_API_KEY = "1722354435:AAHRUa4Pph4zjYgNe8PzfsIX1KLzwSJk7Ow"

from bot_text import (
    START_MESSAGE,
    BAN_MESSAGE,
)

class TestTelebotMethods(unittest.TestCase):

    telebot = TeleBot(DEV_API_KEY)
    LOG_EXCEPTION_ERRORMESSAGE = "Error occured at {}. Error is \n{}\n"
    TEST_ERROR_1 = ValueError
    TEST_ERROR_2 = IndexError
    USER_FILE = 'table.json'
    BIKE_FILE = 'bike.json'
    INVALID_PATH = 'invalid/invalid_dump'
    TABLE_DATA = {"test": 123345, "test2": 1123345}
    USER_DATA = {"user" : "data", "is_ban": False}
    USER_DATA_BANNED = {"user" : "data", "is_ban": True, "chat_id": 123}
    BIKE_DATA = {"orc3bike": {
        "colour": "blue",
        "name": "orc3bike",
        "oldpin": "12345",
        "pin": "00000",
        "status": "Maintenance",
        "type": "mountain",
        "username": ""
      },
                 "orc5bike": {
        "colour": "yellow",
        "name": "orc5bike",
        "oldpin": "12345",
        "pin": "00000",
        "status": 0,
        "type": "mountain",
        "username": ""
      }
    }

    def test_log_exception(self):
        '''Without optional input'''
        capturedOutput = io.StringIO()      
        sys.stdout = capturedOutput                   
        self.telebot.log_exception(self.TEST_ERROR_1)                                    
        sys.stdout = sys.__stdout__  
        self.assertAlmostEqual(capturedOutput.getvalue(), 
            self.LOG_EXCEPTION_ERRORMESSAGE.format(dt.datetime.now(), self.TEST_ERROR_1))

        '''With additional input'''
        capturedOutput = io.StringIO()      
        sys.stdout = capturedOutput 
        self.telebot.log_exception(self.TEST_ERROR_2, "~")                                    
        sys.stdout = sys.__stdout__  
        self.assertAlmostEqual(capturedOutput.getvalue(), "~\n" 
            + self.LOG_EXCEPTION_ERRORMESSAGE.format(dt.datetime.now(), self.TEST_ERROR_2))

    def test_update_user_table(self):
        '''Empty folder path'''
        outfile_path = tempfile.mkdtemp()
        try:
          self.telebot.update_user_table({}, outfile_path)
          with open(f'{outfile_path}/{self.USER_FILE}', 'r') as f:
              table_data = json.load(f)
        finally:
          shutil.rmtree(outfile_path)
        self.assertEqual(table_data, dict())

        '''Invalid folder path'''
        with self.assertRaises(FileNotFoundError):
            self.telebot.update_user_table({}, self.INVALID_PATH)
        
        '''Valid folder path with exisiting content'''
        outfile_path = tempfile.mkdtemp()
        try:
          with open(f'{outfile_path}/{self.USER_FILE}', 'w') as f:
              json.dump(self.TABLE_DATA, f, sort_keys=True, indent=4)
          self.TABLE_DATA["111"] = 00000
          self.telebot.update_user_table(self.TABLE_DATA, outfile_path)
          with open(f'{outfile_path}/{self.USER_FILE}', 'r') as f:
              table_data = json.load(f)
        finally:
            self.assertEqual(table_data, self.TABLE_DATA)
            shutil.rmtree(outfile_path)
            self.TABLE_DATA.__delitem__("111")

    def test_get_user_table(self):
        '''Empty folder path'''
        outfile_path = tempfile.mkdtemp()
        try:
          table_data = self.telebot.get_user_table(outfile_path)
          self.assertEqual(table_data, dict())
        finally:
          shutil.rmtree(outfile_path)

        '''Invalid folder path''' 
        with self.assertRaises(FileNotFoundError):
            self.telebot.get_user_table(self.INVALID_PATH)

        '''Valid folder path with exisiting content'''
        outfile_path = tempfile.mkdtemp()
        try:
          with open(f'{outfile_path}/{self.USER_FILE}', 'w') as f:
              json.dump(self.TABLE_DATA, f, sort_keys=True, indent=4)
          table_data = self.telebot.get_user_table(outfile_path)
        finally:
          shutil.rmtree(outfile_path)
        self.assertEqual(self.TABLE_DATA, table_data)

    def test_get_user(self):
      '''Username not None, chat_id None'''
      outfile_path = tempfile.mkdtemp()
      try:
          with open(f'{outfile_path}/{self.USER_FILE}', 'w') as f:
              json.dump(self.TABLE_DATA, f, sort_keys=True, indent=4)
          user = self.telebot.get_user(username="notNone", userpath=outfile_path)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(user, None)

      '''Username not None, chat_id not None, userfile found'''
      outfile_path = tempfile.mkdtemp()
      try:
          with open(f'{outfile_path}/{self.USER_FILE}', 'w') as f:
              json.dump(self.TABLE_DATA, f, sort_keys=True, indent=4)
          with open(f'{outfile_path}/123345.json', 'w') as f:
              json.dump(self.USER_DATA, f, sort_keys=True, indent=4)
          user_data = self.telebot.get_user(username="test", userpath=outfile_path)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(user_data, self.USER_DATA)

      '''Username not None, chat_id not None, userfile not found'''
      outfile_path = tempfile.mkdtemp()
      try:
          with open(f'{outfile_path}/{self.USER_FILE}', 'w') as f:
              json.dump(self.TABLE_DATA, f, sort_keys=True, indent=4)
          user_data = self.telebot.get_user(username="test", userpath=outfile_path)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(user_data, None)

    @patch.object(TeleBot, "get_user")
    def test_check_user(self, mock_get_user):
      
      '''user_data None'''
      update = Mock()
      context = Mock()
      mock_get_user.return_value = None
      check = self.telebot.check_user(update, context)
      self.assertEqual(check, False)
      context.bot.send_message.assert_called_once_with(chat_id=update.effective_chat.id, text=START_MESSAGE)

      '''user_data not None and not banned'''
      update = Mock()
      context = Mock()
      mock_get_user.return_value = self.USER_DATA
      check = self.telebot.check_user(update, context)
      self.assertEqual(check, True)
      context.bot.send_message.assert_not_called()

      '''user_data not None and banned'''
      update = Mock()
      context = Mock()
      mock_get_user.return_value = self.USER_DATA_BANNED
      check = self.telebot.check_user(update, context)
      self.assertEqual(check, False)
      context.bot.send_message.assert_called_once_with(chat_id=update.effective_chat.id, text=BAN_MESSAGE)

    def test_update_user(self):

      '''chat_id None'''
      update = self.telebot.update_user(self.USER_DATA)
      self.assertEqual(update, None)
      
      '''chat_id non None'''
      outfile_path = tempfile.mkdtemp()
      try:
          self.telebot.update_user(self.USER_DATA_BANNED, userpath=outfile_path)
          with open(f'{outfile_path}/123.json', 'r') as f:
                user_data = json.load(f)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(user_data, self.USER_DATA_BANNED)

    def test_get_bikes(self):

      '''valid file path'''
      outfile_path = tempfile.mkdtemp()
      try:
          with open(f'{outfile_path}/{self.BIKE_FILE}', 'w') as f:
              json.dump(self.BIKE_DATA, f, sort_keys=True, indent=4)
          bike_data = self.telebot.get_bikes(f'{outfile_path}/{self.BIKE_FILE}')
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(bike_data, self.BIKE_DATA)

      '''Invalid folder path'''
      with self.assertRaises(FileNotFoundError):
          self.telebot.get_bikes(self.INVALID_PATH)

    def test_update_bikes(self):

      '''valid file path no existing data'''
      outfile_path = tempfile.mkdtemp()
      try:
          self.telebot.update_bikes(self.BIKE_DATA, f'{outfile_path}/{self.BIKE_FILE}')
          with open(f'{outfile_path}/{self.BIKE_FILE}', 'r') as f:
            bike_data = json.load(f)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(bike_data, self.BIKE_DATA)

      '''valid file path with existing data'''
      outfile_path = tempfile.mkdtemp()
      try:
          with open(f'{outfile_path}/{self.BIKE_FILE}', 'w') as f:
              json.dump(self.USER_DATA, f, sort_keys=True, indent=4)
          self.telebot.update_bikes(self.BIKE_DATA, f'{outfile_path}/{self.BIKE_FILE}')
          with open(f'{outfile_path}/{self.BIKE_FILE}', 'r') as f:
              bike_data = json.load(f)
      finally:
          shutil.rmtree(outfile_path)
      self.assertEqual(bike_data, self.BIKE_DATA)

      '''Invalid folder path'''
      with self.assertRaises(FileNotFoundError):
          self.telebot.update_bikes({}, self.INVALID_PATH)

if __name__ == '__main__':
    unittest.main()