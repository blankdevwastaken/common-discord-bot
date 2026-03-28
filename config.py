import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Required ──────────────────────────────────────────────────────────────
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")

    # ── Optional / Defaults ───────────────────────────────────────────────────
    PREFIX: str = os.getenv("PREFIX", "!")

    # Set this to your server's ID during development for instant slash-command
    # updates. Remove (set to None) before deploying to production.
    TEST_GUILD_ID: int | None = (
        int(os.getenv("TEST_GUILD_ID")) if os.getenv("TEST_GUILD_ID") else None
    )

    # ID of the role that grants bot-admin privileges (beyond server admin)
    BOT_ADMIN_ROLE_ID: int | None = (
        int(os.getenv("BOT_ADMIN_ROLE_ID")) if os.getenv("BOT_ADMIN_ROLE_ID") else None
    )

    # ── Colours (hex int) ─────────────────────────────────────────────────────
    COLOR_DEFAULT: int = 0x5865F2   # Discord Blurple
    COLOR_SUCCESS: int = 0x57F287   # Green
    COLOR_WARNING: int = 0xFEE75C   # Yellow
    COLOR_ERROR:   int = 0xED4245   # Red
    COLOR_INFO:    int = 0x5865F2   # Blurple

    # ── Validation ────────────────────────────────────────────────────────────
    @classmethod
    def validate(cls) -> None:
        if not cls.TOKEN:
            raise ValueError(
                "DISCORD_TOKEN is not set. "
                "Create a .env file based on .env.example."
            )

Config.validate()
