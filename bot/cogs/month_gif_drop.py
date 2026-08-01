import re
import time

import discord
from discord.ext import commands


MONTHS = re.compile(
    r"\b("
    r"jan(?:uary)?|"
    r"feb(?:ruary)?|"
    r"mar(?:ch)?|"
    r"apr(?:il)?|"
    r"may|"
    r"jun(?:e)?|"
    r"jul(?:y)?|"
    r"aug(?:ust)?|"
    r"sep(?:tember)?|"
    r"oct(?:ober)?|"
    r"nov(?:ember)?|"
    r"dec(?:ember)?"
    r")\b",
    re.IGNORECASE,
)


DANCING_COW_GIF = "https://i.makeagif.com/media/6-07-2024/kt6bJB.gif"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        print("✅ Fun Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if not MONTHS.search(message.content):
            return

        now = time.time()

        last_used = self.cooldowns.get(message.channel.id, 0)

        if now - last_used < 30:
            return

        self.cooldowns[message.channel.id] = now

        await message.channel.send(DANCING_COW_GIF)


async def setup(bot):
    await bot.add_cog(Fun(bot))