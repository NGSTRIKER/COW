import discord
from discord import app_commands
from discord.ext import commands

from database.db import SessionLocal
from database.models import Guild

# Default message template sent when a new member joins
WELCOME_PHRASE = "Welcome to the server, {user}!"


class Welcome(commands.Cog):
    """
    Welcome Cog — Dispatches greeting messages when new members join the server.
    Integrates with database settings to select the designated welcome text channel.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[Cog Loaded] Welcome Cog")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event listener invoked when a new member joins the server.
        Queries the database for the server's configured welcome channel.
        """
        guild = member.guild

        # Query configured welcome channel ID from database
        welcome_channel_id = None
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, guild.id)
            if db_guild:
                welcome_channel_id = db_guild.welcome_channel

        # Retrieve text channel object from guild
        channel = None
        if welcome_channel_id:
            channel = guild.get_channel(welcome_channel_id)

        # Fallback to system channel, 'general' channel, or first sendable text channel
        if channel is None:
            channel = guild.system_channel or discord.utils.get(guild.text_channels, name="general") or next(
                (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None
            )

        if channel is None:
            return

        try:
            await channel.send(WELCOME_PHRASE.format(user=member.mention))
        except (discord.Forbidden, discord.HTTPException):
            pass

    @app_commands.command(name="set_welcome_channel", description="Set or clear the welcome message channel.")
    @app_commands.default_permissions(manage_guild=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        """
        Slash command allowing administrators to configure or clear the welcome channel setting.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        channel_id = channel.id if channel else None

        # Update welcome_channel setting in database
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.welcome_channel = channel_id

        msg = f"Welcome channel set to {channel.mention}." if channel else "Welcome channel cleared."
        await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))