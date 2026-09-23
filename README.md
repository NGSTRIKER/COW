# Hu Immortal Discord Bot

A Discord management and security bot designed for community administration, automated raid monitoring, self-assignable reaction roles, and customizable server settings with persistent database storage.

![Hu Immortal Bot Overview](assets/12d38d67-2308-483f-9175-3c9dec3b1a93.png)

---

## Overview

The Hu Immortal Discord Bot provides an integrated suite of server management tools built on top of Discord.py 2.0 and SQLAlchemy 2.0 Async. It features an interactive in-Discord administration control panel, continuous join monitoring for raid detection, custom reaction role distribution, and flexible text and slash command interfaces. All server configurations are persisted directly to PostgreSQL or local SQLite databases.

---

## Key Features

### 1. Interactive Administration Dashboard (`/dashboard`)
The bot includes a centralized control panel accessible exclusively to server administrators.

- **Persistent Configuration:** All setting changes are written directly to the database and preserved across bot restarts.
- **Welcome Channel Selector:** Live dropdown menu to designate or clear the server's welcome channel.
- **Fox Nose Log Channel Selector:** Live dropdown menu to select the channel for security and raid alert notifications.
- **One-Click Toggles:** Instantly enable or disable security monitoring and XP systems using interactive UI buttons.

![Dashboard Interface Screenshot](assets/2026_09_05_08_50_43_screenshot.png)

---

### 2. Fox Nose Security and Anti-Raid System (`/fox_nose`)
Fox Nose is an automated join monitoring engine that calculates account risk scores without taking unauthorized destructive actions.

- **Heuristic Risk Scoring:** Evaluates joining accounts on a 0 to 100 suspicion scale based on account age (created under 24h, 7d, or 30d), default avatar usage, bot-like username patterns, and active join surges.
- **Raid Surge Detection:** Automatically detects join velocity spikes (e.g., 5 joins within 10 seconds) and triggers a 10-minute Raid Alert Mode.
- **Moderation Alerts:** Sends detailed risk reports to designated log channels for human moderator review.
- **Commands:**
  - `/fox_nose status` - View current security monitoring status and active log channel.
  - `/fox_nose audit member:@User` - Manually run risk analysis on any server member.
  - `/fox_nose config` - Update security parameters and log channel settings.
  - `/fox_nose clear_lockdown` - Deactivate active raid alert state.

![Security Alert Interface Screenshot](assets/2026_09_05_08_55_24_screenshot.png)

---

### 3. Reaction Role System (`/auto_role`)
Allows administrators to create interactive reaction role embeds for member self-assignment.

- Supports up to 10 customizable role mappings per message.
- Uses Discord raw reaction event listeners to grant or remove roles instantly upon user reaction.
- Validates bot role hierarchy permissions before assigning roles.

---

### 4. Welcome System (`/set_welcome_channel`)
Sends customizable member join greetings to configured server channels.

- Queries persistent database records to determine destination channels.
- Automatically falls back to system channels or default text channels if no specific channel is set.

---

### 5. Moderation and Discipline Commands
Text and slash moderation utilities for server staff with permission validation and confirmation steps.

- **Timeout Command:** `suppress @user for <seconds> because <reason>` - Applies member timeout.
- **Kick Command:** `expel @user` or `banish @user` - Opens an interactive confirmation prompt before executing a member kick.

---

## Technical Architecture

- **Language & Runtime:** Python 3.10+
- **Framework:** Discord.py 2.7+ (Async Gateway & Application Commands)
- **Database ORM:** SQLAlchemy 2.0 (Async Engine)
- **Database Support:** PostgreSQL (`asyncpg`) or SQLite (`aiosqlite`)
- **Environment Management:** `python-dotenv`

---

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone Repository
```bash
git clone https://github.com/NGSTRIKER/COW.git
cd COW
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# Required: Discord Bot Token
TOKEN=your_discord_bot_token_here

# Optional: Guild ID for instant slash command synchronization during testing
GUILD_ID=1398024265655128194

# Database URL (Defaults to local SQLite if omitted)
# For PostgreSQL: postgresql+asyncpg://user:password@localhost/dbname
DATABASE_URL=sqlite+aiosqlite:///cow.db
```

### 4. Run the Bot
```bash
python bot/main.py
```

Upon startup, the bot automatically initializes database tables, loads all extension cogs, synchronizes slash commands with Discord, and begins serving connected servers.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
