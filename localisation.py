import json
import os

loaded_textmaps = {}

def get_text(lang_code: str, section: str, key: str, **kwargs) -> str:

    if lang_code not in loaded_textmaps:
        path = os.path.join(os.path.dirname(__file__), f"textmap_{lang_code}.json")
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), "textmap_ENG.json")
        with open(path, "r", encoding="utf8") as f:
            loaded_textmaps[lang_code] = json.load(f)

    text = loaded_textmaps[lang_code].get(section, {}).get(key, "")
    for placeholder, value in kwargs.items():
        text = text.replace("{" + placeholder + "}", str(value))
    return text
