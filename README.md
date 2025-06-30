# Discord Bot - Multi-Purpose Bot

A comprehensive Discord bot with moderation tools, TTS functionality, giveaway system, welcome messages, slash commands, and keyword auto-responses.

## Features

### 🔨 Moderation
- **Kick/Ban** members with reasons
- **Mute/Unmute** with automatic timers
- **Clear messages** in bulk
- **Role-based permissions** checking

### 🔊 Text-to-Speech (TTS)
- **Voice channel integration**
- **Text-to-speech conversion** using Google TTS
- **Voice commands** (join, leave, stop)
- **Auto-disconnect** when alone in channel

### 🎉 Giveaways
- **Create timed giveaways** with custom duration
- **Automatic winner selection**
- **React-to-enter** system
- **Giveaway management** (end early, list active)

### 👋 Welcome System
- **Customizable welcome messages**
- **Rich embeds** with user information
- **Welcome channel configuration**
- **Custom colors and images**

### 🔤 Keyword Auto-Response
- **Smart keyword detection**
- **Multiple responses** per keyword
- **Easy management** (add/remove keywords)
- **Case-insensitive matching**

### ⚙️ Utility Commands
- **Server/User information**
- **Bot statistics and uptime**
- **Ping/latency checking**
- **Comprehensive help system**

### ⚡ Slash Commands
- **Modern Discord integration**
- **All major commands** available as slash commands
- **Auto-completion** and validation

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Discord bot token
- FFmpeg (for TTS functionality)

### 2. Installation

1. **Clone or download** the bot files
2. **Install Python dependencies**:
   ```bash
   pip install discord.py python-dotenv gtts aiohttp psutil
   ```
3. **Install FFmpeg**:
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

### 3. Configuration

1. **Create a Discord Bot**:
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Discord bot token:
     ```env
     DISCORD_TOKEN=your_bot_token_here
     BOT_PREFIX=!
     ```

3. **Invite the bot** to your server:
   - In Discord Developer Portal, go to OAuth2 > URL Generator
   - Select "bot" and "applications.commands" scopes
   - Select required permissions:
     - Send Messages
     - Embed Links
     - Add Reactions
     - Manage Messages
     - Kick Members
     - Ban Members
     - Manage Roles
     - Connect (for TTS)
     - Speak (for TTS)
   - Use generated URL to invite bot

### 4. Running the Bot

```bash
python main.py
```

## Commands Overview

### Moderation Commands (Admin only)
- `!kick @user [reason]` - Kick a member
- `!ban @user [reason]` - Ban a member  
- `!mute @user [minutes] [reason]` - Mute a member
- `!unmute @user` - Unmute a member
- `!clear [amount]` - Delete messages (1-100)

### TTS Commands
- `!join` - Join your voice channel
- `!tts [text]` - Convert text to speech
- `!leave` - Leave voice channel
- `!stop` - Stop current audio

### Giveaway Commands (Admin only)
- `!giveaway [duration] [winners] [prize]` - Create giveaway
  - Duration: `1h`, `30m`, `1d` etc.
  - Example: `!giveaway 2h 1 Discord Nitro`
- `!gend [message_id]` - End giveaway early
- `!glist` - List active giveaways

### Welcome Commands (Admin only)
- `!welcomeset [#channel]` - Set welcome channel
- `!welcomemsg [message]` - Set custom message
  - Use `{user}` for mention, `{server}` for server name
- `!welcomecolor [#hex]` - Set embed color
- `!welcomeimage [url]` - Set welcome image
- `!welcometest [@user]` - Test welcome message
- `!welcomeconfig` - Show current config

### Keyword Commands (Admin only)
- `!addkeyword [keyword] [response]` - Add auto-response
- `!removekeyword [keyword]` - Remove keyword
- `!keywords` - List all keywords
- `!searchkeyword [keyword]` - Search specific keyword

### Utility Commands
- `!ping` - Check bot latency
- `!serverinfo` - Server information
- `!userinfo [@user]` - User information
- `!avatar [@user]` - User's avatar
- `!uptime` - Bot uptime
- `!botinfo` - Bot information
- `!help [command]` - Help information

### Slash Commands
All commands are also available as slash commands (use `/` instead of `!`)

## Bot Permissions Required

When inviting the bot, make sure to grant these permissions:
- **General**: View Channels, Send Messages, Embed Links, Add Reactions, Use Slash Commands
- **Text**: Manage Messages, Read Message History
- **Voice**: Connect, Speak, Use Voice Activity
- **Moderation**: Kick Members, Ban Members, Manage Roles, Manage Nicknames

## File Structure

```
discord-bot/
├── bot.py              # Main bot class and configuration
├── main.py             # Bot entry point
├── cogs/               # Bot modules
│   ├── moderation.py   # Kick, ban, mute commands
│   ├── tts.py          # Text-to-speech functionality
│   ├── giveaways.py    # Giveaway system
│   ├── welcome.py      # Welcome messages
│   ├── keywords.py     # Auto-response system
│   └── utility.py      # Utility commands
├── data/               # Data storage
│   ├── config.json     # Bot configuration
│   ├── giveaways.json  # Active giveaways
│   ├── keywords.json   # Keyword responses
│   └── welcome_configs.json # Welcome settings
├── .env                # Environment variables (create this)
├── .env.example        # Environment template
└── README.md           # This file
```

## Configuration Options

Edit `data/config.json` to customize:
```json
{
  "mute_role_name": "Muted",           // Name for mute role
  "max_giveaway_duration": 7200,      // Max giveaway length (seconds)
  "tts_max_length": 200                // Max TTS text length
}
```

## Troubleshooting

### Common Issues:

1. **"DISCORD_TOKEN not found"**
   - Make sure you created `.env` file with your bot token

2. **"PyNaCl not installed" warning**
   - This is normal - voice features still work without it
   - Install with: `pip install PyNaCl` (optional)

3. **Bot not responding to commands**
   - Check bot has proper permissions
   - Verify bot is online in Discord
   - Make sure you're using correct prefix (`!`)

4. **TTS not working**
   - Ensure FFmpeg is installed
   - Check bot has voice permissions
   - Bot must be in a voice channel

5. **Slash commands not appearing**
   - Wait a few minutes after bot startup
   - Try refreshing Discord or restarting it
   - Check bot has "Use Slash Commands" permission

### Getting Help:
- Use `!help` command for command list
- Check bot logs for error messages
- Ensure all dependencies are installed

## Features for External Hosting

This bot is designed for external hosting and includes:
- Comprehensive error handling
- Automatic file creation for data storage
- Environment variable configuration
- Modular cog-based architecture
- Both prefix and slash command support
- Detailed logging system
- Auto-reconnection handling

## License

This bot is provided as-is for educational and personal use.
