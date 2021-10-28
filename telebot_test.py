import unittest, io, sys, os, shutil, json, filecmp, tempfile


from telebot import TeleBot
import datetime as dt
DEV_API_KEY = "1722354435:AAHRUa4Pph4zjYgNe8PzfsIX1KLzwSJk7Ow"



class TestTelebotMethods(unittest.TestCase):

    telebot = TeleBot(DEV_API_KEY)
    LOG_EXCEPTION_ERRORMESSAGE = "Error occured at {}. Error is \n{}\n"
    TEST_ERROR_1 = ValueError
    TEST_ERROR_2 = IndexError
    USER_FILE = 'table.json'
    INVALID_PATH = 'tests/invalid_dump'
    TABLE_DATA = {"test": 123345, "test2": 1123345}

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


if __name__ == '__main__':
    unittest.main()