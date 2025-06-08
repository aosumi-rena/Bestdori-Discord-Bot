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
import aiohttp
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

_repo_map = {
    "ENG": "sekai-master-db-en-diff",
    "JPN": "sekai-master-db-diff",
    "CHS": "sekai-master-db-cn-diff",
    "CHT": "sekai-master-db-tc-diff",
    "KOR": "sekai-master-db-kr-diff",
}

class CharacterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_pjsk_character(self, char_id: int, lang: str) -> dict:
    # PJSK section, fetched from sekai viewer's github
        repo = _repo_map.get(lang, "sekai-master-db-en-diff")
        base = f"https://raw.githubusercontent.com/Sekai-World/{repo}/main"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base}/gameCharacters.json") as resp:
                chars = await resp.json(content_type=None)
            async with session.get(f"{base}/unitProfiles.json") as resp:
                units = await resp.json(content_type=None)

        char = next((c for c in chars if c.get("id") == char_id), None)
        if not char:
            raise ValueError("Character not found")

        unit_name = next((u["unitName"] for u in units if u.get("unit") == char.get("unit")), "N/A")

        name = f"{char.get('firstName', '')} {char.get('givenName', '')}".strip()
        image_url = (
            f"https://storage.sekai.best/sekai-jp-assets/character/character_trim/chr_trim_{char['resourceId']}.png"
        )

        return {"name": name, "band": unit_name, "image": image_url}

    @commands.command(name='character', aliases=['char'])
    async def character(self, ctx: commands.Context, char_id: str = None):

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
            if isinstance(char_id, str) and char_id.lower().startswith("pjsk"):
                pjsk_id = char_id[4:]
                if not pjsk_id.isdigit():
                    raise ValueError("Invalid pjsk character id")
                char_data = await self._get_pjsk_character(int(pjsk_id), lang)
                title_text = get_text(lang, "character", "EMBED_TITLE", CHAR_ID=pjsk_id, NAME=char_data.get("name", "N/A"))
                embed = discord.Embed(title=title_text, color=0x00AAFF)
                embed.add_field(
                    name=get_text(lang, "character", "FIELD_BAND"),
                    value=char_data.get("band", "N/A"),
                    inline=False,
                )
                image_url = char_data.get("image")
                if image_url:
                    embed.set_thumbnail(url=image_url)
                await ctx.reply(embed=embed)
                return

            character = bestdori.characters.Character(int(char_id))
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

            title_text = get_text(lang, "character", "EMBED_TITLE", CHAR_ID=int(char_id), NAME=display_name)
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
            msg = get_text(lang, "character", "NOT_FOUND", CHAR_ID=int(char_id))
            await ctx.reply(msg)
        except Exception as e:
            msg = get_text(lang, "character", "ERROR", ERROR=e)
            await ctx.reply(msg)


async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterCog(bot))
