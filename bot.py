import discord
import asyncio
from discord.ext import commands
import os
import sys
from pathlib import Path

# ── Bot configuration ───────────────────────────────────────────────────────────
TOKEN = "<DISCORD_BOT_TOKEN>"
VERSION = "CHU³-Beta-0.1.50"
# ────────────────────────────────────────────────────────────────────────────────

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents)
bot.version = VERSION

bot.remove_command('help')
# rm default help command

async def load_commands():
    base_dir = Path(__file__).parent
    commands_dir = base_dir / "commands"

    if not commands_dir.exists():
        print(f"[load_commands] No '{commands_dir}' directory found.")
        return

    for file_path in commands_dir.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue

        rel_path = file_path.relative_to(base_dir)
        module_path = ".".join(rel_path.with_suffix("").parts)

        try:
            await bot.load_extension(module_path)
            print(f"[load_commands] Loaded: {module_path}")
        except Exception as e:
            print(f"[load_commands] Failed to load {module_path}: {e}")


@bot.event
async def on_ready():
    print(f"Bot has logged in as {bot.user}")

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="out for errors"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    try:
        synced_global = await bot.tree.sync()
        print(f"[on_ready] Global: Synced {len(synced_global)} slash commands.")

        test_guild_id = 1256645661349249025
        synced_guild = await bot.tree.sync(guild=discord.Object(id=test_guild_id))
        print(f"[on_ready] Guild {test_guild_id}: Synced {len(synced_guild)} slash commands.")
    except Exception as e:
        print(f"[on_ready] Error syncing commands: {e}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()
    raw_commands = {
        "查卡": "card",
        "角色": "character",
        "活动": "event",
        "卡池": "gacha",
        "查谱": "song",
        "帮助": "help",
    }

    for zh_trigger, eng_command in raw_commands.items():
        if content == zh_trigger or content.startswith(f"{zh_trigger} "):
            args = content[len(zh_trigger):].strip()
            new_content = f"^{eng_command}"
            if args:
                new_content += f" {args}"

            message.content = new_content
            await bot.process_commands(message)
            return

    await bot.process_commands(message)

async def main():
    async with bot:
        await load_commands()
        await bot.start(TOKEN)
    

if __name__ == "__main__":
    asyncio.run(main())
