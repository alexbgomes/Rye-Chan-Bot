import discord
from discord.ext import commands
from discord import app_commands
from utils import database

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="toggle_greetings", description="Toggles automatic join/leave messages for this channel.")
    @app_commands.default_permissions(manage_channels=True)
    async def toggle_greetings(self, interaction: discord.Interaction):
        current_channel_id = await database.get_greeting_channel(interaction.guild_id)
        if current_channel_id:
            # Disable it by setting to None
            await database.set_greeting_channel(interaction.guild_id, None)
            await interaction.response.send_message("Automatic greetings have been **disabled** for this server.", ephemeral=True)
        else:
            # Enable it in the current channel
            await database.set_greeting_channel(interaction.guild_id, interaction.channel_id)
            await interaction.response.send_message(f"Automatic greetings have been **enabled** and bound to {interaction.channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = await database.get_greeting_channel(member.guild.id)
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if channel:
            uCount = member.guild.member_count
            
            # Simple suffix logic
            if uCount % 10 == 1 and uCount % 100 != 11:
                suffix = "st"
            elif uCount % 10 == 2 and uCount % 100 != 12:
                suffix = "nd"
            elif uCount % 10 == 3 and uCount % 100 != 13:
                suffix = "rd"
            else:
                suffix = "th"

            msg = f"Welcome to the {member.guild.name}, {member.mention}, what's good?\nYou are the {uCount}{suffix} person in the server!"
            await channel.send(msg)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = await database.get_greeting_channel(member.guild.id)
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if channel:
            person = member.nick if member.nick else member.name
            uCount = member.guild.member_count
            msg = f"Damn, looks like **{person}** left.\nThere are now {uCount} people in the {member.guild.name}!"
            await channel.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Passive live response if bot is mentioned (similar to Protocol in C# bot)
        if self.bot.user.mentioned_in(message) and not message.content.startswith("!"):
            import random
            responses = [
                "Suh dude?",
                "Need help? Just do /help",
                "Got a bug to report? DM Glex.",
                "How's life?",
                "Hey",
                "Hiya",
                "Feeling lonely?",
                "You do know that I'm not a real person... Right?",
                "Someone mentioned me?",
                f"{message.author.mention}, yes?",
                "This isn't an anime, ok?"
            ]
            await message.channel.send(random.choice(responses))

async def setup(bot):
    await bot.add_cog(Events(bot))
