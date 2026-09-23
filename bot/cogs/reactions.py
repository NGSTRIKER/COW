import discord
from discord.ext import commands

from bot.utils.regex import COW, MILK


class Reactions(commands.Cog):
    """
    Reactions Cog — Listens to chat messages and automatically adds reactions
    when specific keyword patterns (cow, milk) are detected in messages.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[Cog Loaded] Reactions Cog")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event listener checking incoming text messages for regex keyword matches.
        """
        if message.author.bot:
            return

        try:
            # React to messages containing cow-related keywords
            if COW.search(message.content):
                await message.add_reaction("🐮")

            # React to messages containing milk-related keywords
            if MILK.search(message.content):
                await message.add_reaction("🥛")

        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))