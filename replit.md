# Overview

This is a comprehensive multi-purpose Discord bot built with Python using the discord.py library. The bot provides moderation tools, text-to-speech functionality, giveaway management, welcome messages, keyword auto-responses, and various utility commands. It features both traditional prefix commands and modern slash commands for enhanced user experience.

## System Architecture

The bot follows a modular cog-based architecture that separates different functionalities into distinct modules. This design promotes maintainability, scalability, and code organization.

### Core Components:
- **Main Bot Class**: `DiscordBot` in `bot.py` - Handles initialization, configuration loading, and core bot setup
- **Entry Point**: `main.py` - Manages bot startup and error handling
- **Cogs System**: Modular functionality split across multiple cog files in the `/cogs` directory

### Data Storage:
- **File-based storage**: JSON files in `/data` directory for persistent configuration and data
- **In-memory storage**: Temporary data like voice clients and muted users stored in memory

## Key Components

### 1. Moderation System (`cogs/moderation.py`)
- **Problem**: Need for server moderation capabilities
- **Solution**: Comprehensive moderation commands with permission checking
- **Features**: Kick, ban, mute/unmute with timers, message clearing, role-based permissions
- **Auto-mute role creation**: Dynamically creates and configures mute roles with appropriate channel permissions

### 2. Text-to-Speech (`cogs/tts.py`)
- **Problem**: Voice channel engagement and accessibility
- **Solution**: Google TTS integration with voice channel connectivity
- **Features**: Voice joining/leaving, text-to-speech conversion, auto-disconnect functionality
- **Dependencies**: gtts library for text-to-speech conversion

### 3. Giveaway System (`cogs/giveaways.py`)
- **Problem**: Community engagement through contests
- **Solution**: Automated giveaway management with reaction-based entry
- **Features**: Timed giveaways, automatic winner selection, persistent storage
- **Background tasks**: Continuous monitoring for giveaway completion

### 4. Welcome System (`cogs/welcome.py`)
- **Problem**: New member onboarding
- **Solution**: Customizable welcome messages with rich embeds
- **Features**: Channel configuration, user information display, custom formatting

### 5. Keyword Auto-Response (`cogs/keywords.py`)
- **Problem**: Automated responses to common phrases
- **Solution**: Smart keyword detection with multiple response options
- **Features**: Case-insensitive matching, easy management, random response selection

### 6. Utility Commands (`cogs/utility.py`)
- **Problem**: Server information and bot diagnostics
- **Solution**: Comprehensive utility commands for server management
- **Features**: Server/user info, bot statistics, latency checking, help system

## Data Flow

### Configuration Management:
1. Bot loads configuration from `data/config.json` on startup
2. Each cog manages its own data files (giveaways.json, keywords.json, welcome_configs.json)
3. Changes are persisted immediately to JSON files

### Command Processing:
1. Discord sends message/interaction to bot
2. discord.py library routes to appropriate command handler
3. Cog processes command with permission checks
4. Response sent back to Discord channel
5. Data persistence occurs if needed

### Event Handling:
1. Discord events (member join, message send) trigger bot listeners
2. Bot processes events through appropriate cog handlers
3. Automated responses or actions executed based on configuration

## External Dependencies

### Required Libraries:
- **discord.py**: Core Discord API interaction
- **gtts**: Google Text-to-Speech for voice functionality
- **python-dotenv**: Environment variable management
- **psutil**: System information for utility commands

### Discord Permissions Required:
- Message content intent for keyword detection
- Members intent for welcome messages
- Voice states intent for TTS functionality
- Various server permissions (kick, ban, manage roles, etc.)

### Environment Variables:
- `DISCORD_TOKEN`: Bot authentication token
- `BOT_PREFIX`: Command prefix (defaults to '!')

## Deployment Strategy

### Local Development:
- Environment variables loaded from `.env` file
- JSON data files created automatically in `/data` directory
- Logging configured for both file and console output

### Production Considerations:
- Bot token must be securely stored as environment variable
- Data directory requires write permissions for persistence
- Voice functionality requires stable network connection
- Consider database migration for larger deployments

### Scalability Notes:
- Current file-based storage suitable for small to medium servers
- May require database backend (PostgreSQL) for high-traffic deployments
- In-memory data structures may need Redis backing for distributed deployment

## Changelog
```
Changelog:
- June 30, 2025. Complete Discord bot implementation with all requested features
  - Moderation system (kick, ban, mute with timers, clear messages)
  - Text-to-speech functionality with voice channel integration
  - Giveaway system with timed events and embed displays
  - Welcome system with customizable join embeds
  - Keyword auto-response system for common phrases
  - Slash command support for all major features
  - Comprehensive documentation and deployment guides
  - External hosting-ready with environment configuration
```

## User Preferences
```
Preferred communication style: Simple, everyday language.
```