import discord
from discord.ext import commands

# HU IMMORTAL BLESSED LAND ITEMS DATASET
BLESSED_LAND_ITEMS = {
    "guts gu": {
        "message": "Little Hu Immortal presents **Rank 5 Guts Gu** from Dang Hun Mountain for {user}! 🏔️✨",
        "gif": "https://media.tenor.com/6OmgWJ8946QAAAAM/komaru.gif"
    },
    "fox tea": {
        "message": "Little Hu Immortal serves freshly brewed **Hu Immortal Fox Tea** to {user}! 🍵🦊",
        "gif": "https://media.tenor.com/hh6zQ8DjSAAAAAAM/cheese.gif"
    },
    "primeval stone": {
        "message": "Little Hu Immortal grants **100 Primeval Stones** to {user}! 💎✨",
        "gif": "https://media1.tenor.com/m/aF6yp5swThkAAAAC/butte-r.gif"
    },
    "pink crane": {
        "message": "A **Pink Cloud Crane** carries {user} across Hu Immortal Blessed Land! 🦩🌸",
        "gif": "https://media.tenor.com/socIN9nPWFsAAAAM/shaving-cream-messy.gif"
    },
    "starlight firefly": {
        "message": "Little Hu Immortal releases **Starlight Firefly Gu** to illuminate the night for {user}! 🌟🌌",
        "gif": "https://media1.tenor.com/m/TkUcZAfuLT0AAAAC/chocolate-ice-cream-cone-vanilla.gif"
    },
}


class DairyFarm(commands.Cog):
    """
    🌸 Hu Immortal Blessed Land Offerings
    Triggers on 'offer <item>' or 'serve <item>'
    """
    def __init__(self, bot):
        self.bot = bot
        print("✅ Hu Immortal Blessed Land Offerings Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.lower().strip()

        prefix = None
        if content.startswith("offer "):
            prefix = "offer "
        elif content.startswith("serve "):
            prefix = "serve "
        elif content.startswith("nom nom "):
            prefix = "nom nom "

        if not prefix:
            return

        product = content[len(prefix):].strip()

        if product not in BLESSED_LAND_ITEMS:
            return

        item = BLESSED_LAND_ITEMS[product]

        embed = discord.Embed(
            title="🌸 Hu Immortal Blessed Land Offerings",
            description=item["message"].format(user=message.author.mention),
            colour=0xffb6c1  # Soft Pink theme for Little Hu Immortal
        )

        embed.set_image(url=item["gif"])

        await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DairyFarm(bot))