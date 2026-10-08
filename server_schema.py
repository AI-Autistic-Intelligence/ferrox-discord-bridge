"""
Ferrox Community Server Blueprint & Schema Specification
Defines roles, categories, channels, permissions, tags, and rich initial embeds.
Primary Language: English (Global)
"""

from typing import List, Dict, Any, Optional

# Color definitions (Hex values)
COLOR_RED = 0xE74C3C
COLOR_ORANGE = 0xE67E22
COLOR_YELLOW = 0xF1C40F
COLOR_GREEN = 0x2ECC71
COLOR_CYAN = 0x1ABC9C
COLOR_PURPLE = 0x9B59B6
COLOR_DARK_BLUE = 0x34495E
COLOR_GREY = 0x95A5A6
COLOR_FERROX = 0xF39C12  # Signature Gold/Orange for Ferrox

# Discord Server Discovery & Community Tags
SERVER_DISCOVERY_TAGS: List[str] = [
    "rust",
    "framework",
    "tokio",
    "axum",
    "nestjs",
    "backend",
    "microservices",
    "cqrs",
    "security"
]

ROLES_SPEC: List[Dict[str, Any]] = [
    {
        "name": "Core Maintainer",
        "color": COLOR_RED,
        "hoist": True,
        "mentionable": True,
        "permissions": {
            "administrator": True
        }
    },
    {
        "name": "Contributor",
        "color": COLOR_ORANGE,
        "hoist": True,
        "mentionable": True,
        "permissions": {
            "manage_messages": True,
            "embed_links": True,
            "attach_files": True,
            "add_reactions": True
        }
    },
    {
        "name": "Community Ambassador",
        "color": COLOR_YELLOW,
        "hoist": True,
        "mentionable": True,
        "permissions": {
            "kick_members": True,
            "manage_messages": True,
            "mute_members": True
        }
    },
    {
        "name": "Ferrox Developer",
        "color": COLOR_GREEN,
        "hoist": True,
        "mentionable": True,
        "permissions": {
            "send_messages": True,
            "read_messages": True,
            "add_reactions": True,
            "connect": True,
            "speak": True
        }
    },
    {
        "name": "Rustacean",
        "color": COLOR_CYAN,
        "hoist": False,
        "mentionable": True,
        "permissions": {}
    },
    {
        "name": "NestJS Enthusiast",
        "color": COLOR_PURPLE,
        "hoist": False,
        "mentionable": True,
        "permissions": {}
    },
    {
        "name": "Bot Bridge",
        "color": COLOR_GREY,
        "hoist": True,
        "mentionable": False,
        "permissions": {
            "administrator": True
        }
    }
]

