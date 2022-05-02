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
    'green':  'https://www.dropbox.com/s/ugbpo904vmzgtfa/green.jpg?dl=0',
}

CHEER_LIST = [
    "",
    "Cheer up!",
    "Ganbatte!",
    "Hwaiting!",
    "Jiayou!",
    "You got this!",
]

GUIDE_PIC = "https://www.dropbox.com/s/couqqkedvunq3ee/guide.png"

HELP_TEXT = """
🏦 /topup - Top up to use the bot now!
🗾 /routes - orc4bikes-curated routes
ℹ️ /status - Credits and rental status
📜 /history - Recent 10 transactions
✨ /fun - Interesting..

Rental rates:
3 credits per minute

🚲 /bikes - See available bikes
🚴 ️/rent - Start your rental trip here!
🔓 /getpin - Get the PIN for the bike you rented
↩️ /return - End your rental trip here!
📢 /report - Report damages or anything sus
✍️ /feedback - A penny for your thoughts, for all our past events!

Top-up:
$1 = 100 credits
"""

FUN_TEXT = """
Feel free to click any of the below, or just send /random...
🐶 /doggo - Get a random dog!
🐕 /shibe - Get a random shiba!
🐈 /neko - Get a random cat!
🐱 /kitty - Get a random kitten!
🦊 /foxy - Get a random fox!
🐥 /birb - Get a random bird!
🐹 /pika - A wild pikachu appeared!

Look out for more easter eggs 🥚... :)
"""

ADMIN_TEXT = """List of admin commands:
Please do NOT add @ before a username
Usernames are case sensitive
User commands:
/user `username` \\- View the user's current status
/admin `topup` `username` AMOUNT \\- Top up the user's credit by an integer amount
\\*\\*\\*NOTE that topup has been used as a user function, to access admin topup, please send /admin topup\\*\\*\\*

/deduct `username` AMOUNT \\- Deduct the user's credit by an integer amount
/setcredit `username` AMOUNT \\- Set the user's credit to an integer amount
/ban `username` \\- Ban a selected user
/unban `username` \\- Unban a selected user


Bikes commands:
/admin `bikes` \\- Get all bikes and their current status
/setpin `BIKENAME` NEWPIN \\- Change the bike's pin in the server to a new pin
/setstatus `BIKENAME` NEWSTATUS \\- Change the bike's status in the server to a new status
/forcereturn  `BIKENAME` \\- Forcefully return a selected bike

Other commands:
/logs \\- Get rental and report logs as a csv file
"""

START_MESSAGE = "Please /start me privately to access this service!"

BAN_MESSAGE = """You are on Santa's naughty list... What have you done?!
If you believe this is a mistake, contact the current admins at @yonx30"""

TERMS_TEXT = """Bicycle Rental -- Terms of Use:
1. You are not to HOG the bike.
2. You must take GOOD CARE of the bike during the duration of rental.
3. If you spot any DEFECTS, /report before your rental. Any defects found after your rental will be your responsibility.
4. You will be FINANCIALLY held liable for any DAMAGES to the bike, and/or LOSS of equipment on the bike.
5. orc4bikes reserve the right to amend the 'Terms of Use' at their discretion.
6. You agree to take good care of YOURSELF and follow proper safety procedures.

In case of emergencies, call ambulance 995, and inform either
 - Wu Yong Xin at 83538111 @yonx30 - ORC4BIKES Head, or
 - Samuel Yow at 83957445 @samyky23 - ORC4BIKES Safety

If you agree, and ONLY if you agree, to the terms stated above, click "Accept".
"""

EMOJI = {
    "tick" : "✅",
    "cross": "❌",
}

PAYMENT_URL = "https://www.dbs.com.sg/personal/mobile/paylink/index.html?tranRef=XtY0BEgubm"
