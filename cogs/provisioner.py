import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, List, Any
from server_schema import (
    ROLES_SPEC,
    CATEGORIES_SPEC,
    WELCOME_EMBED,
    RULES_EMBED,
    FAQ_EMBED,
    ROLES_EMBED
)
from cogs.roles import RolesView

logger = logging.getLogger("FerroxBot.Provisioner")

class ProvisionerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def provision_roles(self, guild: discord.Guild) -> Dict[str, discord.Role]:
        created_roles: Dict[str, discord.Role] = {}
        logger.info(f"Provisioning roles for guild: {guild.name}")

        for role_data in ROLES_SPEC:
            name = role_data["name"]
            existing_role = discord.utils.get(guild.roles, name=name)

            perms = discord.Permissions()
            if role_data.get("permissions", {}).get("administrator"):
                perms.administrator = True
            if role_data.get("permissions", {}).get("manage_messages"):
                perms.manage_messages = True
            if role_data.get("permissions", {}).get("embed_links"):
                perms.embed_links = True
            if role_data.get("permissions", {}).get("attach_files"):
                perms.attach_files = True
            if role_data.get("permissions", {}).get("kick_members"):
                perms.kick_members = True
            if role_data.get("permissions", {}).get("mute_members"):
                perms.mute_members = True

            if existing_role:
                logger.info(f"Role '{name}' already exists. Updating properties.")
                await existing_role.edit(
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"],
                    permissions=perms
                )
                created_roles[name] = existing_role
            else:
                logger.info(f"Creating role '{name}'.")
                new_role = await guild.create_role(
                    name=name,
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"],
                    permissions=perms
                )
                created_roles[name] = new_role

        return created_roles

    async def provision_categories_and_channels(self, guild: discord.Guild, roles_map: Dict[str, discord.Role]):
        logger.info("Provisioning categories and channels...")
        everyone_role = guild.default_role

        for cat_data in CATEGORIES_SPEC:
            cat_name = cat_data["name"]
            existing_cat = discord.utils.get(guild.categories, name=cat_name)

            if not existing_cat:
                logger.info(f"Creating category '{cat_name}'")
                existing_cat = await guild.create_category(name=cat_name)
            else:
                logger.info(f"Category '{cat_name}' already exists.")

            for chan_data in cat_data["channels"]:
                chan_name = chan_data["name"]
                chan_topic = chan_data.get("topic", "")
                read_only = chan_data.get("read_only", False)
                restricted_to = chan_data.get("restricted_to", None)

                # Build permission overwrites
                overwrites = {}
                
                if read_only:
                    overwrites[everyone_role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=False,
                        add_reactions=True
                    )
                
                if restricted_to:
                    # Hide from everyone
                    overwrites[everyone_role] = discord.PermissionOverwrite(read_messages=False)
                    # Allow specified roles
                    for r_name in restricted_to:
                        if r_name in roles_map:
                            overwrites[roles_map[r_name]] = discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=True,
                                attach_files=True,
                                embed_links=True
                            )

                chan_type = chan_data.get("type", "text")

                # Check if channel exists in category
                existing_chan = discord.utils.get(existing_cat.channels, name=chan_name)
                if not existing_chan:
                    logger.info(f"Creating {chan_type} channel '{chan_name}' in '{cat_name}'")
                    if chan_type == "voice":
                        existing_chan = await guild.create_voice_channel(
                            name=chan_name,
                            category=existing_cat,
                            overwrites=overwrites
                        )
                    elif chan_type == "forum":
                        forum_tags = [discord.ForumTag(name=t["name"], emoji=t.get("emoji")) for t in chan_data.get("tags", [])]
                        try:
                            existing_chan = await guild.create_forum(
                                name=chan_name,
                                category=existing_cat,
                                topic=chan_topic,
                                available_tags=forum_tags,
                                overwrites=overwrites
                            )
                        except Exception as e:
                            logger.warning(f"Could not create forum channel '{chan_name}'. Falling back to text channel: {e}")
                            existing_chan = await guild.create_text_channel(
                                name=chan_name,
                                category=existing_cat,
                                topic=chan_topic,
                                overwrites=overwrites
                            )
                    else:
                        existing_chan = await guild.create_text_channel(
                            name=chan_name,
                            category=existing_cat,
                            topic=chan_topic,
                            overwrites=overwrites
                        )
                else:
                    logger.info(f"Updating channel '{chan_name}' permissions.")
                    if chan_type == "voice":
                        await existing_chan.edit(overwrites=overwrites)
                    else:
                        await existing_chan.edit(topic=chan_topic, overwrites=overwrites)

    async def post_initial_announcements(self, guild: discord.Guild):
        logger.info("Posting initial rich embed announcements...")

        # 1. Rules channel
        rules_chan = discord.utils.get(guild.text_channels, name="rules-and-guidelines")
        if rules_chan:
            # Check if already posted to prevent duplication
            history = [msg async for msg in rules_chan.history(limit=5)]
            if not history:
                w_embed = discord.Embed.from_dict(WELCOME_EMBED)
                r_embed = discord.Embed.from_dict(RULES_EMBED)
                await rules_chan.send(embed=w_embed)
                await rules_chan.send(embed=r_embed)

        # 2. FAQ channel
        faq_chan = discord.utils.get(guild.text_channels, name="faq-and-resources")
        if faq_chan:
            history = [msg async for msg in faq_chan.history(limit=5)]
            if not history:
                f_embed = discord.Embed.from_dict(FAQ_EMBED)
                await faq_chan.send(embed=f_embed)

        # 3. Roles selection channel
        roles_chan = discord.utils.get(guild.text_channels, name="roles-select")
        if roles_chan:
            history = [msg async for msg in roles_chan.history(limit=5)]
            if not history:
                ro_embed = discord.Embed.from_dict(ROLES_EMBED)
                view = RolesView()
                await roles_chan.send(embed=ro_embed, view=view)

    async def clean_non_ferrox_channels(self, guild: discord.Guild):
        logger.info("Cleaning up non-Ferrox channels and categories...")
        ferrox_cat_names = {cat["name"] for cat in CATEGORIES_SPEC}
        ferrox_chan_names = set()
        for cat in CATEGORIES_SPEC:
            for ch in cat["channels"]:
                ferrox_chan_names.add(ch["name"])

        # Delete non-Ferrox text and voice channels
        for chan in list(guild.channels):
            if chan.name not in ferrox_chan_names and (chan.category is None or chan.category.name not in ferrox_cat_names):
                try:
                    logger.info(f"Deleting non-Ferrox channel: {chan.name} (ID: {chan.id})")
                    await chan.delete(reason="Purging non-Ferrox default channels")
                except Exception as e:
                    logger.warning(f"Could not delete channel {chan.name}: {e}")

        # Delete non-Ferrox categories
        for cat in list(guild.categories):
            if cat.name not in ferrox_cat_names:
                try:
                    logger.info(f"Deleting non-Ferrox category: {cat.name} (ID: {cat.id})")
                    await cat.delete(reason="Purging non-Ferrox default categories")
                except Exception as e:
                    logger.warning(f"Could not delete category {cat.name}: {e}")

    @app_commands.command(name="setup-server", description="Build or update the full Ferrox Discord Server architecture")
    @app_commands.describe(clean_first="If True, deletes pre-existing non-Ferrox default channels first")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_server(self, interaction: discord.Interaction, clean_first: bool = False):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        if not guild:
            await interaction.followup.send("❌ This command must be executed within a Discord Guild.", ephemeral=True)
            return

        try:
            if clean_first:
                await self.clean_non_ferrox_channels(guild)

            # 1. Provision Roles
            roles_map = await self.provision_roles(guild)

            # 2. Provision Categories & Channels
            await self.provision_categories_and_channels(guild, roles_map)

            # 3. Post Rich Embed Announcements
            await self.post_initial_announcements(guild)

            await interaction.followup.send(
                "⚡ **Ferrox Community Server setup completed successfully!**\n"
                "• All Roles, Categories, Channels, Permissions, and Embed Announcements have been provisioned."
                + ("\n• Pre-existing default channels were cleaned up." if clean_first else ""),
                ephemeral=True
            )
        except Exception as e:
            logger.exception("Error during server setup")
            await interaction.followup.send(f"❌ Error during server setup: {str(e)}", ephemeral=True)

    @app_commands.command(name="clean-old-channels", description="Delete pre-existing default channels/categories not part of Ferrox schema")
    @app_commands.checks.has_permissions(administrator=True)
    async def clean_old_channels(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        if not guild:
            await interaction.followup.send("❌ Command must be used in a guild.", ephemeral=True)
            return

        try:
            await self.clean_non_ferrox_channels(guild)
            await interaction.followup.send("🧹 **Cleanup complete!** Pre-existing non-Ferrox default channels and categories have been deleted.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Cleanup error: {str(e)}", ephemeral=True)

    @app_commands.command(name="server-tags", description="Display recommended Server Discovery Tags and Forum tags")
    async def server_tags(self, interaction: discord.Interaction):
        from server_schema import SERVER_DISCOVERY_TAGS, COLOR_FERROX
        embed = discord.Embed(
            title="🏷️ Ferrox Community Server Discovery & Forum Tags",
            description="Recommended tags for Discord Server Discovery and Forum channels:",
            color=discord.Color(COLOR_FERROX)
        )
        embed.add_field(
            name="🌍 Recommended Server Discovery Tags",
            value="`" + "`, `" .join(SERVER_DISCOVERY_TAGS) + "`",
            inline=False
        )
        embed.add_field(
            name="📌 Forum Channel Tags Available",
            value="• **#help-beginner**: `❓ Question`, `⚙️ Setup`, `📦 Cargo`, `✅ Resolved`\n"
                  "• **#help-advanced**: `🧠 Architecture`, `🔄 CQRS/Saga`, `🛡️ Security`, `⚡ Performance`\n"
                  "• **#help-bug-reports**: `🐛 Bug`, `🔍 Confirmed`, `⏳ Investigating`, `🎉 Fixed`\n"
                  "• **#showcase**: `🚀 App`, `⚙️ Microservice`, `📦 Library`, `🎨 Demo`\n"
                  "• **#rfc-proposals**: `📜 RFC`, `💡 Proposal`, `👀 Under-Review`, `✅ Accepted`",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProvisionerCog(bot))

