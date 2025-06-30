import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil
import time
from datetime import datetime
import logging

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency"""
        start = time.perf_counter()
        message = await ctx.send("🏓 Pinging...")
        end = time.perf_counter()
        
        api_latency = round(self.bot.latency * 1000, 2)
        response_time = round((end - start) * 1000, 2)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Response Time", value=f"{response_time}ms", inline=True)
        
        await message.edit(content="", embed=embed)
    
    @commands.command(name='serverinfo', aliases=['si'])
    async def server_info(self, ctx):
        """Get server information"""
        guild = ctx.guild
        
        # Get member statistics
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        
        # Get channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Get role count
        roles = len(guild.roles) - 1  # Exclude @everyone
        
        # Verification level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Basic info
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        # Members
        embed.add_field(name="Members", value=f"👥 {total_members}\n👤 {humans} humans\n🤖 {bots} bots", inline=True)
        
        # Channels
        embed.add_field(name="Channels", value=f"💬 {text_channels} text\n🔊 {voice_channels} voice\n📁 {categories} categories", inline=True)
        
        # Other info
        embed.add_field(name="Roles", value=roles, inline=True)
        embed.add_field(name="Verification", value=verification_levels.get(guild.verification_level, "Unknown"), inline=True)
        embed.add_field(name="Boosts", value=f"{guild.premium_subscription_count} (Level {guild.premium_tier})", inline=True)
        
        # Features
        if guild.features:
            features = []
            feature_names = {
                'COMMUNITY': 'Community Server',
                'PARTNERED': 'Partnered',
                'VERIFIED': 'Verified',
                'NEWS': 'News Channels',
                'VANITY_URL': 'Vanity URL',
                'ANIMATED_ICON': 'Animated Icon',
                'BANNER': 'Banner',
                'WELCOME_SCREEN_ENABLED': 'Welcome Screen'
            }
            
            for feature in guild.features:
                if feature in feature_names:
                    features.append(feature_names[feature])
            
            if features:
                embed.add_field(name="Features", value='\n'.join(features[:5]), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='userinfo', aliases=['ui', 'whois'])
    async def user_info(self, ctx, member: discord.Member = None):
        """Get user information"""
        if member is None:
            member = ctx.author
        
        # Get roles (excluding @everyone)
        roles = [role.mention for role in member.roles[1:]]
        roles_text = ', '.join(roles) if roles else "None"
        if len(roles_text) > 1024:
            roles_text = f"{len(roles)} roles"
        
        # User status
        status_emojis = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic info
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Status", value=status_emojis.get(member.status, "Unknown"), inline=True)
        
        # Dates
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y\n%I:%M %p UTC"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y\n%I:%M %p UTC") if member.joined_at else "Unknown", inline=True)
        
        # Additional info
        if member.premium_since:
            embed.add_field(name="Boosting Since", value=member.premium_since.strftime("%B %d, %Y"), inline=True)
        
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        embed.add_field(name="Bot Account", value="Yes" if member.bot else "No", inline=True)
        
        # Permissions
        if member.guild_permissions.administrator:
            embed.add_field(name="Permissions", value="Administrator", inline=True)
        
        # Roles
        embed.add_field(name=f"Roles ({len(member.roles) - 1})", value=roles_text, inline=False)
        
        # Activities
        if member.activities:
            activities = []
            for activity in member.activities:
                if isinstance(activity, discord.Game):
                    activities.append(f"🎮 Playing {activity.name}")
                elif isinstance(activity, discord.Streaming):
                    activities.append(f"📺 Streaming {activity.name}")
                elif isinstance(activity, discord.Spotify):
                    activities.append(f"🎵 Listening to {activity.title} by {activity.artist}")
                elif isinstance(activity, discord.CustomActivity):
                    if activity.name:
                        activities.append(f"💭 {activity.name}")
            
            if activities:
                embed.add_field(name="Activities", value='\n'.join(activities[:3]), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='avatar', aliases=['av', 'pfp'])
    async def avatar(self, ctx, member: discord.Member = None):
        """Get user's avatar"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=member.color if member.color != discord.Color.default() else 0x0099ff
        )
        
        embed.set_image(url=member.display_avatar.url)
        
        # Add download link
        embed.add_field(
            name="Download",
            value=f"[PNG]({member.display_avatar.with_format('png').url}) | "
                  f"[JPG]({member.display_avatar.with_format('jpg').url}) | "
                  f"[WEBP]({member.display_avatar.with_format('webp').url})",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Show bot uptime"""
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_string = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"I've been online for **{uptime_string}**",
            color=0x00ff00
        )
        
        embed.add_field(name="Started", value=f"<t:{int(self.start_time)}:F>", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='botinfo')
    async def bot_info(self, ctx):
        """Show bot information"""
        # System info
        python_version = platform.python_version()
        discord_version = discord.__version__
        
        # Bot stats
        total_guilds = len(self.bot.guilds)
        total_users = len(self.bot.users)
        total_commands = len(self.bot.commands)
        
        # System resources
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_used = f"{memory.used / (1024**3):.1f} GB"
            memory_total = f"{memory.total / (1024**3):.1f} GB"
            memory_percent = memory.percent
        except:
            cpu_percent = "N/A"
            memory_used = memory_total = memory_percent = "N/A"
        
        embed = discord.Embed(
            title=f"🤖 {self.bot.user.name}",
            description="A multi-purpose Discord bot with moderation, TTS, giveaways, and more!",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Bot stats
        embed.add_field(name="Servers", value=total_guilds, inline=True)
        embed.add_field(name="Users", value=total_users, inline=True)
        embed.add_field(name="Commands", value=total_commands, inline=True)
        
        # System info
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="Discord.py Version", value=discord_version, inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        
        # Performance
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_used}/{memory_total} ({memory_percent}%)", inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx, command: str = None):
        """Show help information"""
        if command:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if not cmd:
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"No command named '{command}' found.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📖 Help: {cmd.name}",
                description=cmd.help or "No description available",
                color=0x0099ff
            )
            
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
            
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{cmd.name} {cmd.signature}`", inline=False)
            
            await ctx.send(embed=embed)
            return
        
        # Show general help
        embed = discord.Embed(
            title="📚 Bot Commands",
            description=f"Use `{ctx.prefix}help <command>` for detailed information about a command.",
            color=0x0099ff
        )
        
        # Organize commands by cog
        cog_commands = {}
        for command in self.bot.commands:
            if command.cog_name:
                if command.cog_name not in cog_commands:
                    cog_commands[command.cog_name] = []
                cog_commands[command.cog_name].append(command)
        
        # Display commands by category
        categories = {
            'Moderation': '🔨',
            'TTS': '🔊',
            'Giveaways': '🎉',
            'Welcome': '👋',
            'Keywords': '🔤',
            'Utility': '⚙️'
        }
        
        for cog_name, emoji in categories.items():
            if cog_name in cog_commands:
                commands_list = [f"`{cmd.name}`" for cmd in cog_commands[cog_name] if not cmd.hidden]
                if commands_list:
                    embed.add_field(
                        name=f"{emoji} {cog_name}",
                        value=" ".join(commands_list),
                        inline=False
                    )
        
        embed.add_field(
            name="🔗 Useful Links",
            value="• Use slash commands with `/`\n• Bot prefix: `!`\n• Need help? Ask an admin!",
            inline=False
        )
        
        embed.set_footer(text=f"Total Commands: {len([cmd for cmd in self.bot.commands if not cmd.hidden])}")
        
        await ctx.send(embed=embed)
    
    # Slash command versions
    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        """Slash command version of ping"""
        await interaction.response.defer()
        
        start = time.perf_counter()
        await interaction.followup.send("🏓 Pinging...")
        end = time.perf_counter()
        
        api_latency = round(self.bot.latency * 1000, 2)
        response_time = round((end - start) * 1000, 2)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Response Time", value=f"{response_time}ms", inline=True)
        
        await interaction.edit_original_response(content="", embed=embed)
    
    @app_commands.command(name="serverinfo", description="Get server information")
    async def slash_serverinfo(self, interaction: discord.Interaction):
        """Slash command version of serverinfo"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.server_info(ctx)
    
    @app_commands.command(name="userinfo", description="Get user information")
    @app_commands.describe(member="The member to get info about")
    async def slash_userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        """Slash command version of userinfo"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.user_info(ctx, member)

async def setup(bot):
    await bot.add_cog(Utility(bot))
