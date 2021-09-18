import json
from os import listdir
from os.path import isfile, join
from admin import ADMIN_LIST

def update_all_users(field='credits', value=0):
    """Update all user in database"""
    files = [f for f in listdir('users/') if isfile(join('users/', f))]
    for file in files: # Get all
        if 'table.json' in file.name:
            continue
        with open(f'users/{file}', 'r') as f:
            user_data = json.load(f)
        if user_data.get('chat_id') not in ADMIN_LIST:
            user_data[field] = value
        with open(f'users/{file}', 'w') as f:
            json.dump(user_data, f, sort_keys=True, indent=4)

def update_all_credits(credits=0):
    update_all_users('credits',credits)

if __name__ == '__main__':
    while True:
        credits = input("Change all users credits to: (number)")
        if credits.isnumeric():
            update_all_credits(int(credits))
            print('Done')
        else:
            print('Not a number')
