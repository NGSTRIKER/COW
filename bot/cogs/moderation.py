import re
from datetime import timedelta

import discord
from discord.ext import commands


MILK_RE = re.compile(
    r"^milk\s+<@!?(\d+)>\s+for\s+(\d+)\s+because\s+(.+)$",
    re.IGNORECASE,
)

KILL_RE = re.compile(
    r"^kill\s+<@!?(\d+)>$",
    re.IGNORECASE,
)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Moderation Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        # ==========================
        # MILK
        # ==========================
        milk = MILK_RE.match(message.content)

        if milk:
            member_id = int(milk.group(1))
            seconds = int(milk.group(2))
            reason = milk.group(3)

            member = message.guild.get_member(member_id)

            if member is None:
                return await message.reply("❌ User not found.")

            if member == message.author:
                return await message.reply("🐄 You can't milk yourself.")

            if not message.author.guild_permissions.moderate_members:
                return await message.reply(
                    "❌ You need the **Timeout Members** permission."
                )

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
                    "❌ I can't milk that user. They might have a higher role than me."
                )

            return

        # ==========================
        # KILL
        # ==========================
        kill = KILL_RE.match(message.content)

        if kill:
            member_id = int(kill.group(1))

            member = message.guild.get_member(member_id)

            if member is None:
                return await message.reply("❌ User not found.")

            if member == message.author:
                return await message.reply("🐄 You can't kill yourself. I will not allow you to DIE")

            if not message.author.guild_permissions.kick_members:
                return await message.reply(
                    "❌ You need the **Kick Members** permission buddy. ur just a insignificant person"
                )

            try:
                await member.kick(
                    reason=f"Killed by {message.author}"
                )

                await message.channel.send(
                    f"💀 **{member} was smashed under a horde of cows.** 🐄🐄🐄"
                )

            except discord.Forbidden:
                await message.reply(
                    " I can't kick that user lil vro. They may have a higher role than me. just kys"
                )

            return


async def setup(bot):
    await bot.add_cog(Moderation(bot))