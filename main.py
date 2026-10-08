import discord
from discord.ext import commands
import asyncio
import logging
import sys
from config import Config

# Configure Logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("FerroxBot.Main")

# Define Default Intents (Works out of the box without requiring Privileged Gateway Intents)
intents = discord.Intents.default()
intents.guilds = True

class FerroxBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        logger.info("Loading Cogs...")
        await self.load_extension("cogs.roles")
        await self.load_extension("cogs.provisioner")
        await self.load_extension("cogs.bridge")
        logger.info("All Cogs loaded successfully.")

        # Sync Slash Commands to Target Guild if GUILD_ID is specified, otherwise global sync
        if Config.GUILD_ID:
            guild = discord.Object(id=Config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} slash command(s) to target Guild ID {Config.GUILD_ID}.")
        else:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s) globally.")

    async def on_ready(self):
        logger.info("=" * 60)
        logger.info(f"⚡ Ferrox Bridge Bot is ONLINE!")
        logger.info(f"Bot Username : {self.user.name} (ID: {self.user.id})")
        logger.info(f"Guild Count  : {len(self.guilds)}")
        for g in self.guilds:
            logger.info(f"  - {g.name} (ID: {g.id}, Members: {g.member_count})")
        logger.info(f"HTTP Bridge  : http://localhost:{Config.BRIDGE_HTTP_PORT}")
        logger.info("=" * 60)

async def main():
    Config.validate()

    if not Config.DISCORD_TOKEN or Config.DISCORD_TOKEN == "your_discord_bot_token_here":
        logger.error("Cannot start bot without a valid DISCORD_TOKEN. Please set it in .env file.")
        sys.exit(1)

    bot = FerroxBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot execution terminated by user (KeyboardInterrupt).")
