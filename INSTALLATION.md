# Discord Bot Installation Guide

## Quick Start

1. **Download the bot files** to your computer
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Get your Discord bot token** (see instructions below)
4. **Edit the .env file** and add your token
5. **Start the bot**:
   ```bash
   python main.py
   ```

## Getting a Discord Bot Token

### Step 1: Create Discord Application
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "My Server Bot")
4. Click "Create"

### Step 2: Create Bot User
1. In your application, click "Bot" in the left sidebar
2. Click "Add Bot"
3. Click "Yes, do it!"
4. Under "Token", click "Copy" to copy your bot token
5. **Keep this token secret - never share it publicly**

### Step 3: Configure Bot Settings
1. **Public Bot**: Turn OFF if you only want to use it on your servers
2. **Requires OAuth2 Code Grant**: Leave OFF
3. **Message Content Intent**: Turn ON (required for keyword responses)
4. **Server Members Intent**: Turn ON (required for welcome messages)
5. **Presence Intent**: Turn ON (recommended)

### Step 4: Invite Bot to Server
1. Go to "OAuth2" > "URL Generator"
2. Select these scopes:
   - ✓ `bot`
   - ✓ `applications.commands`

3. Select these bot permissions:
   - **General Permissions**:
     - ✓ View Channels
     - ✓ Send Messages
     - ✓ Embed Links
     - ✓ Add Reactions
     - ✓ Use Slash Commands
   - **Text Permissions**:
     - ✓ Manage Messages
     - ✓ Read Message History
   - **Voice Permissions**:
     - ✓ Connect
     - ✓ Speak
     - ✓ Use Voice Activity
   - **Moderation Permissions**:
     - ✓ Kick Members
     - ✓ Ban Members
     - ✓ Manage Roles

4. Copy the generated URL and open it in your browser
5. Select your server and click "Authorize"

## Manual Installation (Alternative)

If the setup script doesn't work, install manually:

```bash
# Install Python packages
pip install discord.py python-dotenv gtts aiohttp psutil

# Create environment file
cp .env.example .env

# Edit .env file with your bot token
# Then start the bot
python main.py
```

## System Requirements

- **Python 3.8+** (Python 3.11 recommended)
- **FFmpeg** (for text-to-speech)
  - Windows: Download from https://ffmpeg.org/download.html
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

## Hosting Options

### Local Computer
- Good for testing and small servers
- Bot goes offline when computer is off
- No hosting costs

### VPS/Cloud Server
- **Recommended for production use**
- 24/7 uptime
- Popular options: DigitalOcean, Linode, AWS EC2
- Minimum: 1GB RAM, 1 CPU core

### Free Hosting Platforms
- **Heroku** (with scheduler addon)
- **Railway**
- **Render**
- Note: May have limitations on uptime

## Configuration Files

### .env File
```env
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!
```

### data/config.json (Auto-created)
```json
{
  "mute_role_name": "Muted",
  "max_giveaway_duration": 7200,
  "tts_max_length": 200
}
```

## Testing Your Bot

1. **Check if bot is online** - Look for green dot in Discord
2. **Test basic command**: Type `!ping` in a channel
3. **Test permissions**: Try `!serverinfo` 
4. **Test TTS**: Join a voice channel and use `!tts hello`
5. **Check slash commands**: Type `/` and look for your bot's commands

## Troubleshooting

### Bot Won't Start
- Check your Discord token in .env file
- Make sure all dependencies are installed
- Check Python version (needs 3.8+)

### Commands Not Working
- Verify bot has required permissions
- Check if bot can read messages in the channel
- Try using slash commands instead: `/ping`

### TTS Not Working
- Install FFmpeg on your system
- Check bot has voice permissions
- Make sure bot is in a voice channel

### Slash Commands Missing
- Wait 5-10 minutes after starting bot
- Check bot has "Use Slash Commands" permission
- Try refreshing Discord

## Getting Help

- Use `!help` command for command list
- Check console/logs for error messages
- Verify all permissions are granted
- Make sure bot has admin rights for moderation features

## Security Notes

- Never share your bot token publicly
- Regenerate token if accidentally exposed
- Use environment variables for sensitive data
- Regular security updates recommended