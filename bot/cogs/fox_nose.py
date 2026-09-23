import time
import re
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from database.db import SessionLocal
from database.models import Guild

# Default regular expression patterns matching suspicious or bot-like usernames
DEFAULT_SUSPICIOUS_NAMES = [
    r"^user[_\-]?\d+$",
    r"^discord[_\-]?user",
    r"raid",
    r"bot",
    r"nuke",
    r"spam",
]


class FoxNose(commands.GroupCog, name="fox_nose", description="Commands for Fox Nose Raid Detection and Security Alerts."):
    """
    Fox Nose Security Cog — Anti-Raid & Suspicious Account Monitoring System.
    Monitors incoming server joins, calculates risk scores based on account heuristics,
    and alerts moderators when a raid surge or suspicious user is detected.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Maps guild_id to list of join timestamps for raid surge calculations: {guild_id: [timestamp1, ...]}
        self.join_tracker: dict[int, list[float]] = {}
        # Maps guild_id to raid alert expiry timestamp: {guild_id: expiry_timestamp}
        self.raid_lockdown: dict[int, float] = {}
        super().__init__()

    def calculate_sus_score(self, member: discord.Member, is_raid_active: bool) -> tuple[int, list[str]]:
        """
        Calculates a suspicion score (0 to 100) for a given member based on account age,
        avatar presence, username pattern, and raid surge context.
        """
        score = 0
        reasons = []

        now = datetime.now(timezone.utc)
        created_at = member.created_at
        account_age_days = (now - created_at).total_seconds() / 86400.0

        # Heuristic 1: Account Age Analysis
        if account_age_days < 1:
            score += 50
            reasons.append("Account created less than 24 hours ago (+50)")
        elif account_age_days < 7:
            score += 30
            reasons.append("Account created less than 7 days ago (+30)")
        elif account_age_days < 30:
            score += 15
            reasons.append("Account created less than 30 days ago (+15)")

        # Heuristic 2: Custom Avatar Check
        if member.avatar is None:
            score += 20
            reasons.append("Default Discord avatar (+20)")

        # Heuristic 3: Username Pattern Matching
        name_lower = member.name.lower()
        display_lower = member.display_name.lower()
        for pattern in DEFAULT_SUSPICIOUS_NAMES:
            if re.search(pattern, name_lower) or re.search(pattern, display_lower):
                score += 15
                reasons.append(f"Suspicious username pattern matched: '{pattern}' (+15)")
                break

        # Heuristic 4: Active Raid Surge Penalty
        if is_raid_active:
            score += 20
            reasons.append("Joined during an active Raid Surge (+20)")

        return min(score, 100), reasons

    def check_raid_surge(self, guild_id: int, threshold_joins: int, threshold_seconds: int) -> bool:
        """
        Tracks join timestamps within a sliding time window. Returns True if join count
        exceeds the threshold limit within the specified window.
        """
        now = time.time()
        if guild_id not in self.join_tracker:
            self.join_tracker[guild_id] = []

        # Remove join timestamps older than the threshold time window
        self.join_tracker[guild_id] = [
            t for t in self.join_tracker[guild_id] if now - t <= threshold_seconds
        ]
        self.join_tracker[guild_id].append(now)

        return len(self.join_tracker[guild_id]) >= threshold_joins

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event listener invoked when a new member joins the server.
        Calculates suspicion score and alerts moderators if risk thresholds are met.
        """
        guild = member.guild

        # Read Fox Nose settings from database
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, guild.id)
            enabled = db_guild.fox_nose_enabled if db_guild else True
            if not enabled:
                return

            log_channel_id = db_guild.fox_nose_log_channel if db_guild else None
            threshold_joins = db_guild.raid_threshold_joins if db_guild else 5
            threshold_seconds = db_guild.raid_threshold_seconds if db_guild else 10

        now = time.time()
        is_raid_active = guild.id in self.raid_lockdown and now < self.raid_lockdown[guild.id]

        # Check for rapid join surge
        surge_detected = self.check_raid_surge(guild.id, threshold_joins, threshold_seconds)
        if surge_detected and not is_raid_active:
            # Activate raid alert state for 10 minutes (600 seconds)
            self.raid_lockdown[guild.id] = now + 600
            is_raid_active = True
            await self._notify_raid_alert(guild, log_channel_id)

        sus_score, reasons = self.calculate_sus_score(member, is_raid_active)

        # Dispatch alert to moderation log channel if user is suspicious or raid is active
        if sus_score >= 30 or is_raid_active:
            log_channel = guild.get_channel(log_channel_id) if log_channel_id else None
            if log_channel is None:
                # Fallback to system channel or first sendable text channel
                log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

            if log_channel:
                embed = discord.Embed(
                    title="Fox Nose - Suspicious Account Alert",
                    description="Fox Nose security has analyzed a user joining the server.",
                    color=discord.Color.red() if sus_score >= 70 else discord.Color.gold(),
                )
                embed.add_field(name="User", value=f"{member.mention} (`{member.id}`)", inline=True)
                embed.add_field(name="Suspect Score", value=f"**{sus_score} / 100**", inline=True)
                embed.add_field(
                    name="Account Created",
                    value=f"<t:{int(member.created_at.timestamp())}:R>",
                    inline=True,
                )
                embed.add_field(
                    name="Risk Indicators",
                    value="\n".join(reasons) if reasons else "None",
                    inline=False,
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Fox Nose Security Monitoring System")

                try:
                    await log_channel.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

    async def _notify_raid_alert(self, guild: discord.Guild, log_channel_id: int | None):
        """
        Sends a high-priority Raid Alert notification embed to the moderation log channel.
        """
        log_channel = guild.get_channel(log_channel_id) if log_channel_id else None
        if log_channel is None:
            log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

        if log_channel:
            embed = discord.Embed(
                title="RAID SURGE DETECTED - SERVER UNDER ATTACK",
                description=(
                    "An abnormal join rate surge has been detected!\n"
                    "Raid Alert Mode has been activated for 10 minutes.\n"
                    "Incoming users will be logged and monitored closely."
                ),
                color=discord.Color.dark_red(),
            )
            embed.set_footer(text="Fox Nose Anti-Raid Alert System")

            try:
                await log_channel.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

    @app_commands.command(name="status", description="Check current Raid alert status and Fox Nose settings.")
    @app_commands.default_permissions(manage_guild=True)
    async def status(self, interaction: discord.Interaction):
        """
        Displays current Fox Nose settings, active log channel, and raid alert status.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        now = time.time()
        is_raid_active = guild_id in self.raid_lockdown and now < self.raid_lockdown[guild_id]

        async with SessionLocal() as session:
            db_guild = await session.get(Guild, guild_id)
            enabled = db_guild.fox_nose_enabled if db_guild else True
            log_ch = db_guild.fox_nose_log_channel if db_guild else None

        embed = discord.Embed(
            title="Fox Nose Status and Settings",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Protection Status", value="Active" if enabled else "Disabled", inline=True)
        embed.add_field(name="Raid Alert Mode", value="ACTIVE" if is_raid_active else "Normal", inline=True)
        embed.add_field(name="Log Channel", value=f"<#{log_ch}>" if log_ch else "None (Default system channel)", inline=False)
        embed.set_footer(text="Fox Nose Security Monitoring System")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="audit", description="Manually analyze a member for suspicious account indicators.")
    @app_commands.default_permissions(manage_guild=True)
    async def audit(self, interaction: discord.Interaction, member: discord.Member):
        """
        Manually runs the risk scoring engine on any specified server member.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        now = time.time()
        is_raid = interaction.guild_id in self.raid_lockdown and now < self.raid_lockdown[interaction.guild_id]
        sus_score, reasons = self.calculate_sus_score(member, is_raid)

        embed = discord.Embed(
            title=f"Fox Nose Security Audit: {member.display_name}",
            color=discord.Color.red() if sus_score >= 70 else (discord.Color.gold() if sus_score >= 30 else discord.Color.green()),
        )
        embed.add_field(name="User", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Suspect Score", value=f"**{sus_score} / 100**", inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Risk Indicators", value="\n".join(reasons) if reasons else "No suspicious indicators detected.", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Fox Nose Security Audit System")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear_lockdown", description="Clear active Raid Alert Mode.")
    @app_commands.default_permissions(manage_guild=True)
    async def clear_lockdown(self, interaction: discord.Interaction):
        """
        Deactivates active Raid Alert state for the server.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        if guild_id in self.raid_lockdown:
            del self.raid_lockdown[guild_id]

        await interaction.response.send_message("Raid Alert Mode has been deactivated by an Administrator.", ephemeral=False)

    @app_commands.command(name="config", description="Configure Fox Nose settings for this server.")
    @app_commands.default_permissions(manage_guild=True)
    async def config(
        self,
        interaction: discord.Interaction,
        enabled: bool | None = None,
        log_channel: discord.TextChannel | None = None,
    ):
        """
        Updates Fox Nose configuration settings in the persistent database.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        async with SessionLocal() as session:
            async with session.begin():
                db_guild = await session.get(Guild, guild_id)
                if db_guild is None:
                    db_guild = Guild(guild_id=guild_id)
                    session.add(db_guild)
                    await session.flush()

                if enabled is not None:
                    db_guild.fox_nose_enabled = enabled
                if log_channel is not None:
                    db_guild.fox_nose_log_channel = log_channel.id

        await interaction.response.send_message("Fox Nose configuration updated successfully.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FoxNose(bot))
