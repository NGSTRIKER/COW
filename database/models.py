from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Guild(Base):
    __tablename__ = "guilds"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    welcome_channel: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    cow_drop_channel: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    xp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    xp_min: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    xp_max: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    xp_cooldown: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    reaction_roles: Mapped[list[ReactionRole]] = relationship(
        back_populates="guild", cascade="all, delete-orphan", passive_deletes=True
    )


class ReactionRole(Base):
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

    guild: Mapped[Guild] = relationship(back_populates="reaction_roles")
    items: Mapped[list[ReactionRoleItem]] = relationship(
        back_populates="reaction_role", cascade="all, delete-orphan", passive_deletes=True
    )


class ReactionRoleItem(Base):
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

    reaction_role: Mapped[ReactionRole] = relationship(back_populates="items")
