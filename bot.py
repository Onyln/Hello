import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class DiscordBot(commands.Bot):
    def __init__(self):
        # Bot configuration
        self.prefix = os.getenv('BOT_PREFIX', '!')
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        intents.guilds = True
        
        # Initialize bot
        super().__init__(
            command_prefix=self.prefix,
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load bot configuration from config.json"""
        try:
            with open('data/config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Create default config
            self.config = {
                "welcome_channel_id": None,
                "log_channel_id": None,
                "mute_role_name": "Muted",
                "max_giveaway_duration": 7200,  # 2 hours in seconds
                "tts_max_length": 200
            }
            self.save_config()
        except json.JSONDecodeError:
            logging.error("Error reading config.json - using default configuration")
            self.config = {}
    
    def save_config(self):
        """Save bot configuration to config.json"""
        try:
            with open('data/config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        cogs = [
            'cogs.moderation',
            'cogs.tts',
            'cogs.giveaways',
            'cogs.welcome',
            'cogs.keywords',
            'cogs.utility'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logging.info(f"Loaded cog: {cog}")
            except Exception as e:
                logging.error(f"Failed to load cog {cog}: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logging.error(f"Failed to sync slash commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logging.info(f"{self.user} has connected to Discord!")
        logging.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{self.prefix}help | Serving {len(self.guilds)} servers"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have the required permissions to use this command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I don't have the required permissions to execute this command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Arguments",
                description=f"Please provide all required arguments.\nUsage: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
        
        else:
            logging.error(f"Unhandled error in command {ctx.command}: {error}")
            embed = discord.Embed(
                title="❌ An Error Occurred",
                description="An unexpected error occurred while processing your command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        logging.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Update bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{self.prefix}help | Serving {len(self.guilds)} servers"
            )
        )
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logging.info(f"Left guild: {guild.name} (ID: {guild.id})")
        
        # Update bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{self.prefix}help | Serving {len(self.guilds)} servers"
            )
        )
