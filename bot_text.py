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

HELP_TEXT = """
🗾 /routes - orc4bikes-curated routes
ℹ️ /status - Credits and rental status
📜 /history - Recent 10 transactions
✨ /fun - Interesting..

🚴 ️/rent - Start your rental trip here!
🔓 /getpin - Get the PIN for the bike you rented
↩️ /return - End your rental trip here!
📢 /report - Report damages or anything sus
"""

FUN_TEXT = """
Feel free to click any of the below, or just send /random...
/doggo - Get a random dog!
/shibe - Get a random shiba!
/neko - Get a random cat!
/kitty - Get a random kitten!
/foxy - Get a random fox!
/birb - Get a random bird!
/pika - A wild pikachu appeared!

Try other commands for easter eggs... :)
"""

ADMIN_TEXT = """List of admin commands:
Please do NOT add @ before a username
Usernames are case sensitive
User commands:
/user `username` \\- View the user's current status
/topup `username` AMOUNT \\- Top up the user's credit by an integer amount
/deduct `username` AMOUNT \\- Deduct the user's credit by an integer amount
/setcredit `username` AMOUNT \\- Set the user's credit to an integer amount

Bikes commands:
/admin `bikes` \\- Get all bikes and their current status
/setpin `BIKENAME` NEW_PIN \\- Change the bike's pin in the server to a new pin
/setstatus `BIKENAME` NEW_STATUS \\- Change the bike's status in the server to a new status

Other commands:
/logs \\- Get rental and report logs as a csv file
"""

START_MESSAGE = "Please /start me privately to access this service!"


EMOJI = {
        "tick" : "✅",
        "cross": "❌"
        }
