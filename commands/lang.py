# ─── Monkey-patch typing.Self (so bestdori can import it on python 3.10) ───
# ——— Not needed for python 3.11+ ———
# ——— Un-comment this section only if you are using python 3.10 and below ———
# import typing
# try:
#     _ = typing.Self
# except AttributeError:
#     from typing_extensions import Self
#     typing.Self = Self
# ─────────────────────────────────────────────────────────────────────────────

import discord
from discord import app_commands
from discord.ext import commands
from lang_settings import language_settings, save_language_settings
from localisation import get_text

class Lang(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lang", description="Set bot language for this server or DM")
    @app_commands.describe(code="Language code (ENG, JPN, CHS, CHT, KOR)")
    @app_commands.choices(code=[
        app_commands.Choice(name="English", value="ENG"),
        app_commands.Choice(name="Japanese", value="JPN"),
        app_commands.Choice(name="Chinese (Simplified)", value="CHS"),
        app_commands.Choice(name="Chinese (Traditional)", value="CHT"),
        app_commands.Choice(name="Korean", value="KOR")
    ])
    async def set_language(self, interaction: discord.Interaction, code: str):
        if interaction.guild is not None:
            if not interaction.user.guild_permissions.administrator:
                current_lang = language_settings["guild"].get(str(interaction.guild.id), "ENG")
                msg = get_text(current_lang, "lang", "NO_ADMIN")
                await interaction.response.send_message(msg, ephemeral=True)
                return

            language_settings["guild"][str(interaction.guild.id)] = code
            save_language_settings()

            confirm = get_text(code, "lang", "CONFIRM_GUILD", LANG=code)
            await interaction.response.send_message(confirm, ephemeral=True)

        else:
            language_settings["user"][str(interaction.user.id)] = code
            save_language_settings()

            confirm = get_text(code, "lang", "CONFIRM_USER", LANG=code)
            await interaction.response.send_message(confirm, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Lang(bot))
