import re
from datetime import timedelta

import discord
from discord.ext import commands

from bot.views.confirm import ConfirmView


SUPPRESS_RE = re.compile(
    r"^(seal|suppress|milk)\s+<@!?(\d+)>\s+for\s+(\d+)\s+because\s+(.+)$",
    re.IGNORECASE,
)

KILL_RE = re.compile(
    r"^(kill|execute|begone|banish|farewell\s+friend|expel)\s+<@!?(\d+)>$",
    re.IGNORECASE,
)


class Moderation(commands.Cog):
    """
    🌸 Hu Immortal Blessed Land Moderation & Discipline
    """
    def __init__(self, bot):
        self.bot = bot
        print("✅ Hu Immortal Moderation Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        content = message.content.strip()

        # ==================================================
        # SEAL / SUPPRESS (TIMEOUT)
        # ==================================================

        suppress = SUPPRESS_RE.match(content)

        if suppress:
            member_id = int(suppress.group(2))
            seconds = int(suppress.group(3))
            reason = suppress.group(4)

            member = message.guild.get_member(member_id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(member_id)
                except (discord.NotFound, discord.HTTPException):
                    member = None

            if member is None:
                await message.reply("❌ User not found in Hu Immortal Blessed Land.")
                return

            if member == message.author:
                await message.reply("🦊 Little Hu Immortal stops you: 'Master, you cannot seal yourself!'")
                return

            if not message.author.guild_permissions.moderate_members:
                await message.reply(
                    "❌ You need the **Timeout Members** permission to command Dang Hun Mountain."
                )
                return

            try:
                await member.timeout(
                    discord.utils.utcnow() + timedelta(seconds=seconds),
                    reason=f"{reason} | By {message.author}",
                )

                await message.channel.send(
                    f"🏔️ **{member.mention} has been suppressed beneath Dang Hun Mountain for {seconds} seconds.**\n"
                    f"🥀 Reason: **{reason}**"
                )

            except discord.Forbidden:
                await message.reply(
                    "❌ Little Hu Immortal lacks the power to suppress that user (higher role)."
                )

            return

        # ==================================================
        # EXPEL / BANISH / EXECUTE (KICK)
        # ==================================================

        kill = KILL_RE.match(content)

        if not kill:
            return

        command = kill.group(1).lower()
        member_id = int(kill.group(2))

        member = message.guild.get_member(member_id)
        if member is None:
            try:
                member = await message.guild.fetch_member(member_id)
            except (discord.NotFound, discord.HTTPException):
                member = None

        if member is None:
            await message.reply("❌ User not found.")
            return


        if member == message.author:
            await message.reply("🦊 Little Hu Immortal refuses to expel Master!")
            return

        if not message.author.guild_permissions.kick_members:
            await message.reply(
                "❌ You need the **Kick Members** permission."
            )
            return

        embed = discord.Embed(
            title=f"⚠️ Confirm Expulsion ({command.title()})",
            description=f"Master, are you sure you wish to **{command}** {member.mention} from Hu Immortal Blessed Land?",
            colour=discord.Colour.orange(),
        )

        embed.add_field(
            name="Moderator",
            value=message.author.mention,
            inline=True,
        )

        embed.add_field(
            name="Target Intruders",
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
                content="❌ Action cancelled by Master.",
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
                content="❌ Little Hu Immortal could not expel that user (higher role than bot).",
                embed=None,
                view=None,
            )
            return

        if command in ("execute", "kill"):
            text = (
                f"⚔️ **{member} was struck down by Dang Hun Mountain's divine vibration.**\n"
                "Little Hu Immortal cleanses the battlefield. 🦊🌸"
            )

        elif command == "farewell friend":
            text = (
                f"👋 **Farewell, {member}.**\n"
                "May your soul find peace outside Hu Immortal Blessed Land. 🌸"
            )

        elif command in ("begone", "banish", "expel"):
            text = (
                f"🌌 **{member} has been banished beyond the boundaries of Hu Immortal Blessed Land!** 🦊"
            )

        else:
            text = (
                f"💀 **{member} was expelled from the Blessed Land.** 🌸"
            )

        await confirm_message.edit(
            content=text,
            embed=None,
            view=None,
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))