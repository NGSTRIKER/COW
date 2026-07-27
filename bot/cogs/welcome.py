import discord
from discord.ext import commands

WELCOME_PHRASE = "mooo mooooo mooo {user} moooo mooo moooo"


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("✅ Welcome cog loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Replace with your selected channel ID later
        channel = discord.utils.get(guild.text_channels, name="general")
        if channel is None:
            return

        try:
            await channel.send(WELCOME_PHRASE.format(user=member.mention))
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))