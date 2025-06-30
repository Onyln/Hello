# Discord Bot Setup on Hot-Hosting.net

Hot-hosting.net provides free web hosting services. Here's how to deploy your Discord bot on their platform.

## Prerequisites

1. **Account on hot-hosting.net**
2. **cPanel access** (provided after registration)
3. **Your Discord bot token**
4. **Bot files ready for upload**

## Step 1: Register Account

1. Go to **hot-hosting.net**
2. Click **"Free Hosting"**
3. Fill registration form
4. Verify email address
5. Wait for account activation (usually 24-48 hours)

## Step 2: Access cPanel

1. Login to your hot-hosting account
2. Access **cPanel** from control panel
3. Note your hosting details:
   - **Domain**: your-username.hot-hosting.net
   - **Server**: Server name/IP
   - **MySQL**: Database credentials (if needed)

## Step 3: Upload Bot Files

### Method A: File Manager (Recommended)

1. Open **File Manager** in cPanel
2. Navigate to **public_html** folder
3. Create new folder: **discord-bot**
4. Upload these files to discord-bot folder:
   ```
   bot.py
   main.py
   setup.py
   .env.example
   README.md
   cogs/ (entire folder)
   data/ (entire folder)
   ```

### Method B: FTP Upload

1. Use FTP client (FileZilla recommended)
2. Connect with credentials:
   - **Host**: your-domain or server IP
   - **Username**: cPanel username
   - **Password**: cPanel password
   - **Port**: 21
3. Upload files to **public_html/discord-bot/**

## Step 4: Configure Environment

### Create .env File

1. In File Manager, go to **discord-bot** folder
2. Create new file: **.env**
3. Add your configuration:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   BOT_PREFIX=!
   ```

### Set File Permissions

1. Right-click on files in File Manager
2. Set permissions:
   - **Python files**: 755
   - **.env file**: 644
   - **data/ folder**: 755

## Step 5: Install Python Dependencies

### Check Python Version

1. Open **Terminal** in cPanel (if available)
2. Check Python version:
   ```bash
   python3 --version
   ```

### Install Dependencies

Most shared hosting doesn't allow pip install. Try these alternatives:

#### Option A: Contact Support
- Email hot-hosting.net support
- Request Python modules installation:
  - discord.py
  - python-dotenv
  - gtts
  - aiohttp
  - psutil

#### Option B: Use Virtual Environment (if supported)
```bash
python3 -m venv botenv
source botenv/bin/activate
pip install discord.py python-dotenv gtts aiohttp psutil
```

#### Option C: Local Installation
If pip is restricted, you may need to:
1. Download packages manually
2. Upload to your hosting space
3. Modify Python path

## Step 6: Create Startup Script

### Create bot_runner.py

Create a wrapper script for better hosting compatibility:

```python
#!/usr/bin/env python3
import sys
import os
import subprocess
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def restart_bot():
    """Restart bot if it crashes"""
    while True:
        try:
            print("Starting Discord bot...")
            result = subprocess.run([sys.executable, "main.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Bot crashed with error: {result.stderr}")
                print("Restarting in 30 seconds...")
                time.sleep(30)
            else:
                break
                
        except Exception as e:
            print(f"Error starting bot: {e}")
            time.sleep(30)

if __name__ == "__main__":
    restart_bot()
```

## Step 7: Setup Cron Jobs

### Create Cron Job for Auto-restart

1. Go to **Cron Jobs** in cPanel
2. Add new cron job:
   - **Minute**: */5 (every 5 minutes)
   - **Hour**: * (every hour)
   - **Day**: * (every day)
   - **Month**: * (every month)
   - **Weekday**: * (every weekday)
   - **Command**: 
     ```bash
     cd /home/username/public_html/discord-bot && python3 bot_runner.py
     ```

### Keep-Alive Script

Create **keepalive.py**:
```python
import requests
import time
import os

def ping_server():
    """Ping server to keep it active"""
    try:
        # Replace with your domain
        response = requests.get("http://your-username.hot-hosting.net")
        print(f"Server ping: {response.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")

if __name__ == "__main__":
    while True:
        ping_server()
        time.sleep(300)  # Ping every 5 minutes
```

## Step 8: Test Bot Deployment

### Check Bot Status

1. Access your domain: **your-username.hot-hosting.net/discord-bot/**
2. Create simple status page (optional):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Discord Bot Status</title>
</head>
<body>
    <h1>Discord Bot Status</h1>
    <p>Bot is running on hot-hosting.net</p>
    <p>Last updated: <span id="time"></span></p>
    
    <script>
        document.getElementById('time').innerHTML = new Date();
    </script>
</body>
</html>
```

### Monitor Logs

Create **check_logs.php** for web-based log viewing:
```php
<?php
$logfile = 'bot.log';
if (file_exists($logfile)) {
    echo "<pre>";
    echo htmlspecialchars(file_get_contents($logfile));
    echo "</pre>";
} else {
    echo "No log file found";
}
?>
```

## Step 9: Troubleshooting

### Common Issues

1. **Python not found**
   - Try `python3` instead of `python`
   - Check available Python versions
   - Contact hosting support

2. **Modules not installed**
   - Request installation from support
   - Try alternative hosting if not supported

3. **Permission denied**
   - Check file permissions (755 for executables)
   - Ensure proper ownership

4. **Bot doesn't stay running**
   - Shared hosting may kill long-running processes
   - Use cron job restart method
   - Consider upgrading to VPS

### Resource Limitations

Hot-hosting.net free plans typically have:
- **Limited CPU time**
- **Memory restrictions**
- **Process time limits**
- **No persistent processes**

### Monitoring Solutions

1. **Create status endpoint**
2. **Use external monitoring** (UptimeRobot)
3. **Email notifications** for downtime
4. **Log file analysis**

## Step 10: Optimization for Shared Hosting

### Reduce Resource Usage

1. **Optimize imports**:
   ```python
   # Only import what you need
   from discord.ext import commands
   import discord
   ```

2. **Add sleep delays**:
   ```python
   import time
   time.sleep(1)  # Reduce CPU usage
   ```

3. **Limit concurrent operations**:
   ```python
   # Process one command at a time
   @commands.cooldown(1, 2, commands.BucketType.guild)
   ```

### Error Handling

```python
import logging
import sys

# Robust error handling
try:
    # Bot code here
    pass
except Exception as e:
    logging.error(f"Critical error: {e}")
    sys.exit(1)
```

## Alternative Hosting Options

If hot-hosting.net doesn't support your bot requirements:

1. **000webhost.com** - Similar free hosting
2. **InfinityFree** - Free hosting with more features
3. **Heroku** - Cloud platform (has free tier)
4. **Railway** - Modern hosting platform
5. **DigitalOcean** - VPS starting at $4/month

## Important Notes

- **Free hosting limitations**: May not support long-running processes
- **Bot token security**: Never expose in web-accessible files
- **Resource monitoring**: Watch CPU and memory usage
- **Backup strategy**: Regular backups of bot data
- **Support contact**: Use hosting support for technical issues

Most shared hosting providers are designed for websites, not bots. For reliable 24/7 bot hosting, consider upgrading to VPS or specialized bot hosting services.