import discord
from discord.ext import commands

from utils.regex import COW, MILK


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("✅ Reactions Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        try:
            if COW.search(message.content):
                await message.add_reaction("🐮")

            if MILK.search(message.content):
                await message.add_reaction("🥛")

        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))