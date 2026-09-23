import discord
from discord.ext import commands

# Dataset of server items and offerings
BLESSED_LAND_ITEMS = {
    "guts gu": {
        "message": "Presents Rank 5 Guts Gu from Dang Hun Mountain for {user}!",
        "gif": "https://media.tenor.com/6OmgWJ8946QAAAAM/komaru.gif"
    },
    "fox tea": {
        "message": "Serves freshly brewed Fox Tea to {user}!",
        "gif": "https://media.tenor.com/hh6zQ8DjSAAAAAAM/cheese.gif"
    },
    "primeval stone": {
        "message": "Grants 100 Primeval Stones to {user}!",
        "gif": "https://media1.tenor.com/m/aF6yp5swThkAAAAC/butte-r.gif"
    },
    "pink crane": {
        "message": "A Pink Cloud Crane carries {user} across the land!",
        "gif": "https://media.tenor.com/socIN9nPWFsAAAAM/shaving-cream-messy.gif"
    },
    "starlight firefly": {
        "message": "Releases Starlight Firefly Gu to illuminate the night for {user}!",
        "gif": "https://media1.tenor.com/m/TkUcZAfuLT0AAAAC/chocolate-ice-cream-cone-vanilla.gif"
    },
}


class DairyFarm(commands.Cog):
    """
    DairyFarm Cog — Responds to chat offering triggers ('offer <item>', 'serve <item>', 'nom nom <item>')
    and posts formatted item embeds with GIF attachments.
    """
    def __init__(self, bot):
        self.bot = bot
        print("[Cog Loaded] Dairy Farm Offerings Cog")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event listener checking text messages for item offering prefixes.
        """
        if message.author.bot:
            return

        content = message.content.lower().strip()

        # Match offering command prefixes
        prefix = None
        if content.startswith("offer "):
            prefix = "offer "
        elif content.startswith("serve "):
            prefix = "serve "
        elif content.startswith("nom nom "):
            prefix = "nom nom "

        if not prefix:
            return

        # Extract product name
        product = content[len(prefix):].strip()

        if product not in BLESSED_LAND_ITEMS:
            return

        item = BLESSED_LAND_ITEMS[product]

        # Build and send item embed
        embed = discord.Embed(
            title="Blessed Land Offerings",
            description=item["message"].format(user=message.author.mention),
            colour=0xffb6c1,
        )

        embed.set_image(url=item["gif"])

        await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DairyFarm(bot))