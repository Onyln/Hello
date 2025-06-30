# Discord Bot Setup on Termux (Android)

Termux is a powerful terminal emulator for Android that lets you run your Discord bot directly on your phone.

## Prerequisites

1. **Install Termux** from F-Droid (recommended) or Google Play Store
2. **Android device with 2GB+ RAM** (recommended)
3. **Stable internet connection**

## Step 1: Setup Termux Environment

Open Termux and run these commands:

```bash
# Update package lists
pkg update && pkg upgrade

# Install required packages
pkg install python git ffmpeg

# Install pip (Python package manager)
pkg install python-pip

# Create bot directory
mkdir discord-bot
cd discord-bot
```

## Step 2: Download Bot Files

```bash
# If you have the files on your phone, copy them to Termux
# Or download from your repository
git clone <your-bot-repository-url> .

# Or manually create files (if copying from another source)
```

## Step 3: Install Python Dependencies

```bash
# Install bot dependencies
pip install discord.py python-dotenv gtts aiohttp psutil

# Verify installation
python -c "import discord; print('Discord.py installed successfully')"
```

## Step 4: Configure Bot

```bash
# Create environment file
cp .env.example .env

# Edit the file with nano
nano .env
```

Add your Discord bot token:
```env
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!
```

**To save in nano**: Press `Ctrl+X`, then `Y`, then `Enter`

## Step 5: Run the Bot

```bash
# Start the bot
python main.py
```

## Running Bot in Background

To keep the bot running when you close Termux:

```bash
# Install tmux (terminal multiplexer)
pkg install tmux

# Start tmux session
tmux new-session -d -s discord-bot

# Run bot in tmux
tmux send-keys -t discord-bot "cd discord-bot && python main.py" Enter

# To check bot status
tmux attach -t discord-bot

# To detach (keep running): Press Ctrl+B, then D
```

## Auto-Start Bot on Termux Launch

Create a startup script:

```bash
# Create startup script
nano ~/start-bot.sh
```

Add this content:
```bash
#!/bin/bash
cd ~/discord-bot
tmux new-session -d -s discord-bot "python main.py"
echo "Discord bot started in background"
```

Make executable:
```bash
chmod +x ~/start-bot.sh
```

Add to Termux startup:
```bash
# Edit bashrc
nano ~/.bashrc

# Add at the end:
~/start-bot.sh
```

## Troubleshooting

### Common Issues:

1. **"Permission denied" errors**
   ```bash
   termux-setup-storage
   chmod +x main.py
   ```

2. **Python module not found**
   ```bash
   pip install --upgrade pip
   pip install discord.py --force-reinstall
   ```

3. **FFmpeg not working**
   ```bash
   pkg install ffmpeg
   # If still issues, try:
   pkg install clang
   ```

4. **Bot stops when phone sleeps**
   - Enable "Don't kill app" in Android settings
   - Disable battery optimization for Termux
   - Use tmux session as shown above

### Performance Tips:

- **Close other apps** to free RAM
- **Use Wi-Fi** instead of mobile data when possible
- **Keep phone plugged in** for 24/7 hosting
- **Monitor temperature** - phones can overheat

### Storage Management:

```bash
# Check storage usage
du -sh ~/discord-bot

# Clean old logs
rm ~/discord-bot/bot.log

# Backup important data
tar -czf bot-backup.tar.gz ~/discord-bot/data/
```

## Limitations of Phone Hosting

- **Limited uptime** (phone restarts, battery issues)
- **Performance constraints** (CPU, RAM limitations)
- **Network reliability** (mobile connection instability)
- **Background restrictions** (Android battery optimization)

## Recommended Settings

### Android Settings:
1. **Battery Optimization**: Disable for Termux
2. **Auto-start**: Enable for Termux
3. **Background App Limits**: Set to "No limit" for Termux
4. **Developer Options**: Enable "Stay awake" when charging

### Termux Settings:
1. **Acquire Wakelock**: Enable in Termux settings
2. **CPU Wake Lock**: Enable if available

## Monitoring Your Bot

```bash
# Check if bot is running
tmux list-sessions

# View bot logs
tail -f ~/discord-bot/bot.log

# Check system resources
top

# Check network
ping google.com
```

## Updating the Bot

```bash
# Stop bot
tmux kill-session -t discord-bot

# Update code
cd ~/discord-bot
git pull origin main

# Update dependencies
pip install --upgrade discord.py

# Restart bot
~/start-bot.sh
```

## Security Considerations

- **Never share your bot token**
- **Use strong passwords** for any accounts
- **Regular backups** of configuration
- **Monitor for unusual activity**

## Alternative: Using Cloud Shell

If phone hosting is unreliable, consider:
- **Google Cloud Shell** (free, limited hours)
- **GitHub Codespaces** (free tier available)
- **Replit** (free hosting with limitations)

These provide more stable hosting than mobile devices.