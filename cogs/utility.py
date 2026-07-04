import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Replies with the bot's latency (Pong!)")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"{interaction.user.mention} Pong! {latency} ms :ping_pong:")

    @app_commands.command(name="about", description="About Rye-Chan-Bot")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="About Rye-Chan",
            description="Rye-Chan is a multi-purpose Discord bot originally written in C# and rewritten in Python.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Version", value="V3.0", inline=True)
        embed.add_field(name="Developer", value="Glex", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Shows a list of available commands")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Command List",
            description="Here are the commands you can use:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Utility", value="`/ping`, `/about`, `/help`", inline=False)
        embed.add_field(name="Fun", value="`/xkcd`, `/8ball`, `/mock`", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
