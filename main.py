#!/usr/bin/env python3
"""
Discord Bot Main Entry Point
Starts the bot and handles initial setup
"""

import asyncio
import os
from bot import DiscordBot

def main():
    """Main function to start the Discord bot"""
    try:
        # Create bot instance
        bot = DiscordBot()
        
        # Get token from environment
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("ERROR: DISCORD_TOKEN environment variable not found!")
            print("Please set your Discord bot token in the environment variables.")
            return
        
        # Run the bot
        bot.run(token)
        
    except KeyboardInterrupt:
        print("\nBot shutdown requested by user.")
    except Exception as e:
        print(f"Fatal error starting bot: {e}")

if __name__ == "__main__":
    main()
