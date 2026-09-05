import sys
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.init_db import init_db

load_dotenv()

TEST_GUILD_ID = 1398024265655128194
BOT_DIRECTORY = Path(__file__).resolve().parent


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class CowBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        print("=" * 50)
        print("[COW] Starting")
        print("=" * 50)

        print("[COW] Initializing PostgreSQL...")
        await init_db()

        print("[COW] Loading cogs...")

        for file in (BOT_DIRECTORY / "cogs").glob("*.py"):
            if file.name.startswith("_"):
                continue

            extension = f"bot.cogs.{file.stem}"

            try:
                await self.load_extension(extension)
                print(f"✅ Loaded {file.stem}")
            except Exception as e:
                print(f"❌ Failed to load {file.stem}")
                raise e

        guild = discord.Object(id=TEST_GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"[COW] Synced {len(synced)} command(s)")
        print("=" * 50)

    async def on_ready(self):
        print("=" * 50)
        print(f"[COW] Logged in as {self.user}")
        print(f"[COW] Guilds : {len(self.guilds)}")
        print("=" * 50)


def main():
    token = os.getenv("TOKEN")

    if not token:
        raise RuntimeError("TOKEN not found in .env")

    bot = CowBot()
    bot.run(token)


if __name__ == "__main__":
    main()
