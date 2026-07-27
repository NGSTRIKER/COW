import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class CowBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        print("Loading cogs...")

        for file in Path(__file__).parent.joinpath("cogs").glob("*.py"):
            await self.load_extension(f"cogs.{file.stem}")
            print(f"Loaded {file.stem}")


bot = CowBot()


@bot.event
async def on_ready():
    print(f"🐄 Logged in as {bot.user}")


bot.run(os.getenv("TOKEN"))