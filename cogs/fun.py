import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random
import urllib.parse
from utils.database import increment_confession_count, get_confession_count

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @app_commands.command(name="xkcd", description="Craving some comics? Get a random xkcd comic!")
    async def xkcd(self, interaction: discord.Interaction):
        comic_id = random.randint(1, 2800)
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

    @app_commands.command(name="confess", description="Submit an anonymous confession instantly.")
    @app_commands.describe(confession="Your confession.")
    async def confess(self, interaction: discord.Interaction, confession: str):
        guild = interaction.guild
        channel = discord.utils.get(guild.text_channels, name="confessions")
        if not channel:
            channel = await guild.create_text_channel("confessions")
            
        count = await increment_confession_count()
        embed = discord.Embed(
            title=f"Confession #{count}",
            description=confession,
            color=discord.Color.dark_gray()
        )
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Your confession was posted anonymously to {channel.mention}!", ephemeral=True)

    @app_commands.command(name="morph", description="Morphs a word down line by line.")
    @app_commands.describe(word="The word to morph.")
    async def morph(self, interaction: discord.Interaction, word: str):
        if len(word) > 20 or len(word) < 2:
            await interaction.response.send_message("Word must be between 2 and 20 characters.", ephemeral=True)
            return
            
        lines = []
        for i in range(len(word), 0, -1):
            lines.append(word[:i])
        for i in range(2, len(word) + 1):
            lines.append(word[:i])
            
        await interaction.response.send_message("```\n" + "\n".join(lines) + "\n```")



    @app_commands.command(name="pick", description="Picks a random choice from a comma-separated list.")
    @app_commands.describe(choices="Comma-separated choices (e.g. Waffles, Pancakes)")
    async def pick(self, interaction: discord.Interaction, choices: str):
        options = [opt.strip() for opt in choices.split(",")]
        if len(options) < 2:
            await interaction.response.send_message("Please provide at least 2 options separated by commas.")
            return
        await interaction.response.send_message(f"I pick: **{random.choice(options)}**")

    @app_commands.command(name="fact", description="Posts a random fun fact.")
    async def fact(self, interaction: discord.Interaction):
        facts = [
            "Banging your head against a wall for one hour burns 150 calories.",
            "In Switzerland, it is illegal to own just one guinea pig.",
            "Pteronophobia is the fear of being tickled by feathers.",
            "Snakes can help predict earthquakes.",
            "A flock of crows is known as a murder.",
            "The oldest \"your mom\" joke was discovered on a 3,500 year old Babylonian tablet."
        ]
        await interaction.response.send_message(random.choice(facts))

    @app_commands.command(name="say", description="Makes the bot echo your message.")
    @app_commands.describe(message="What the bot should say.")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="inspiro", description="Posts a randomly generated quote from inspirobot.me")
    async def inspiro(self, interaction: discord.Interaction):
        async with self.session.get("http://inspirobot.me/api?generate=true") as response:
            if response.status == 200:
                img_url = await response.text()
                embed = discord.Embed(color=discord.Color.blue())
                embed.set_image(url=img_url)
                embed.set_footer(text="Powered by inspirobot.me")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Could not generate a quote.", ephemeral=True)

    @app_commands.command(name="dadjoke", description="Posts a random dad joke.")
    async def dadjoke(self, interaction: discord.Interaction):
        headers = {"Accept": "application/json"}
        async with self.session.get("https://icanhazdadjoke.com/", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                await interaction.response.send_message(data.get("joke", "Failed to get a joke."))
            else:
                await interaction.response.send_message("Failed to fetch dad joke.", ephemeral=True)

    @app_commands.command(name="urban", description="Searches Urban Dictionary for a term.")
    @app_commands.describe(term="The term to search.")
    async def urban(self, interaction: discord.Interaction, term: str):
        url = f"http://api.urbandictionary.com/v0/define?term={urllib.parse.quote(term)}"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                results = data.get("list", [])
                if results:
                    best = results[0]
                    embed = discord.Embed(title=best.get("word"), url=best.get("permalink"), color=discord.Color.orange())
                    
                    definition = best.get("definition", "").replace("[", "").replace("]", "")
                    if len(definition) > 1000:
                        definition = definition[:1000] + "..."
                        
                    example = best.get("example", "").replace("[", "").replace("]", "")
                    if len(example) > 1000:
                        example = example[:1000] + "..."
                        
                    embed.add_field(name="Definition", value=definition, inline=False)
                    embed.add_field(name="Example", value=example or "No example", inline=False)
                    embed.set_footer(text=f"👍 {best.get('thumbs_up')} | 👎 {best.get('thumbs_down')}")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No definition found.", ephemeral=True)
            else:
                await interaction.response.send_message("Could not reach Urban Dictionary.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))
