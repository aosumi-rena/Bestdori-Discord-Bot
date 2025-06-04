# Bestdori API Discord Bot

This Discord bot provides card, character, event, gacha, and song information from the BanG Dream! mobile game, using the [Bestdori API](https://github.com/WindowsSov8forUs/bestdori-api). It supports multiple languages (ENG, CHS, CHT, JPN, KOR) and allows per-guild or per-user language selection via a `/lang` slash command.

---

## Table of Contents

* [Features](#features)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Configuration](#configuration)
* [Commands & Usage](#commands--usage)

  * [`/lang` Command](#lang-command)
  * `^card <ID>`
  * `^char <ID>`
  * `^help`
  * (Future: `^event`, `^gacha`, `^song`)
* [Localization](#localization)

  * [Language Settings Storage](#language-settings-storage)
  * [Adding or Editing Textmaps](#adding-or-editing-textmaps)
* [Project Structure](#project-structure)
* [Dependencies](#dependencies)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* **Card Lookup** (`^card <ID>`)

  * Shows a single‐language card title and character name, plus attaches full "normal" and "after-training" card images.

* **Character Lookup** (`^char <ID>`)

  * Displays a single‐language character name, band name, and character icon.

* **Help Menu** (`^help`)

  * Lists all available commands and usage instructions, localized.

* **Slash Command for Language** (`/lang <code>`)

  * Allows per-guild or per-user language selection (ENG, CHS, CHT, JPN, KOR).
  * Guild setting can only be changed by administrators; DM setting can be changed by any user.

* **Localization**

  * All bot messages (usage hints, embed titles, field names, error messages) are stored in external JSON textmaps (`textmap_<LANG>.json`).
  * By default, responses appear in English.
  * Adding or updating textmaps for other languages is straightforward.

* **Raw Command Handling**

  * The bot can handle raw chinese as commands, where
    * `查卡`->`^card`  
      没错，可以复刻`查卡 947`（
    * `角色`->`char`
    * `活动`->`event`
    * `卡池`->`gacha`
    * `查谱`->`song`
    * `帮助`->`help`


* **Bestdori API Integration**

  * Uses the [Bestdori API](https://github.com/WindowsSov8forUs/bestdori-api) to fetch game data (cards, characters, etc.) in the requested language only.

---

## Getting Started

### Prerequisites

* **Python 3.10+**
* A Discord bot token (create one via the [Discord Developer Portal](https://discord.com/developers/applications))
* A stable internet connection (to reach the Bestdori API)
* (Optional) A virtual environment for Python package isolation

### Installation

1. **Clone or Download** this repository to your local machine:

   ```bash
   git clone https://github.com/aosumi-rena/Bestdori-Discord-Bot.git
   cd bang-dream-discord-bot
   ```

2. **Create a Virtual Environment** (recommended) and activate it:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   *If you don’t have a `requirements.txt`, install manually:*

   ```bash
   pip install discord.py bestdori-api typing-extensions
   ```

4. **Edit `bot.py`**:

   * Open `bot.py` in your code editor.
   * Replace `TOKEN = "REDACTED"` with your actual Discord bot token.
   * Optionally adjust any other settings (e.g. version, test guild ID for slash syncing).

5. **(First Run) Generate `language_settings.json`**:

   The file `language_settings.json` is created automatically in the project root the first time you run the bot. You do not need to create it manually.

6. **Run the Bot**:

   ```bash
   python bot.py
   ```

   You should see output indicating that cogs have been loaded and that the bot has logged in.

---

## Configuration

### `language_settings.json`

After the first run, you will have a file named `language_settings.json`. Its initial contents look like:

```json
{
  "guild": {},
  "user": {}
}
```

* **guild**: Maps guild (server) IDs to language codes.
* **user**: Maps user IDs (for DMs) to language codes.

Whenever someone in a server with Administrator permission runs `/lang <code>`, that guild’s ID and chosen code are stored here. Commands in that guild will then respond in that language. If a user runs `/lang <code>` in a direct message, their user ID and code are stored here.

You should not edit `language_settings.json` by hand—using `/lang` ensures format consistency—but you can if needed. Just follow the same JSON structure.

---

## Commands & Usage

Below is a brief overview of the bot commands. All text shown is localized based on the per-guild or per-user language setting.

### `/lang` Command

Changes the bot’s language. Usage:

```
/lang <code>
```

* **Options**:
  * `ENG` (English, default)
  * `JPN` (Japanese)
  * `CHS` (Chinese, Simplified)
  * `CHT` (Chinese, Traditional)
  * `KOR` (Korean)

* **Guild (Server) Context**:
  Only users with Administrator permission may run in a guild to set that guild’s language.
  For example, after running `/lang JPN`, all subsequent responses in that server will appear in Japanese.

* **DM Context**:
  Any user may run `/lang <code>` in a DM. This sets their personal language for DM‐only interactions.

### `^card <ID>`

Fetches and displays information about a card.

```
^card 947
```

* **Features**:

  * Shows the card’s single‐language title (based on the chosen language).
  * Shows the character name in that language.
  * Attaches both the “normal” and “after-training” full-size card images.
  * Replies localized usage, embed title, field names, “not found,” and error messages.

### `^char <ID>`

Fetches and displays information about a character.

```
^char 35
```

* **Features**:

  * Shows the character’s name in the chosen language.
  * Shows the band name in that language.
  * Attaches the character’s icon image.
  * Replies localized usage, embed title, field name, “not found,” and error messages.

### `^help`

Shows an embed listing all available commands and their descriptions.

```
^help
```

* **Features**:

  * Lists every command (`^card`, `^char`, `^event`, `^gacha`, `^song`, `^help`, `/lang`) with usage and short description.
  * All field names and descriptions are pulled from the active language’s textmap.
  * Footer shows the bot’s version.

> **Note**: Future commands for events, gacha, and songs can be added using the same pattern. Each new command should read from the appropriate textmap section.

---

## Localization

### Language Settings Storage

* **File**: `language_settings.json`
* **Structure**:

  ```json
  {
    "guild": {
      "123456789012345678": "JPN",
      "234567890123456789": "CHS"
    },
    "user": {
      "111111111111111111": "CHS",
      "222222222222222222": "ENG"
    }
  }
  ```

  * `"guild"` maps guild IDs (strings) to their chosen language.
  * `"user"` maps user IDs (strings) to their chosen language (for DMs).

### Adding or Editing Textmaps

All translatable strings are kept in JSON files named `textmap_<LANG>.json` (e.g. `textmap_ENG.json`, `textmap_CHS.json`, `textmap_CHT.json`, `textmap_JPN.json`, `textmap_KOR.json`).

Each textmap has these top-level sections:

* **`card`**
  * `USAGE`
  * `EMBED_TITLE`
  * `FIELD_TITLE`
  * `FIELD_CHARACTER`
  * `NOT_FOUND`
  * `ERROR`

* **`character`**
  * `USAGE`
  * `EMBED_TITLE`
  * `FIELD_BAND`
  * `NOT_FOUND`
  * `ERROR`

* **`help`**
  * `EMBED_TITLE`
  * `EMBED_DESCRIPTION`
  * `CARD_FIELD_NAME`
  * `CARD_FIELD_DESC`
  * `CHAR_FIELD_NAME`
  * `CHAR_FIELD_DESC`
  * `EVENT_FIELD_NAME`
  * `EVENT_FIELD_DESC`
  * `GACHA_FIELD_NAME`
  * `GACHA_FIELD_DESC`
  * `SONG_FIELD_NAME`
  * `SONG_FIELD_DESC`
  * `HELP_FIELD_NAME`
  * `HELP_FIELD_DESC`
  * `LANG_FIELD_NAME`
  * `LANG_FIELD_DESC`
  * `FOOTER`

* **`lang`**
  * `NO_ADMIN`
  * `CONFIRM_GUILD`
  * `CONFIRM_USER`
  * `UNKNOWN_ERROR`

Whenever you add a new command that sends text, add the relevant section/key into each `textmap_<LANG>.json`. The bot loads only the chosen language’s file on demand (falling back to English if missing).

The textmap can be hot fixed, i.e. whenever the text is edited, it will reflect immediately without needing to restart the bot.

---

## Project Structure

```
/Bestdori-Discord-Bot
├─ bot.py                    # Bot activator + raw Chinese alias handler + slash sync
├─ lang_settings.py          # Reads/writes language_settings.json for guild/user preferences
├─ localisation.py           # get_text(lang, section, key) helper for loading textmaps
├─ language_settings.json    # (auto-generated) stores per-guild and per-user language codes
├─ textmap_ENG.json          # English translations (this file)
├─ textmap_CHS.json          # Simplified Chinese translations
├─ textmap_CHT.json          # Traditional Chinese translations
├─ textmap_JPN.json          # Japanese translations
├─ textmap_KOR.json          # Korean translations
└─ commands/                 # Cog folder
   ├─ __init__.py
   ├─ lang.py                # Slash command /lang for setting language
   ├─ card.py                # ^card command (single‐language title + images)
   ├─ character.py           # ^char command (single‐language name + icon)
   ├─ help.py                # ^help command (lists available commands)
   └─ (future: event.py, gacha.py, song.py, etc.)
```

---

## Dependencies

* **Python 3.10+**
* **discord.py 2.x** (`pip install discord.py`)
* **bestdori-api** (`pip install bestdori-api`)
* **typing-extensions** (`pip install typing-extensions`)

Your `requirements.txt` might look like:

```
discord.py>=2.0.0
bestdori-api>=0.1.0
typing-extensions>=4.0.0
```

---

## Contributing

1. **Fork** this repository.
2. **Create a new branch** (`git checkout -b feature/my-new-feature`).
3. **Make your changes** (add new commands, improve localization, fix bugs).
4. **Update textmaps** for all supported languages if you add new user‐facing text.
5. **Submit a Pull Request**.

Please ensure that any new text keys are added to every `textmap_<LANG>.json` to maintain complete localization.

---

## License

This project is licensed under the [MIT License](LICENSE).
