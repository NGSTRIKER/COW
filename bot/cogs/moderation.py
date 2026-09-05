import re
from datetime import timedelta

import discord
from discord.ext import commands

from bot.views.confirm import ConfirmView


MILK_RE = re.compile(
    r"^milk\s+<@!?(\d+)>\s+for\s+(\d+)\s+because\s+(.+)$",
    re.IGNORECASE,
)

KILL_RE = re.compile(
    r"^(kill|execute|begone|banish|farewell\s+friend)\s+<@!?(\d+)>$",
    re.IGNORECASE,
)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Moderation Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        # ==================================================
        # MILK
        # ==================================================

        milk = MILK_RE.match(message.content)

        if milk:
            member_id = int(milk.group(1))
            seconds = int(milk.group(2))
            reason = milk.group(3)

            member = message.guild.get_member(member_id)

            if member is None:
                await message.reply("❌ User not found.")
                return

            if member == message.author:
                await message.reply("🐄 You can't milk yourself.")
                return

            if not message.author.guild_permissions.moderate_members:
                await message.reply(
                    "❌ You need the **Timeout Members** permission."
                )
                return

            try:
                await member.timeout(
                    discord.utils.utcnow() + timedelta(seconds=seconds),
                    reason=f"{reason} | By {message.author}",
                )

                await message.channel.send(
                    f"🥛 **{member.mention} has been milked for {seconds} seconds.**\n"
                    f"🥀 Reason: **{reason}**"
                )

            except discord.Forbidden:
                await message.reply(
                    "❌ I can't milk that user. They may have a higher role than me."
                )

            return

        # ==================================================
        # KILL / EXECUTE / BEGONE / BANISH / FAREWELL FRIEND
        # ==================================================

        kill = KILL_RE.match(message.content)

        if not kill:
            return

        command = kill.group(1).lower()
        member_id = int(kill.group(2))

        member = message.guild.get_member(member_id)

        if member is None:
            await message.reply("❌ User not found.")
            return

        if member == message.author:
            await message.reply("🐄 The cows refuse to let you kick yourself.")
            return

        if not message.author.guild_permissions.kick_members:
            await message.reply(
                "❌ You need the **Kick Members** permission."
            )
            return

        embed = discord.Embed(
            title=f"⚠️ Confirm {command.title()}",
            description=f"Are you sure you want to **{command}** {member.mention}?",
            colour=discord.Colour.orange(),
        )

        embed.add_field(
            name="Moderator",
            value=message.author.mention,
            inline=True,
        )

        embed.add_field(
            name="Target",
            value=member.mention,
            inline=True,
        )

        view = ConfirmView(message.author)

        confirm_message = await message.reply(
            embed=embed,
            view=view,
        )

        view.message = confirm_message

        await view.wait()

        if view.value is None:
            await confirm_message.edit(
                content="⌛ Request timed out.",
                embed=None,
                view=None,
            )
            return

        if view.value is False:
            await confirm_message.edit(
                content="❌ Action cancelled.",
                embed=None,
                view=None,
            )
            return

        try:
            await member.kick(
                reason=f"{command.title()} by {message.author}"
            )

        except discord.Forbidden:
            await confirm_message.edit(
                content="❌ I can't kick that user. They probably have a higher role than me.",
                embed=None,
                view=None,
            )
            return

        if command == "execute":
            text = (
                f"⚔️ **{member} has been publicly executed.**\n"
                "The cows watched in silence. 🐄"
            )

        elif command == "farewell friend":
            text = (
                f"👋 **Farewell, {member}.**\n"
                "The cows shall remember your sacrifice. 🐄"
            )

        elif command == "begone":
            text = (
                f"🚪 **{member} has been banished from the pasture.**"
            )

        elif command == "banish":
            text = (
                f"🌌 **{member} has been exiled to the forbidden fields.**"
            )

        else:
            text = (
                f"💀 **{member} was trampled beneath a horde of cows.** 🐄🐄🐄"
            )

        await confirm_message.edit(
            content=text,
            embed=None,
            view=None,
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))