CATEGORIES_SPEC: List[Dict[str, Any]] = [
    {
        "name": "📜｜WELCOME & INFO",
        "channels": [
            {
                "name": "rules-and-guidelines",
                "topic": "Community Code of Conduct and Server Rules (English).",
                "read_only": True,
                "type": "text"
            },
            {
                "name": "announcements",
                "topic": "Official announcements, releases, and framework updates for Ferrox.",
                "read_only": True,
                "type": "text"
            },
            {
                "name": "faq-and-resources",
                "topic": "Useful links, framework documentation, crates inventory, and server tags.",
                "read_only": True,
                "type": "text"
            },
            {
                "name": "roles-select",
                "topic": "Select your self-assignable developer roles using the buttons below.",
                "read_only": True,
                "type": "text"
            }
        ]
    },
    {
        "name": "💬｜COMMUNITY",
        "channels": [
            {
                "name": "general",
                "topic": "Main global lounge for general discussions regarding the Ferrox ecosystem.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "showcase",
                "topic": "Show off projects, microservices, and apps built using Ferrox framework!",
                "read_only": False,
                "type": "forum",
                "tags": [
                    {"name": "App", "emoji": "🚀"},
                    {"name": "Microservice", "emoji": "⚙️"},
                    {"name": "Library", "emoji": "📦"},
                    {"name": "Demo", "emoji": "🎨"}
                ]
            },
            {
                "name": "events-and-meetups",
                "topic": "Community streams, RFC discussion meetups, and developer office hours.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "lounge-random",
                "topic": "Off-topic discussions, tech news, and casual banter.",
                "read_only": False,
                "type": "text"
            }
        ]
    },
    {
        "name": "🌐｜INTERNATIONAL CHATS",
        "channels": [
            {
                "name": "chat-english",
                "topic": "Primary English discussion channel for international community members.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-spanish",
                "topic": "Canal de conversación en Español (España y América Latina).",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-portuguese",
                "topic": "Canal de bate-papo em Português (Brasil e Portugal).",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-french",
                "topic": "Canal de discussion en Français.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-german",
                "topic": "Diskussionskanal auf Deutsch.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-italian",
                "topic": "Canale di conversazione in Italiano.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-chinese",
                "topic": "中文讨论区 (Chinese Discussion & Support).",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-japanese",
                "topic": "日本語コミュニティ (Japanese Community Channel).",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "chat-korean",
                "topic": "한국어 커뮤니티 (Korean Community Channel).",
                "read_only": False,
                "type": "text"
            }
        ]
    },
    {
        "name": "⚡｜FERROX CORE",
        "channels": [
            {
                "name": "core-architecture",
                "topic": "Discussion on ferrox-app, IoC container, lifecycle management, and application startup.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "cqrs-and-sagas",
                "topic": "CommandBus, QueryBus, Saga orchestrators, domain events, and asynchronous buses.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "databases-and-storage",
                "topic": "SeaORM, MongoDB, Redis caching, migrations, and S3 storage abstraction.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "security-and-guards",
                "topic": "PASETO/JWT security engine, Role Guards, Rate Limiters, and Circuit Breakers.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "transports-and-graphql",
                "topic": "Multi-transport engines: HTTP (Axum), gRPC, WebSockets, GraphQL, and SSE push streams.",
                "read_only": False,
                "type": "text"
            },
            {
                "name": "cli-and-tooling",
                "topic": "Ferrox CLI (`cargo-ferrox`), code generators, TypeScript definitions, and OpenAPI/Zod specs.",
                "read_only": False,
                "type": "text"
            }
        ]
    },
    {
        "name": "🆘｜HELP & SUPPORT",
        "channels": [
            {
                "name": "help-beginner",
                "topic": "Getting started with Ferrox, setup questions, and first steps (English).",
                "read_only": False,
                "type": "forum",
                "tags": [
                    {"name": "Question", "emoji": "❓"},
                    {"name": "Setup", "emoji": "⚙️"},
                    {"name": "Cargo", "emoji": "📦"},
                    {"name": "Resolved", "emoji": "✅"}
                ]
            },
            {
                "name": "help-advanced",
                "topic": "Complex microservice architectures, custom interceptors, custom guards, and performance tuning.",
                "read_only": False,
                "type": "forum",
                "tags": [
                    {"name": "Architecture", "emoji": "🧠"},
                    {"name": "CQRS/Saga", "emoji": "🔄"},
                    {"name": "Security", "emoji": "🛡️"},
                    {"name": "Performance", "emoji": "⚡"},
                    {"name": "Resolved", "emoji": "✅"}
                ]
            },
            {
                "name": "help-bug-reports",
                "topic": "Report bugs or unexpected behaviors before creating an official GitHub issue.",
                "read_only": False,
                "type": "forum",
                "tags": [
                    {"name": "Bug", "emoji": "🐛"},
                    {"name": "Confirmed", "emoji": "🔍"},
                    {"name": "Investigating", "emoji": "⏳"},
                    {"name": "Fixed", "emoji": "🎉"}
                ]
            }
        ]
    },
    {
        "name": "🛠️｜CONTRIBUTORS",
        "channels": [
            {
                "name": "contributors-lounge",
                "topic": "Discussion area for official framework contributors and core maintainers.",
                "read_only": False,
                "restricted_to": ["Core Maintainer", "Contributor"],
                "type": "text"
            },
            {
                "name": "rfc-proposals",
                "topic": "Request For Comments (RFC) proposals for new Ferrox crates and core API changes.",
                "read_only": False,
                "type": "forum",
                "tags": [
                    {"name": "RFC", "emoji": "📜"},
                    {"name": "Proposal", "emoji": "💡"},
                    {"name": "Under-Review", "emoji": "👀"},
                    {"name": "Accepted", "emoji": "✅"}
                ]
            },
            {
                "name": "github-activity",
                "topic": "Automated feed for GitHub commits, pull requests, issues, and releases.",
                "read_only": True,
                "type": "text"
            }
        ]
    },
    {
        "name": "🔊｜VOICE LOUNGES",
        "channels": [
            {
                "name": "🔊 General Lounge 1",
                "topic": "Global open voice channel.",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 General Lounge 2",
                "topic": "Global open voice channel.",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 Architecture & Pair Dev",
                "topic": "Voice lounge for architecture discussions and pair programming.",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 Voice (English)",
                "topic": "English spoken voice channel.",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 Voice (Español / PT-BR)",
                "topic": "Spanish & Portuguese voice lounge (Americas & Iberia).",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 Voice (FR / DE / IT)",
                "topic": "European languages voice lounge (French, German, Italian).",
                "read_only": False,
                "type": "voice"
            },
            {
                "name": "🔊 Voice (ZH / JA / KO)",
                "topic": "Asian languages voice lounge (Chinese, Japanese, Korean).",
                "read_only": False,
                "type": "voice"
            }
        ]
    },
    {
        "name": "🤖｜BRIDGE CONTROL",
        "channels": [
            {
                "name": "bridge-control",
                "topic": "Automated bridge channel for AI assistant management and server status logs.",
                "read_only": False,
                "restricted_to": ["Core Maintainer", "Bot Bridge"],
                "type": "text"
            }
        ]
    }
]

