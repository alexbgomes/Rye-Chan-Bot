import discord
from discord import app_commands
from discord.ext import commands
import random
import string

from utils import database

def generate_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

class Mirror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="listen", description="Start listening to a specific user/bot in this channel.")
    @app_commands.describe(from_user="The user or bot to listen to.")
    @app_commands.default_permissions(manage_channels=True)
    async def listen(self, interaction: discord.Interaction, from_user: discord.Member):
        code = generate_code()
        # Verify code is unique (though extremely likely)
        while await database.get_listen_by_code(code) is not None:
            code = generate_code()

        await database.create_listen(code, interaction.channel_id, from_user.id)
        
        embed = discord.Embed(
            title="Started Listening",
            description=f"Listening to {from_user.mention} in {interaction.channel.mention}.\nUse the following code to mirror these messages to another channel:\n\n**`{code}`**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Keep this code secret!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # DM the user with the code and details
        try:
            guild_name = interaction.guild.name if interaction.guild else "DMs"
            dm_embed = discord.Embed(
                title="Listen Configuration Created",
                description=f"Here is your secret code: **`{code}`**\n\n**Server:** {guild_name}\n**Channel:** {interaction.channel.name}\n**Target:** {from_user.name}",
                color=discord.Color.blue()
            )
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            pass # The user has DMs disabled

    @app_commands.command(name="unlisten", description="Stop listening and remove all mirrors for a specific code.")
    @app_commands.describe(code="The 8-character code provided by /listen")
    @app_commands.default_permissions(manage_channels=True)
    async def unlisten(self, interaction: discord.Interaction, code: str):
        success = await database.delete_listen(code)
        if success:
            await interaction.response.send_message(f"Successfully stopped listening and removed all mirrors for code **`{code}`**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Could not find a listen configuration for code **`{code}`**.", ephemeral=True)

    @app_commands.command(name="mirror", description="Mirror messages to this channel using a code.")
    @app_commands.describe(code="The 8-character code provided by /listen")
    @app_commands.default_permissions(manage_channels=True)
    async def mirror(self, interaction: discord.Interaction, code: str):
        config = await database.get_listen_by_code(code)
        if not config:
            await interaction.response.send_message(f"Invalid code: **`{code}`**. Make sure you copied it correctly and it respects capitalization.", ephemeral=True)
            return

        # Check if already mirroring
        mirrors = await database.get_mirrors_for_source(config[0], config[1])
        if interaction.channel_id in mirrors:
            await interaction.response.send_message("This channel is already mirroring that source.", ephemeral=True)
            return

        await database.add_mirror(code, interaction.channel_id)
        await interaction.response.send_message(f"Successfully linked! This channel will now mirror messages from the source associated with code **`{code}`**.", ephemeral=True)

        # DM the user with the setup confirmation
        try:
            guild_name = interaction.guild.name if interaction.guild else "DMs"
            dm_embed = discord.Embed(
                title="Mirror Successfully Linked",
                description=f"You have set up a mirror for code **`{code}`**.\n\n**Destination Server:** {guild_name}\n**Destination Channel:** {interaction.channel.name}",
                color=discord.Color.blue()
            )
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @app_commands.command(name="unmirror", description="Stop mirroring messages to this channel for a specific code.")
    @app_commands.describe(code="The 8-character code provided by /listen")
    @app_commands.default_permissions(manage_channels=True)
    async def unmirror(self, interaction: discord.Interaction, code: str):
        success = await database.remove_mirror(code, interaction.channel_id)
        if success:
            await interaction.response.send_message(f"Successfully removed mirror for code **`{code}`** in this channel.", ephemeral=True)
        else:
            await interaction.response.send_message(f"This channel was not mirroring code **`{code}`**.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # Get mirrors for this channel and user
        dest_channel_ids = await database.get_mirrors_for_source(message.channel.id, message.author.id)
        
        if not dest_channel_ids:
            return

        # Prepare content and embeds
        content = "" # The text content will be in the embed
        
        quote_embed = discord.Embed(description=message.content, color=message.author.color)
        quote_embed.set_author(
            name=message.author.display_name, 
            icon_url=message.author.display_avatar.url if message.author.display_avatar else None
        )
        
        embeds = [quote_embed] + message.embeds
        
        # Send to all destination channels
        for dest_id in dest_channel_ids:
            # Don't mirror to the same channel
            if dest_id == message.channel.id:
                continue
                
            dest_channel = self.bot.get_channel(dest_id)
            if not dest_channel:
                try:
                    dest_channel = await self.bot.fetch_channel(dest_id)
                except (discord.NotFound, discord.Forbidden):
                    continue

            if dest_channel:
                try:
                    send_kwargs = {}
                    if content:
                        send_kwargs['content'] = content
                    if embeds:
                        send_kwargs['embeds'] = embeds
                    if message.attachments:
                        # Files can only be sent once, so we need to recreate them for each channel if multiple
                        current_files = []
                        for attachment in message.attachments:
                            try:
                                current_files.append(await attachment.to_file())
                            except discord.HTTPException:
                                pass
                        if current_files:
                            send_kwargs['files'] = current_files
                        
                    if send_kwargs:
                        await dest_channel.send(**send_kwargs)
                except discord.Forbidden:
                    # Bot lacks permissions to send in this channel
                    pass
                except discord.HTTPException:
                    # Other errors
                    pass

async def setup(bot):
    await bot.add_cog(Mirror(bot))
