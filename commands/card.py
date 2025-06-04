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


class CardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='card', aliases=['check_card', 'card_check'])
    async def card(self, ctx: commands.Context, card_id: int = None):
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
            card = bestdori.cards.Card(card_id)
            card_info = await card.get_info_async()

            character = bestdori.characters.Character(card_info['characterId'])
            char_info = await character.get_info_async()

            card_image_normal = None
            card_image_after = None
            try:
                card_image_normal = await card.get_card_async('normal')
            except bestdori.exceptions.NotExistException:
                card_image_normal = None
            try:
                card_image_after = await card.get_card_async('after_training')
            except bestdori.exceptions.NotExistException:
                card_image_after = None

            title_text = get_text(lang, "card", "EMBED_TITLE", CARD_ID=card_id)
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
