import discord
from discord import app_commands
from discord.ext import commands

from database.db import SessionLocal
from database.models import Guild


async def get_or_create_guild(guild_id: int) -> Guild:
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
    def __init__(self, current_channel_id: int | None):
        super().__init__(
            placeholder="🌸 Select Welcome Channel...",
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
            async with session.begin():
                db_guild = await session.get(Guild, interaction.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=interaction.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.welcome_channel = selected_id

        await self.view.update_dashboard(interaction, f"✅ Welcome channel updated to {self.values[0].mention if self.values else 'None'}.")


class FoxLogChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, current_channel_id: int | None):
        super().__init__(
            placeholder="🦊 Select Fox Nose Log Channel...",
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
            async with session.begin():
                db_guild = await session.get(Guild, interaction.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=interaction.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.fox_nose_log_channel = selected_id

        await self.view.update_dashboard(interaction, f"✅ Fox Nose log channel updated to {self.values[0].mention if self.values else 'None'}.")


class DashboardView(discord.ui.View):
    def __init__(self, author_id: int, guild_id: int):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Only the Administrator who opened this dashboard can use these controls.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Toggle Fox Nose", style=discord.ButtonStyle.primary, emoji="🦊", row=2)
    async def toggle_fox_nose(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, self.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=self.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.fox_nose_enabled = not db_guild.fox_nose_enabled
                new_state = "Enabled" if db_guild.fox_nose_enabled else "Disabled"

        await self.update_dashboard(interaction, f"✅ Fox Nose protection is now **{new_state}**.")

    @discord.ui.button(label="Toggle XP System", style=discord.ButtonStyle.secondary, emoji="✨", row=2)
    async def toggle_xp(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, self.guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=self.guild_id)
                    session.add(db_guild)
                    await session.flush()
                db_guild.xp_enabled = not db_guild.xp_enabled
                new_state = "Enabled" if db_guild.xp_enabled else "Disabled"

        await self.update_dashboard(interaction, f"✅ XP system is now **{new_state}**.")

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.success, emoji="🔄", row=2)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_dashboard(interaction, "🔄 Dashboard refreshed from database.")

    async def build_embed_and_view(self, guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, self.guild_id)
            welcome_ch = db_guild.welcome_channel if db_guild else None
            fox_enabled = db_guild.fox_nose_enabled if db_guild else True
            fox_log_ch = db_guild.fox_nose_log_channel if db_guild else None
            xp_enabled = db_guild.xp_enabled if db_guild else False

        embed = discord.Embed(
            title=f"🌸 Hu Immortal Blessed Land — Admin Dashboard",
            description=f"Server Control Panel for **{guild.name}**\nAll settings are saved directly in the database.",
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="🌸 Welcome Messages",
            value=f"**Channel:** <#{welcome_ch}>" if welcome_ch else "**Channel:** *Not Configured (Default system channel)*",
            inline=False,
        )

        embed.add_field(
            name="🦊 Fox Nose Security Gu",
            value=(
                f"**Status:** {'✅ Active' if fox_enabled else '❌ Disabled'}\n"
                f"**Log Channel:** {f'<#{fox_log_ch}>' if fox_log_ch else '*Not Configured (Default system channel)*'}\n"
                f"**Raid Sensitivity:** 5 joins within 10s"
            ),
            inline=False,
        )

        embed.add_field(
            name="✨ XP & Cultivation System",
            value=f"**Status:** {'✅ Enabled' if xp_enabled else '❌ Disabled'}",
            inline=False,
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text="Little Hu Immortal Blessed Land Guardian • Persistent Storage 💾")

        self.clear_items()
        self.add_item(WelcomeChannelSelect(welcome_ch))
        self.add_item(FoxLogChannelSelect(fox_log_ch))

        # Re-add buttons
        self.add_item(self.toggle_fox_nose)
        self.add_item(self.toggle_xp)
        self.add_item(self.refresh)

        return embed, self

    async def update_dashboard(self, interaction: discord.Interaction, status_msg: str):
        if interaction.guild is None:
            return
        embed, view = await self.build_embed_and_view(interaction.guild)
        await interaction.response.edit_message(content=f"ℹ️ {status_msg}", embed=embed, view=view)


class DashboardCog(commands.Cog):
    """
    🌸 Hu Immortal Admin Control Center
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("✅ Dashboard Cog Loaded")

    @app_commands.command(name="dashboard", description="Open the Hu Immortal Server Admin Control Panel.")
    @app_commands.default_permissions(manage_guild=True)
    async def dashboard(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        view = DashboardView(author_id=interaction.user.id, guild_id=interaction.guild_id)
        embed, view = await view.build_embed_and_view(interaction.guild)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DashboardCog(bot))
