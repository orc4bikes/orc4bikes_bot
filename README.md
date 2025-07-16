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

### Local Development

1. Download and install Python by following the instructions [here](https://www.python.org/downloads/). Ensure that the version is at least the major version declared in `src/runtime.txt`.

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

### Production Deployment

This bot is designed to run on [fly.io](https://fly.io) for production deployment.

#### Automated Deployment (Recommended)

The repository includes GitHub Actions for automatic deployment when you push to the `main` branch.

**Setup (one-time):**
1. Get your fly.io API token:
```bash
flyctl auth token
```

2. Add it to GitHub Secrets:
   - Go to your GitHub repository
   - Navigate to Settings > Secrets and variables > Actions
   - Add a new secret named `FLY_API_TOKEN` with your token

3. Push to main branch:
```bash
git add .
git commit -m "Deploy changes"
git push origin main
```

**How it works:**
- Any push to `main` triggers automatic deployment
- Uses `.github/workflows/fly.yml` configuration
- Runs `flyctl deploy --remote-only` on GitHub's servers
- Monitor progress in the Actions tab

#### Manual Deployment

If you prefer manual deployment or need to deploy immediately:

1. **Install flyctl CLI** and authenticate:
```bash
flyctl auth login
```

2. **Connect to your existing app**:
```bash
flyctl config save -a orc4bikes
```

3. **Deploy your changes**:
```bash
flyctl deploy
```

#### New Deployment

For complete deployment instructions including:
- First-time setup
- Environment variables configuration
- Web interface management
- Generating new bicycle QR codes
- Troubleshooting

**See [FLYIO_SETUP.md](FLYIO_SETUP.md) for detailed deployment guide.**

#### Environment Variables

The bot requires these key environment variables:
- `TELE_API_TOKEN` - Your Telegram bot token
- `DB_ACCESS_KEY` & `DB_SECRET_KEY` - AWS DynamoDB credentials
- `ADMIN_GROUP_ID` - Admin group chat ID
- `ADMIN_LIST` - Comma-separated admin usernames

For the complete list, see `.env.example` and [FLYIO_SETUP.md](FLYIO_SETUP.md).
