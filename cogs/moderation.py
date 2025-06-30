import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import logging

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_users = {}  # Store muted users and their unmute times
    
    async def get_mute_role(self, guild):
        """Get or create the mute role"""
        mute_role_name = self.bot.config.get('mute_role_name', 'Muted')
        mute_role = discord.utils.get(guild.roles, name=mute_role_name)
        
        if not mute_role:
            # Create mute role
            try:
                mute_role = await guild.create_role(
                    name=mute_role_name,
                    color=discord.Color.dark_gray(),
                    reason="Mute role for moderation"
                )
                
                # Set permissions for mute role in all channels
                for channel in guild.channels:
                    try:
                        if isinstance(channel, discord.TextChannel):
                            await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(mute_role, speak=False)
                    except discord.Forbidden:
                        continue
                
                logging.info(f"Created mute role in guild {guild.name}")
            except discord.Forbidden:
                return None
        
        return mute_role
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Kick",
                description="You cannot kick someone with a higher or equal role.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Cannot Kick",
                description="You cannot kick yourself.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="You have been kicked",
                    description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}\n**Moderator:** {ctx.author}",
                    color=0xff6b35
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Kick the member
            await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Member Kicked",
                description=f"**Member:** {member}\n**Reason:** {reason}\n**Moderator:** {ctx.author}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            logging.info(f"Member {member} kicked from {ctx.guild.name} by {ctx.author}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Kick",
                description="I don't have permission to kick this member.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Ban",
                description="You cannot ban someone with a higher or equal role.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Cannot Ban",
                description="You cannot ban yourself.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="You have been banned",
                    description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}\n**Moderator:** {ctx.author}",
                    color=0xff0000
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Ban the member
            await member.ban(reason=f"Banned by {ctx.author}: {reason}")
            
            # Send confirmation
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**Member:** {member}\n**Reason:** {reason}\n**Moderator:** {ctx.author}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            
            logging.info(f"Member {member} banned from {ctx.guild.name} by {ctx.author}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Ban",
                description="I don't have permission to ban this member.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = None, *, reason="No reason provided"):
        """Mute a member (duration in minutes)"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Mute",
                description="You cannot mute someone with a higher or equal role.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Cannot Mute",
                description="You cannot mute yourself.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        mute_role = await self.get_mute_role(ctx.guild)
        if not mute_role:
            embed = discord.Embed(
                title="❌ Cannot Mute",
                description="Unable to create or find mute role.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if mute_role in member.roles:
            embed = discord.Embed(
                title="❌ Already Muted",
                description="This member is already muted.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Add mute role
            await member.add_roles(mute_role, reason=f"Muted by {ctx.author}: {reason}")
            
            # Calculate unmute time
            duration_str = "indefinitely"
            if duration:
                unmute_time = datetime.now() + timedelta(minutes=duration)
                self.muted_users[member.id] = unmute_time
                duration_str = f"for {duration} minutes"
                
                # Schedule unmute
                asyncio.create_task(self.schedule_unmute(member, unmute_time))
            
            # Send confirmation
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**Member:** {member}\n**Duration:** {duration_str}\n**Reason:** {reason}\n**Moderator:** {ctx.author}",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
            
            logging.info(f"Member {member} muted in {ctx.guild.name} by {ctx.author}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Mute",
                description="I don't have permission to mute this member.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member"""
        mute_role = await self.get_mute_role(ctx.guild)
        if not mute_role:
            embed = discord.Embed(
                title="❌ Cannot Unmute",
                description="Unable to find mute role.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if mute_role not in member.roles:
            embed = discord.Embed(
                title="❌ Not Muted",
                description="This member is not muted.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Remove mute role
            await member.remove_roles(mute_role, reason=f"Unmuted by {ctx.author}")
            
            # Remove from muted users dict
            if member.id in self.muted_users:
                del self.muted_users[member.id]
            
            # Send confirmation
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**Member:** {member}\n**Moderator:** {ctx.author}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            logging.info(f"Member {member} unmuted in {ctx.guild.name} by {ctx.author}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Unmute",
                description="I don't have permission to unmute this member.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    async def schedule_unmute(self, member, unmute_time):
        """Schedule automatic unmute"""
        await asyncio.sleep((unmute_time - datetime.now()).total_seconds())
        
        if member.id in self.muted_users:
            try:
                mute_role = await self.get_mute_role(member.guild)
                if mute_role and mute_role in member.roles:
                    await member.remove_roles(mute_role, reason="Automatic unmute")
                    del self.muted_users[member.id]
                    logging.info(f"Automatically unmuted {member} in {member.guild.name}")
            except Exception as e:
                logging.error(f"Error auto-unmuting {member}: {e}")
    
    @commands.command(name='clear', aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear messages from channel"""
        if amount <= 0 or amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between 1 and 100.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Delete the command message first
            await ctx.message.delete()
            
            # Delete the specified number of messages
            deleted = await ctx.channel.purge(limit=amount)
            
            # Send confirmation (will auto-delete)
            embed = discord.Embed(
                title="🗑️ Messages Cleared",
                description=f"Deleted {len(deleted)} messages.",
                color=0x00ff00
            )
            msg = await ctx.send(embed=embed)
            
            # Delete confirmation after 5 seconds
            await asyncio.sleep(5)
            await msg.delete()
            
            logging.info(f"Cleared {len(deleted)} messages in {ctx.guild.name} by {ctx.author}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Clear",
                description="I don't have permission to delete messages.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    # Slash command versions
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="The member to kick", reason="Reason for the kick")
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Slash command version of kick"""
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.kick(ctx, member, reason=reason)
    
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="The member to ban", reason="Reason for the ban")
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Slash command version of ban"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.ban(ctx, member, reason=reason)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
