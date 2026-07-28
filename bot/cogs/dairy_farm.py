import discord
from discord.ext import commands


# GIF DATASET
DAIRY = {
    "milk": {
        "message": "{user} is served **PEAK milk.** 🥛",
        "gif": "https://media.tenor.com/6OmgWJ8946QAAAAM/komaru.gif"
    },
    "cheese": {
        "message": "{user} is served **Premium Cheese.** 🧀",
        "gif": "https://media.tenor.com/hh6zQ8DjSAAAAAAM/cheese.gif"
    },
    "butter": {
        "message": "{user} is served **Fresh Farm Butter.** 🧈",
        "gif": "https://media1.tenor.com/m/aF6yp5swThkAAAAC/butte-r.gif"
    },
    "cream": {
        "message": "{user} is served **Rich Cream.** 🍦",
        "gif": "https://media.tenor.com/socIN9nPWFsAAAAM/shaving-cream-messy.gif"
    },
    "icecream": {
        "message": "{user} is served **ICEEE CREAMMM YAYYYY.** 🍨",
        "gif": "https://media1.tenor.com/m/TkUcZAfuLT0AAAAC/chocolate-ice-cream-cone-vanilla.gif"
    },
    "yogurt": {
        "message": "{user} sorry but nameless eated all yogurt",
        "gif": "https://media1.tenor.com/m/x8v1oNUOmg4AAAAd/rickroll-roll.gif"
    }
}


class DairyFarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Dairy Farm Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.lower().strip()

        if not content.startswith("nom nom "):
            return

        product = content[8:].strip()

        if product not in DAIRY:
            return

        item = DAIRY[product]

        embed = discord.Embed(
            title="🥛 Dairy Farm",
            description=item["message"].format(user=message.author.mention),
            colour=0xf7f7f7
        )

        embed.set_image(url=item["gif"])

        await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DairyFarm(bot))