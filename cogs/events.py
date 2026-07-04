import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_welcome_channel(self, guild):
        # Finds a channel named 'welcome-mat' or 'general'
        for channel in guild.text_channels:
            if channel.name == "welcome-mat":
                return channel
        for channel in guild.text_channels:
            if channel.name == "general":
                return channel
        return guild.system_channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.get_welcome_channel(member.guild)
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
        channel = self.get_welcome_channel(member.guild)
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
        if self.bot.user.mentioned_in(message) and not message.content.startswith(self.bot.command_prefix):
            import random
            responses = [
                "Suh dude?",
                "Need help? Just do /help",
                "Got a bug to report? DM GlexAomes.",
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
