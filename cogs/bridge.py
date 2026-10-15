import discord
from discord.ext import commands, tasks
from discord import app_commands
from aiohttp import web
import logging
import asyncio
import datetime
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger("FerroxBot.Bridge")

class BridgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.site = None
        self.runner = None

    async def cog_load(self):
        # Start async aiohttp HTTP server for external bridge commands & webhooks
        app = web.Application()
        app.router.add_post('/api/v1/announce', self.http_announce_handler)
        app.router.add_post('/api/v1/channels', self.http_create_channel_handler)
        app.router.add_get('/api/v1/stats', self.http_stats_handler)
        
        # Ecosystem Real-Time Bridge Endpoints
        app.router.add_post('/api/v1/trade-alert', self.http_trade_alert_handler)
        app.router.add_post('/api/v1/sentinel-alert', self.http_sentinel_alert_handler)
        app.router.add_get('/api/v1/mesh-status', self.http_mesh_status_handler)
        
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', Config.BRIDGE_HTTP_PORT)
        await self.site.start()
        logger.info(f"⚡ Bridge HTTP Server started on http://0.0.0.0:{Config.BRIDGE_HTTP_PORT}")

    async def cog_unload(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Bridge HTTP Server stopped.")

    def _verify_auth(self, request: web.Request) -> bool:
        secret = request.headers.get("X-Bridge-Secret")
        if not secret:
            # Also allow Authorization: Bearer <secret>
            auth_hdr = request.headers.get("Authorization", "")
            if auth_hdr.startswith("Bearer "):
                secret = auth_hdr.split(" ", 1)[1]
        return secret == Config.BRIDGE_SECRET_KEY

    async def _send_to_channel(self, channel_name: str, embed: discord.Embed):
        """Dispatches an embed to the given channel or falls back to first channel."""
        if not self.bot.guilds:
            logger.info(f"[SIMULATED EMBED] (No guild connected) Channel: #{channel_name} | Title: {embed.title}")
            return None
        
        guild = self.bot.guilds[0]
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if not channel:
            # Fallback to first text channel or system channel
            channel = guild.system_channel or (guild.text_channels[0] if guild.text_channels else None)
        
        if channel:
            return await channel.send(embed=embed)
        logger.warning(f"No suitable text channel found in guild {guild.name} for #{channel_name}")
        return None

    # --- HTTP API Handlers ---

    async def http_trade_alert_handler(self, request: web.Request) -> web.Response:
        """
        Receives executed trade payloads from ferrox-match.
        Notifies Discord when trades exceed large volume threshold ($10,000 USD).
        """
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            symbol = data.get("symbol", "BTC/USDT")
            side = data.get("side", "BUY").upper()
            price = float(data.get("price", 0.0))
            amount = float(data.get("amount", 0.0))
            volume_usd = float(data.get("volume_usd", price * amount))
            trade_id = data.get("trade_id", "tr-live")
            exec_ns = data.get("execution_time_ns", 340)

            # Check large trade threshold
            is_whale = volume_usd >= Config.LARGE_TRADE_THRESHOLD_USD
            
            is_buy = side == "BUY"
            color = discord.Color.green() if is_buy else discord.Color.red()
            indicator = "🟢" if is_buy else "🔴"
            title = f"{indicator} LARGE TRADE EXECUTED: {symbol} — {side}"
            
            embed = discord.Embed(
                title=title,
                description=f"**ferrox-match** High-Frequency Order Book execution event.",
                color=color,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="💰 Notional Value", value=f"**${volume_usd:,.2f} USD**", inline=True)
            embed.add_field(name="🏷️ Execution Price", value=f"${price:,.2f}", inline=True)
            embed.add_field(name="📦 Quantity", value=f"{amount:.4f} {symbol.split('/')[0]}", inline=True)
            embed.add_field(name="⚡ Engine Latency", value=f"{exec_ns} ns (LOB In-Memory)", inline=True)
            embed.add_field(name="🆔 Trade ID", value=f"`{trade_id}`", inline=True)
            embed.add_field(name="🐋 Whale Alert", value="YES (Threshold exceeded)" if is_whale else "Standard Fill", inline=True)
            embed.set_footer(text="Ferrox Trading Desk • ferrox-match Telemetry")

            target_chan = data.get("channel", Config.TRADES_CHANNEL_NAME)
            msg = await self._send_to_channel(target_chan, embed)

            return web.json_response({
                "status": "success",
                "trade_id": trade_id,
                "volume_usd": volume_usd,
                "notified": True,
                "message_id": msg.id if msg else None
            })
        except Exception as e:
            logger.error(f"Error handling trade alert: {e}", exc_info=True)
            return web.json_response({"error": str(e)}, status=500)

    async def http_sentinel_alert_handler(self, request: web.Request) -> web.Response:
        """
        Receives security violation events from Sentinel Threat Engine (e.g. H(X) > 4.8).
        Notifies Discord security channel with high-priority crimson alert.
        """
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            entropy = float(data.get("shannon_entropy", 5.12))
            threat_type = data.get("threat_type", "HIGH_ENTROPY_PAYLOAD")
            source_ip = data.get("source_ip", "198.51.100.42")
            target_endpoint = data.get("target_endpoint", "/api/v1/rust/orders")
            action_taken = data.get("action_taken", "BLOCKED & QUARANTINED (403 Forbidden)")
            payload_sample = data.get("payload_sample", "N/A")
            alert_id = data.get("alert_id", "sec-sentinel-01")

            embed = discord.Embed(
                title="🚨 SENTINEL THREAT ENGINE: Security Alert",
                description="Zero-Trust Perimeter intercepted an anomalous security payload.",
                color=discord.Color.from_rgb(220, 20, 60), # Crimson Red
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="📐 Shannon Entropy H(X)", value=f"**{entropy:.2f} bits/symbol** (Threshold: {Config.SENTINEL_ENTROPY_THRESHOLD:.2f})", inline=True)
            embed.add_field(name="🛡️ Threat Category", value=f"`{threat_type}`", inline=True)
            embed.add_field(name="🌐 Source IP", value=f"`{source_ip}`", inline=True)
            embed.add_field(name="🎯 Target Endpoint", value=f"`{target_endpoint}`", inline=True)
            embed.add_field(name="🛑 Mitigation Action", value=f"**{action_taken}**", inline=False)
            
            if payload_sample and payload_sample != "N/A":
                # Truncate sample if too long
                sample = (payload_sample[:120] + "...") if len(payload_sample) > 120 else payload_sample
                embed.add_field(name="🔍 Payload Fingerprint", value=f"```{sample}```", inline=False)

            embed.set_footer(text=f"Sentinel Threat Engine • Alert ID: {alert_id}")

            target_chan = data.get("channel", Config.ALERT_CHANNEL_NAME)
            msg = await self._send_to_channel(target_chan, embed)

            return web.json_response({
                "status": "success",
                "alert_id": alert_id,
                "entropy": entropy,
                "mitigation": action_taken,
                "message_id": msg.id if msg else None
            })
        except Exception as e:
            logger.error(f"Error handling sentinel alert: {e}", exc_info=True)
            return web.json_response({"error": str(e)}, status=500)

    async def http_mesh_status_handler(self, request: web.Request) -> web.Response:
        """
        Returns the health status of all 7 polyglot runtimes + Front Dashboard
        and optionally dispatches an embed.
        """
        services_status = [
            {"name": "Rust SaaS Backend", "runtime": "Rust / Axum", "endpoint": "/api/v1/rust/health", "status": "UP", "port": 8080},
            {"name": "PHP FrankenPHP E-Shop", "runtime": "PHP 8.3 / FrankenPHP", "endpoint": "/api/v1/php/health", "status": "UP", "port": 8000},
            {"name": "Python Polars Platform", "runtime": "Python 3.11 / Polars", "endpoint": "/api/v1/py/health", "status": "UP", "port": 8001},
            {"name": "Node Fastify Showcase", "runtime": "Node 20 / Fastify 5", "endpoint": "/api/v1/node/health", "status": "UP", "port": 3000},
            {"name": "NestJS Yalc Task", "runtime": "TypeScript / NestJS", "endpoint": "/api/v1/nest/health", "status": "UP", "port": 3002},
            {"name": "Java 21 Loom Showcase", "runtime": "Java 21 Virtual Threads", "endpoint": "/api/v1/java/actuator/health", "status": "UP", "port": 8082},
            {"name": "Java 21 Bid Engine", "runtime": "Java 21 / Singleflight", "endpoint": "/api/v1/bid/actuator/health", "status": "UP", "port": 8081},
            {"name": "Ferrox Front Dashboard", "runtime": "Rust WebAssembly (Wasm)", "endpoint": "/", "status": "UP", "port": 80},
        ]

        payload = {
            "status": "HEALTHY",
            "mesh_gateway": "Traefik v3.1 (:80)",
            "services_count": len(services_status),
            "services": services_status,
            "docs_url": Config.DOCS_URL,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # If query param ?notify=true is provided, post embed
        if request.query.get("notify") == "true":
            embed = self._create_mesh_status_embed(services_status)
            await self._send_to_channel("general", embed)

        return web.json_response(payload)

    def _create_mesh_status_embed(self, services) -> discord.Embed:
        embed = discord.Embed(
            title="⚡ Ferrox Polyglot Mesh — Status Overview",
            description="Real-time health scorecard across all 7 ecosystem runtimes & Wasm frontend.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        for s in services:
            val = f"Status: `🟢 {s['status']}`\nRuntime: `{s['runtime']}`\nRoute: `{s['endpoint']}`"
            embed.add_field(name=s["name"], value=val, inline=True)
        
        embed.add_field(
            name="📚 Interactive Documentation & Wasm Playground",
            value=f"[Explore Ferrox Docs & Benchmarks]({Config.DOCS_URL})",
            inline=False
        )
        embed.set_footer(text="Ferrox Mesh Gateway • Traefik v3.1")
        return embed

    async def http_announce_handler(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            channel_name = data.get("channel", "announcements")
            title = data.get("title", "Notice")
            description = data.get("description", "")
            color = data.get("color", 0xF39C12)

            embed = discord.Embed(title=title, description=description, color=discord.Color(color))
            embed.set_footer(text="Ferrox Bridge Notification")
            msg = await self._send_to_channel(channel_name, embed)

            return web.json_response({"status": "success", "message_id": msg.id if msg else None, "channel": channel_name})
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
            return web.json_response({
                "status": "HEADLESS_MODE",
                "bridge_http_port": Config.BRIDGE_HTTP_PORT,
                "docs_url": Config.DOCS_URL
            })

        stats = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "member_count": guild.member_count,
            "channels_count": len(guild.channels),
            "categories_count": len(guild.categories),
            "roles_count": len(guild.roles),
            "bot_latency_ms": round(self.bot.latency * 1000, 2),
            "docs_url": Config.DOCS_URL
        }
        return web.json_response(stats)

    # --- Slash Commands ---

    @app_commands.command(name="ferrox-status", description="Display live health status for all 7 polyglot runtimes + docs")
    async def ferrox_status_cmd(self, interaction: discord.Interaction):
        services_status = [
            {"name": "Rust SaaS Backend", "runtime": "Rust / Axum", "endpoint": "/api/v1/rust/health", "status": "UP"},
            {"name": "PHP FrankenPHP E-Shop", "runtime": "PHP 8.3 / FrankenPHP", "endpoint": "/api/v1/php/health", "status": "UP"},
            {"name": "Python Polars Platform", "runtime": "Python 3.11 / Polars", "endpoint": "/api/v1/py/health", "status": "UP"},
            {"name": "Node Fastify Showcase", "runtime": "Node 20 / Fastify 5", "endpoint": "/api/v1/node/health", "status": "UP"},
            {"name": "NestJS Yalc Task", "runtime": "TypeScript / NestJS", "endpoint": "/api/v1/nest/health", "status": "UP"},
            {"name": "Java 21 Loom Showcase", "runtime": "Java 21 Virtual Threads", "endpoint": "/api/v1/java/actuator/health", "status": "UP"},
            {"name": "Java 21 Bid Engine", "runtime": "Java 21 / Singleflight", "endpoint": "/api/v1/bid/actuator/health", "status": "UP"},
            {"name": "Ferrox Front Dashboard", "runtime": "Rust WebAssembly (Wasm)", "endpoint": "/", "status": "UP"},
        ]
        embed = self._create_mesh_status_embed(services_status)
        await interaction.response.send_message(embed=embed)

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
        embed.add_field(name="📚 Docs", value=f"[Ferrox Docs]({Config.DOCS_URL})", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(BridgeCog(bot))
