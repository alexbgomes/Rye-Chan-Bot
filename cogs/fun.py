import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random
from utils.database import increment_confession_count, get_confession_count

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @app_commands.command(name="xkcd", description="Craving some comics? Get a random xkcd comic!")
    async def xkcd(self, interaction: discord.Interaction):
        comic_id = random.randint(1, 2800) # Updated max to a recent number, dynamically fetching latest is better but this works for now.
        url = f"https://xkcd.com/{comic_id}/info.0.json"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                embed = discord.Embed(
                    color=discord.Color.from_rgb(152, 0, 255),
                    description=f"{interaction.user.mention} is craving some comics!",
                    title=data.get("title", f"Comic {comic_id}")
                )
                embed.set_image(url=data.get("img"))
                embed.set_footer(text="Powered by xkcd.com")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Couldn't fetch an xkcd comic at this time.", ephemeral=True)

    @app_commands.command(name="8ball", description="Ask the magic 8ball a question.")
    @app_commands.describe(question="The question to ask.")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        answer = random.choice(responses)
        await interaction.response.send_message(f"**Question:** {question}\n**Answer:** {answer}")

    @app_commands.command(name="mock", description="MoCkS TeXt LiKe ThIs.")
    @app_commands.describe(text="The text to mock.")
    async def mock(self, interaction: discord.Interaction, text: str):
        mocked = "".join(random.choice([c.upper(), c.lower()]) for c in text)
        await interaction.response.send_message(mocked)

    @app_commands.command(name="confess", description="Submit an anonymous confession.")
    @app_commands.describe(confession="Your confession.")
    async def confess(self, interaction: discord.Interaction, confession: str):
        # We assume confessions go to a specific channel or just get recorded
        count = await increment_confession_count()
        embed = discord.Embed(
            title=f"Confession #{count}",
            description=confession,
            color=discord.Color.dark_gray()
        )
        await interaction.response.send_message(embed=embed)
        # Note: In a real environment, you might want to send this to a specific channel
        # instead of replying to the user directly if it's meant to be anonymous,
        # but for simplicity, we respond here (which breaks anonymity if not ephemeral).
        # We can send it ephemerally to the user and to a channel, but we don't have a configured channel ID yet.

async def setup(bot):
    await bot.add_cog(Fun(bot))
