import discord
from discord.ext import commands
from discord import app_commands
import json
import re
import logging

class Keywords(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keywords = self.load_keywords()
    
    def load_keywords(self):
        """Load keywords and responses from JSON file"""
        try:
            with open('data/keywords.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default keywords
            default_keywords = {
                "hello": ["Hello there! 👋", "Hi! How are you doing?", "Hey! Welcome!"],
                "thanks": ["You're welcome! 😊", "No problem!", "Happy to help!"],
                "help": ["Need help? Use `!help` to see available commands!", "I'm here to help! Try `!help`"],
                "good morning": ["Good morning! ☀️", "Morning! Have a great day!"],
                "good night": ["Good night! 🌙", "Sweet dreams!", "Sleep well!"],
                "how are you": ["I'm doing great! Thanks for asking 😊", "I'm fine, how about you?"],
                "bot": ["Yes, I'm a bot! 🤖", "Beep boop! I'm a helpful bot!"],
                "ping": ["Pong! 🏓"]
            }
            self.save_keywords(default_keywords)
            return default_keywords
        except json.JSONDecodeError:
            logging.error("Error reading keywords.json")
            return {}
    
    def save_keywords(self, keywords=None):
        """Save keywords to JSON file"""
        try:
            if keywords is None:
                keywords = self.keywords
            with open('data/keywords.json', 'w') as f:
                json.dump(keywords, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving keywords: {e}")
    
    @commands.command(name='addkeyword')
    @commands.has_permissions(manage_guild=True)
    async def add_keyword(self, ctx, keyword: str, *, response: str):
        """Add a keyword response"""
        keyword = keyword.lower()
        
        if keyword in self.keywords:
            if response not in self.keywords[keyword]:
                self.keywords[keyword].append(response)
            else:
                embed = discord.Embed(
                    title="❌ Response Already Exists",
                    description=f"This response already exists for keyword '{keyword}'",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
        else:
            self.keywords[keyword] = [response]
        
        self.save_keywords()
        
        embed = discord.Embed(
            title="✅ Keyword Added",
            description=f"**Keyword:** {keyword}\n**Response:** {response}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='removekeyword', aliases=['delkeyword'])
    @commands.has_permissions(manage_guild=True)
    async def remove_keyword(self, ctx, keyword: str, response_index: int = None):
        """Remove a keyword or specific response"""
        keyword = keyword.lower()
        
        if keyword not in self.keywords:
            embed = discord.Embed(
                title="❌ Keyword Not Found",
                description=f"Keyword '{keyword}' doesn't exist",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if response_index is None:
            # Remove entire keyword
            del self.keywords[keyword]
            embed = discord.Embed(
                title="✅ Keyword Removed",
                description=f"Keyword '{keyword}' and all its responses have been removed",
                color=0x00ff00
            )
        else:
            # Remove specific response
            try:
                response_index -= 1  # Convert to 0-indexed
                if 0 <= response_index < len(self.keywords[keyword]):
                    removed_response = self.keywords[keyword].pop(response_index)
                    
                    # If no responses left, remove the keyword
                    if not self.keywords[keyword]:
                        del self.keywords[keyword]
                        embed = discord.Embed(
                            title="✅ Response Removed",
                            description=f"Last response removed for '{keyword}'. Keyword deleted.",
                            color=0x00ff00
                        )
                    else:
                        embed = discord.Embed(
                            title="✅ Response Removed",
                            description=f"**Keyword:** {keyword}\n**Removed:** {removed_response}",
                            color=0x00ff00
                        )
                else:
                    embed = discord.Embed(
                        title="❌ Invalid Index",
                        description=f"Response index must be between 1 and {len(self.keywords[keyword])}",
                        color=0xff0000
                    )
                    await ctx.send(embed=embed)
                    return
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Index",
                    description="Response index must be a number",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
        
        self.save_keywords()
        await ctx.send(embed=embed)
    
    @commands.command(name='keywords', aliases=['listkeywords'])
    async def list_keywords(self, ctx):
        """List all keywords and their responses"""
        if not self.keywords:
            embed = discord.Embed(
                title="📋 Keywords",
                description="No keywords configured. Use `!addkeyword` to add some!",
                color=0x0099ff
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Keywords & Responses",
            color=0x0099ff
        )
        
        keyword_list = []
        for i, (keyword, responses) in enumerate(self.keywords.items(), 1):
            if i > 10:  # Limit to 10 keywords to avoid embed limits
                keyword_list.append(f"... and {len(self.keywords) - 10} more")
                break
            
            responses_text = '\n'.join([f"  {j}. {resp[:50]}{'...' if len(resp) > 50 else ''}" 
                                      for j, resp in enumerate(responses, 1)])
            keyword_list.append(f"**{keyword}**\n{responses_text}")
        
        embed.description = '\n\n'.join(keyword_list)
        
        if len(self.keywords) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.keywords)} keywords")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='searchkeyword')
    async def search_keyword(self, ctx, *, keyword: str):
        """Search for a specific keyword"""
        keyword = keyword.lower()
        
        if keyword not in self.keywords:
            embed = discord.Embed(
                title="❌ Keyword Not Found",
                description=f"No responses found for '{keyword}'",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        responses = self.keywords[keyword]
        embed = discord.Embed(
            title=f"🔍 Keyword: {keyword}",
            color=0x0099ff
        )
        
        responses_text = '\n'.join([f"{i}. {resp}" for i, resp in enumerate(responses, 1)])
        embed.description = responses_text
        embed.set_footer(text=f"{len(responses)} response(s)")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='keywordstats')
    async def keyword_stats(self, ctx):
        """Show keyword statistics"""
        if not self.keywords:
            embed = discord.Embed(
                title="📊 Keyword Statistics",
                description="No keywords configured.",
                color=0x0099ff
            )
            await ctx.send(embed=embed)
            return
        
        total_keywords = len(self.keywords)
        total_responses = sum(len(responses) for responses in self.keywords.values())
        avg_responses = total_responses / total_keywords if total_keywords > 0 else 0
        
        # Find most/least responses
        most_responses = max(self.keywords.items(), key=lambda x: len(x[1]))
        least_responses = min(self.keywords.items(), key=lambda x: len(x[1]))
        
        embed = discord.Embed(
            title="📊 Keyword Statistics",
            color=0x0099ff
        )
        
        embed.add_field(name="Total Keywords", value=str(total_keywords), inline=True)
        embed.add_field(name="Total Responses", value=str(total_responses), inline=True)
        embed.add_field(name="Avg. Responses/Keyword", value=f"{avg_responses:.1f}", inline=True)
        embed.add_field(name="Most Responses", value=f"{most_responses[0]} ({len(most_responses[1])})", inline=True)
        embed.add_field(name="Least Responses", value=f"{least_responses[0]} ({len(least_responses[1])})", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for keywords in messages"""
        # Ignore bot messages and commands
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return
        
        # Check for keywords in message
        message_content = message.content.lower()
        
        for keyword, responses in self.keywords.items():
            # Check if keyword is in message (word boundary matching)
            if re.search(r'\b' + re.escape(keyword) + r'\b', message_content):
                try:
                    # Pick a random response
                    import random
                    response = random.choice(responses)
                    await message.channel.send(response)
                    logging.info(f"Keyword '{keyword}' triggered in {message.guild.name}")
                    break  # Only respond to first matched keyword
                except Exception as e:
                    logging.error(f"Error responding to keyword '{keyword}': {e}")
    
    # Slash command versions
    @app_commands.command(name="addkeyword", description="Add a keyword response")
    @app_commands.describe(keyword="The keyword to respond to", response="The response message")
    async def slash_add_keyword(self, interaction: discord.Interaction, keyword: str, response: str):
        """Slash command version of add keyword"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You don't have permission to manage keywords.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.add_keyword(ctx, keyword, response=response)
    
    @app_commands.command(name="keywords", description="List all keywords")
    async def slash_keywords(self, interaction: discord.Interaction):
        """Slash command version of keywords list"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.list_keywords(ctx)

async def setup(bot):
    await bot.add_cog(Keywords(bot))
