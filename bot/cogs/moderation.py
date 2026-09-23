import re
from datetime import timedelta

import discord
from discord.ext import commands

from bot.views.confirm import ConfirmView

# Regular expression pattern matching timeout/suppress commands
# Format: "suppress @user for 60 because spamming"
SUPPRESS_RE = re.compile(
    r"^(seal|suppress|milk)\s+<@!?(\d+)>\s+for\s+(\d+)\s+because\s+(.+)$",
    re.IGNORECASE,
)

# Regular expression pattern matching member expulsion/kick commands
# Format: "expel @user" or "banish @user"
KILL_RE = re.compile(
    r"^(kill|execute|begone|banish|farewell\s+friend|expel)\s+<@!?(\d+)>$",
    re.IGNORECASE,
)


class Moderation(commands.Cog):
    """
    Moderation Cog — Text-triggered moderation commands (Timeout & Kick)
    with confirmation prompts and permission verification.
    """
    def __init__(self, bot):
        self.bot = bot
        print("[Cog Loaded] Moderation Cog")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listens to text messages and executes matching moderation triggers
        if the message author possesses the required permissions.
        """
        # Ignore messages sent by bots or outside of server channels
        if message.author.bot or message.guild is None:
            return

        content = message.content.strip()

        # ==================================================
        # TIMEOUT / SUPPRESS COMMAND HANDLER
        # ==================================================
        suppress = SUPPRESS_RE.match(content)

        if suppress:
            member_id = int(suppress.group(2))
            seconds = int(suppress.group(3))
            reason = suppress.group(4)

            # Retrieve member from guild cache or fetch from API if uncached
            member = message.guild.get_member(member_id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(member_id)
                except (discord.NotFound, discord.HTTPException):
                    member = None

            if member is None:
                await message.reply("User not found in this server.")
                return

            if member == message.author:
                await message.reply("You cannot seal or timeout yourself.")
                return

            # Check if moderator possesses Moderate Members permission
            if not message.author.guild_permissions.moderate_members:
                await message.reply("You need the Timeout Members permission to use this command.")
                return

            try:
                # Apply member timeout
                await member.timeout(
                    discord.utils.utcnow() + timedelta(seconds=seconds),
                    reason=f"{reason} | By {message.author}",
                )

                await message.channel.send(
                    f"**{member.mention} has been suppressed for {seconds} seconds.**\n"
                    f"Reason: **{reason}**"
                )

            except discord.Forbidden:
                await message.reply("Lacks permission to timeout that user (role hierarchy conflict).")

            return

        # ==================================================
        # EXPEL / KICK COMMAND HANDLER
        # ==================================================
        kill = KILL_RE.match(content)

        if not kill:
            return

        command = kill.group(1).lower()
        member_id = int(kill.group(2))

        # Retrieve member from guild cache or fetch from API if uncached
        member = message.guild.get_member(member_id)
        if member is None:
            try:
                member = await message.guild.fetch_member(member_id)
            except (discord.NotFound, discord.HTTPException):
                member = None

        if member is None:
            await message.reply("User not found.")
            return

        if member == message.author:
            await message.reply("You cannot expel yourself.")
            return

        # Check if moderator possesses Kick Members permission
        if not message.author.guild_permissions.kick_members:
            await message.reply("You need the Kick Members permission to use this command.")
            return

        # Build confirmation embed prompt
        embed = discord.Embed(
            title=f"Confirm Expulsion ({command.title()})",
            description=f"Are you sure you wish to **{command}** {member.mention} from the server?",
            colour=discord.Colour.orange(),
        )

        embed.add_field(
            name="Moderator",
            value=message.author.mention,
            inline=True,
        )

        embed.add_field(
            name="Target User",
            value=member.mention,
            inline=True,
        )

        # Attach interactive confirmation view buttons
        view = ConfirmView(message.author)

        confirm_message = await message.reply(
            embed=embed,
            view=view,
        )

        view.message = confirm_message

        # Await moderator button interaction
        await view.wait()

        if view.value is None:
            await confirm_message.edit(
                content="Request timed out.",
                embed=None,
                view=None,
            )
            return

        if view.value is False:
            await confirm_message.edit(
                content="Action cancelled by moderator.",
                embed=None,
                view=None,
            )
            return

        try:
            # Execute member kick
            await member.kick(
                reason=f"{command.title()} by {message.author}"
            )

        except discord.Forbidden:
            await confirm_message.edit(
                content="Could not expel that user (role hierarchy conflict).",
                embed=None,
                view=None,
            )
            return

        text = f"**{member} was expelled from the server by {message.author}.**"

        await confirm_message.edit(
            content=text,
            embed=None,
            view=None,
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))