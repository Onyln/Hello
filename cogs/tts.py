import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import tempfile
import logging
from gtts import gTTS

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Store voice clients for each guild
    
    @commands.command(name='join')
    async def join(self, ctx):
        """Join the voice channel"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Not in Voice Channel",
                description="You need to be in a voice channel for me to join.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            try:
                voice_client = await channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
                
                embed = discord.Embed(
                    title="🎤 Joined Voice Channel",
                    description=f"Connected to {channel.name}",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
                
            except discord.ClientException:
                embed = discord.Embed(
                    title="❌ Connection Failed",
                    description="Failed to connect to voice channel.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
    
    @commands.command(name='leave', aliases=['disconnect'])
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client is None:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.disconnect()
        if ctx.guild.id in self.voice_clients:
            del self.voice_clients[ctx.guild.id]
        
        embed = discord.Embed(
            title="👋 Left Voice Channel",
            description="Disconnected from voice channel.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='tts', aliases=['speak'])
    async def tts(self, ctx, *, text):
        """Convert text to speech and play in voice channel"""
        # Check if bot is in voice channel
        if ctx.voice_client is None:
            # Try to join user's voice channel
            if ctx.author.voice:
                await self.join(ctx)
            else:
                embed = discord.Embed(
                    title="❌ No Voice Connection",
                    description="I need to be in a voice channel to use TTS. Join a voice channel and use `!join` first.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
        
        # Check text length
        max_length = self.bot.config.get('tts_max_length', 200)
        if len(text) > max_length:
            embed = discord.Embed(
                title="❌ Text Too Long",
                description=f"Text must be {max_length} characters or less. Your text is {len(text)} characters.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Check if already playing audio
        if ctx.voice_client.is_playing():
            embed = discord.Embed(
                title="⏳ Audio Playing",
                description="Please wait for the current audio to finish.",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Create TTS audio
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_filename = temp_file.name
                tts.save(temp_filename)
            
            # Play audio
            source = discord.FFmpegPCMAudio(temp_filename)
            ctx.voice_client.play(source, after=lambda e: self.cleanup_temp_file(temp_filename, e))
            
            embed = discord.Embed(
                title="🔊 Playing TTS",
                description=f"**Text:** {text[:100]}{'...' if len(text) > 100 else ''}\n**Requested by:** {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            logging.info(f"TTS played in {ctx.guild.name} by {ctx.author}")
            
        except Exception as e:
            logging.error(f"TTS error: {e}")
            embed = discord.Embed(
                title="❌ TTS Error",
                description="Failed to generate or play text-to-speech audio.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    def cleanup_temp_file(self, filename, error):
        """Clean up temporary TTS file after playback"""
        try:
            os.unlink(filename)
        except Exception as e:
            logging.error(f"Error cleaning up temp file {filename}: {e}")
        
        if error:
            logging.error(f"Audio playback error: {error}")
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop current audio playback"""
        if ctx.voice_client is None:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            embed = discord.Embed(
                title="⏹️ Stopped Audio",
                description="Stopped current audio playback.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Nothing Playing",
                description="No audio is currently playing.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='volume')
    async def volume(self, ctx, vol: int = None):
        """Change or view volume (0-100)"""
        if ctx.voice_client is None:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if vol is None:
            # Show current volume
            current_vol = int(ctx.voice_client.source.volume * 100) if hasattr(ctx.voice_client.source, 'volume') else 100
            embed = discord.Embed(
                title="🔊 Current Volume",
                description=f"Volume is set to {current_vol}%",
                color=0x0099ff
            )
            await ctx.send(embed=embed)
            return
        
        if vol < 0 or vol > 100:
            embed = discord.Embed(
                title="❌ Invalid Volume",
                description="Volume must be between 0 and 100.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if hasattr(ctx.voice_client.source, 'volume'):
            ctx.voice_client.source.volume = vol / 100
            embed = discord.Embed(
                title="🔊 Volume Changed",
                description=f"Volume set to {vol}%",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Cannot Change Volume",
                description="Volume control is not available for the current audio source.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    # Slash command versions
    @app_commands.command(name="join", description="Join your voice channel")
    async def slash_join(self, interaction: discord.Interaction):
        """Slash command version of join"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.join(ctx)
    
    @app_commands.command(name="tts", description="Convert text to speech")
    @app_commands.describe(text="The text to convert to speech")
    async def slash_tts(self, interaction: discord.Interaction, text: str):
        """Slash command version of TTS"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.tts(ctx, text=text)
    
    @app_commands.command(name="leave", description="Leave the voice channel")
    async def slash_leave(self, interaction: discord.Interaction):
        """Slash command version of leave"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.leave(ctx)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""
        # If bot is alone in voice channel, leave after 5 minutes
        if member == self.bot.user:
            return
        
        guild = member.guild
        if guild.id not in self.voice_clients:
            return
        
        voice_client = self.voice_clients[guild.id]
        if not voice_client or not voice_client.channel:
            return
        
        # Check if bot is alone
        members_in_channel = [m for m in voice_client.channel.members if not m.bot]
        if len(members_in_channel) == 0:
            # Wait 5 minutes then leave if still alone
            await asyncio.sleep(300)  # 5 minutes
            
            # Check again if still alone
            members_in_channel = [m for m in voice_client.channel.members if not m.bot]
            if len(members_in_channel) == 0 and voice_client.is_connected():
                await voice_client.disconnect()
                if guild.id in self.voice_clients:
                    del self.voice_clients[guild.id]
                logging.info(f"Left voice channel in {guild.name} due to inactivity")

async def setup(bot):
    await bot.add_cog(TTS(bot))
