import re
import discord
from discord.ext import commands


LARPS = re.compile(r"\blarp\b", re.IGNORECASE)


Larp_COW_GIF = "https://media1.tenor.com/m/4IlahlpKSZMAAAAC/aura-aura-monster.gif"


class LarpGifDrop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Larp GIF Drop Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if not message.guild:
            return

        if not LARPS.search(message.content):
            return

        await message.channel.send(Larp_COW_GIF)


async def setup(bot):
    await bot.add_cog(LarpGifDrop(bot))
