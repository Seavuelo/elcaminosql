"""Reglas de Liga de Dioses, independientes de la interfaz y sin conexión"""
import random

RANKS = [("Madera", 0), ("Fierro", 120), ("Platilla", 300), ("Dorado", 600),
         ("Platino", 1000), ("Rubí", 1500), ("Prime", 2200), ("GOD", 3100)]
GODS = {
    "astra": ("Astra", "Maga", "team", (115, 145, 245)),
    "bront": ("Bront", "Tanque", "safe", (100, 190, 145)),
    "nix": ("Nix", "Asesina", "pressure", (210, 125, 190)),
}
STRATEGIES = {"safe": "Seguro", "pressure": "Presión", "team": "En equipo"}
UPGRADES = {
    "vision": ("Visión", "Aprendiste a poner visión en la jungla"),
    "mechanics": ("Mecánicas", "Mejoras el farmeo y aciertas más habilidades"),
    "positioning": ("Posicionamiento", "Evitas entrar a peleas que ya estaban perdidas"),
    "macro": ("Objetivos", "Conviertes una ventaja en torres y objetivos"),
    "mastery": ("Maestría del dios", "Dominas las habilidades del dios elegido"),
}


def new_state():
    return {"xp": 0, "rewards": [], "rating": 0, "matches": 0, "wins": 0,
            "god": "astra", "strategy": "safe", "upgrades": {key: 0 for key in UPGRADES if key != "mastery"},
            "mastery": {key: 0 for key in GODS}, "battle": None, "last_match": None}


def award_xp(save, amount, source):
    state = save.data.setdefault("league", new_state())
    if amount <= 0 or source in state["rewards"]:
        return 0
    state["xp"] += amount
    state["rewards"].append(source)
    return amount


class LeagueGame:
    def __init__(self, save):
        self.save = save

    @property
    def state(self):
        return self.save.data.setdefault("league", new_state())

    @property
    def rank(self):
        if self.state["matches"] < 3:
            return "Unranked"
        return next(name for name, threshold in reversed(RANKS) if self.state["rating"] >= threshold)

    def level(self, key):
        if key == "mastery":
            return self.state["mastery"][self.state["god"]]
        return self.state["upgrades"][key]

    def cost(self, key):
        return 100 + self.level(key) * 60

    def buy(self, key):
        if self.state["battle"]:
            return False, "Espera a que termine la partida para comprar aumentos"
        level, cost = self.level(key), self.cost(key)
        if level >= 10:
            return False, "Este aumento ya llegó a nivel 10"
        if self.state["xp"] < cost:
            return False, f"Necesitas {cost} XP para este aumento"
        self.state["xp"] -= cost
        target = self.state["mastery"] if key == "mastery" else self.state["upgrades"]
        target[self.state["god"] if key == "mastery" else key] = level + 1
        self.save.save()
        return True, f"{UPGRADES[key][1]}, nivel {level + 1}/10"

    def choose_god(self, god):
        if god not in GODS or self.state["battle"]:
            return False
        self.state["god"] = god
        self.save.save()
        return True

    def choose_strategy(self, strategy):
        if strategy not in STRATEGIES or self.state["battle"]:
            return False
        self.state["strategy"] = strategy
        self.save.save()
        return True

    def simulate(self, seed):
        rng = random.Random(seed)
        vision, mechanics, positioning, macro, mastery = (self.level(key) for key in UPGRADES)
        strategy = self.state["strategy"]
        synergy = 0.05 if GODS[self.state["god"]][2] == strategy else 0
        weights = {"safe": (1.1, 0.7, 1.4, 0.8, 0.9),
                   "pressure": (0.9, 1.4, 0.8, 1.0, 1.1),
                   "team": (1.3, 0.8, 1.0, 1.4, 0.9)}[strategy]
        strength = sum(level * weight for level, weight in zip((vision, mechanics, positioning, macro, mastery), weights))
        opposition = self.state["rating"] / 9000
        chance = max(0.12, min(0.90, 0.20 + strength * 0.014 + synergy - opposition))
        win = rng.random() < chance
        kills = max(0, round(2 + mechanics * 0.55 + mastery * 0.5 + rng.uniform(-2, 3) + (2 if win else 0)))
        deaths = max(0, round(11 - positioning * 0.55 - vision * 0.35 + rng.uniform(-2, 3) - (2 if win else 0)))
        assists = max(0, round(2 + macro * 0.5 + vision * 0.35 + rng.uniform(0, 3) + (3 if strategy == "team" else 0)))
        return {"win": win, "kills": kills, "deaths": deaths, "assists": assists,
                "god": self.state["god"], "strategy": strategy, "win_chance": round(chance, 3)}

    def start_battle(self, seed=None):
        if self.state["battle"]:
            return False
        seed = random.randrange(2**31) if seed is None else seed
        self.state["battle"] = {"seed": seed, "elapsed": 0.0, "duration": 14.0,
                                "result": self.simulate(seed)}
        self.save.save()
        return True

    def update(self, dt):
        battle = self.state["battle"]
        if not battle:
            return False
        battle["elapsed"] = min(battle["duration"], battle["elapsed"] + max(0, dt))
        if battle["elapsed"] < battle["duration"]:
            return False
        result = battle["result"]
        before = self.rank
        self.state["matches"] += 1
        self.state["wins"] += int(result["win"])
        self.state["rating"] = max(0, self.state["rating"] + (45 if result["win"] else -12))
        self.state["last_match"] = {**result, "rank_before": before, "rank_after": self.rank}
        self.state["battle"] = None
        self.save.save()
        return True
