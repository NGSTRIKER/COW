import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from database.db import SessionLocal
from database.leveling_db import LevelingSessionLocal
from database.leveling_models import ChannelXpRate, GuildLevelingConfig
from database.models import Guild

MAX_CHANNEL_SLOTS = 10


async def get_or_create_guild(guild_id: int) -> Guild:
    """
    Helper function to query a Guild record from the database.
    If no record exists for the given guild_id, a new Guild record is created and returned.
    """
    async with SessionLocal() as session:
        db_guild = await session.get(Guild, guild_id)
        if db_guild is None:
            db_guild = Guild(guild_id=guild_id)
            session.add(db_guild)
            await session.commit()
            await session.refresh(db_guild)
        return db_guild


async def get_or_create_leveling_config(guild_id: int) -> GuildLevelingConfig:
    """
    Helper function to query or initialize GuildLevelingConfig from dedicated leveling database.
    """
    async with LevelingSessionLocal() as session:
        config = await session.get(GuildLevelingConfig, guild_id)
        if config is None:
            config = GuildLevelingConfig(guild_id=guild_id)
            session.add(config)
            await session.commit()
            await session.refresh(config)
        return config


class ChannelRateModal(discord.ui.Modal):
    """
    Interactive Modal allowing administrators to specify XP rate and cooldown
    for a chosen channel from the dashboard (up to 10 slots).
    """

    def __init__(self, channel: discord.TextChannel, dashboard_view: "DashboardView", current_rate: int = 15, current_cooldown: int = 30):
        super().__init__(title=f"XP Rate: #{channel.name[:20]}")
        self.channel = channel
        self.dashboard_view = dashboard_view

        self.exp_input = discord.ui.TextInput(
            label="XP Per Message",
            placeholder="e.g. 15",
            default=str(current_rate),
            min_length=1,
            max_length=5,
            required=True,
        )
        self.cooldown_input = discord.ui.TextInput(
            label="Cooldown (Seconds)",
            placeholder="e.g. 30",
            default=str(current_cooldown),
            min_length=1,
            max_length=5,
            required=True,
        )
        self.add_item(self.exp_input)
        self.add_item(self.cooldown_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            exp_val = int(self.exp_input.value.strip())
            cd_val = int(self.cooldown_input.value.strip())
            if exp_val <= 0 or cd_val < 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "Invalid values provided. XP must be positive integer and cooldown >= 0.",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild_id
        if guild_id is None:
            return

        async with LevelingSessionLocal() as session:
            # Query all existing slots in guild
            stmt = select(ChannelXpRate).where(ChannelXpRate.guild_id == guild_id)
            existing_rates = (await session.execute(stmt)).scalars().all()
            existing_by_channel = {r.channel_id: r for r in existing_rates}
            existing_slots = {r.slot_number: r for r in existing_rates}

            target_rate = existing_by_channel.get(self.channel.id)

            if target_rate is None:
                available_slots = [s for s in range(1, MAX_CHANNEL_SLOTS + 1) if s not in existing_slots]
                if not available_slots:
                    await interaction.response.send_message(
                        f"All {MAX_CHANNEL_SLOTS} channel leveling slots are full! Please use `/leveling channel_remove` to free a slot.",
                        ephemeral=True,
                    )
                    return
                assigned_slot = available_slots[0]
                target_rate = ChannelXpRate(
                    guild_id=guild_id,
                    slot_number=assigned_slot,
                    channel_id=self.channel.id,
                    channel_name=self.channel.name,
                    system_name=f"#{self.channel.name} Leveling System",
                    exp_per_msg=exp_val,
                    cooldown=cd_val,
                    is_enabled=True,
                )
                session.add(target_rate)
            else:
                assigned_slot = target_rate.slot_number
                target_rate.channel_name = self.channel.name
                target_rate.system_name = f"#{self.channel.name} Leveling System"
                target_rate.exp_per_msg = exp_val
                target_rate.cooldown = cd_val
                target_rate.is_enabled = True

            await session.commit()

        await self.dashboard_view.update_dashboard(
            interaction,
            f"Configured Slot {assigned_slot}: #{self.channel.name} Leveling System with {exp_val} XP/msg ({cd_val}s cooldown).",
        )


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

        selected_id = self.values[0].id if self.values else None

        async with SessionLocal() as session:
            db_guild = await session.get(Guild, interaction.guild_id)
            if db_guild is None:
                db_guild = Guild(guild_id=interaction.guild_id)
                session.add(db_guild)
            db_guild.welcome_channel = selected_id
            await session.commit()

        selected_mention = self.values[0].mention if self.values else "None"
        await self.view.update_dashboard(
            interaction,
            f"Welcome channel updated to {selected_mention}.",
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

        selected_id = self.values[0].id if self.values else None

        async with SessionLocal() as session:
            db_guild = await session.get(Guild, interaction.guild_id)
            if db_guild is None:
                db_guild = Guild(guild_id=interaction.guild_id)
                session.add(db_guild)
            db_guild.fox_nose_log_channel = selected_id
            await session.commit()

        selected_mention = self.values[0].mention if self.values else "None"
        await self.view.update_dashboard(
            interaction,
            f"Fox Nose log channel updated to {selected_mention}.",
        )


class LevelingChannelSelect(discord.ui.ChannelSelect):
    """
    Discord UI Channel Select Menu allowing administrators to select a channel
    and configure its multi-channel XP rate via a modal.
    """

    def __init__(self):
        super().__init__(
            placeholder="Configure a Channel Leveling System slot...",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild_id is None or not self.values:
            return

        selected_channel = self.values[0]
        # Query existing channel configuration if any
        async with LevelingSessionLocal() as session:
            stmt = select(ChannelXpRate).where(
                ChannelXpRate.guild_id == interaction.guild_id,
                ChannelXpRate.channel_id == selected_channel.id,
            )
            rate = (await session.execute(stmt)).scalar_one_or_none()
            cur_exp = rate.exp_per_msg if rate else 15
            cur_cd = rate.cooldown if rate else 30

        modal = ChannelRateModal(
            channel=selected_channel,
            dashboard_view=self.view,
            current_rate=cur_exp,
            current_cooldown=cur_cd,
        )
        await interaction.response.send_modal(modal)


class DashboardView(discord.ui.View):
    """
    Interactive Discord UI View containing control buttons and dropdown menus
    for managing server settings, standard leveling, and multi-channel leveling.
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

    @discord.ui.button(label="Toggle Fox Nose", style=discord.ButtonStyle.primary, row=3)
    async def toggle_fox_nose(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to toggle Fox Nose anti-raid protection ON or OFF.
        """
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, self.guild_id)
            if db_guild is None:
                db_guild = Guild(guild_id=self.guild_id)
                session.add(db_guild)
            db_guild.fox_nose_enabled = not db_guild.fox_nose_enabled
            new_state = "Enabled" if db_guild.fox_nose_enabled else "Disabled"
            await session.commit()

        await self.update_dashboard(interaction, f"Fox Nose protection is now {new_state}.")

    @discord.ui.button(label="Toggle Standard XP", style=discord.ButtonStyle.secondary, row=3)
    async def toggle_std_xp(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to toggle standard server leveling ON or OFF in leveling.db.
        """
        async with LevelingSessionLocal() as session:
            cfg = await session.get(GuildLevelingConfig, self.guild_id)
            if cfg is None:
                cfg = GuildLevelingConfig(guild_id=self.guild_id)
                session.add(cfg)
            cfg.standard_enabled = not cfg.standard_enabled
            new_state = "Enabled" if cfg.standard_enabled else "Disabled"
            await session.commit()

        # Also sync core Guild.xp_enabled for backward compatibility
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, self.guild_id)
            if db_guild:
                db_guild.xp_enabled = cfg.standard_enabled
                await session.commit()

        await self.update_dashboard(interaction, f"Standard XP system is now {new_state}.")

    @discord.ui.button(label="Toggle Multi-Channel XP", style=discord.ButtonStyle.secondary, row=3)
    async def toggle_multi_xp(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to toggle multi-channel leveling ON or OFF in leveling.db.
        """
        async with LevelingSessionLocal() as session:
            cfg = await session.get(GuildLevelingConfig, self.guild_id)
            if cfg is None:
                cfg = GuildLevelingConfig(guild_id=self.guild_id)
                session.add(cfg)
            cfg.multichannel_enabled = not cfg.multichannel_enabled
            new_state = "Enabled" if cfg.multichannel_enabled else "Disabled"
            await session.commit()

        await self.update_dashboard(interaction, f"Multi-Channel XP system is now {new_state}.")

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.success, row=3)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button callback to re-fetch settings from the databases and refresh embed.
        """
        await self.update_dashboard(interaction, "Dashboard refreshed from database.")

    async def build_embed_and_view(self, guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
        """
        Queries databases for current settings and builds the status Embed with active controls.
        """
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, self.guild_id)
            welcome_ch = db_guild.welcome_channel if db_guild else None
            fox_enabled = db_guild.fox_nose_enabled if db_guild else True
            fox_log_ch = db_guild.fox_nose_log_channel if db_guild else None

        async with LevelingSessionLocal() as session:
            cfg = await session.get(GuildLevelingConfig, self.guild_id)
            std_enabled = cfg.standard_enabled if cfg else True
            multi_enabled = cfg.multichannel_enabled if cfg else True

            stmt = select(ChannelXpRate).where(ChannelXpRate.guild_id == self.guild_id).order_by(ChannelXpRate.slot_number.asc())
            configured_channels = (await session.execute(stmt)).scalars().all()

        embed = discord.Embed(
            title=f"Server Admin Dashboard - {guild.name}",
            description="Server Control Panel\nManage security, welcome, standard leveling, and multi-channel leveling with persistent local SQLite storage.",
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
            name="Standard Leveling System",
            value=(
                f"Status: {'Enabled' if std_enabled else 'Disabled'}\n"
                f"Rate: 10-20 XP/msg | Cooldown: 30s"
            ),
            inline=True,
        )

        slot_lines = []
        for rate in configured_channels:
            ch_name = rate.system_name or f"#{rate.channel_name}"
            slot_lines.append(f"• Slot {rate.slot_number}: {ch_name} (<#{rate.channel_id}>) — {rate.exp_per_msg} XP/msg")
        ch_text = "\n".join(slot_lines) if slot_lines else "No slots configured."

        embed.add_field(
            name=f"Multi-Channel Leveling ({len(configured_channels)}/{MAX_CHANNEL_SLOTS} Slots)",
            value=(
                f"Status: {'Enabled' if multi_enabled else 'Disabled'}\n"
                f"{ch_text}"
            ),
            inline=False,
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text="Persistent Database Storage | WAL Mode Enabled")

        # Refresh UI components
        self.clear_items()
        self.add_item(WelcomeChannelSelect(welcome_ch))
        self.add_item(FoxLogChannelSelect(fox_log_ch))
        self.add_item(LevelingChannelSelect())

        # Buttons on row 3
        self.add_item(self.toggle_fox_nose)
        self.add_item(self.toggle_std_xp)
        self.add_item(self.toggle_multi_xp)
        self.add_item(self.refresh)

        return embed, self

    async def update_dashboard(self, interaction: discord.Interaction, status_msg: str):
        """
        Helper method to edit interaction response with updated Embed and View.
        """
        if interaction.guild is None:
            return
        embed, view = await self.build_embed_and_view(interaction.guild)
        if interaction.response.is_done():
            await interaction.followup.send(content=f"Info: {status_msg}", embed=embed, ephemeral=True)
        else:
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
