import random
import time
import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import func, select

from database.leveling_db import LevelingSessionLocal
from database.leveling_models import (
    ChannelXpRate,
    GuildLevelingConfig,
    UserChannelXP,
    UserStandardXP,
)

MAX_CHANNEL_SLOTS = 10


def get_xp_needed(level: int) -> int:
    """
    Calculates total cumulative XP required to reach the given level.
    Formula: 50 * (level ** 2) + 100 * level
    """
    return 50 * (level ** 2) + 100 * level


def create_progress_bar(current: int, total: int, length: int = 8) -> str:
    """
    Creates a text-based progress bar showing completion percentage.
    """
    if total <= 0:
        return "[" + "=" * length + "]"
    progress = min(1.0, max(0.0, current / total))
    filled = int(progress * length)
    empty = length - filled
    return "[" + "=" * filled + "-" * empty + "]"


class LevelingCog(commands.Cog):
    """
    Comprehensive Leveling System Cog supporting:
    1. Standard Leveling System (Server-wide XP and levels)
    2. Multi-Channel Leveling System (Up to 10 channel slots, each with its own named leveling system)
    3. Dedicated SQLite database storage in WAL mode (zero data loss across restarts)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # In-memory cooldown tracking: (guild_id, user_id) -> timestamp
        self.standard_cooldowns: dict[tuple[int, int], float] = {}
        # In-memory cooldown tracking: (guild_id, channel_id, user_id) -> timestamp
        self.channel_cooldowns: dict[tuple[int, int, int], float] = {}
        print("[Cog Loaded] Comprehensive Leveling Cog (Standard + Multi-Channel, 10 Slots)")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event listener checking incoming messages for both standard server XP
        and configured multi-channel slot XP allocations.
        """
        if message.author.bot or message.guild is None:
            return

        guild_id = message.guild.id
        channel_id = message.channel.id
        user_id = message.author.id
        now = time.time()

        # 1. Fetch guild leveling configuration and check channel rate
        async with LevelingSessionLocal() as session:
            config = await session.get(GuildLevelingConfig, guild_id)
            if config is None:
                config = GuildLevelingConfig(guild_id=guild_id)
                session.add(config)
                await session.commit()
                await session.refresh(config)

            standard_enabled = config.standard_enabled
            multichannel_enabled = config.multichannel_enabled
            std_min_xp = config.standard_min_xp
            std_max_xp = config.standard_max_xp
            std_cooldown = config.standard_cooldown
            announcements_enabled = config.announcements_enabled

            channel_rate = None
            if multichannel_enabled:
                stmt = select(ChannelXpRate).where(
                    ChannelXpRate.guild_id == guild_id,
                    ChannelXpRate.channel_id == channel_id,
                    ChannelXpRate.is_enabled == True,
                )
                channel_rate = (await session.execute(stmt)).scalar_one_or_none()

        std_leveled_up = False
        std_new_level = 1
        ch_leveled_up = False
        ch_new_level = 1
        ch_system_name = ""

        # 2. Process Multi-Channel XP allocation if this channel has a configured slot
        if multichannel_enabled and channel_rate is not None:
            ch_cooldown_key = (guild_id, channel_id, user_id)
            last_ch_earned = self.channel_cooldowns.get(ch_cooldown_key, 0.0)

            if now - last_ch_earned >= channel_rate.cooldown:
                self.channel_cooldowns[ch_cooldown_key] = now
                xp_gain = channel_rate.exp_per_msg
                ch_system_name = channel_rate.system_name or f"#{message.channel.name} Leveling"

                async with LevelingSessionLocal() as session:
                    stmt = select(UserChannelXP).where(
                        UserChannelXP.guild_id == guild_id,
                        UserChannelXP.channel_id == channel_id,
                        UserChannelXP.user_id == user_id,
                    )
                    ch_xp_record = (await session.execute(stmt)).scalar_one_or_none()

                    if ch_xp_record is None:
                        ch_xp_record = UserChannelXP(
                            guild_id=guild_id,
                            channel_id=channel_id,
                            user_id=user_id,
                            xp=0,
                            level=1,
                            message_count=0,
                        )
                        session.add(ch_xp_record)

                    ch_xp_record.xp += xp_gain
                    ch_xp_record.message_count += 1

                    # Channel level up calculation
                    needed_ch_xp = get_xp_needed(ch_xp_record.level)
                    while ch_xp_record.xp >= needed_ch_xp:
                        ch_xp_record.level += 1
                        ch_leveled_up = True
                        needed_ch_xp = get_xp_needed(ch_xp_record.level)

                    ch_new_level = ch_xp_record.level
                    await session.commit()

        # 3. Process Standard Server XP allocation
        if standard_enabled:
            std_cooldown_key = (guild_id, user_id)
            last_std_earned = self.standard_cooldowns.get(std_cooldown_key, 0.0)

            if now - last_std_earned >= std_cooldown:
                self.standard_cooldowns[std_cooldown_key] = now
                std_xp_gain = random.randint(std_min_xp, std_max_xp)

                async with LevelingSessionLocal() as session:
                    stmt = select(UserStandardXP).where(
                        UserStandardXP.guild_id == guild_id,
                        UserStandardXP.user_id == user_id,
                    )
                    std_xp_record = (await session.execute(stmt)).scalar_one_or_none()

                    if std_xp_record is None:
                        std_xp_record = UserStandardXP(
                            guild_id=guild_id,
                            user_id=user_id,
                            xp=0,
                            level=1,
                            message_count=0,
                        )
                        session.add(std_xp_record)

                    std_xp_record.xp += std_xp_gain
                    std_xp_record.message_count += 1

                    # Standard level up calculation
                    needed_std_xp = get_xp_needed(std_xp_record.level)
                    while std_xp_record.xp >= needed_std_xp:
                        std_xp_record.level += 1
                        std_leveled_up = True
                        needed_std_xp = get_xp_needed(std_xp_record.level)

                    std_new_level = std_xp_record.level
                    await session.commit()

        # 4. Send Level Up Announcements if enabled
        if announcements_enabled:
            if ch_leveled_up:
                try:
                    embed = discord.Embed(
                        title="Channel Level Up",
                        description=f"Congratulations {message.author.mention}! You reached **Level {ch_new_level}** in **{ch_system_name}** (<#{message.channel.id}>)!",
                        color=discord.Color.teal(),
                    )
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.set_footer(text=f"{ch_system_name} | Multi-Channel Leveling")
                    await message.channel.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

            if std_leveled_up:
                try:
                    embed = discord.Embed(
                        title="Server Level Up",
                        description=f"Congratulations {message.author.mention}! You have reached server **Level {std_new_level}**!",
                        color=discord.Color.green(),
                    )
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.set_footer(text="Standard Server Leveling")
                    await message.channel.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

    # =========================================================================
    # User Profile & Rank Commands
    # =========================================================================

    @app_commands.command(
        name="profile",
        description="View your or another user's leveling profile across all channel leveling systems.",
    )
    @app_commands.describe(user="The server member whose profile you want to view")
    async def profile(self, interaction: discord.Interaction, user: discord.Member | None = None):
        """
        Displays user's full leveling profile including:
        - Global standard server level, total XP, rank position, and progress bar
        - Every configured channel leveling system (up to 10 slots) with channel name, level, XP, and rank
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        target = user or interaction.user
        guild_id = interaction.guild_id
        target_id = target.id

        async with LevelingSessionLocal() as session:
            # 1. Query standard server XP record
            std_stmt = select(UserStandardXP).where(
                UserStandardXP.guild_id == guild_id,
                UserStandardXP.user_id == target_id,
            )
            std_record = (await session.execute(std_stmt)).scalar_one_or_none()

            current_std_xp = std_record.xp if std_record else 0
            current_std_level = std_record.level if std_record else 1
            std_messages = std_record.message_count if std_record else 0

            # Global server rank
            rank_stmt = select(func.count(UserStandardXP.id)).where(
                UserStandardXP.guild_id == guild_id,
                UserStandardXP.xp > current_std_xp,
            )
            higher_users = (await session.execute(rank_stmt)).scalar() or 0
            std_rank_position = higher_users + 1

            # 2. Query all configured channel slots for this guild (up to 10 slots)
            slots_stmt = (
                select(ChannelXpRate)
                .where(ChannelXpRate.guild_id == guild_id)
                .order_by(ChannelXpRate.slot_number.asc())
            )
            configured_slots = (await session.execute(slots_stmt)).scalars().all()

            # 3. Query all user channel XP records for target
            user_ch_stmt = select(UserChannelXP).where(
                UserChannelXP.guild_id == guild_id,
                UserChannelXP.user_id == target_id,
            )
            user_channel_records = {r.channel_id: r for r in (await session.execute(user_ch_stmt)).scalars().all()}

            # 4. Compute per-channel rank for target for each configured channel
            channel_ranks: dict[int, int] = {}
            for slot in configured_slots:
                ch_xp_val = user_channel_records[slot.channel_id].xp if slot.channel_id in user_channel_records else 0
                ch_rank_stmt = select(func.count(UserChannelXP.id)).where(
                    UserChannelXP.guild_id == guild_id,
                    UserChannelXP.channel_id == slot.channel_id,
                    UserChannelXP.xp > ch_xp_val,
                )
                higher_ch = (await session.execute(ch_rank_stmt)).scalar() or 0
                channel_ranks[slot.channel_id] = higher_ch + 1

        # Build Standard Progress Bar
        prev_xp = get_xp_needed(current_std_level - 1) if current_std_level > 1 else 0
        next_xp = get_xp_needed(current_std_level)
        needed_in_lvl = max(1, next_xp - prev_xp)
        xp_in_lvl = max(0, current_std_xp - prev_xp)
        std_progress_bar = create_progress_bar(xp_in_lvl, needed_in_lvl, length=10)

        embed = discord.Embed(
            title=f"Leveling Profile - {target.display_name}",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        # Standard Leveling Field
        embed.add_field(
            name="Global Server Leveling",
            value=(
                f"**Rank:** #{std_rank_position} • **Level:** {current_std_level} ({current_std_xp:,} XP)\n"
                f"**Progress:** `{std_progress_bar}` ({xp_in_lvl:,}/{needed_in_lvl:,} XP)\n"
                f"**Messages Sent:** {std_messages:,}"
            ),
            inline=False,
        )

        # Multi-Channel Leveling Slots
        if configured_slots:
            slot_sections = []
            for slot in configured_slots:
                ch_obj = interaction.guild.get_channel(slot.channel_id)
                ch_mention = ch_obj.mention if ch_obj else f"<#{slot.channel_id}>"
                system_name = slot.system_name or f"#{slot.channel_name or 'channel'} Leveling System"

                rec = user_channel_records.get(slot.channel_id)
                ch_lvl = rec.level if rec else 1
                ch_xp = rec.xp if rec else 0
                ch_msgs = rec.message_count if rec else 0
                ch_rank = channel_ranks.get(slot.channel_id, 1)

                ch_prev_xp = get_xp_needed(ch_lvl - 1) if ch_lvl > 1 else 0
                ch_next_xp = get_xp_needed(ch_lvl)
                ch_needed = max(1, ch_next_xp - ch_prev_xp)
                ch_current_in_lvl = max(0, ch_xp - ch_prev_xp)
                ch_bar = create_progress_bar(ch_current_in_lvl, ch_needed, length=8)

                status_icon = "Active" if slot.is_enabled else "Paused"

                slot_sections.append(
                    f"**Slot {slot.slot_number}: {system_name}** ({ch_mention})\n"
                    f"• **Level {ch_lvl}** | **{ch_xp:,} XP** | Rank #{ch_rank} | {ch_msgs:,} msgs\n"
                    f"• Progress: `{ch_bar}` ({ch_current_in_lvl:,}/{ch_needed:,} XP) • Rate: {slot.exp_per_msg} XP/msg [{status_icon}]"
                )

            embed.add_field(
                name=f"Channel Leveling Systems ({len(configured_slots)}/{MAX_CHANNEL_SLOTS} Slots)",
                value="\n\n".join(slot_sections),
                inline=False,
            )
        else:
            embed.add_field(
                name=f"Channel Leveling Systems (0/{MAX_CHANNEL_SLOTS} Slots Configured)",
                value="No multi-channel leveling systems configured yet.\nServer admins can configure up to 10 channel slots via `/leveling channel_set` or `/dashboard`.",
                inline=False,
            )

        embed.set_footer(text="Multi-Channel & Standard Leveling System | Persistent SQLite")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank", description="Check your current global server rank and progress.")
    @app_commands.describe(member="The server member whose rank you want to check")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None):
        """
        Fast command displaying global server level, total XP, and progress bar.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        target = member or interaction.user
        guild_id = interaction.guild_id
        user_id = target.id

        async with LevelingSessionLocal() as session:
            stmt = select(UserStandardXP).where(
                UserStandardXP.guild_id == guild_id,
                UserStandardXP.user_id == user_id,
            )
            user_xp = (await session.execute(stmt)).scalar_one_or_none()

            current_xp = user_xp.xp if user_xp else 0
            current_level = user_xp.level if user_xp else 1
            messages_sent = user_xp.message_count if user_xp else 0

            rank_stmt = select(func.count(UserStandardXP.id)).where(
                UserStandardXP.guild_id == guild_id,
                UserStandardXP.xp > current_xp,
            )
            higher_users = (await session.execute(rank_stmt)).scalar() or 0
            rank_position = higher_users + 1

        prev_level_xp = get_xp_needed(current_level - 1) if current_level > 1 else 0
        next_level_xp = get_xp_needed(current_level)
        xp_in_level = current_xp - prev_level_xp
        needed_in_level = next_level_xp - prev_level_xp

        bar = create_progress_bar(xp_in_level, needed_in_level, length=12)

        embed = discord.Embed(
            title=f"Rank Card - {target.display_name}",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Server Rank", value=f"#{rank_position}", inline=True)
        embed.add_field(name="Level", value=f"Level {current_level}", inline=True)
        embed.add_field(name="Total XP", value=f"{current_xp:,} XP", inline=True)
        embed.add_field(
            name="Progress to Next Level",
            value=f"`{bar}` ({xp_in_level:,} / {needed_in_level:,} XP)",
            inline=False,
        )
        embed.add_field(name="Messages Sent", value=f"{messages_sent:,}", inline=True)
        embed.set_footer(text="Standard Server Leveling | For all channel systems use /profile")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="leaderboard",
        description="Display top members by XP (global server or specific channel system).",
    )
    @app_commands.describe(channel="Filter leaderboard by a specific channel system (leave empty for global server leaderboard)")
    async def leaderboard(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        """
        Displays top 10 leaderboard either globally or for a specific channel.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        async with LevelingSessionLocal() as session:
            if channel is not None:
                stmt = (
                    select(UserChannelXP)
                    .where(
                        UserChannelXP.guild_id == guild_id,
                        UserChannelXP.channel_id == channel.id,
                    )
                    .order_by(UserChannelXP.xp.desc())
                    .limit(10)
                )
                top_users = (await session.execute(stmt)).scalars().all()

                # Get system name
                rate_stmt = select(ChannelXpRate).where(
                    ChannelXpRate.guild_id == guild_id,
                    ChannelXpRate.channel_id == channel.id,
                )
                rate = (await session.execute(rate_stmt)).scalar_one_or_none()
                sys_title = rate.system_name if rate else f"#{channel.name} Leveling"

                title = f"Leaderboard - {sys_title}"
                footer = f"Channel Leaderboard for #{channel.name}"
            else:
                stmt = (
                    select(UserStandardXP)
                    .where(UserStandardXP.guild_id == guild_id)
                    .order_by(UserStandardXP.xp.desc())
                    .limit(10)
                )
                top_users = (await session.execute(stmt)).scalars().all()
                title = f"Leaderboard - {interaction.guild.name}"
                footer = "Global Server Leaderboard"

        if not top_users:
            await interaction.response.send_message("No leveling records found for this query yet.", ephemeral=True)
            return

        description_lines = []
        for index, record in enumerate(top_users, start=1):
            member = interaction.guild.get_member(record.user_id)
            name = member.display_name if member else f"User ID {record.user_id}"
            description_lines.append(
                f"**#{index}** {name} — Level {record.level} ({record.xp:,} XP • {record.message_count:,} msgs)"
            )

        embed = discord.Embed(
            title=title,
            description="\n".join(description_lines),
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=footer)

        await interaction.response.send_message(embed=embed)

    # =========================================================================
    # Admin Configuration Commands (/leveling group)
    # =========================================================================

    leveling_group = app_commands.Group(
        name="leveling",
        description="Administrative commands for managing multi-channel and standard leveling.",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @leveling_group.command(
        name="channel_set",
        description="Configure a channel leveling system in one of the 10 slots.",
    )
    @app_commands.describe(
        channel="The text channel to configure for its own leveling system",
        exp_per_msg="XP points awarded per message in this channel",
        slot="Slot number (1 to 10). Leave empty to use next available slot.",
        system_name="Custom name for this leveling system (defaults to '#<channel> Leveling System')",
        cooldown="Cooldown between XP awards in seconds (default: 30)",
        enabled="Whether XP earning is active in this channel (default: True)",
    )
    async def channel_set(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        exp_per_msg: int,
        slot: int | None = None,
        system_name: str | None = None,
        cooldown: int = 30,
        enabled: bool = True,
    ):
        """
        Configures or updates a channel leveling system slot (maximum 10 slots).
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        if exp_per_msg <= 0:
            await interaction.response.send_message("XP per message must be greater than 0.", ephemeral=True)
            return

        if cooldown < 0:
            await interaction.response.send_message("Cooldown cannot be negative.", ephemeral=True)
            return

        if slot is not None and not (1 <= slot <= MAX_CHANNEL_SLOTS):
            await interaction.response.send_message(f"Slot must be between 1 and {MAX_CHANNEL_SLOTS}.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        final_system_name = system_name.strip() if system_name else f"#{channel.name} Leveling System"

        async with LevelingSessionLocal() as session:
            # Check existing slots in guild
            stmt = select(ChannelXpRate).where(ChannelXpRate.guild_id == guild_id)
            existing_rates = (await session.execute(stmt)).scalars().all()
            existing_by_channel = {r.channel_id: r for r in existing_rates}
            existing_slots = {r.slot_number: r for r in existing_rates}

            target_rate = existing_by_channel.get(channel.id)

            if slot is not None:
                assigned_slot = slot
                # If slot is taken by another channel, we can overwrite or update
                if assigned_slot in existing_slots and existing_slots[assigned_slot].channel_id != channel.id:
                    await session.delete(existing_slots[assigned_slot])
            else:
                if target_rate is not None:
                    assigned_slot = target_rate.slot_number
                else:
                    # Find lowest available slot
                    available_slots = [s for s in range(1, MAX_CHANNEL_SLOTS + 1) if s not in existing_slots]
                    if not available_slots:
                        await interaction.response.send_message(
                            f"All {MAX_CHANNEL_SLOTS} channel leveling slots are full! Please use `/leveling channel_remove` to free up a slot.",
                            ephemeral=True,
                        )
                        return
                    assigned_slot = available_slots[0]

            if target_rate is None:
                target_rate = ChannelXpRate(
                    guild_id=guild_id,
                    slot_number=assigned_slot,
                    channel_id=channel.id,
                    channel_name=channel.name,
                    system_name=final_system_name,
                    exp_per_msg=exp_per_msg,
                    cooldown=cooldown,
                    is_enabled=enabled,
                )
                session.add(target_rate)
            else:
                target_rate.slot_number = assigned_slot
                target_rate.channel_name = channel.name
                target_rate.system_name = final_system_name
                target_rate.exp_per_msg = exp_per_msg
                target_rate.cooldown = cooldown
                target_rate.is_enabled = enabled

            await session.commit()

        embed = discord.Embed(
            title=f"Slot {assigned_slot} Configured: {final_system_name}",
            description=f"Successfully configured leveling system for {channel.mention}.",
            color=discord.Color.green(),
        )
        embed.add_field(name="Slot Number", value=f"Slot {assigned_slot} / {MAX_CHANNEL_SLOTS}", inline=True)
        embed.add_field(name="System Name", value=final_system_name, inline=True)
        embed.add_field(name="XP Per Message", value=f"{exp_per_msg} XP", inline=True)
        embed.add_field(name="Cooldown", value=f"{cooldown}s", inline=True)
        embed.add_field(name="Status", value="Active" if enabled else "Disabled", inline=True)
        embed.set_footer(text="Persistent SQLite leveling.db storage | WAL Mode")

        await interaction.response.send_message(embed=embed)

    @leveling_group.command(
        name="channel_remove",
        description="Remove a channel leveling system from its slot.",
    )
    @app_commands.describe(
        channel="The channel to remove",
        slot="Or the slot number (1 to 10) to remove",
    )
    async def channel_remove(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
        slot: int | None = None,
    ):
        """
        Removes a channel configuration by channel or slot number.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        if channel is None and slot is None:
            await interaction.response.send_message("Please provide either a `channel` or a `slot` number to remove.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        async with LevelingSessionLocal() as session:
            if channel is not None:
                stmt = select(ChannelXpRate).where(
                    ChannelXpRate.guild_id == guild_id,
                    ChannelXpRate.channel_id == channel.id,
                )
            else:
                stmt = select(ChannelXpRate).where(
                    ChannelXpRate.guild_id == guild_id,
                    ChannelXpRate.slot_number == slot,
                )

            rate = (await session.execute(stmt)).scalar_one_or_none()

            if rate is None:
                await interaction.response.send_message("No channel leveling slot found matching your query.", ephemeral=True)
                return

            removed_name = rate.system_name or f"<#{rate.channel_id}>"
            removed_slot = rate.slot_number
            await session.delete(rate)
            await session.commit()

        await interaction.response.send_message(
            f"Removed **Slot {removed_slot}: {removed_name}** from multi-channel leveling.",
            ephemeral=True,
        )

    @leveling_group.command(
        name="channel_list",
        description="List all 10 channel leveling system slots and their configurations.",
    )
    async def channel_list(self, interaction: discord.Interaction):
        """
        Lists all 10 slots showing active channel leveling systems.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        async with LevelingSessionLocal() as session:
            stmt = (
                select(ChannelXpRate)
                .where(ChannelXpRate.guild_id == guild_id)
                .order_by(ChannelXpRate.slot_number.asc())
            )
            rates = {r.slot_number: r for r in (await session.execute(stmt)).scalars().all()}

        lines = []
        for s in range(1, MAX_CHANNEL_SLOTS + 1):
            if s in rates:
                rate = rates[s]
                status_txt = "Active" if rate.is_enabled else "Paused"
                sys_title = rate.system_name or f"#{rate.channel_name} Leveling"
                lines.append(
                    f"**Slot {s}:** {sys_title} (<#{rate.channel_id}>)\n"
                    f"└ **{rate.exp_per_msg} XP/msg** • Cooldown: {rate.cooldown}s • [{status_txt}]"
                )
            else:
                lines.append(f"**Slot {s}:** *[Empty Slot]*")

        embed = discord.Embed(
            title=f"Multi-Channel Leveling Slots - {interaction.guild.name}",
            description="\n\n".join(lines),
            color=discord.Color.teal(),
        )
        embed.set_footer(text=f"Total: {len(rates)} / {MAX_CHANNEL_SLOTS} Slots Configured | Use /leveling channel_set")

        await interaction.response.send_message(embed=embed)

    @leveling_group.command(
        name="settings",
        description="Toggle leveling subsystems or adjust announcements.",
    )
    @app_commands.describe(
        standard_enabled="Toggle global server leveling system",
        multichannel_enabled="Toggle multi-channel leveling system",
        announcements="Toggle level-up announcement messages",
    )
    async def settings(
        self,
        interaction: discord.Interaction,
        standard_enabled: bool | None = None,
        multichannel_enabled: bool | None = None,
        announcements: bool | None = None,
    ):
        """
        Slash command to view or update leveling settings.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        async with LevelingSessionLocal() as session:
            config = await session.get(GuildLevelingConfig, guild_id)
            if config is None:
                config = GuildLevelingConfig(guild_id=guild_id)
                session.add(config)

            if standard_enabled is not None:
                config.standard_enabled = standard_enabled
            if multichannel_enabled is not None:
                config.multichannel_enabled = multichannel_enabled
            if announcements is not None:
                config.announcements_enabled = announcements

            await session.commit()
            await session.refresh(config)

            std_status = "Enabled" if config.standard_enabled else "Disabled"
            mc_status = "Enabled" if config.multichannel_enabled else "Disabled"
            ann_status = "Enabled" if config.announcements_enabled else "Disabled"

        embed = discord.Embed(
            title="Leveling System Settings",
            description=f"Current configuration for **{interaction.guild.name}**:",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Standard Server Leveling", value=std_status, inline=True)
        embed.add_field(name="Multi-Channel Leveling", value=mc_status, inline=True)
        embed.add_field(name="Level Up Announcements", value=ann_status, inline=True)
        embed.set_footer(text="Settings stored in dedicated SQLite leveling.db")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelingCog(bot))
