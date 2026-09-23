import time
import random
import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select, func

from database.db import SessionLocal
from database.models import Guild, UserXP


def get_xp_needed(level: int) -> int:
    """
    Calculates total cumulative XP required to reach the given level.
    Formula: 50 * (level ** 2) + 100 * level
    """
    return 50 * (level ** 2) + 100 * level


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Creates a text-based progress bar showing completion percentage.
    """
    if total <= 0:
        return "[" + "=" * length + "]"
    progress = min(1.0, max(0.0, current / total))
    filled = int(progress * length)
    empty = length - filled
    return "[" + "=" * filled + "-" * empty + "]"


class XPCog(commands.Cog):
    """
    XP & Leveling System Cog — Tracks message activity, awards experience points,
    handles level-up calculations, and provides /rank and /leaderboard commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Maps (guild_id, user_id) to last XP earning timestamp
        self.cooldowns: dict[tuple[int, int], float] = {}
        print("[Cog Loaded] XP & Leveling Cog")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event listener checking incoming messages for XP distribution.
        """
        # Ignore bot messages and non-guild messages
        if message.author.bot or message.guild is None:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        now = time.time()

        # Query guild XP settings from database
        async with SessionLocal() as session:
            db_guild = await session.get(Guild, guild_id)
            if db_guild is None or not db_guild.xp_enabled:
                return

            xp_min = db_guild.xp_min
            xp_max = db_guild.xp_max
            cooldown = db_guild.xp_cooldown

        # Rate limiting check per user
        last_earned = self.cooldowns.get((guild_id, user_id), 0.0)
        if now - last_earned < cooldown:
            return

        self.cooldowns[(guild_id, user_id)] = now
        xp_gain = random.randint(xp_min, xp_max)

        leveled_up = False
        new_level = 1

        # Atomically update or insert user XP record
        async with SessionLocal() as session:
            async with session.begin():
                stmt = select(UserXP).where(UserXP.guild_id == guild_id, UserXP.user_id == user_id)
                user_xp = (await session.execute(stmt)).scalar_one_or_none()

                if user_xp is None:
                    user_xp = UserXP(guild_id=guild_id, user_id=user_id, xp=0, level=1, message_count=0)
                    session.add(user_xp)
                    await session.flush()

                user_xp.xp += xp_gain
                user_xp.message_count += 1

                # Level up calculation
                needed_xp = get_xp_needed(user_xp.level)
                while user_xp.xp >= needed_xp:
                    user_xp.level += 1
                    leveled_up = True
                    needed_xp = get_xp_needed(user_xp.level)

                new_level = user_xp.level

        # Dispatch level-up notification message
        if leveled_up:
            try:
                embed = discord.Embed(
                    title="Level Up",
                    description=f"Congratulations {message.author.mention}! You have reached **Level {new_level}**.",
                    color=discord.Color.green(),
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

    @app_commands.command(name="rank", description="Check your current level, total XP, and rank progress.")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None):
        """
        Slash command displaying level, XP, message count, and progress bar for a user.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        target = member or interaction.user
        guild_id = interaction.guild_id
        user_id = target.id

        async with SessionLocal() as session:
            # Query target user's XP record
            stmt = select(UserXP).where(UserXP.guild_id == guild_id, UserXP.user_id == user_id)
            user_xp = (await session.execute(stmt)).scalar_one_or_none()

            if user_xp is None:
                current_xp = 0
                current_level = 1
                messages_sent = 0
            else:
                current_xp = user_xp.xp
                current_level = user_xp.level
                messages_sent = user_xp.message_count

            # Calculate server rank position
            rank_stmt = (
                select(func.count(UserXP.id))
                .where(UserXP.guild_id == guild_id, UserXP.xp > current_xp)
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
        embed.set_footer(text="XP and Leveling System")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Display the top 10 members with highest XP in this server.")
    async def leaderboard(self, interaction: discord.Interaction):
        """
        Slash command displaying the server's top 10 leaderboard by XP.
        """
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        async with SessionLocal() as session:
            stmt = (
                select(UserXP)
                .where(UserXP.guild_id == guild_id)
                .order_by(UserXP.xp.desc())
                .limit(10)
            )
            top_users = (await session.execute(stmt)).scalars().all()

        if not top_users:
            await interaction.response.send_message("No XP records found for this server yet.", ephemeral=True)
            return

        description_lines = []
        for index, record in enumerate(top_users, start=1):
            member = interaction.guild.get_member(record.user_id)
            name = member.display_name if member else f"User ID {record.user_id}"
            description_lines.append(
                f"**#{index}** {name} — Level {record.level} ({record.xp:,} XP)"
            )

        embed = discord.Embed(
            title=f"Leaderboard - {interaction.guild.name}",
            description="\n".join(description_lines),
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text="Top Server Members by XP")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(XPCog(bot))
