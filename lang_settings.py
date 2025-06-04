import json
import os

FILE_PATH = os.path.join(os.path.dirname(__file__), "language_settings.json")

if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r", encoding="utf8") as f:
        language_settings = json.load(f)
else:
    language_settings = {"guild": {}, "user": {}}
    with open(FILE_PATH, "w", encoding="utf8") as f:
        json.dump(language_settings, f, indent=4, ensure_ascii=False)

def save_language_settings():
    with open(FILE_PATH, "w", encoding="utf8") as f:
        json.dump(language_settings, f, indent=4, ensure_ascii=False)
