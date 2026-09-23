from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy Declarative ORM Models.
    """
    pass


class Guild(Base):
    """
    Represents Discord Server (Guild) persistent configuration data stored in the database.
    """
    __tablename__ = "guilds"

    # Primary Key: Discord Guild Unique Identifier (BigInteger)
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Welcome System Configuration
    welcome_channel: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Cow Drop / Economy Channel Configuration
    cow_drop_channel: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Experience (XP) & Leveling System Settings
    xp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    xp_min: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    xp_max: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    xp_cooldown: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # Fox Nose Security & Anti-Raid System Settings
    fox_nose_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fox_nose_log_channel: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    auto_quarantine_score: Mapped[int] = mapped_column(Integer, default=70, nullable=False)
    raid_threshold_joins: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    raid_threshold_seconds: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # One-to-many relationship with Reaction Role messages
    reaction_roles: Mapped[list[ReactionRole]] = relationship(
        back_populates="guild", cascade="all, delete-orphan", passive_deletes=True
    )


class ReactionRole(Base):
    """
    Represents a Reaction Role Message created within a specific channel.
    """
    __tablename__ = "reaction_roles"
    __table_args__ = (
        UniqueConstraint("guild_id", "channel_id", "message_id", name="uq_reaction_roles_message"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Parent relationship back to Guild model
    guild: Mapped[Guild] = relationship(back_populates="reaction_roles")

    # One-to-many relationship with Reaction Role Emoji-Role Mappings
    items: Mapped[list[ReactionRoleItem]] = relationship(
        back_populates="reaction_role", cascade="all, delete-orphan", passive_deletes=True
    )


class ReactionRoleItem(Base):
    """
    Represents an individual mapping between an Emoji reaction and a Discord Role ID.
    """
    __tablename__ = "reaction_role_items"
    __table_args__ = (
        UniqueConstraint("reaction_role_id", "emoji", name="uq_reaction_role_items_emoji"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reaction_role_id: Mapped[int] = mapped_column(
        ForeignKey("reaction_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    emoji: Mapped[str] = mapped_column(String(64), nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Parent relationship back to ReactionRole message
    reaction_role: Mapped[ReactionRole] = relationship(back_populates="items")


class UserXP(Base):
    """
    Represents an individual user's Experience Points (XP), Level, and Message Stats
    within a specific Discord Server (Guild).
    """
    __tablename__ = "user_xp"
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_user_xp_guild_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
