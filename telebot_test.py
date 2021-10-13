import unittest, io, sys, os, shutil, json, filecmp


from telebot import TeleBot
import datetime as dt
DEV_API_KEY = "1722354435:AAHRUa4Pph4zjYgNe8PzfsIX1KLzwSJk7Ow"



class TestTelebotMethods(unittest.TestCase):

    telebot = TeleBot(DEV_API_KEY)
    LOG_EXCEPTION_ERRORMESSAGE = "Error occured at {}. Error is \n{}\n"
    TEST_ERROR_1 = ValueError
    TEST_ERROR_2 = IndexError
    USER_PATH = 'test/data'
    TABLE_DATA = {"test": 123345, "test2": 1123345}

    def test_log_exception(self):
        '''Without optional input'''
        capturedOutput = io.StringIO()      
        sys.stdout = capturedOutput                   
        self.telebot.log_exception(self.TEST_ERROR_1)                                    
        sys.stdout = sys.__stdout__  
        self.assertEqual(capturedOutput.getvalue(), 
            self.LOG_EXCEPTION_ERRORMESSAGE.format(dt.datetime.now(), self.TEST_ERROR_1))

        '''With additional input'''
        capturedOutput = io.StringIO()      
        sys.stdout = capturedOutput 
        self.telebot.log_exception(self.TEST_ERROR_2, "~")                                    
        sys.stdout = sys.__stdout__  
        self.assertEqual(capturedOutput.getvalue(), "~\n" 
            + self.LOG_EXCEPTION_ERRORMESSAGE.format(dt.datetime.now(), self.TEST_ERROR_2))

    def test_update_user_table(self):
        '''Empty folder path'''
        self.telebot.update_user_table({}, 'tests/data_dump')
        with open('tests/data_dump/table.json', 'r') as f:
            table_data = json.load(f)
        self.assertEqual(table_data, dict())
        os.remove("tests/data_dump/table.json")

        '''Invalid folder path'''
        with self.assertRaises(FileNotFoundError):
            self.telebot.update_user_table({}, 'tests/invalid_dump')
        
        '''Valid folder path with exisiting content'''
        
        self.TABLE_DATA["111"] = 00000
        shutil.copy2("tests/data/users/table.json", "tests/data_dump/table.json")
        self.telebot.update_user_table(self.TABLE_DATA, 'tests/data_dump')
        self.assertTrue(filecmp.cmp("tests/data/users/existing_table_updated.json", 'tests/data_dump/table.json'))
        os.remove("tests/data_dump/table.json")
        self.TABLE_DATA.__delitem__("111")

    def test_get_user_table(self):
        '''Empty folder path'''
        table_data = self.telebot.get_user_table('tests/data_dump')
        self.assertEqual(table_data, dict())

        '''Invalid folder path @TODO''' 
        table_data = self.telebot.get_user_table('tests/invalid_dump')
        self.assertEqual(table_data, dict())
        
        '''Valid folder path with exisiting content'''
        table_data = self.telebot.get_user_table("tests/data/users")
        self.assertEqual(self.TABLE_DATA, table_data)


if __name__ == '__main__':
    unittest.main()