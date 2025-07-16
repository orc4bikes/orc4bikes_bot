# Fly.io Deployment Setup Guide for @orc4bikes_bot

This guide explains how to deploy the @orc4bikes_bot Telegram bot to fly.io using the existing configuration in this repository.

## Prerequisites

1. **Python 3.10.4** (as specified in `src/runtime.txt`)
2. **fly.io account** - Sign up at [fly.io](https://fly.io)
3. **flyctl CLI** - Install the fly.io command line tool
4. **Git** - For version control and GitHub Actions (optional)

## Part 1: CLI Setup and Management

### 1. Install flyctl CLI

**On Windows:**
```cmd
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**On macOS:**
```bash
curl -L https://fly.io/install.sh | sh
```

**On Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Authenticate with fly.io

```bash
flyctl auth login
```

This will open a browser window to log you into your fly.io account.

### 3. Connect to Existing App (If App Already Exists)

If you already have the app running on fly.io:

1. **List your apps**:
```bash
flyctl apps list
```
This will show your existing apps. Look for 'orc4bikes' in the list.

2. **Connect to your existing app**:
```bash
flyctl config save -a orc4bikes
```
This creates/updates your local `fly.toml` to point to your existing app.

### 4. Create New App (If Starting Fresh)

**Option A: Using launch command**
```bash
flyctl launch
```
This will create the app, generate configuration, and deploy.

**Option B: Manual creation**
```bash
flyctl apps create orc4bikes
```

### 5. CLI Commands Reference

#### Deployment Commands
```bash
# Deploy code changes
flyctl deploy

# Check deployment status
flyctl status

# View application logs
flyctl logs

# View app information
flyctl info
```

#### Environment Variables (Secrets) Management
```bash
# Import from .env file (recommended)
flyctl secrets import < .env

# Set individual secrets
flyctl secrets set VARIABLE_NAME=value

# List all secrets (values hidden)
flyctl secrets list

# Import with filtering (if .env has comments)
# Windows PowerShell:
Get-Content .env | Where-Object { $_ -notmatch "^\s*#" -and $_ -notmatch "^\s*$" } | flyctl secrets import

# macOS/Linux:
grep -v '^#' .env | grep -v '^$' | flyctl secrets import
```
Note: It is not necessary to re-deploy the application after importing secrets.

#### Application Management
```bash
# Scale application (number of machines)
flyctl scale count 1

# Suspend app (scale to 0)
flyctl scale count 0

# Resume app (redeploy after suspension)
flyctl deploy

# Restart application
flyctl restart

# Access app shell for debugging
flyctl ssh console

# Destroy app permanently (WARNING: irreversible)
flyctl apps destroy
```

## Part 2: Web Interface Setup and Management

### 1. Access the Dashboard

Visit [fly.io/dashboard](https://fly.io/dashboard) and click on your 'orc4bikes' app.

### 2. Web Interface Features

The web interface provides:
- **Application metrics and logs** - Real-time monitoring
- **Secrets management** - GUI for environment variables
- **Machine scaling controls** - Scale up/down without CLI
- **Deployment history** - Track all deployments
- **Restart controls** - Restart app with one click

### 3. Managing Environment Variables via Web Interface

1. Navigate to the **"Secrets"** tab in your app dashboard
2. Click **"Add Secret"** or edit existing ones
3. Enter variable name and value
4. Click **"Save"** to apply changes

### 4. Suspending/Resuming via Web Interface

**To Suspend (Scale to 0):**
1. Go to the **"Machines"** tab
2. Use scaling controls to set machine count to **0**
3. Or stop/destroy individual machines

**To Resume:**
1. Go to the **"Machines"** tab
2. Set machine count back to **1** (or desired number)
3. Or click **"Deploy"** to redeploy

### 5. Web Interface vs CLI Comparison

| Feature | Web Interface | CLI |
|---------|---------------|-----|
| View logs | ✅ Real-time log viewer | ✅ `flyctl logs` |
| Manage secrets | ✅ GUI for adding/editing | ✅ `flyctl secrets set` |
| Deploy code | ❌ Not available | ✅ `flyctl deploy` |
| Scale app | ✅ Machine scaling controls | ✅ `flyctl scale count` |
| Monitor metrics | ✅ Detailed dashboard | ✅ `flyctl status` |
| Restart app | ✅ Restart button | ✅ `flyctl restart` |
| Suspend app | ✅ Scale to 0 machines | ✅ `flyctl scale count 0` |

**Key Point**: The web interface is excellent for monitoring and configuration, but you'll need the CLI to deploy code changes.

## Part 3: Environment Variables Management

### Setting Up Your .env File

1. **Create your .env file** (if you haven't already):
```bash
cp .env.example .env
```

2. **Edit the .env file** with your actual values:
```bash
# Example .env file format
BOT_ENV=production
BOT_GMT_OFFSET=8
BOT_PROMO=False
BOT_DEDUCT_RATE=20
LOGGING_URL=https://script.google.com/macros/s/your_script_id/exec
DB_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
DB_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DB_REGION_NAME=ap-southeast-1
TELE_API_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_GROUP_ID=-1001234567890
ADMIN_LIST=admin1,admin2,admin3
ADMIN_HEAD=headusername
ADMIN_HEAD_MOBILE=+6512345678
ADMIN_HEAD_NAME=Head Name
ADMIN_SAFETY=safetyusername
ADMIN_SAFETY_MOBILE=+6512345679
ADMIN_SAFETY_NAME=Safety Name
ADMIN_TREASURER=treasurerusername
ADMIN_TREASURER_MOBILE=+6512345680
ADMIN_TREASURER_NAME=Treasurer Name
ADMIN_TREASURER_URL=https://payment.example.com
ADMIN_DEV=devusername
```

### Required Environment Variables

Based on the `.env.example` file, you'll need to configure these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_ENV` | Environment (development/production) | `production` |
| `BOT_GMT_OFFSET` | Timezone offset | `8` |
| `BOT_PROMO` | Promotional mode | `False` |
| `BOT_DEDUCT_RATE` | Credit deduction rate | `20` |
| `LOGGING_URL` | Google Apps Script logging URL | `https://script.google.com/...` |
| `DB_ACCESS_KEY` | AWS DynamoDB access key | `AKIA...` |
| `DB_SECRET_KEY` | AWS DynamoDB secret key | `wJalr...` |
| `DB_REGION_NAME` | AWS region | `ap-southeast-1` |
| `TELE_API_TOKEN` | Telegram bot token | `123456789:ABC...` |
| `ADMIN_GROUP_ID` | Admin group chat ID | `-1001234567890` |
| `ADMIN_LIST` | Comma-separated admin usernames | `admin1,admin2,admin3` |
| `ADMIN_*` | Admin contact details | Various formats |

### Verifying Your Configuration

After setting up environment variables:

```bash
# Check which secrets are configured
flyctl secrets list

# Test your bot locally (optional)
python main.py
```

**Note**: Values are hidden for security, but you can see which secrets are configured.

## Part 4: Understanding the Configuration Files

### `fly.toml`
```toml
app = 'orc4bikes'
primary_region = 'sin'
```
- **app**: Your app name on fly.io (must be unique globally)
- **primary_region**: Singapore region ('sin') for optimal performance

### `Dockerfile`
```dockerfile
FROM python:3.10
COPY . .
RUN pip install -r requirements.txt
RUN pip install python-dotenv
CMD python main.py
```
- Uses Python 3.10 base image
- Copies all files to the container
- Installs dependencies from `requirements.txt`
- Installs `python-dotenv` for environment variable handling
- Runs the bot with `python main.py`

### `Procfile`
```
worker: python main.py
```
- Defines the worker process that runs the bot

## Part 5: Codebase Modification & Deployment

### Making Code Changes

1. **Edit your code locally** in your preferred editor
2. **Test changes locally** (optional but recommended):
   ```bash
   python main.py
   ```
3. **Deploy the updated code**:
   ```bash
   flyctl deploy
   ```
4. **Monitor deployment**:
   ```bash
   flyctl logs
   ```

### Deployment Workflow

**For Existing Apps (Most Common):**
```bash
# 1. Make your code changes
# 2. Deploy changes
flyctl deploy

# 3. Verify deployment
flyctl status

# 4. Check logs for issues
flyctl logs

# 5. Test bot functionality in Telegram
```

**For New Apps:**
```bash
# 1. Create app
flyctl apps create orc4bikes

# 2. Set up environment variables
flyctl secrets import < .env

# 3. Deploy
flyctl deploy
```

### Verifying Deployment

1. **Check app status**:
```bash
flyctl status
```

2. **View logs**:
```bash
flyctl logs
```

3. **Test bot functionality**:
- Open Telegram and send `/start` to your bot
- Try other commands to ensure everything works
- Check logs for any errors

### Common Deployment Issues

1. **Bot not responding**: Check logs for token issues or API connectivity
2. **Database errors**: Verify AWS credentials and DynamoDB access
3. **Deployment fails**: Check `requirements.txt` and Python version compatibility
4. **Environment variable issues**: Ensure all required secrets are set

## Part 6: GitHub Actions Automatic Deployment (Optional)

### Setting Up Automated Deployment

The repository includes a GitHub Actions workflow (`.github/workflows/fly.yml`) for automatic deployment:

```yaml
name: Fly Deploy
on:
  push:
    branches:
      - main
jobs:
  deploy:
    name: Deploy app
    runs-on: ubuntu-latest
    concurrency: deploy-group
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Enabling Automatic Deployment

1. **Get your fly.io API token**:
```bash
flyctl auth token
```

2. **Add it to GitHub Secrets**:
   - Go to your GitHub repository
   - Navigate to Settings > Secrets and variables > Actions
   - Add a new secret named `FLY_API_TOKEN` with your token

3. **Deploy automatically**:
   - Any push to the `main` branch will trigger automatic deployment
   - Monitor deployment progress in the Actions tab

## Part 7: Application Architecture

The bot runs as a single worker process that:
- Connects to Telegram Bot API using the token from `TELE_API_TOKEN`
- Uses AWS DynamoDB for data storage (credentials from `DB_ACCESS_KEY` and `DB_SECRET_KEY`)
- Handles bicycle rental operations for ORC4BIKES
- Supports admin commands for management

## Part 8: Generating new bicycle QR codes

Brief outline of the process to generate new bike QR codes (local deployment):
1. Create the qr/ directory within the home directory
2. Run `pip install qrcode pillow`
3. Ensure data.json file is present (location configured via QR_DATA_FILEPATH environment variable)
4. Run `python scripts/generate_qr.py`

## Part 9: Troubleshooting & Debugging

### Debugging Commands

```bash
# View current secrets (values are hidden)
flyctl secrets list

# Access app shell for debugging
flyctl ssh console

# View detailed app information
flyctl info

# Check machine status
flyctl machine list
```

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Bot not responding | Invalid token | Check `TELE_API_TOKEN` in secrets |
| Database errors | AWS credentials | Verify `DB_ACCESS_KEY` and `DB_SECRET_KEY` |
| Deployment fails | Dependencies | Check `requirements.txt` compatibility |
| App keeps restarting | Code errors | Check logs with `flyctl logs` |
| Out of memory | Resource limits | Scale to larger machine or optimize code |

## Part 10: Cost Considerations & Monitoring

### Free Tier Limits
- fly.io has a free tier that includes 256MB RAM and 1GB storage
- This bot should run comfortably within the free tier limits
- Monitor usage at [fly.io/dashboard](https://fly.io/dashboard)

### Monitoring Your App
- **Resource usage**: Check dashboard for CPU/memory usage
- **Costs**: Monitor billing section for any charges
- **Performance**: Use logs to track response times and errors

## Support Resources

**For fly.io specific issues:**
- [fly.io Documentation](https://fly.io/docs/)
- [fly.io Community Forum](https://community.fly.io/)

**For bot-specific issues:**
- Check application logs with `flyctl logs`
- Ensure all environment variables are properly configured
- Test bot functionality in Telegram