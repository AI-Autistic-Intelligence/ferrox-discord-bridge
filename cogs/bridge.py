import discord
from discord.ext import commands
from discord import app_commands
from aiohttp import web
import logging
import asyncio
from typing import Optional
from config import Config

logger = logging.getLogger("FerroxBot.Bridge")

class BridgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.site = None

    async def cog_load(self):
        # Start async aiohttp HTTP server for external bridge commands
        app = web.Application()
        app.router.add_post('/api/v1/announce', self.http_announce_handler)
        app.router.add_post('/api/v1/channels', self.http_create_channel_handler)
        app.router.add_get('/api/v1/stats', self.http_stats_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, '0.0.0.0', Config.BRIDGE_HTTP_PORT)
        await self.site.start()
        logger.info(f"Bridge HTTP Server started on http://0.0.0.0:{Config.BRIDGE_HTTP_PORT}")

    async def cog_unload(self):
        if self.site:
            await self.site.stop()
            logger.info("Bridge HTTP Server stopped.")

    def _verify_auth(self, request: web.Request) -> bool:
        secret = request.headers.get("X-Bridge-Secret")
        return secret == Config.BRIDGE_SECRET_KEY

    # --- HTTP API Handlers ---
    async def http_announce_handler(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            channel_name = data.get("channel")
            title = data.get("title", "Notice")
            description = data.get("description", "")
            color = data.get("color", 0xF39C12)

            guild = self.bot.guilds[0] if self.bot.guilds else None
            if not guild:
                return web.json_response({"error": "Bot is not in any guild"}, status=400)

            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if not channel:
                return web.json_response({"error": f"Channel '{channel_name}' not found"}, status=404)

            embed = discord.Embed(title=title, description=description, color=discord.Color(color))
            embed.set_footer(text="Ferrox Bridge Notification")
            msg = await channel.send(embed=embed)

            return web.json_response({"status": "success", "message_id": msg.id, "channel": channel.name})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def http_create_channel_handler(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            data = await request.json()
            category_name = data.get("category")
            channel_name = data.get("name")
            topic = data.get("topic", "")

            guild = self.bot.guilds[0] if self.bot.guilds else None
            if not guild:
                return web.json_response({"error": "Bot is not in any guild"}, status=400)

            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(name=category_name)

            new_chan = await guild.create_text_channel(name=channel_name, category=category, topic=topic)
            return web.json_response({"status": "success", "channel_id": new_chan.id, "channel_name": new_chan.name})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def http_stats_handler(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)

        guild = self.bot.guilds[0] if self.bot.guilds else None
        if not guild:
            return web.json_response({"error": "Bot is not connected to a guild"}, status=400)

        stats = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "member_count": guild.member_count,
            "channels_count": len(guild.channels),
            "categories_count": len(guild.categories),
            "roles_count": len(guild.roles),
            "bot_latency_ms": round(self.bot.latency * 1000, 2)
        }
        return web.json_response(stats)

    # --- Slash Commands ---
    @app_commands.command(name="announce", description="Post a formatted announcement embed into a specific channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color(0xF39C12)
        )
        embed.set_footer(text="Official Announcement • Ferrox Community")
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Announcement sent to {channel.mention}!", ephemeral=True)

    @app_commands.command(name="server-stats", description="Display server statistics and bridge status")
    async def server_stats(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Command must be used in a guild.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📊 Ferrox Server Statistics — {guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 Total Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="📁 Categories", value=str(len(guild.categories)), inline=True)
        embed.add_field(name="💬 Text Channels", value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name="🏷️ Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="⚡ Bot Latency", value=f"{round(self.bot.latency * 1000, 2)} ms", inline=True)
        embed.add_field(name="🤖 Bridge Port", value=str(Config.BRIDGE_HTTP_PORT), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(BridgeCog(bot))
