import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: int = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None
    BOT_PREFIX: str = os.getenv("BOT_PREFIX", "!")
    BRIDGE_HTTP_PORT: int = int(os.getenv("BRIDGE_HTTP_PORT", "8080"))
    BRIDGE_SECRET_KEY: str = os.getenv("BRIDGE_SECRET_KEY", "ferrox_super_secret_bridge_key_change_me")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN or cls.DISCORD_TOKEN == "your_discord_bot_token_here":
            print("[WARNING] DISCORD_TOKEN is missing or set to placeholder in .env file.")
            print("[INFO] Please edit .env file and set a valid DISCORD_TOKEN.")
