import discord
from discord.ext import commands
from discord import app_commands
import json
import logging

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_configs = self.load_welcome_configs()
    
    def load_welcome_configs(self):
        """Load welcome configurations for each guild"""
        try:
            with open('data/welcome_configs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logging.error("Error reading welcome_configs.json")
            return {}
    
    def save_welcome_configs(self):
        """Save welcome configurations"""
        try:
            with open('data/welcome_configs.json', 'w') as f:
                json.dump(self.welcome_configs, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving welcome configs: {e}")
    
    @commands.command(name='welcomeset')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the welcome channel"""
        if channel is None:
            channel = ctx.channel
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_configs:
            self.welcome_configs[guild_id] = {}
        
        self.welcome_configs[guild_id]['channel_id'] = channel.id
        self.save_welcome_configs()
        
        embed = discord.Embed(
            title="✅ Welcome Channel Set",
            description=f"Welcome messages will be sent to {channel.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='welcomemsg')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_message(self, ctx, *, message):
        """Set custom welcome message (use {user} for mention, {server} for server name)"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_configs:
            self.welcome_configs[guild_id] = {}
        
        self.welcome_configs[guild_id]['custom_message'] = message
        self.save_welcome_configs()
        
        embed = discord.Embed(
            title="✅ Welcome Message Set",
            description=f"Custom welcome message updated:\n\n{message}",
            color=0x00ff00
        )
        embed.add_field(
            name="Variables",
            value="`{user}` - User mention\n`{server}` - Server name\n`{username}` - Username\n`{membercount}` - Total members",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='welcomecolor')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_color(self, ctx, color: str):
        """Set welcome embed color (hex format: #FF0000)"""
        try:
            # Remove # if present and validate hex
            color = color.lstrip('#')
            if len(color) != 6:
                raise ValueError("Invalid hex color")
            
            # Convert to integer
            color_int = int(color, 16)
            
            guild_id = str(ctx.guild.id)
            if guild_id not in self.welcome_configs:
                self.welcome_configs[guild_id] = {}
            
            self.welcome_configs[guild_id]['embed_color'] = color_int
            self.save_welcome_configs()
            
            embed = discord.Embed(
                title="✅ Welcome Color Set",
                description=f"Welcome embed color updated to #{color.upper()}",
                color=color_int
            )
            await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Color",
                description="Please provide a valid hex color (e.g., #FF0000 or FF0000)",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='welcomeimage')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_image(self, ctx, image_url: str = None):
        """Set welcome embed image URL"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_configs:
            self.welcome_configs[guild_id] = {}
        
        if image_url:
            self.welcome_configs[guild_id]['image_url'] = image_url
            embed = discord.Embed(
                title="✅ Welcome Image Set",
                description="Welcome embed image updated",
                color=0x00ff00
            )
            embed.set_image(url=image_url)
        else:
            if 'image_url' in self.welcome_configs[guild_id]:
                del self.welcome_configs[guild_id]['image_url']
            embed = discord.Embed(
                title="✅ Welcome Image Removed",
                description="Welcome embed image has been removed",
                color=0x00ff00
            )
        
        self.save_welcome_configs()
        await ctx.send(embed=embed)
    
    @commands.command(name='welcometest')
    @commands.has_permissions(manage_guild=True)
    async def test_welcome(self, ctx, member: discord.Member = None):
        """Test the welcome message"""
        if member is None:
            member = ctx.author
        
        await self.send_welcome_message(member, test=True)
        
        embed = discord.Embed(
            title="✅ Welcome Test Sent",
            description=f"Test welcome message sent for {member.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='welcomedisable')
    @commands.has_permissions(manage_guild=True)
    async def disable_welcome(self, ctx):
        """Disable welcome messages"""
        guild_id = str(ctx.guild.id)
        if guild_id in self.welcome_configs:
            self.welcome_configs[guild_id]['enabled'] = False
            self.save_welcome_configs()
        
        embed = discord.Embed(
            title="✅ Welcome Messages Disabled",
            description="Welcome messages have been disabled for this server",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='welcomeenable')
    @commands.has_permissions(manage_guild=True)
    async def enable_welcome(self, ctx):
        """Enable welcome messages"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_configs:
            self.welcome_configs[guild_id] = {}
        
        self.welcome_configs[guild_id]['enabled'] = True
        self.save_welcome_configs()
        
        embed = discord.Embed(
            title="✅ Welcome Messages Enabled",
            description="Welcome messages have been enabled for this server",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='welcomeconfig')
    async def show_welcome_config(self, ctx):
        """Show current welcome configuration"""
        guild_id = str(ctx.guild.id)
        config = self.welcome_configs.get(guild_id, {})
        
        if not config:
            embed = discord.Embed(
                title="📋 Welcome Configuration",
                description="No welcome configuration set for this server.\nUse `!welcomeset` to get started!",
                color=0x0099ff
            )
            await ctx.send(embed=embed)
            return
        
        # Get channel
        channel_id = config.get('channel_id')
        channel = self.bot.get_channel(channel_id) if channel_id else None
        
        embed = discord.Embed(
            title="📋 Welcome Configuration",
            color=config.get('embed_color', 0x0099ff)
        )
        
        embed.add_field(
            name="Status",
            value="✅ Enabled" if config.get('enabled', True) else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Channel",
            value=channel.mention if channel else "❌ Not set",
            inline=True
        )
        
        embed.add_field(
            name="Color",
            value=f"#{config.get('embed_color', 0x0099ff):06X}",
            inline=True
        )
        
        if 'custom_message' in config:
            embed.add_field(
                name="Custom Message",
                value=config['custom_message'][:500] + ("..." if len(config['custom_message']) > 500 else ""),
                inline=False
            )
        
        if 'image_url' in config:
            embed.add_field(
                name="Image",
                value="✅ Set",
                inline=True
            )
            embed.set_thumbnail(url=config['image_url'])
        
        await ctx.send(embed=embed)
    
    async def send_welcome_message(self, member, test=False):
        """Send welcome message for new member"""
        guild_id = str(member.guild.id)
        config = self.welcome_configs.get(guild_id, {})
        
        # Check if welcome messages are enabled
        if not config.get('enabled', True):
            return
        
        # Get welcome channel
        channel_id = config.get('channel_id')
        if not channel_id:
            return
        
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
        
        try:
            # Create welcome embed
            embed_color = config.get('embed_color', 0x00ff7f)
            
            if 'custom_message' in config:
                # Use custom message
                message = config['custom_message']
                message = message.replace('{user}', member.mention)
                message = message.replace('{server}', member.guild.name)
                message = message.replace('{username}', member.display_name)
                message = message.replace('{membercount}', str(member.guild.member_count))
                
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=message,
                    color=embed_color
                )
            else:
                # Default welcome message
                embed = discord.Embed(
                    title="👋 Welcome to the server!",
                    description=f"Welcome {member.mention} to **{member.guild.name}**!\n\nYou are member #{member.guild.member_count}",
                    color=embed_color
                )
            
            # Set user avatar
            embed.set_thumbnail(url=member.display_avatar.url)
            
            # Set custom image if configured
            if 'image_url' in config:
                embed.set_image(url=config['image_url'])
            
            # Add footer
            embed.set_footer(
                text=f"Account created: {member.created_at.strftime('%B %d, %Y')}",
                icon_url=member.display_avatar.url
            )
            embed.timestamp = member.joined_at or member.created_at
            
            # Add test indicator if this is a test
            if test:
                embed.title = "🧪 " + embed.title + " (TEST)"
            
            await channel.send(embed=embed)
            
            if not test:
                logging.info(f"Welcome message sent for {member} in {member.guild.name}")
            
        except Exception as e:
            logging.error(f"Error sending welcome message: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Called when a member joins the server"""
        await self.send_welcome_message(member)
    
    # Slash command versions
    @app_commands.command(name="welcomeset", description="Set the welcome channel")
    @app_commands.describe(channel="The channel to send welcome messages")
    async def slash_welcomeset(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Slash command version of welcomeset"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You don't have permission to manage welcome settings.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.set_welcome_channel(ctx, channel)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