# Rich Embed Definitions (Primary Localization: English)
WELCOME_EMBED = {
    "title": "⚡ Welcome to the Official Ferrox Framework Global Community!",
    "description": (
        "Welcome to the global home of **Ferrox** — a progressive, enterprise-grade server-side framework for Rust.\n\n"
        "Bringing the developer experience of **NestJS & Angular** to the unmatched speed and safety of **Tokio & Axum**.\n\n"
        "### 🚀 Getting Started\n"
        "• Check out <#rules-and-guidelines> for community rules.\n"
        "• Explore <#faq-and-resources> for official documentation, server tags & GitHub repos.\n"
        "• Find your native language chat in **`🌐｜INTERNATIONAL CHATS`**.\n"
        "• Assign yourself roles in <#roles-select> to customize your badge and notifications.\n"
        "• Say hello in <#general>!"
    ),
    "color": COLOR_FERROX,
    "fields": [
        {
            "name": "🛡️ Zero-Trust Security",
            "value": "Built-in PASETO JWT engine, Role Guards, and HMAC verification.",
            "inline": True
        },
        {
            "name": "⚡ Extreme Resilience",
            "value": "Singleflight cache stampede protection, Circuit Breakers, and Rate Limiters.",
            "inline": True
        },
        {
            "name": "🧠 Enterprise Patterns",
            "value": "CQRS Command/Query buses, Saga orchestrators, and Event Emitters out of the box.",
            "inline": True
        }
    ],
    "footer": {"text": "Ferrox Global Community • Built with Rust & Tokio"}
}

RULES_EMBED = {
    "title": "📜 Server Rules & Community Guidelines",
    "description": (
        "To ensure a productive, welcoming, and inclusive community for developers worldwide, please adhere to these guidelines:\n\n"
        "1. **Be Respectful & Inclusive**: Treat all community members with courtesy regardless of experience level or background. Zero tolerance for harassment or toxic behavior.\n"
        "2. **Language Channels**: Main announcements and core architecture discussions are in **English**. For localized conversations, use the respective channels in **`🌐｜INTERNATIONAL CHATS`**.\n"
        "3. **Use Appropriate Channels & Forum Tags**: Post technical questions in designated channels and use appropriate forum tags (e.g. `🐛 Bug`, `❓ Question`, `🧠 Architecture`).\n"
        "4. **Code & Trace Formatting**: Always use syntax-highlighted code blocks for sharing code or stack traces (e.g. ```rust ... ```).\n"
        "5. **No Unsolicited Promotion or Spam**: Avoid DMs to members, self-promotion, or spamming links."
    ),
    "color": COLOR_RED,
    "footer": {"text": "Ferrox Global Community Guidelines"}
}

FAQ_EMBED = {
    "title": "📚 Ferrox Framework Documentation & Server Tags",
    "description": (
        "Essential resources and inventory for the **Ferrox Framework** ecosystem:\n\n"
        "• **GitHub Repository:** [Ferrox Framework Core](https://github.com/ferrox-rs/ferrox)\n"
        "• **Crates Workspace:** 35+ specialized crates (`ferrox-app`, `ferrox-cqrs`, `ferrox-security`, `ferrox-database-seaorm`, etc.)\n"
        "• **Architecture:** Onion Request Pipeline built on Tokio & Axum\n\n"
        "### 🏷️ Server Discovery Tags\n"
        "`" + "`, `" .join(SERVER_DISCOVERY_TAGS) + "`\n\n"
        "### 📦 Quick Cargo Setup\n"
        "```toml\n"
        "[dependencies]\n"
        "ferrox-app = \"0.1\"\n"
        "ferrox-transports = \"0.1\"\n"
        "ferrox-errors = \"0.1\"\n"
        "tokio = { version = \"1\", features = [\"full\"] }\n"
        "```"
    ),
    "color": COLOR_CYAN,
    "footer": {"text": "Ferrox Documentation Center"}
}

ROLES_EMBED = {
    "title": "🏷️ Select Your Developer Badges & Roles",
    "description": (
        "Click the buttons below to assign or remove roles from your profile:\n\n"
        "• 🟢 **Ferrox Developer**: Active member of the Ferrox developer community.\n"
        "• 🦀 **Rustacean**: Rust developer / systems programming enthusiast.\n"
        "• 🪺 **NestJS Enthusiast**: Developer interested in NestJS architecture brought to Rust."
    ),
    "color": COLOR_PURPLE,
    "footer": {"text": "Ferrox Role Manager"}
}
