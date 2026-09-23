import sys
import os
from pathlib import Path

# Add project root directory to Python's module search path (sys.path)
# This allows imports like 'database.init_db' to work regardless of execution location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.init_db import init_db

# Load environment variables from .env file
load_dotenv()

# Fallback test guild ID used when GUILD_ID is not specified in environment
TEST_GUILD_ID = 1398024265655128194
BOT_DIRECTORY = Path(__file__).resolve().parent

# Configure Discord bot gateway intents
# Enabled Message Content intent for text-based commands & reactions
# Enabled Guild Members intent for join tracking & role management
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class HuImmortalBot(commands.Bot):
    """
    Main Discord Bot class handling initialization, cog loading, database setup,
    and slash command synchronization across Discord servers.
    """

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        """
        Asynchronous initialization hook called before the bot connects to Discord.
        Initializes the database schema, dynamically loads all cogs in bot/cogs/,
        and syncs application slash commands to Discord.
        """
        print("=" * 50)
        print("[Hu Immortal Bot] Starting initialization sequence...")
        print("=" * 50)

        # Initialize database tables
        print("[Hu Immortal Bot] Initializing database models...")
        await init_db()

        # Dynamically load all extension cogs inside the bot/cogs directory
        print("[Hu Immortal Bot] Loading extensions and cogs...")
        for file in (BOT_DIRECTORY / "cogs").glob("*.py"):
            # Ignore internal files starting with underscore
            if file.name.startswith("_"):
                continue

            extension = f"bot.cogs.{file.stem}"
            try:
                await self.load_extension(extension)
                print(f"[Loaded Extension] {file.stem}")
            except Exception as e:
                print(f"[Failed Extension] Could not load {file.stem}")
                raise e

        # Synchronize slash application commands
        # If GUILD_ID or TEST_GUILD_ID is provided, sync instantly to that specific server
        # Otherwise, sync commands globally across all Discord servers
        guild_id_str = os.getenv("GUILD_ID") or os.getenv("TEST_GUILD_ID")
        if guild_id_str:
            guild_id = int(guild_id_str)
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"[Command Sync] Synced {len(synced)} command(s) to Guild ID: {guild_id}")
        else:
            synced = await self.tree.sync()
            print(f"[Command Sync] Synced {len(synced)} command(s) globally")
        print("=" * 50)

    async def on_ready(self):
        """
        Event listener triggered when the bot successfully connects to Gateway.
        """
        print("=" * 50)
        print(f"[Hu Immortal Bot] Logged in successfully as {self.user}")
        print(f"[Hu Immortal Bot] Connected to {len(self.guilds)} server(s)")
        print("=" * 50)


def main():
    """
    Application entry point. Reads bot token from environment and starts bot event loop.
    """
    token = os.getenv("TOKEN")

    if not token:
        raise RuntimeError("TOKEN not found in .env file. Please check your .env setup.")

    bot = HuImmortalBot()
    bot.run(token)


if __name__ == "__main__":
    main()
