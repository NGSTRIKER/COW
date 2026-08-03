import logging

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from database.db import SessionLocal
from database.models import Guild, ReactionRole, ReactionRoleItem

NUMBER_EMOJIS = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")
LOGGER = logging.getLogger(__name__)


def can_create_auto_role(interaction: discord.Interaction) -> bool:
    permissions = interaction.permissions
    return permissions.administrator or permissions.manage_roles


class AutoRole(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="auto_role", description="Create a reaction role message.")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.check(can_create_auto_role)
    async def auto_role(
        self, interaction: discord.Interaction, title: str, description: str,
        role1: discord.Role, role2: discord.Role | None = None,
        role3: discord.Role | None = None, role4: discord.Role | None = None,
        role5: discord.Role | None = None, role6: discord.Role | None = None,
        role7: discord.Role | None = None, role8: discord.Role | None = None,
        role9: discord.Role | None = None, role10: discord.Role | None = None,
    ) -> None:
        if interaction.guild is None or interaction.channel_id is None:
            await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
            return

        roles = [role for role in (role1, role2, role3, role4, role5, role6, role7, role8, role9, role10) if role is not None]
        if any(not self._can_manage_role(role) for role in roles):
            await interaction.response.send_message(
                "I cannot manage one or more selected roles. Ensure none are managed integration roles and that my highest role is above them.",
                ephemeral=True,
            )
            return

        embed_description = "\n".join(
            [description, "", *(f"{emoji} {role.mention}" for emoji, role in zip(NUMBER_EMOJIS, roles))]
        )
        if len(title) > 256 or len(embed_description) > 4096:
            await interaction.response.send_message(
                "The title must be 256 characters or fewer and the description, including role lines, must be 4,096 characters or fewer.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=title,
            description=embed_description,
            colour=discord.Colour.green(),
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        try:
            for emoji in NUMBER_EMOJIS[:len(roles)]:
                await message.add_reaction(emoji)
        except discord.HTTPException:
            await interaction.followup.send(
                "The message was sent, but I could not add its reactions. Check that I have Add Reactions and Read Message History permissions.",
                ephemeral=True,
            )
            return

        try:
            async with SessionLocal.begin() as session:
                guild = await session.get(Guild, interaction.guild_id)
                if guild is None:
                    session.add(Guild(guild_id=interaction.guild_id))
                session.add(ReactionRole(
                    guild_id=interaction.guild_id,
                    channel_id=interaction.channel_id,
                    message_id=message.id,
                    title=title,
                    description=description,
                    items=[ReactionRoleItem(emoji=emoji, role_id=role.id) for emoji, role in zip(NUMBER_EMOJIS, roles)],
                ))
        except Exception:
            LOGGER.exception("Failed to save reaction role message %s", message.id)
            await interaction.followup.send(
                "The message was created, but its role mappings could not be saved. Please delete the message and try again.",
                ephemeral=True,
            )
            return

        await interaction.followup.send("Auto-role message created.", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if self.bot.user is not None and payload.user_id == self.bot.user.id:
            return
        member = payload.member or await self._get_member(payload.guild_id, payload.user_id)
        if member is None or member.bot:
            return
        role = await self._get_mapped_role(payload)
        if role is None or not self._can_manage_role(role):
            return
        try:
            await member.add_roles(role, reason="Reaction role selected")
        except (discord.Forbidden, discord.HTTPException):
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        if self.bot.user is not None and payload.user_id == self.bot.user.id:
            return
        member = await self._get_member(payload.guild_id, payload.user_id)
        if member is None or member.bot:
            return
        role = await self._get_mapped_role(payload)
        if role is None or not self._can_manage_role(role):
            return
        try:
            await member.remove_roles(role, reason="Reaction role removed")
        except (discord.Forbidden, discord.HTTPException):
            return

    async def _get_mapped_role(self, payload: discord.RawReactionActionEvent) -> discord.Role | None:
        if payload.guild_id is None:
            return None
        async with SessionLocal() as session:
            statement = select(ReactionRoleItem.role_id).join(
                ReactionRole, ReactionRoleItem.reaction_role_id == ReactionRole.id
            ).where(
                ReactionRole.guild_id == payload.guild_id,
                ReactionRole.channel_id == payload.channel_id,
                ReactionRole.message_id == payload.message_id,
                ReactionRoleItem.emoji == str(payload.emoji),
            )
            role_id = (await session.execute(statement)).scalar_one_or_none()
        guild = self.bot.get_guild(payload.guild_id)
        return guild.get_role(role_id) if role_id is not None and guild is not None else None

    async def _get_member(self, guild_id: int | None, user_id: int) -> discord.Member | None:
        if guild_id is None or (guild := self.bot.get_guild(guild_id)) is None:
            return None
        if (member := guild.get_member(user_id)) is not None:
            return member
        try:
            return await guild.fetch_member(user_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None

    @staticmethod
    def _can_manage_role(role: discord.Role) -> bool:
        return (
            role.guild.me is not None
            and not role.is_default()
            and not role.managed
            and role < role.guild.me.top_role
        )

    @auto_role.error
    async def auto_role_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        message = "You need Administrator or Manage Roles permission to use this command." if isinstance(error, app_commands.CheckFailure) else "Unable to create the auto-role message. Please try again."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoRole(bot))
