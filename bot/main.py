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


class HuImmortalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        print("=" * 50)
        print("🦊 [Little Hu Immortal] Awakening Land Spirit...")
        print("=" * 50)

        print("🌸 [Hu Immortal] Initializing Database...")
        await init_db()

        print("🌸 [Hu Immortal] Loading Cogs & Divine Gu...")

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

        guild_id_str = os.getenv("GUILD_ID") or os.getenv("TEST_GUILD_ID")
        if guild_id_str:
            guild_id = int(guild_id_str)
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"🦊 [Hu Immortal] Synced {len(synced)} command(s) to Blessed Land (Guild ID: {guild_id})")
        else:
            synced = await self.tree.sync()
            print(f"🦊 [Hu Immortal] Synced {len(synced)} command(s) globally")
        print("=" * 50)


    async def on_ready(self):
        print("=" * 50)
        print(f"🦊 [Little Hu Immortal] Logged in as {self.user}")
        print(f"🌸 [Hu Immortal] Guarding {len(self.guilds)} Blessed Land(s)")
        print("=" * 50)


def main():
    token = os.getenv("TOKEN")

    if not token:
        raise RuntimeError("TOKEN not found in .env")

    bot = HuImmortalBot()
    bot.run(token)


if __name__ == "__main__":
    main()
