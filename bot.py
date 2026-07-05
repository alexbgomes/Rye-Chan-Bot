import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

from utils.database import setup_db

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Required for welcome/goodbye messages
intents.presences = True # Required for /playing command

class RyeChanBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None # We will use a custom slash command for help
        )

    async def setup_hook(self):
        # Setup Database
        await setup_db()
        print("Database initialized.")

        # Load Cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename}")
        
        # Sync Slash Commands
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        await self.change_presence(activity=discord.Game(name="/help for commands"))

if __name__ == "__main__":
    if not TOKEN or TOKEN == "your_token_here":
        print("DISCORD TOKEN IS MISSING.")
    else:
        bot = RyeChanBot()
        bot.run(TOKEN)
