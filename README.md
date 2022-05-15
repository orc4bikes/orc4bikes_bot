# @orc4bikes_bot
Telegram bot for ORC4BIKES, an RC4 interest group

## What this bot does
Handles the rental of bicycles from ORC4BIKES.

Using telegram, users are able to check the availability of bikes, and rent them after verification.

## Commands available

|Command|Description|
|---|---|
|/start|Initializes the bot|
|/topup|Top-up via PayLah / PayNow|
|/routes|orc4bikes-curated routes|
|/status|Credits and rental status|
|/history|Recent transactions history|
|/bikes|See available bikes|
|/rent|Start your rental trip here!|
|/getpin|Get the PIN for the bike you rented|
|/return|Return the current bicycle|
|/report|Report damages or anything sus|


## Setup

1. Download and install Python by following the instructions [here](https://www.python.org/downloads/). Ensure that the version is at least the major version declared in `runtime.txt`.

2. Install Python modules required.
```
python3 -m pip install -r requirements.txt
```

3. Additionally, install the [`python-dotenv`](https://pypi.org/project/python-dotenv/) library if you are testing locally.
```
python3 -m pip install python-dotenv
```

4. Make a copy of `.env.example` as `.env`, then fill in the necessary environment variables.

5. Start the bot.
```
python3 main.py
```
