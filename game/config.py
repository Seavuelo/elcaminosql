import json
import os
import pygame

CONFIG_PATH = os.path.expanduser("~/.config/sql-quest/config.json")

DEFAULT_CONFIG = {
    "screen_mode": "windowed",  # "windowed", "fullscreen", "borderless"
    "resolution": [960, 600],   # [960, 600], [1280, 720], [1366, 768]
    "music_volume": 0.25,       # 0.0 a 1.0
    "sfx_volume": 0.70,         # 0.0 a 1.0
    "current_day": 1,           # 1 a 5
    "semester_attempts": 1,     # Cuántas veces ha cursado el ramo
}

class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config.update(data)
        except Exception as e:
            print(f"[ConfigManager] Error al cargar configuración: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"[ConfigManager] Error al guardar configuración: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()
