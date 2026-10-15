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
    BRIDGE_HTTP_PORT: int = int(os.getenv("BRIDGE_HTTP_PORT", "8085"))
    BRIDGE_SECRET_KEY: str = os.getenv("BRIDGE_SECRET_KEY", "ferrox_super_secret_bridge_key_change_me")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Ecosystem Telemetry & Alerts
    DOCS_URL: str = os.getenv("DOCS_URL", "https://ai-autistic-intelligence.github.io/ferrox-docs/")
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "http://localhost:80")
    LARGE_TRADE_THRESHOLD_USD: float = float(os.getenv("LARGE_TRADE_THRESHOLD_USD", "10000.0"))
    SENTINEL_ENTROPY_THRESHOLD: float = float(os.getenv("SENTINEL_ENTROPY_THRESHOLD", "4.8"))
    ALERT_CHANNEL_NAME: str = os.getenv("ALERT_CHANNEL_NAME", "security-alerts")
    TRADES_CHANNEL_NAME: str = os.getenv("TRADES_CHANNEL_NAME", "trading-feed")

    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN or cls.DISCORD_TOKEN == "your_discord_bot_token_here":
            print("[WARNING] DISCORD_TOKEN is missing or set to placeholder in .env file.")
            print("[INFO] Running in headless/webhook telemetry mode. Discord Gateway events will be simulated.")
