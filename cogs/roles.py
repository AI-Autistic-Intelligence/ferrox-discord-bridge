import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger("FerroxBot.Roles")

class RoleButton(discord.ui.Button):
    def __init__(self, role_name: str, emoji: str, style: discord.ButtonStyle):
        super().__init__(label=role_name, emoji=emoji, style=style, custom_id=f"role_btn_{role_name.lower().replace(' ', '_')}")
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=self.role_name)

        if not role:
            await interaction.response.send_message(f"❌ Role **{self.role_name}** not found on this server.", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"➖ Removed role **{self.role_name}** from your profile.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"➕ Added role **{self.role_name}** to your profile!", ephemeral=True)


class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(RoleButton("Ferrox Developer", "🟢", discord.ButtonStyle.success))
        self.add_item(RoleButton("Rustacean", "🦀", discord.ButtonStyle.primary))
        self.add_item(RoleButton("NestJS Enthusiast", "🪺", discord.ButtonStyle.secondary))


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Register persistent view so button interactions survive bot restarts
        self.bot.add_view(RolesView())
        logger.info("Roles Cog loaded and persistent view registered.")

    @app_commands.command(name="post-role-select", description="Post interactive role selection menu into current channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def post_role_select(self, interaction: discord.Interaction):
        from server_schema import ROLES_EMBED, COLOR_PURPLE

        embed = discord.Embed(
            title=ROLES_EMBED["title"],
            description=ROLES_EMBED["description"],
            color=COLOR_PURPLE
        )
        embed.set_footer(text=ROLES_EMBED["footer"]["text"])

        view = RolesView()
        await interaction.response.send_message("Role selector posted!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))
