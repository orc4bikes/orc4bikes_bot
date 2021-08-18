ROUTES_LIST = {
    "orange": "Orange: From RC4 Level 1 to Fine Foods",
    "pink":   "Pink: From Fine Foods to Octobox (SRC L1)",
    "blue":   "Blue: From RC4 B1 to Fine Foods (Wet Weather route)",
    "green":  "Green: From RC4 B1 to Fine Foods",
    }

ROUTES_PICS = {
    "orange": 'https://www.dropbox.com/s/jsjfhld1ob6owrv/orange.jpg',
    "pink":   'https://www.dropbox.com/s/fpulbka6kqovo3o/pink.jpg',
    'blue':   'https://www.dropbox.com/s/m559ohyre39njok/blue.jpg',
    'green': 'https://www.dropbox.com/s/ugbpo904vmzgtfa/green.jpg?dl=0'
    }

CHEER_LIST = ["",
    "Cheer up!",
    "Ganbatte!",
    "Hwaiting!",
    "Jiayou!",
    "You got this!",
    ]
    
HELP_TEXT = """List of commands:
Basic info:
/start - Starts the bot
/help - Get all available commands
/routes - Get orc4bikes routes

Your info:
/status - View your current credits and rental status!
/history - Show your past transaction history

Bike-related info:
/bikes - Shows currently available bikes
/rent - Rent a bike!
/getpin - Get the pin for the bike you rented
/return - Return the current bicycle
/report - Report damages of our bikes, or anything sus...

Fun stuff :D
Feel free to click any of the below, or just send /random...
/doggo - Get a random dog!
/shibe - Get a random shiba!
/neko - Get a random cat!
/kitty - Get a random kitten!
/foxy - Get a random fox!
/birb - Get a random bird!
/pika - A wild pikachu appeared!
"""

ADMIN_TEXT = """List of admin commands\:
Please do NOT add @ before a username, usernames are case sensitive
User commands\:
/user `username` \- _View the user's current status_
/topup `username AMOUNT` \- _Top up the user's credit by an integer amount_
/deduct `username AMOUNT` \- _Deduct the user's credit by an integer amount_
/setcredit `username AMOUNT` \- _Set the user's credit to an integer amount_

Bikes commands\:
/admin `bikes` \- _Get all bikes and their current status_
/setpin `BIKENAME NEWPIN` \- _Change the bike's pin in the server to a new pin_
/setstatus `BIKENAME NEWSTATUS` \- _Change the bike's status in the server to a new status_

Other commands\:
/logs \- _Get rental and report logs as a csv file_
/admin `COMMAND ACTION` \- _deprecated except for bikes, commands can be accessed individually instead of calling /admin command_
"""

START_MESSAGE = "Please /start me privately to access this service!"


EMOJI = {
        "tick" : "✅",
        "cross": "❌"
        }
