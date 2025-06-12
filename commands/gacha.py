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
import datetime
import aiohttp
import discord
from discord.ext import commands

import bestdori.gacha
import bestdori.cards
import bestdori.characters
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

class GachaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_pjsk_gacha(self, gacha_id: int, lang: str) -> dict:
        repo = _repo_map.get(lang, "sekai-master-db-en-diff")
        base = f"https://raw.githubusercontent.com/Sekai-World/{repo}/main"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base}/gachas.json") as resp:
                gachas = await resp.json(content_type=None)
            async with session.get(f"{base}/cards.json") as resp:
                cards = await resp.json(content_type=None)
            async with session.get(f"{base}/gameCharacters.json") as resp:
                characters = await resp.json(content_type=None)

        gacha = next((g for g in gachas if g.get("id") == gacha_id), None)
        if not gacha:
            raise ValueError("Gacha not found")

        start = gacha.get("startAt")
        end = gacha.get("endAt")
        start_str = datetime.datetime.utcfromtimestamp(start / 1000).strftime("%Y-%m-%d %H:%M") if start else "N/A"
        end_str = datetime.datetime.utcfromtimestamp(end / 1000).strftime("%Y-%m-%d %H:%M") if end else "N/A"

        banner_url = (
            f"https://storage.sekai.best/sekai-jp-assets/homebanner/{gacha['assetbundleName']}_rip/{gacha['assetbundleName']}.png"
        )
        banner_bytes = None
        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as resp:
                if resp.status == 200:
                    banner_bytes = await resp.read()

        pickup_ids = [p.get("cardId") for p in gacha.get("gachaPickups", [])]
        pickups = []
        for cid in pickup_ids[:3]:
            card = next((c for c in cards if c.get("id") == cid), None)
            if card:
                char = next((ch for ch in characters if ch.get("id") == card.get("characterId")), None)
                char_name = f"{char.get('firstName', '')} {char.get('givenName', '')}".strip() if char else "N/A"
                pickups.append(f"{card.get('prefix', 'N/A')} ({char_name})")
            else:
                pickups.append(str(cid))

        return {
            "title": gacha.get("name", "N/A"),
            "start": start_str,
            "end": end_str,
            "banner": banner_bytes,
            "pickups": pickups,
        }

    @commands.command(name="gacha")
    async def gacha(self, ctx: commands.Context, gacha_id: str = None):
        if ctx.guild:
            lang = language_settings["guild"].get(str(ctx.guild.id), "ENG")
        else:
            lang = language_settings["user"].get(str(ctx.author.id), "ENG")

        idx = _lang_to_index.get(lang, 3)

        if gacha_id is None:
            await ctx.reply(get_text(lang, "gacha", "USAGE"))
            return

        try:
            if isinstance(gacha_id, str) and gacha_id.lower().startswith("pjsk"):
                pjsk_id = gacha_id[4:]
                if not pjsk_id.isdigit():
                    raise ValueError("Invalid pjsk gacha id")
                data = await self._get_pjsk_gacha(int(pjsk_id), lang)

                embed = discord.Embed(
                    title=get_text(lang, "gacha", "EMBED_TITLE", GACHA_ID=pjsk_id),
                    color=0xFF66FF,
                )
                embed.add_field(name=get_text(lang, "gacha", "FIELD_NAME"), value=data["title"], inline=False)
                embed.add_field(
                    name=get_text(lang, "gacha", "FIELD_PERIOD"),
                    value=f"{data['start']} - {data['end']}",
                    inline=False,
                )
                if data["pickups"]:
                    embed.add_field(
                        name=get_text(lang, "gacha", "FIELD_PICKUPS"),
                        value="\n".join(data["pickups"]),
                        inline=False,
                    )

                files = []
                if data["banner"]:
                    files.append(
                        discord.File(io.BytesIO(data["banner"]), filename=f"pjsk_gacha_{pjsk_id}.png")
                    )
                    embed.set_image(url=f"attachment://pjsk_gacha_{pjsk_id}.png")

                await ctx.reply(embed=embed, files=files)
                return

            gacha = bestdori.gacha.Gacha(int(gacha_id))
            info = await gacha.get_info_async()

            server = ["jp", "en", "tw", "cn", "kr"][idx]

            banner_bytes = None
            try:
                banner_bytes = await gacha.get_banner_async(server)
            except Exception:
                banner_bytes = None

            names = info.get("gachaName", [])
            name = names[idx] if len(names) > idx and names[idx] else next((n for n in names if n), "N/A")

            start_list = info.get("publishedAt", [])
            end_list = info.get("closedAt", [])
            start = next((start_list[idx], *start_list), None)
            end = next((end_list[idx], *end_list), None)
            start_str = start[:10] if isinstance(start, str) else str(start)
            end_str = end[:10] if isinstance(end, str) else str(end)

            embed = discord.Embed(
                title=get_text(lang, "gacha", "EMBED_TITLE", GACHA_ID=int(gacha_id)),
                color=0xFF66FF,
            )
            embed.add_field(name=get_text(lang, "gacha", "FIELD_NAME"), value=name, inline=False)
            embed.add_field(
                name=get_text(lang, "gacha", "FIELD_PERIOD"), value=f"{start_str} - {end_str}", inline=False
            )

            if banner_bytes:
                file = discord.File(io.BytesIO(banner_bytes), filename=f"gacha_{gacha_id}.png")
                embed.set_image(url=f"attachment://gacha_{gacha_id}.png")
                await ctx.reply(embed=embed, file=file)
            else:
                await ctx.reply(embed=embed)

        except bestdori.exceptions.NotExistException:
            msg = get_text(lang, "gacha", "NOT_FOUND", GACHA_ID=gacha_id)
            await ctx.reply(msg)
        except Exception as e:
            msg = get_text(lang, "gacha", "ERROR", ERROR=e)
            await ctx.reply(msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(GachaCog(bot))