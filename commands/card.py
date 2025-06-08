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
import json
import re
import aiohttp
import discord
from discord.ext import commands

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

class CardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # PJSK section, fetched from sekai viewer's github
    async def _get_pjsk_card(self, card_id: int, lang: str) -> dict:
        repo = _repo_map.get(lang, "sekai-master-db-en-diff")
        base = f"https://raw.githubusercontent.com/Sekai-World/{repo}/main"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base}/cards.json") as resp:
                cards = await resp.json(content_type=None)
            async with session.get(f"{base}/gameCharacters.json") as resp:
                chars = await resp.json(content_type=None)

            card = next((c for c in cards if c.get("id") == card_id), None)
            if not card:
                raise ValueError("Card not found")

            char = next((c for c in chars if c.get("id") == card.get("characterId")), None)
            if char:
                char_name = f"{char.get('firstName', '')} {char.get('givenName', '')}".strip()
            else:
                char_name = "N/A"

            base_img = (
                f"https://storage.sekai.best/sekai-jp-assets/character/member/{card['assetbundleName']}"
            )
            normal_url = f"{base_img}/card_normal.png"
            after_url = f"{base_img}/card_after_training.png"

            async with session.get(normal_url) as img_resp:
                normal_bytes = await img_resp.read() if img_resp.status == 200 else None

            after_bytes = None
            if card.get("cardRarityType") not in ("rarity_1", "rarity_2"):
                async with session.get(after_url) as img_resp:
                    if img_resp.status == 200:
                        after_bytes = await img_resp.read()

        return {
            "title": card.get("prefix", "N/A"),
            "character": char_name,
            "normal": normal_bytes,
            "after": after_bytes,
        }
    

    @commands.command(name='card', aliases=['check_card', 'card_check'])
    async def card(self, ctx: commands.Context, card_id: str = None):
        if ctx.guild:
            lang = language_settings["guild"].get(str(ctx.guild.id), "ENG")
        else:
            lang = language_settings["user"].get(str(ctx.author.id), "ENG")

        idx = _lang_to_index.get(lang, 3)  # default to english / index=3

        if card_id is None:
            msg = get_text(lang, "card", "USAGE")
            await ctx.reply(msg)
            return

        try:
            if isinstance(card_id, str) and card_id.lower().startswith("pjsk"):
                pjsk_id = card_id[4:]
                if not pjsk_id.isdigit():
                    raise ValueError("Invalid pjsk card id")
                card_data = await self._get_pjsk_card(int(pjsk_id), lang)

                title_text = get_text(lang, "card", "EMBED_TITLE", CARD_ID=pjsk_id)
                embed = discord.Embed(title=title_text, color=0x00ff00)
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_TITLE"),
                    value=card_data.get("title", "N/A"),
                    inline=False,
                )
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_CHARACTER"),
                    value=card_data.get("character", "N/A"),
                    inline=False,
                )

                files = []
                if card_data.get("normal"):
                    files.append(
                        discord.File(
                            io.BytesIO(card_data["normal"]),
                            filename=f"pjsk_{pjsk_id}_normal.png",
                        )
                    )
                if card_data.get("after"):
                    files.append(
                        discord.File(
                            io.BytesIO(card_data["after"]),
                            filename=f"pjsk_{pjsk_id}_after.png",
                        )
                    )

                await ctx.reply(embed=embed, files=files)
                return
            
 
            card = bestdori.cards.Card(int(card_id))
            card = bestdori.cards.Card(card_id)
            card_info = await card.get_info_async()

            character = bestdori.characters.Character(card_info['characterId'])
            char_info = await character.get_info_async()

            card_image_normal = None
            card_image_after = None
            can_train = True
            try:
                card_image_normal = await card.get_card_async('normal')

            except Exception:
                card_image_normal = None
            try:
                card_image_after = await card.get_card_async('after_training')
        
            except Exception:
                card_image_after = None
                can_train = False

            title_text = get_text(lang, "card", "EMBED_TITLE", CARD_ID=int(card_id))
            embed = discord.Embed(title=title_text, color=0x00ff00)

            prefix = card_info.get('prefix', [])
            if len(prefix) > idx and prefix[idx]:
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_TITLE"),
                    value=prefix[idx],
                    inline=False
                )
            else:
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_TITLE"),
                    value="N/A",
                    inline=False
                )

            char_names = char_info.get('characterName', [])
            if len(char_names) > idx and char_names[idx]:
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_CHARACTER"),
                    value=char_names[idx],
                    inline=False
                )
            else:
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_CHARACTER"),
                    value="N/A",
                    inline=False
                )

            if not can_train:
                embed.add_field(
                    name=get_text(lang, "card", "FIELD_TRAINING"),
                    value=get_text(lang, "card", "NOT_TRAINABLE"),
                    inline=False
                )

            files = []
            if card_image_normal:
                files.append(discord.File(io.BytesIO(card_image_normal),
                                          filename=f"card_{card_id}_normal.png"))
            if card_image_after:
                files.append(discord.File(io.BytesIO(card_image_after),
                                          filename=f"card_{card_id}_after.png"))

            await ctx.reply(embed=embed, files=files)

        except bestdori.exceptions.NotExistException:
            msg = get_text(lang, "card", "NOT_FOUND", CARD_ID=card_id)
            await ctx.reply(msg)
        except Exception as e:
            msg = get_text(lang, "card", "ERROR", ERROR=e)
            await ctx.reply(msg)


async def setup(bot: commands.Bot):
    await bot.add_cog(CardCog(bot))
