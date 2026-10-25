import json
import os
from copy import deepcopy
import tempfile
from game.appearance import CUSTOM_FIELDS
from game.data_model import DEFAULT_FOUNDATION

SAVE_DIR = os.path.expanduser("~/.config/sql-quest")
SAVE_FILE = os.path.join(SAVE_DIR, "savegame.json")

DEFAULT_SAVE = {
    "has_save": False,
    "player_name": "Novato",
    "gender": "male",          # "male", "female", "neutral"
    "pronoun_welcome": "Bienvenido",
    "title_role": "Alumno",
    "skin_tone": 0,            # 0: claro, 1: trigueño, 2: moreno, 3: oscuro
    "hair_color": 0,           # 0: castaño, 1: negro, 2: rubio, 3: pelirojo, 4: cyan
    "hair_style": 0,           # 0: corto, 1: largo/coleta, 2: moderno
    "shirt_color": 0,          # 0: azul, 1: rojo, 2: verde, 3: negro, 4: purpura
    "eye_color": 0,
    "pants_color": 0,
    "shoe_color": 0,
    "clothing_style": 0,
    "shoe_style": 0,
    "backpack_color": 0,
    "current_year": 1,         # 1 a 4
    "current_day": 1,          # 1 a 5
    "year_attempts": {
        "1": 1,
        "2": 1,
        "3": 1,
        "4": 1
    },
    "passed_notes": [],        # Lista de IDs de notas desbloqueadas en el cuaderno
    "last_grade": None,
    "is_graduated": False
}

DEFAULT_SAVE["foundation"] = deepcopy(DEFAULT_FOUNDATION)

class SaveSystem:
    def __init__(self):
        self.data = deepcopy(DEFAULT_SAVE)
        self.load()

    def exists(self):
        return os.path.exists(SAVE_FILE) and self.data.get("has_save", False)

    def load(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
                    if "foundation" not in saved:
                        # Las partidas anteriores conservan su lugar en la carrera.
                        self.data["foundation"]["completed"] = True
        except Exception as e:
            print(f"[SaveSystem] Error cargando partida: {e}")

    def save(self):
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            self.data["has_save"] = True
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=SAVE_DIR,
                                             delete=False) as f:
                temp_path = f.name
                json.dump(self.data, f, indent=4)
            os.replace(temp_path, SAVE_FILE)
            print("[SaveSystem] ¡Partida autoguardada con éxito!")
        except Exception as e:
            print(f"[SaveSystem] Error guardando partida: {e}")
        finally:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

    def reset_new_game(self, name, gender, skin_tone, hair_color, hair_style, shirt_color, **appearance):
        pronoun = "Bienvenido" if gender == "male" else ("Bienvenida" if gender == "female" else "Bienvenide")
        role = "Alumno" if gender == "male" else ("Alumna" if gender == "female" else "Estudiante")

        self.data = deepcopy(DEFAULT_SAVE)
        self.data.update({
            "has_save": True,
            "player_name": name,
            "gender": gender,
            "pronoun_welcome": pronoun,
            "title_role": role,
            "skin_tone": skin_tone,
            "hair_color": hair_color,
            "hair_style": hair_style,
            "shirt_color": shirt_color,
            "current_year": 1,
            "current_day": 1,
            "year_attempts": {"1": 1, "2": 1, "3": 1, "4": 1},
            "passed_notes": ["nota_bienvenida"],
            "last_grade": None,
            "is_graduated": False
        })
        self.data.update({key: appearance[key] for key in CUSTOM_FIELDS if key in appearance})
        self.save()

    def unlock_note(self, note_id):
        if note_id not in self.data["passed_notes"]:
            self.data["passed_notes"].append(note_id)
            self.save()

    def award_league_xp(self, amount, source):
        from game.league import award_xp
        return award_xp(self, amount, source)
