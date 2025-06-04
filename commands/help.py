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
from discord.ext import commands

from lang_settings import language_settings
from localisation import get_text

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx: commands.Context):
        if ctx.guild:
            lang = language_settings["guild"].get(str(ctx.guild.id), "ENG")
        else:
            lang = language_settings["user"].get(str(ctx.author.id), "ENG")

        title = get_text(lang, "help", "EMBED_TITLE")
        description = get_text(lang, "help", "EMBED_DESCRIPTION")

        embed = discord.Embed(title=title, description=description, color=0x00ff00)
        
        embed.add_field(
            name=get_text(lang, "help", "HELP_FIELD_NAME"),
            value=get_text(lang, "help", "HELP_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "LANG_FIELD_NAME"),
            value=get_text(lang, "help", "LANG_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "CARD_FIELD_NAME"),
            value=get_text(lang, "help", "CARD_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "CHAR_FIELD_NAME"),
            value=get_text(lang, "help", "CHAR_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "EVENT_FIELD_NAME"),
            value=get_text(lang, "help", "EVENT_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "GACHA_FIELD_NAME"),
            value=get_text(lang, "help", "GACHA_FIELD_DESC"),
            inline=False
        )
        embed.add_field(
            name=get_text(lang, "help", "SONG_FIELD_NAME"),
            value=get_text(lang, "help", "SONG_FIELD_DESC"),
            inline=False
        )

        footer = get_text(lang, "help", "FOOTER", VERSION=self.bot.version)
        embed.set_footer(text=footer)

        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
