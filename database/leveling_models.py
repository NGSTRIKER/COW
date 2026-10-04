from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class LevelingBase(DeclarativeBase):
    """
    Base class for all SQLAlchemy Declarative ORM models in the leveling subsystem.
    Stored in a separate, dedicated database file (leveling.db).
    """
    pass


class GuildLevelingConfig(LevelingBase):
    """
    Persistent leveling configuration per Discord guild.
    Controls standard global leveling, multi-channel leveling, and announcement behaviors.
    """
    __tablename__ = "guild_leveling_config"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    standard_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    multichannel_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    standard_min_xp: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    standard_max_xp: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    standard_cooldown: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    announcements_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    announcement_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


class ChannelXpRate(LevelingBase):
    """
    Per-channel configuration for multi-channel leveling (up to 10 slots per guild).
    Defines the rate of XP awarded per message, cooldown duration, slot number (1-10),
    and system name named after the channel.
    """
    __tablename__ = "channel_xp_rates"
    __table_args__ = (
        UniqueConstraint("guild_id", "channel_id", name="uq_channel_xp_guild_channel"),
        UniqueConstraint("guild_id", "slot_number", name="uq_channel_xp_guild_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    slot_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    channel_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    system_name: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    exp_per_msg: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    cooldown: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserStandardXP(LevelingBase):
    """
    Tracks a user's global standard server XP and level across the entire guild.
    """
    __tablename__ = "user_standard_xp"
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_user_std_xp_guild_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class UserChannelXP(LevelingBase):
    """
    Tracks a user's multi-channel XP and level within a specific channel.
    """
    __tablename__ = "user_channel_xp"
    __table_args__ = (
        UniqueConstraint("guild_id", "channel_id", "user_id", name="uq_user_channel_xp_entry"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
