import discord
from discord import app_commands
from discord.ext import commands

from database.db import SessionLocal
from database.models import Guild


async def get_or_create_guild(guild_id: int) -> Guild:
    """
    Helper function to query a Guild record from the database.
    If no record exists for the given guild_id, a new Guild record is created and returned.
    """
    async with SessionLocal() as session:
        db_guild = await session.get(Guild, guild_id)
        if db_guild is None:
            async with session.begin():
                db_guild = Guild(guild_id=guild_id)
                session.add(db_guild)
                await session.flush()
                await session.refresh(db_guild)
        return db_guild


class WelcomeChannelSelect(discord.ui.ChannelSelect):
    """
    Discord UI Channel Select Menu allowing administrators to select or clear
    the text channel designated for welcoming new members.
    """
    def __init__(self, current_channel_id: int | None):
        super().__init__(
            placeholder="Select Welcome Channel...",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild_id is None:
            return

        # Extract selected channel ID (or None if selection was cleared)
        selected_id = self.values[0].id if self.values else None

        # Update welcome_channel setting in database
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, interaction.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=interaction.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.welcome_channel = selected_id

        selected_mention = self.values[0].mention if self.values else "None"
        await self.view.update_dashboard(
            interaction,
            f"Welcome channel updated to {selected_mention}."
        )


class FoxLogChannelSelect(discord.ui.ChannelSelect):
    """
    Discord UI Channel Select Menu allowing administrators to select or clear
    the text channel designated for Fox Nose security and raid alerts.
    """
    def __init__(self, current_channel_id: int | None):
        super().__init__(
            placeholder="Select Fox Nose Log Channel...",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild_id is None:
            return

        # Extract selected channel ID (or None if selection was cleared)
        selected_id = self.values[0].id if self.values else None

        # Update fox_nose_log_channel setting in database
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, interaction.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=interaction.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.fox_nose_log_channel = selected_id

        selected_mention = self.values[0].mention if self.values else "None"
        await self.view.update_dashboard(
            interaction,
            f"Fox Nose log channel updated to {selected_mention}."
        )


class DashboardView(discord.ui.View):
    """
    Interactive Discord UI View containing control buttons and dropdown menus
    for managing server settings in real-time with persistent database storage.
    """
    def __init__(self, author_id: int, guild_id: int):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Ensures only the administrator who opened the dashboard can interact with UI controls.
        """
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the Administrator who opened this dashboard can use these controls.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Toggle Fox Nose", style=discord.ButtonStyle.primary, row=2)
    async def toggle_fox_nose(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to toggle Fox Nose anti-raid protection ON or OFF in database.
        """
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, self.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=self.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.fox_nose_enabled = not db_guild.fox_nose_enabled
                new_state = "Enabled" if db_guild.fox_nose_enabled else "Disabled"

        await self.update_dashboard(interaction, f"Fox Nose protection is now {new_state}.")

    @discord.ui.button(label="Toggle XP System", style=discord.ButtonStyle.secondary, row=2)
    async def toggle_xp(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to toggle XP system ON or OFF in database.
        """
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, self.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=self.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.xp_enabled = not db_guild.xp_enabled
                new_state = "Enabled" if db_guild.xp_enabled else "Disabled"

        await self.update_dashboard(interaction, f"XP system is now {new_state}.")

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.success, row=2)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to re-fetch settings from the database and refresh embed.
        """
        await self.update_dashboard(interaction, "Dashboard refreshed from database.")

    async def build_embed_and_view(self, guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
        """
        Queries the database for current Guild settings and builds the status Embed
        along with updating active UI components.
        """
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, self.guild_id)
            welcome_ch = db_guild.welcome_channel if db_guild else None
            fox_enabled = db_guild.fox_nose_enabled if db_guild else True
            fox_log_ch = db_guild.fox_nose_log_channel if db_guild else None
            xp_enabled = db_guild.xp_enabled if db_guild else False

        embed = discord.Embed(
            title=f"Server Admin Dashboard - {guild.name}",
            description="Server Control Panel\nAll settings are saved directly in the database.",
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="Welcome Messages",
            value=f"Channel: <#{welcome_ch}>" if welcome_ch else "Channel: Not Configured (Default system channel)",
            inline=False,
        )

        embed.add_field(
            name="Fox Nose Security System",
            value=(
                f"Status: {'Active' if fox_enabled else 'Disabled'}\n"
                f"Log Channel: {f'<#{fox_log_ch}>' if fox_log_ch else 'Not Configured (Default system channel)'}\n"
                f"Raid Sensitivity: 5 joins within 10s"
            ),
            inline=False,
        )

        embed.add_field(
            name="XP and Leveling System",
            value=f"Status: {'Enabled' if xp_enabled else 'Disabled'}",
            inline=False,
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text="Server Admin Control Panel | Persistent Database Storage")

        # Refresh UI components with latest values
        self.clear_items()
        self.add_item(WelcomeChannelSelect(welcome_ch))
        self.add_item(FoxLogChannelSelect(fox_log_ch))

        # Re-add button items
        self.add_item(self.toggle_fox_nose)
        self.add_item(self.toggle_xp)
        self.add_item(self.refresh)

        return embed, self

    async def update_dashboard(self, interaction: discord.Interaction, status_msg: str):
        """
        Helper method to edit interaction response with updated Embed and View.
        """
        if interaction.guild is None:
            return
        embed, view = await self.build_embed_and_view(interaction.guild)
        await interaction.response.edit_message(content=f"Info: {status_msg}", embed=embed, view=view)


class DashboardCog(commands.Cog):
    """
    Server Admin Control Center Cog exposing the /dashboard slash command.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[Cog Loaded] Dashboard Cog")

    @app_commands.command(name="dashboard", description="Open the Server Admin Control Panel.")
    @app_commands.default_permissions(manage_guild=True)
    async def dashboard(self, interaction: discord.Interaction):
        """
        Slash command handler for /dashboard.
        Renders the server control panel UI for administrators.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        view = DashboardView(author_id=interaction.user.id, guild_id=interaction.guild_id)
        embed, view = await view.build_embed_and_view(interaction.guild)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DashboardCog(bot))
