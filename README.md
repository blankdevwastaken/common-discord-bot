# common-discord-bot
---

## Project Structure

```
discord-bot/
├── bot.py                  # Entry point — creates and runs the Bot
├── config.py               # Centralised config, reads from .env
├── requirements.txt
├── .env.example            # Copy to .env and fill in your values
│
├── cogs/                   # Feature modules (auto-loaded on startup)
│   ├── general.py          # /ping /help /info /uptime /avatar /serverinfo
│   ├── moderation.py       # /kick /ban /unban /timeout /purge /warn /warnings
│   ├── admin.py            # /reload /sync /status /listcogs
│   └── error_handler.py    # Global slash-command error handling
│
├── utils/
│   ├── embeds.py           # Embed factory helpers (success / error / warning …)
│   ├── checks.py           # Permission predicates + decorators
│   └── logger.py           # Rotating-file + stdout logger
│
├── data/                   # Persistent data goes here (JSON, SQLite, etc.)
└── logs/                   # Auto-created; rotating .log files per module
```

## Quick Start

### 1. Clone & install dependencies

```bash
git clone <your-repo>
cd discord-bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN (and optionally TEST_GUILD_ID)
```

### 3. Enable Privileged Intents

Go to [Discord Developer Portal](https://discord.com/developers/applications) → your app → **Bot** tab:

- ✅ Server Members Intent
- ✅ Message Content Intent

### 4. Run the bot

```bash
python bot.py
```

---

## Slash Command Sync

| Mode | How |
|------|-----|
| **Development** (instant) | Set `TEST_GUILD_ID` in `.env` |
| **Production** (global, ~1 h) | Leave `TEST_GUILD_ID` empty |
| **Manual re-sync** | Use `/sync` in Discord (bot-admin only) |

---

## Adding a New Cog

1. Create `cogs/my_feature.py`:

```python
from discord import app_commands, Interaction
from discord.ext import commands
import utils.embeds as em

class MyFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello.")
    async def hello(self, interaction: Interaction):
        await interaction.response.send_message(
            embed=em.success("Hello!", f"Hey {interaction.user.mention}!")
        )

async def setup(bot):
    await bot.add_cog(MyFeature(bot))
```

2. Register it in `bot.py`:

```python
self.initial_extensions = [
    ...
    "cogs.my_feature",   # ← add this line
]
```

That's it. The bot loads it automatically on the next start (or use `/reload cogs.my_feature`).

---

## 🔒 Permissions

| Decorator | Who can use it |
|-----------|---------------|
| `@bot_admin_only()` | Server admins + `BOT_ADMIN_ROLE_ID` holders |
| `@moderator_only()` | Members with kick/ban/manage_messages etc. |
| `@app_commands.default_permissions(...)` | Enforced by Discord natively |
| `@app_commands.guild_only()` | Blocks DM usage |

---
