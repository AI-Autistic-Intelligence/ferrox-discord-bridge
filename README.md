# ⚡ Ferrox Discord Community Bridge Bot & Server Provisioner

A production-grade, automated Discord Bot and Control Bridge for establishing and managing the official **Ferrox Framework Community Server** (inspired by NestJS and AzerothCore Discord community structures).

---

## 🎯 Features

- 🏗️ **Automated Server Provisioner (`/setup-server`)**: Programmatically creates all roles, categories, channels, topic descriptions, permission overwrites, and initial rich embed announcements in seconds.
- 💬 **Structured Channel Architecture**: Preconfigured categories for `WELCOME & INFO`, `COMMUNITY`, `FERROX CORE` (Architecture, CQRS/Sagas, Databases, Security, Transports, CLI), `HELP & SUPPORT`, `CONTRIBUTORS`, and `BRIDGE CONTROL`.
- 🏷️ **Interactive Self-Assignable Roles**: Interactive buttons for `#roles-select` to toggle `Ferrox Developer`, `Rustacean`, and `NestJS Enthusiast` badges.
- 🌉 **HTTP REST Control Bridge**: Asynchronous HTTP API running on port `8080` allowing external scripts, automation pipelines, and AI assistants to post announcements, query server metrics, or provision channels dynamically.
- 🛡️ **Role-Based Access Control**: Pre-set permissions enforcing read-only info channels, member-verified chat, and restricted channels for maintainers and contributors.

---

## 🛠️ Quick Setup Guide

### 1. Create your Discord Bot Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**, name it `Ferrox Bridge Bot`, and save.
3. In the left menu, click **Bot**:
   - Click **Reset Token** and copy your bot token.
   - Under **Privileged Gateway Intents**, enable:
     - ✅ **Server Members Intent**
     - ✅ **Message Content Intent**
4. In the left menu, click **OAuth2** -> **URL Generator**:
   - Scopes: Select `bot` and `applications.commands`.
   - Bot Permissions: Select `Administrator` (or *Manage Channels*, *Manage Roles*, *Manage Webhooks*, *Send Messages*, *Embed Links*).
5. Open the generated OAuth2 URL in your browser to invite the bot to your Discord Server.

---

### 2. Installation & Configuration

1. Navigate to the bot directory:
```bash
cd C:\Users\nn\Desktop\code\ferrox-discord-bridge
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Create your `.env` configuration file from the template:
```bash
cp .env.example .env
```

4. Edit `.env` and fill in your token:
```env
DISCORD_TOKEN=your_copied_bot_token_here
GUILD_ID=your_discord_server_id_optional
BOT_PREFIX=!
BRIDGE_HTTP_PORT=8080
BRIDGE_SECRET_KEY=ferrox_super_secret_bridge_key_change_me
LOG_LEVEL=INFO
```

---

### 3. Validate & Start the Bot

1. **Dry-Run Schema Check**:
```bash
python setup_cli.py --validate-schema
```

2. **Start the Bot**:
```bash
python main.py
```

3. **Provision Your Discord Server**:
Once the bot is online in your Discord Server, log into Discord and type the slash command:
```
/setup-server
```
The bot will automatically build all roles, categories, channels, permissions, and post rich embed announcements!

---

## 🤖 HTTP REST Bridge API

When the bot is running, it exposes a lightweight HTTP REST Bridge on port `8080`.

### Endpoints:
- `GET /api/v1/stats`: Returns server members, channel count, and bot latency.
- `POST /api/v1/announce`: Posts an embed announcement to a specified channel.
- `POST /api/v1/channels`: Programmatically creates a new channel.

*All HTTP requests must include the header `X-Bridge-Secret: <YOUR_BRIDGE_SECRET_KEY>`.*

#### Example HTTP Request (Post Announcement):
```bash
curl -X POST http://localhost:8080/api/v1/announce \
  -H "Content-Type: application/json" \
  -H "X-Bridge-Secret: ferrox_super_secret_bridge_key_change_me" \
  -d '{
    "channel": "announcements",
    "title": "⚡ Ferrox v0.2 Release",
    "description": "We are excited to announce new CQRS and PASETO security features!",
    "color": 15965202
  }'
```

---

## 📁 File Structure

```
ferrox-discord-bridge/
├── config.py             # Environment configuration & dotenv loader
├── server_schema.py      # Declarative Ferrox community server blueprint & embeds
├── main.py               # Main bot launcher & intents setup
├── setup_cli.py          # Utility script for dry-run schema checks & bridge tests
├── requirements.txt      # Python dependencies (discord.py, aiohttp, pydantic, etc.)
├── .env.example          # Environment variable template
├── README.md             # Complete documentation and setup guide
└── cogs/
    ├── __init__.py
    ├── roles.py          # Interactive role selector buttons cog
    ├── provisioner.py    # /setup-server and /sync-channels setup engine
    └── bridge.py         # HTTP REST Bridge & administrative slash commands cog
```
