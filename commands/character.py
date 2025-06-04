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

import io
import discord
from discord.ext import commands

import bestdori.characters
import bestdori.bands
import bestdori.exceptions

from lang_settings import language_settings
from localisation import get_text

_lang_to_index = {
    "JPN": 0,
    "ENG": 1,
    "CHT": 2, 
    "CHS": 3,
    "KOR": 4
}


class CharacterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='character', aliases=['char'])
    async def character(self, ctx: commands.Context, char_id: int = None):

        if ctx.guild:
            lang = language_settings["guild"].get(str(ctx.guild.id), "ENG")
        else:
            lang = language_settings["user"].get(str(ctx.author.id), "ENG")

        idx = _lang_to_index.get(lang, 3)  # default to eng

        if char_id is None:
            msg = get_text(lang, "character", "USAGE")
            await ctx.reply(msg)
            return

        try:
            character = bestdori.characters.Character(char_id)
            char_info = await character.get_info_async()

            bands_info: dict = bestdori.bands.get_all()
            band_id = char_info.get('bandId')
            band_name = "Unknown"
            if band_id is not None:
                band_entry = bands_info.get(str(band_id))
                if band_entry:
                    if len(band_entry['bandName']) > idx and band_entry['bandName'][idx]:
                        band_name = band_entry['bandName'][idx]
                    else:
                        band_name = band_entry['bandName'][3] or band_entry['bandName'][0] or "Unknown"

            icon_bytes = None
            try:
                icon_bytes = await character.get_icon_async()
            except bestdori.exceptions.NotExistException:
                icon_bytes = None

            char_names = char_info.get('characterName', [])
            if len(char_names) > idx and char_names[idx]:
                display_name = char_names[idx]
            else:
                display_name = char_names[3] if len(char_names) > 3 and char_names[3] else (char_names[0] if len(char_names) > 0 else "N/A")

            title_text = get_text(lang, "character", "EMBED_TITLE", CHAR_ID=char_id, NAME=display_name)
            embed = discord.Embed(title=title_text, color=0x00AAFF)

            embed.add_field(
                name=get_text(lang, "character", "FIELD_BAND"),
                value=band_name,
                inline=False
            )

            if icon_bytes:
                file = discord.File(io.BytesIO(icon_bytes), filename=f"char_{char_id}.png")
                embed.set_thumbnail(url=f"attachment://char_{char_id}.png")
                await ctx.reply(embed=embed, file=file)
            else:
                await ctx.reply(embed=embed)

        except bestdori.exceptions.NotExistException:
            msg = get_text(lang, "character", "NOT_FOUND", CHAR_ID=char_id)
            await ctx.reply(msg)
        except Exception as e:
            msg = get_text(lang, "character", "ERROR", ERROR=e)
            await ctx.reply(msg)


async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterCog(bot))
