import discord
from discord import app_commands
from discord.ext import commands
import urllib.parse
from deep_translator import GoogleTranslator

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
        embed.add_field(name="Utility", value="`/ping`, `/about`, `/help`, `/desc`, `/avatar`, `/conv`, `/page`, `/playing`, `/members`, `/trim`, `/whois`, `/tex`, `/translate`, `/translate_langs`, `/quote`, `/listen`, `/unlisten`, `/mirror`, `/unmirror`", inline=False)
        embed.add_field(name="Fun", value="`/xkcd`, `/8ball`, `/mock`, `/confess`, `/morph`, `/pick`, `/fact`, `/say`, `/inspiro`, `/dadjoke`, `/urban`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="desc", description="Posts the topic of the current channel.")
    async def desc(self, interaction: discord.Interaction):
        topic = interaction.channel.topic
        if topic:
            await interaction.response.send_message(f"**Channel Topic:**\n{topic}")
        else:
            await interaction.response.send_message("This channel has no topic.")

    @app_commands.command(name="avatar", description="Returns the link to a user's avatar.")
    @app_commands.describe(user="The user to get the avatar for (leave blank for yourself).")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"{user.name}'s Avatar", color=user.color)
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="conv", description="Convert a number between bases (dec, hex, oct, bin).")
    async def conv(self, interaction: discord.Interaction, num: str, base_from: str, base_to: str):
        bases = {"dec": 10, "hex": 16, "oct": 8, "bin": 2}
        
        base_from = base_from.lower()
        base_to = base_to.lower()
        
        if base_from not in bases or base_to not in bases:
            await interaction.response.send_message("Bases must be one of: dec, hex, oct, bin.", ephemeral=True)
            return
            
        try:
            # Convert to decimal first
            dec_val = int(num, bases[base_from])
            
            # Convert to target base
            if base_to == "dec":
                result = str(dec_val)
            elif base_to == "hex":
                result = hex(dec_val)[2:].upper()
            elif base_to == "oct":
                result = oct(dec_val)[2:]
            elif base_to == "bin":
                result = bin(dec_val)[2:]
                
            await interaction.response.send_message(f"**{num}** ({base_from}) => **{result}** ({base_to})")
        except ValueError:
            await interaction.response.send_message(f"Invalid number '{num}' for base {base_from}.", ephemeral=True)

    @app_commands.command(name="page", description="Moves the chat up to clear messages visually (Bulk deletes 40 messages).")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def page(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=40)
        await interaction.followup.send(f"Paged (deleted {len(deleted)} messages).", ephemeral=True)

    @app_commands.command(name="trim", description="Bulk deletes a specified number of messages.")
    @app_commands.describe(amount="Amount to delete (1-99).")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def trim(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 99:
            await interaction.response.send_message("Amount must be between 1 and 99.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Trimmed {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(name="playing", description="Returns a list of users playing the inquired game.")
    @app_commands.describe(game="The game name or shortcut (e.g. lol, csgo, ow).")
    async def playing(self, interaction: discord.Interaction, game: str):
        shortcuts = {
            "lol": "League of Legends", "league": "League of Legends", "leg": "League of Legends",
            "wf": "Warframe", "osu": "osu!", "poe": "Path of Exile", "rl": "Rocket League",
            "csgo": "Counter-Strike: Global Offensive", "wow": "World of Warcraft",
            "bf1": "Battlefield 1", "d2": "Destiny 2", "pubg": "PLAYERUNKNOWN'S BATTLEGROUNDS",
            "gta v": "Grand Theft Auto V", "gta 5": "Grand Theft Auto V", "gtav": "Grand Theft Auto V",
            "ddlc": "Doki Doki Literature Club", "l4d2": "Left 4 Dead 2"
        }
        
        target_game = shortcuts.get(game.lower(), game)
        players = []
        
        for member in interaction.guild.members:
            if member.activity and member.activity.name and member.activity.name.lower() == target_game.lower():
                players.append(member.display_name)
                
        if players:
            player_list = "\n".join(players)
            await interaction.response.send_message(f"**Users playing {target_game}:**\n{player_list}")
        else:
            await interaction.response.send_message(f"Nobody is currently playing {target_game}.")

    @app_commands.command(name="members", description="Returns a list of people in the inquired role.")
    async def members(self, interaction: discord.Interaction, role: discord.Role):
        if not role.members:
            await interaction.response.send_message(f"No one has the {role.name} role.")
            return
            
        member_list = "\n".join([m.display_name for m in role.members])
        if len(member_list) > 2000:
            member_list = member_list[:1995] + "..."
            
        await interaction.response.send_message(f"**Members in {role.name}:**\n{member_list}")

    @app_commands.command(name="whois", description="Returns detailed user data.")
    async def whois(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        
        embed = discord.Embed(title=f"User Info for {user.name}", color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Nickname", value=user.nick or "None", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(user.created_at, style='F'), inline=False)
        embed.add_field(name="Joined", value=discord.utils.format_dt(user.joined_at, style='F'), inline=False)
        
        if user.activity:
            embed.add_field(name="Playing", value=user.activity.name, inline=False)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tex", description="Returns LaTeX formatted image.")
    @app_commands.describe(equation="The LaTeX equation.")
    async def tex(self, interaction: discord.Interaction, equation: str):
        url = f"https://latex.codecogs.com/png.image?\\dpi{{150}}\\bg{{white}}{urllib.parse.quote(equation)}"
        embed = discord.Embed(color=discord.Color.light_gray())
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="translate", description="Translates text from source language to destination language.")
    async def translate(self, interaction: discord.Interaction, source: str, dest: str, text: str):
        try:
            translator = GoogleTranslator(source=source.lower(), target=dest.lower())
            result = translator.translate(text)
            
            embed = discord.Embed(color=discord.Color.green())
            embed.add_field(name=f"Original ({source})", value=text, inline=False)
            embed.add_field(name=f"Translated ({dest})", value=result, inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Translation failed: {str(e)}", ephemeral=True)

    @app_commands.command(name="translate_langs", description="Returns a list of supported languages for translation.")
    async def translate_langs(self, interaction: discord.Interaction):
        langs = GoogleTranslator().get_supported_languages(as_dict=True)
        # Just send a link or a truncated list as there are many
        lang_str = ", ".join([f"{name} ({code})" for name, code in list(langs.items())[:50]])
        await interaction.response.send_message(f"**Supported Languages (Partial List):**\n{lang_str}...\n\nUse standard abbreviations like 'en', 'es', 'ja', 'fr'.")

    @app_commands.command(name="quote", description="Quotes a message in the same channel using its ID.")
    async def quote(self, interaction: discord.Interaction, message_id: str):
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            embed = discord.Embed(description=msg.content, color=msg.author.color, timestamp=msg.created_at)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
            
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].url)
                
            embed.add_field(name="Source", value=f"[Jump to message]({msg.jump_url})")
            await interaction.response.send_message(embed=embed)
        except (ValueError, discord.NotFound, discord.HTTPException):
            await interaction.response.send_message("Could not find that message. Make sure the ID is valid and it is in this channel.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Utility(bot))
