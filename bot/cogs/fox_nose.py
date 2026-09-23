import time
import re
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from database.db import SessionLocal
from database.models import Guild

DEFAULT_SUSPICIOUS_NAMES = [
    r"^user[_\-]?\d+$",
    r"^discord[_\-]?user",
    r"raid",
    r"bot",
    r"nuke",
    r"spam",
]


class FoxNose(commands.GroupCog, name="fox_nose", description="Commands for Fox Nose Raid Protection & Divine Sniffing Gu."):
    """
    🦊 Fox Nose - Divine Sniffing Gu & Anti-Raid System
    Protects Hu Immortal Blessed Land from raids and suspicious / alt accounts.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Structure: {guild_id: [timestamp1, timestamp2, ...]}
        self.join_tracker: dict[int, list[float]] = {}
        # Structure: {guild_id: lockdown_expiry_timestamp}
        self.raid_lockdown: dict[int, float] = {}
        super().__init__()

    def calculate_sus_score(self, member: discord.Member, is_raid_active: bool) -> tuple[int, list[str]]:
        score = 0
        reasons = []

        now = datetime.now(timezone.utc)
        created_at = member.created_at
        account_age_days = (now - created_at).total_seconds() / 86400.0

        # 1. Account Age Heuristics
        if account_age_days < 1:
            score += 50
            reasons.append("⚡ Account created < 24 hours ago (+50)")
        elif account_age_days < 7:
            score += 30
            reasons.append("⏳ Account created < 7 days ago (+30)")
        elif account_age_days < 30:
            score += 15
            reasons.append("📅 Account created < 30 days ago (+15)")

        # 2. Avatar Heuristic
        if member.avatar is None:
            score += 20
            reasons.append("🖼️ Default Discord avatar (+20)")

        # 3. Username / Display Name Pattern
        name_lower = member.name.lower()
        display_lower = member.display_name.lower()
        for pattern in DEFAULT_SUSPICIOUS_NAMES:
            if re.search(pattern, name_lower) or re.search(pattern, display_lower):
                score += 15
                reasons.append(f"🔍 Suspicious username pattern matched: `{pattern}` (+15)")
                break

        # 4. Raid Active Context
        if is_raid_active:
            score += 20
            reasons.append("🚨 Joined during an active Raid Surge (+20)")

        return min(score, 100), reasons

    def check_raid_surge(self, guild_id: int, threshold_joins: int, threshold_seconds: int) -> bool:
        now = time.time()
        if guild_id not in self.join_tracker:
            self.join_tracker[guild_id] = []

        # Filter out joins outside the threshold window
        self.join_tracker[guild_id] = [
            t for t in self.join_tracker[guild_id] if now - t <= threshold_seconds
        ]
        self.join_tracker[guild_id].append(now)

        return len(self.join_tracker[guild_id]) >= threshold_joins

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        async with SessionLocal() as session:
            db_guild = await session.get(Guild, guild.id)
            enabled = db_guild.fox_nose_enabled if db_guild else True
            if not enabled:
                return

            log_channel_id = db_guild.fox_nose_log_channel if db_guild else None
            auto_quarantine_score = db_guild.auto_quarantine_score if db_guild else 70
            threshold_joins = db_guild.raid_threshold_joins if db_guild else 5
            threshold_seconds = db_guild.raid_threshold_seconds if db_guild else 10

        now = time.time()
        is_raid_active = guild.id in self.raid_lockdown and now < self.raid_lockdown[guild.id]

        # Check if join surge triggers raid lockdown
        surge_detected = self.check_raid_surge(guild.id, threshold_joins, threshold_seconds)
        if surge_detected and not is_raid_active:
            # Activate lockdown for 10 minutes (600 seconds)
            self.raid_lockdown[guild.id] = now + 600
            is_raid_active = True
            await self._notify_raid_alert(guild, log_channel_id)

        sus_score, reasons = self.calculate_sus_score(member, is_raid_active)

        # Send alert if suspicious or raid active
        if sus_score >= 30 or is_raid_active:
            log_channel = guild.get_channel(log_channel_id) if log_channel_id else None
            if log_channel is None:
                # Fallback to system channel or default text channel
                log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

            if log_channel:
                embed = discord.Embed(
                    title="🦊 Fox Nose - Divine Sniffing Alert!",
                    description=f"Little Hu Immortal has sniffed a user joining **Hu Immortal Blessed Land**!",
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
                    name="Sniffed Indicators",
                    value="\n".join(reasons) if reasons else "None",
                    inline=False,
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Hu Immortal Blessed Land Guardian System 🦊")

                try:
                    await log_channel.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

        # Auto Quarantine if score is high
        if sus_score >= auto_quarantine_score:
            try:
                await member.timeout(
                    discord.utils.utcnow() + discord.utils.timedelta(minutes=30),
                    reason=f"[Fox Nose] High Suspect Score ({sus_score}/100)",
                )
            except (discord.Forbidden, discord.HTTPException):
                pass

    async def _notify_raid_alert(self, guild: discord.Guild, log_channel_id: int | None):
        log_channel = guild.get_channel(log_channel_id) if log_channel_id else None
        if log_channel is None:
            log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

        if log_channel:
            embed = discord.Embed(
                title="🚨 RAID SURGE DETECTED - BLESSED LAND UNDER ATTACK!",
                description=(
                    "Master! Little Hu Immortal detected an incoming wave of intruders!\n"
                    "**Raid Lockdown Mode** has been activated for **10 minutes**.\n"
                    "Incoming users will be closely sniffed and quarantined."
                ),
                color=discord.Color.dark_red(),
            )
            embed.set_footer(text="Hu Immortal Blessed Land Anti-Raid 🦊")
            try:
                await log_channel.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

    @app_commands.command(name="status", description="Check current Raid alert status and Fox Nose settings.")
    @app_commands.default_permissions(manage_guild=True)
    async def status(self, interaction: discord.Interaction):
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
            auto_quarantine = db_guild.auto_quarantine_score if db_guild else 70

        embed = discord.Embed(
            title="🦊 Fox Nose Status & Settings",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Protection Enabled", value="✅ Active" if enabled else "❌ Disabled", inline=True)
        embed.add_field(name="Raid Lockdown Mode", value="🚨 ACTIVE" if is_raid_active else "🟢 Normal", inline=True)
        embed.add_field(name="Log Channel", value=f"<#{log_ch}>" if log_ch else "None (Default system channel)", inline=False)
        embed.add_field(name="Auto Quarantine Score", value=f"{auto_quarantine} / 100", inline=True)
        embed.set_footer(text="Little Hu Immortal Blessed Land Protection 🦊")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="audit", description="Manually sniff a member for suspect/fake account indicators.")
    @app_commands.default_permissions(manage_guild=True)
    async def audit(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        now = time.time()
        is_raid = interaction.guild_id in self.raid_lockdown and now < self.raid_lockdown[interaction.guild_id]
        sus_score, reasons = self.calculate_sus_score(member, is_raid)

        embed = discord.Embed(
            title=f"🦊 Divine Sniffing Audit: {member.display_name}",
            color=discord.Color.red() if sus_score >= 70 else (discord.Color.gold() if sus_score >= 30 else discord.Color.green()),
        )
        embed.add_field(name="User", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Suspect Score", value=f"**{sus_score} / 100**", inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Sniffed Indicators", value="\n".join(reasons) if reasons else "✨ No suspicious indicators detected!", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Little Hu Immortal Fox Nose Audit 🦊")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear_lockdown", description="Clear active Raid Lockdown Mode.")
    @app_commands.default_permissions(manage_guild=True)
    async def clear_lockdown(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        if guild_id in self.raid_lockdown:
            del self.raid_lockdown[guild_id]

        await interaction.response.send_message("✅ **Raid Lockdown Mode** has been deactivated by Master.", ephemeral=False)

    @app_commands.command(name="config", description="Configure Fox Nose settings for this server.")
    @app_commands.default_permissions(manage_guild=True)
    async def config(
        self,
        interaction: discord.Interaction,
        enabled: bool | None = None,
        log_channel: discord.TextChannel | None = None,
        auto_quarantine_score: int | None = None,
    ):
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
                if auto_quarantine_score is not None:
                    db_guild.auto_quarantine_score = max(10, min(100, auto_quarantine_score))

        await interaction.response.send_message("✅ **Fox Nose** configuration updated successfully!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FoxNose(bot))

