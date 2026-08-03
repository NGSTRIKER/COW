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
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        print("=" * 50)
        print("[COW] Starting")
        print("=" * 50)

        print("[COW] Initializing PostgreSQL...")
        await init_db()

        print("[COW] Loading cogs...")
        for file in BOT_DIRECTORY.joinpath("cogs").glob("*.py"):
            if file.stem.startswith("_"):
                continue
            try:
                await self.load_extension(f"cogs.{file.stem}")
                print(f"[COW] Loaded {file.stem}")
            except Exception:
                print(f"[COW] Failed to load {file.stem}")
                raise

        guild = discord.Object(id=TEST_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        print(f"[COW] Synced {len(synced)} command(s) to guild {TEST_GUILD_ID}")
        print("=" * 50)

    async def on_ready(self) -> None:
        print(f"[COW] Logged in as {self.user} ({self.user.id})")


token = os.getenv("TOKEN")
if token is None:
    raise RuntimeError("TOKEN not found in .env")

bot = CowBot()
bot.run(token)
