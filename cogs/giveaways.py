import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import random
from datetime import datetime, timedelta
import logging

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = self.load_giveaways()
        
        # Start giveaway checker task
        self.bot.loop.create_task(self.check_giveaways())
    
    def load_giveaways(self):
        """Load giveaways from JSON file"""
        try:
            with open('data/giveaways.json', 'r') as f:
                data = json.load(f)
                # Convert timestamp strings back to datetime objects
                for giveaway_id, giveaway in data.items():
                    giveaway['end_time'] = datetime.fromisoformat(giveaway['end_time'])
                return data
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logging.error("Error reading giveaways.json")
            return {}
    
    def save_giveaways(self):
        """Save giveaways to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data = {}
            for giveaway_id, giveaway in self.giveaways.items():
                data[giveaway_id] = giveaway.copy()
                data[giveaway_id]['end_time'] = giveaway['end_time'].isoformat()
            
            with open('data/giveaways.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving giveaways: {e}")
    
    @commands.command(name='giveaway', aliases=['gcreate'])
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, duration: str, winners: int, *, prize):
        """Create a giveaway (duration format: 1h, 30m, 1d)"""
        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Duration format: `1h` (hours), `30m` (minutes), `1d` (days)\nExample: `!giveaway 2h 1 Discord Nitro`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        max_duration = self.bot.config.get('max_giveaway_duration', 7200)  # 2 hours default
        if duration_seconds > max_duration:
            embed = discord.Embed(
                title="❌ Duration Too Long",
                description=f"Maximum giveaway duration is {max_duration // 3600} hours.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if winners < 1 or winners > 20:
            embed = discord.Embed(
                title="❌ Invalid Winner Count",
                description="Number of winners must be between 1 and 20.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate end time
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        # Create giveaway embed
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>\n**Hosted by:** {ctx.author.mention}",
            color=0xff6b9d
        )
        embed.add_field(name="How to Enter", value="React with 🎉 to enter!", inline=False)
        embed.set_footer(text=f"Ends at")
        embed.timestamp = end_time
        
        # Send giveaway message
        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("🎉")
        
        # Store giveaway data
        giveaway_id = str(giveaway_msg.id)
        self.giveaways[giveaway_id] = {
            'message_id': giveaway_msg.id,
            'channel_id': ctx.channel.id,
            'guild_id': ctx.guild.id,
            'host_id': ctx.author.id,
            'prize': prize,
            'winners': winners,
            'end_time': end_time,
            'active': True,
            'participants': []
        }
        
        self.save_giveaways()
        logging.info(f"Giveaway created in {ctx.guild.name} by {ctx.author}")
    
    def parse_duration(self, duration_str):
        """Parse duration string (e.g., '1h', '30m', '2d') into seconds"""
        try:
            if duration_str.endswith('s'):
                return int(duration_str[:-1])
            elif duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith('d'):
                return int(duration_str[:-1]) * 86400
            else:
                return None
        except ValueError:
            return None
    
    @commands.command(name='gend')
    @commands.has_permissions(manage_guild=True)
    async def end_giveaway(self, ctx, message_id: int):
        """Manually end a giveaway"""
        giveaway_id = str(message_id)
        
        if giveaway_id not in self.giveaways:
            embed = discord.Embed(
                title="❌ Giveaway Not Found",
                description="No active giveaway found with that message ID.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        giveaway = self.giveaways[giveaway_id]
        if not giveaway['active']:
            embed = discord.Embed(
                title="❌ Giveaway Already Ended",
                description="This giveaway has already ended.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # End the giveaway
        await self.end_giveaway_process(giveaway_id)
        
        embed = discord.Embed(
            title="✅ Giveaway Ended",
            description="The giveaway has been manually ended.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    async def end_giveaway_process(self, giveaway_id):
        """Process ending a giveaway"""
        giveaway = self.giveaways[giveaway_id]
        
        try:
            # Get the giveaway message
            channel = self.bot.get_channel(giveaway['channel_id'])
            if not channel:
                return
            
            message = await channel.fetch_message(giveaway['message_id'])
            if not message:
                return
            
            # Get participants from reactions
            participants = []
            for reaction in message.reactions:
                if str(reaction.emoji) == "🎉":
                    async for user in reaction.users():
                        if not user.bot:
                            participants.append(user)
            
            # Select winners
            winners = []
            if participants:
                num_winners = min(giveaway['winners'], len(participants))
                winners = random.sample(participants, num_winners)
            
            # Update giveaway embed
            if winners:
                winner_mentions = ", ".join([winner.mention for winner in winners])
                embed = discord.Embed(
                    title="🎉 GIVEAWAY ENDED! 🎉",
                    description=f"**Prize:** {giveaway['prize']}\n**Winners:** {winner_mentions}\n**Participants:** {len(participants)}",
                    color=0x00ff00
                )
                embed.set_footer(text="Giveaway ended")
                embed.timestamp = datetime.now()
                
                # Announce winners
                announcement = f"🎉 **Congratulations {winner_mentions}!** 🎉\nYou won **{giveaway['prize']}**!"
                await channel.send(announcement)
            else:
                embed = discord.Embed(
                    title="🎉 GIVEAWAY ENDED! 🎉",
                    description=f"**Prize:** {giveaway['prize']}\n**Winners:** No valid participants\n**Participants:** 0",
                    color=0xff0000
                )
                embed.set_footer(text="Giveaway ended")
                embed.timestamp = datetime.now()
                
                await channel.send("🎉 Giveaway ended, but no one participated! 😢")
            
            await message.edit(embed=embed)
            
            # Mark giveaway as ended
            giveaway['active'] = False
            self.save_giveaways()
            
            logging.info(f"Giveaway ended in {channel.guild.name}, {len(winners)} winners selected")
            
        except Exception as e:
            logging.error(f"Error ending giveaway {giveaway_id}: {e}")
    
    async def check_giveaways(self):
        """Background task to check for ended giveaways"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                current_time = datetime.now()
                ended_giveaways = []
                
                for giveaway_id, giveaway in self.giveaways.items():
                    if giveaway['active'] and current_time >= giveaway['end_time']:
                        ended_giveaways.append(giveaway_id)
                
                for giveaway_id in ended_giveaways:
                    await self.end_giveaway_process(giveaway_id)
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in giveaway checker: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    @commands.command(name='glist')
    async def list_giveaways(self, ctx):
        """List active giveaways"""
        active_giveaways = [g for g in self.giveaways.values() if g['active'] and g['guild_id'] == ctx.guild.id]
        
        if not active_giveaways:
            embed = discord.Embed(
                title="📋 Active Giveaways",
                description="No active giveaways in this server.",
                color=0x0099ff
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Active Giveaways",
            color=0x0099ff
        )
        
        for giveaway in active_giveaways[:10]:  # Limit to 10
            channel = self.bot.get_channel(giveaway['channel_id'])
            channel_mention = channel.mention if channel else "Unknown Channel"
            
            embed.add_field(
                name=f"🎉 {giveaway['prize']}",
                value=f"**Channel:** {channel_mention}\n**Winners:** {giveaway['winners']}\n**Ends:** <t:{int(giveaway['end_time'].timestamp())}:R>",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    # Slash command versions
    @app_commands.command(name="giveaway", description="Create a giveaway")
    @app_commands.describe(
        duration="Duration (e.g., 1h, 30m, 1d)",
        winners="Number of winners",
        prize="What are you giving away?"
    )
    async def slash_giveaway(self, interaction: discord.Interaction, duration: str, winners: int, prize: str):
        """Slash command version of giveaway creation"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You don't have permission to create giveaways.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.create_giveaway(ctx, duration, winners, prize=prize)

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
