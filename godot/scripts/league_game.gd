extends RefCounted
const Course = preload("res://scripts/course_data.gd")
const DURATION = 42.0
const KEYS = ["vision", "mechanics", "positioning", "macro", "mastery"]
var store
var content: Dictionary
var notice = ""
func _init(save_system) -> void:
	store = save_system
	content = Course.all()["league"]
	for field in ["god", "strategy", "relic"]:
		var options = content[{"god": "gods", "strategy": "strategies", "relic": "relics"}[field]]
		if not options.has(state()[field]): state()[field] = options.keys()[0]
func state() -> Dictionary: return store.data["league"]
func rank_name() -> String:
	if state()["matches"] < 3: return "Unranked"
	var rank = "Madera 3"
	for item in content["ranks"]:
		if state()["rating"] >= item[1]: rank = item[0]
	return rank
func level(key: String) -> int:
	return int(state()["mastery"].get(state()["god"], 0)) if key == "mastery" else int(state()["upgrades"].get(key, 0))
func cost(key: String) -> int:
	return 100 + level(key) * 60 + int(float(state()["rating"]) / 250) * 15
func commit(previous: Dictionary) -> bool:
	if store.save(): return true
	store.data = previous
	notice = store.notice
	return false
func buy(key: String) -> bool:
	if key not in KEYS: notice = "Ese aumento no existe"; return false
	if state()["battle"] != null: notice = "Espera a que termine la partida para comprar aumentos"; return false
	if level(key) >= 10: notice = "Este aumento ya llegó a nivel 10"; return false
	if state()["xp"] < cost(key): notice = "Necesitas %s XP para este aumento" % cost(key); return false
	var previous = store.data.duplicate(true)
	var next = level(key) + 1
	state()["xp"] -= cost(key)
	if key == "mastery": state()["mastery"][state()["god"]] = next
	else: state()["upgrades"][key] = next
	notice = content["upgrades"][key][1] + ", nivel %s/10" % next
	return commit(previous)
func choose(key: String, value: String) -> bool:
	if key not in ["god", "strategy", "relic"] or state()["battle"] != null: return false
	if not content[{"god": "gods", "strategy": "strategies", "relic": "relics"}[key]].has(value): return false
	var previous = store.data.duplicate(true)
	state()[key] = value
	return commit(previous)
func scout() -> Dictionary:
	return content["scouts"][int(state()["matches"]) % content["scouts"].size()].duplicate(true)
func preparation() -> Dictionary:
	var god = state()["god"]
	var strategy = state()["strategy"]
	var relic = state()["relic"]
	var foe = scout()
	var profile = content["profiles"][god]
	var effective = []
	var strength = 0.0
	for index in range(KEYS.size()):
		var power = clampi(level(KEYS[index]) + int(content["relics"][relic][2][index]), 0, 12)
		effective.append(power)
		strength += power * float(content["strategy_info"][strategy][1][index]) * float(profile["weights"][index])
	var synergy = content["gods"][god][2] == strategy
	var relic_match = profile["relic"] == relic
	var counter = strategy in foe["counters"]
	var focus = effective[KEYS.find(foe["weak"])]
	var chance = clampf(0.20 + strength * 0.010 + (0.05 if synergy else 0.0) + (0.025 if relic_match else 0.0) + (0.055 if counter else -0.015) + focus * 0.004 - float(state()["rating"]) / 10000, 0.12, 0.85)
	return {"chance": snappedf(chance, 0.0001), "synergy": synergy, "relic_match": relic_match, "counter": counter, "enemy": foe, "effective": effective}
static func rate(result: Dictionary) -> void:
	var k = int(result["kills"])
	var d = int(result["deaths"])
	var a = int(result["assists"])
	var mvp = result["win"] and ((k >= 10 and d <= 5) or (k + a >= 18 and d <= 4) or (k >= 6 and d == 0))
	var delta = clampi(roundi(22 + k * 1.5 + a * 0.7 - d), 13, 42) + (3 if mvp else 0) if result["win"] else clampi(roundi(-18 - clampf(-(k * 0.8 + a * 0.4 - d * 0.8), -10, 10)), -26, -8)
	result.merge({"rating_delta": delta, "mvp": mvp}, true)
static func chronicle(events: Array) -> void:
	events.sort_custom(func(a, b): return float(a["time"]) < float(b["time"]))
	var first = true
	for event in events:
		event["text"] = event["text"].trim_prefix("¡Primera sangre! ")
		if first and int(event.get("k", 0)) + int(event.get("d", 0)) + int(event.get("a", 0)) > 0:
			if event["type"] == "kill" and event["k"] == 1: event["text"] = "¡Primera sangre! " + event["text"]
			first = false
static func shuffle(items: Array, rng: RandomNumberGenerator) -> void:
	for index in range(items.size() - 1, 0, -1):
		var other = rng.randi_range(0, index)
		var item = items[index]
		items[index] = items[other]
		items[other] = item
func simulate(seed_value: int, duration: float = DURATION) -> Dictionary:
	var rng = RandomNumberGenerator.new()
	rng.seed = seed_value
	var prep = preparation()
	var v = level("vision")
	var m = level("mechanics")
	var p = level("positioning")
	var o = level("macro")
	var z = level("mastery")
	var god = state()["god"]
	var roll = rng.randf()
	var win = roll < prep["chance"]
	var support = god in ["selka", "varda", "bront"]
	var stats = content["profiles"][god]["stats"]
	var k = maxi(1, roundi(2 + m * 0.55 + z * 0.5 + rng.randf_range(-1, 3) + (2 if win else 0) - int(support) + (float(stats[0]) - 7) * 0.2))
	var d = maxi(0, roundi(10 - p * 0.55 - v * 0.35 + rng.randf_range(-2, 2) - (2 if win else 0) - (float(stats[1]) - 5) * 0.2))
	var a = maxi(1, roundi(2 + o * 0.5 + v * 0.35 + rng.randf_range(0, 3) + (3 if state()["strategy"] == "team" else 0) + int(support) * 2 + (float(stats[2]) - 6) * 0.2))
	var result = {"win": win, "kills": k, "deaths": d, "assists": a, "god": god, "strategy": state()["strategy"], "relic": state()["relic"], "win_chance": prep["chance"], "outcome_roll": roll, "bonus": 0.0, "enemy": prep["enemy"], "events": [], "precision": []}
	rate(result)
	var actions = []
	var burst = mini(4, k) if k >= 2 and rng.randf() < minf(0.72, 0.08 + (m + z) * 0.03) else 0
	for i in range(k - burst): actions.append({"type": "kill", "k": 1, "d": 0, "a": 0})
	for i in range(d): actions.append({"type": "death", "k": 0, "d": 1, "a": 0})
	while a > 0:
		var count = mini(a, 2)
		actions.append({"type": "assist", "k": 0, "d": 0, "a": count})
		a -= count
	shuffle(actions, rng)
	var locations = [[0.34, 0.35], [0.53, 0.53], [0.70, 0.72], [0.28, 0.70], [0.74, 0.27]]
	for index in range(actions.size()):
		var event = actions[index]
		event.merge({"time": snappedf(duration * (0.07 + 0.61 * (index + 0.5) / maxf(1, actions.size())), 0.0001), "pos": locations[index % locations.size()], "lane": ["superior", "central", "inferior"][index % 3]})
		if event["type"] == "death":
			var reasons = ["Cruzas sin visión y te cazan en el carril " + event["lane"], "Un rival esperaba en la maleza, faltó un centinela", "Pierdes de vista al jungla y llega por tu espalda"] if v < 3 else ["Entras antes que el equipo y concentran el daño", "Gastaste tu salida muy pronto y el rival te alcanza", "Te alejas de la línea aliada y cierran la retirada"] if p < 3 else ["Tres rivales conectan sus habilidades y caes", "El rival te enfoca en el intercambio del río", "Tu equipo se retira, pero no alcanzas la salida"]
			event["text"] = reasons[rng.randi_range(0, reasons.size() - 1)]
		elif event["type"] == "kill":
			var words = ["Aíslas a un rival en el carril " + event["lane"], content["profiles"][god]["skill"] + " conecta y aseguras una baja", "Castigas la retirada del rival en el carril " + event["lane"]]
			event["text"] = words[rng.randi_range(0, words.size() - 1)]
		else:
			var words = ["Tu control abre la entrada del equipo", "El grupo aprovecha tu cobertura", "Cierras la ruta de escape del rival", "Conectas la habilidad y el equipo remata", "Tu presión facilita el intercambio"]
			event["text"] = words[rng.randi_range(0, words.size() - 1)] + ", +%s %s" % [event["a"], "asistencias" if event["a"] > 1 else "asistencia"]
		result["events"].append(event)
	if burst > 0:
		result["events"].append({"time": duration * 0.735, "type": "kill", "k": burst, "d": 0, "a": 0, "pos": [0.66, 0.48], "lane": "central", "combo": burst, "text": {2: "¡Doble! Dos rivales caen en la pelea del río", 3: "¡Triple! Tres rivales caen en la pelea del río", 4: "¡Cuadra! Cuatro rivales caen en la pelea del río"}[burst]})
	for index in range(1 + int(float(o) / 4)):
		var objective = "torre" if index % 2 == 0 else "Guardián"
		result["events"].append({"time": duration * (0.35 + index * 0.24), "type": "objective", "k": 0, "d": 0, "a": 0, "pos": [0.69, 0.54], "objective": objective, "text": "La presión abre espacio, tu equipo asegura " + ("una torre" if objective == "torre" else "al Guardián")})
	result["events"].append({"time": 0.1, "type": "info", "k": 0, "d": 0, "a": 0, "pos": [0.12, 0.84], "text": "Se abren los carriles, tu equipo sale de la base"})
	chronicle(result["events"])
	return result
func start_battle(seed_value: int = -1, duration: float = DURATION) -> bool:
	if state()["battle"] != null or not is_finite(duration) or duration < 12: return false
	if seed_value < 0: seed_value = randi_range(0, 2147483647)
	var previous = store.data.duplicate(true)
	var rng = RandomNumberGenerator.new()
	rng.seed = seed_value + 8041
	var kinds = ["vision", "positioning", "macro", "mastery"]
	shuffle(kinds, rng)
	kinds = kinds.slice(0, 1 + seed_value % 2)
	kinds.append("mechanics")
	var fractions = [0.30, 0.76] if kinds.size() == 2 else [0.23, 0.48, 0.76]
	var windows = []
	for index in range(kinds.size()):
		var kind = kinds[index]
		var jitter = rng.randf_range(-0.012, 0.012) if kind == "mechanics" else rng.randf_range(-0.025, 0.025)
		var point = [0.66, 0.48] if kind == "mechanics" else [rng.randf_range(0.22, 0.76), rng.randf_range(0.27, 0.72)]
		windows.append({"id": index, "kind": kind, "at": duration * (fractions[index] + jitter), "windup": 0.85, "window": snappedf(0.30 + level(kind) * 0.10, 0.01), "radius": 9 + level(kind) * 1.4, "pos": point, "status": "pending"})
	state()["battle"] = {"version": 2, "seed": seed_value, "elapsed": 0.0, "duration": duration, "result": simulate(seed_value, duration), "windows": windows}
	return commit(previous)
func current_cue() -> Dictionary:
	var battle = state()["battle"]
	if battle == null: return {}
	for window in battle.get("windows", []):
		if window["status"] == "pending" and window["at"] <= battle["elapsed"] and battle["elapsed"] <= window["at"] + window["windup"] + window["window"]:
			return window
	return {}
func live_score() -> Array:
	var score = [0, 0, 0]
	if state()["battle"] == null: return score
	for event in state()["battle"]["result"]["events"]:
		if event["time"] <= state()["battle"]["elapsed"]:
			for index in range(3): score[index] += int(event.get(["k", "d", "a"][index], 0))
	return score
func attempt_timing(point: Variant = null) -> Dictionary:
	var battle = state()["battle"]
	var cue = current_cue()
	if battle == null or cue.is_empty(): return {}
	var previous_state = store.data.duplicate(true)
	var progress = (float(battle["elapsed"]) - float(cue["at"]) - float(cue["windup"])) / float(cue["window"])
	var inside = point == null or ((Vector2(point) - Vector2(cue["pos"][0], cue["pos"][1])) * Vector2(304, 154)).length() <= cue["radius"]
	var success = inside and progress >= 0.15 and progress <= 0.92
	var perfect = success and progress >= 0.38 and progress <= 0.69
	cue["status"] = "perfect" if perfect else "hit" if success else "miss"
	var result: Dictionary = battle["result"]
	var kind = cue["kind"]
	var text = ""
	if not success:
		text = "La ventana se cerró antes de conectar" if progress > 0.92 else "Te anticipaste al anillo" if progress < 0.15 else "El golpe quedó fuera del círculo"
	elif kind in ["mechanics", "mastery"]:
		result["kills"] += 1
		var previous = 0
		for event in result["events"]:
			if kind == "mechanics" and event.get("combo", 0) > 1 and battle["elapsed"] - event["time"] >= 0 and battle["elapsed"] - event["time"] <= 4:
				previous = int(event["combo"])
		var combo = previous + 1 if previous > 0 else 1
		text = {3: "¡Triple! Alcanzas a otro rival con el último combo", 4: "¡Cuadra! Conectas el remate antes de la retirada", 5: "¡Penta! Alcanzas al quinto rival con el último combo"}.get(combo, "¡Remate preciso! Conectas la habilidad y sumas una baja")
		result["events"].append({"time": battle["elapsed"], "type": "kill", "k": 1, "d": 0, "a": 0, "pos": cue["pos"], "text": text, "combo": combo})
	elif kind == "positioning":
		var future = {}
		for event in result["events"]:
			if event["type"] == "death" and event["time"] > battle["elapsed"]:
				future = event
				break
		if not future.is_empty():
			future.merge({"type": "dodge", "d": 0, "text": "La ruta de retirada te salva de la siguiente emboscada"}, true)
			result["deaths"] -= 1
			text = "¡Esquiva precisa! Preparaste una retirada segura"
		else:
			result["assists"] += 1
			result["events"].append({"time": battle["elapsed"], "type": "assist", "k": 0, "d": 0, "a": 1, "pos": cue["pos"], "text": "Reposicionas al equipo y habilitas una baja"})
			text = "¡Buena posición! Tu equipo aprovecha el espacio"
	else:
		result["assists"] += int(kind == "vision")
		text = "¡Lo viste venir! Marcas al rival y tu equipo lo intercepta" if kind == "vision" else "¡Objetivo asegurado! El Guardián cae de tu lado"
		result["events"].append({"time": battle["elapsed"], "type": "assist" if kind == "vision" else "objective", "k": 0, "d": 0, "a": int(kind == "vision"), "pos": cue["pos"], "text": text, "objective": "Guardián" if kind == "macro" else ""})
	if success: result["bonus"] += 0.065 if perfect else 0.04
	result["precision"].append({"kind": kind, "status": cue["status"], "text": text, "time": battle["elapsed"]})
	chronicle(result["events"])
	if not commit(previous_state): return {"success": false, "perfect": false, "text": notice}
	return {"success": success, "perfect": perfect, "text": text}
func update(delta: float, interactive: bool = false) -> bool:
	var battle = state()["battle"]
	if battle == null or not is_finite(delta) or delta < 0: return false
	battle["elapsed"] = minf(battle["duration"], battle["elapsed"] + delta)
	for cue in battle.get("windows", []):
		if cue["status"] == "pending" and battle["elapsed"] > cue["at"] + cue["windup"] + cue["window"]:
			cue["status"] = "miss" if interactive else "skipped"
			battle["result"]["precision"].append({"kind": cue["kind"], "status": cue["status"], "text": "Oportunidad no aprovechada" if interactive else "La simulación siguió en segundo plano", "time": cue["at"] + cue["windup"] + cue["window"]})
	if battle["elapsed"] < battle["duration"]: return false
	var previous = store.data.duplicate(true)
	var result: Dictionary = battle["result"]
	if battle.get("version", 1) == 2:
		result["win_chance"] = minf(0.95, result["win_chance"] + result["bonus"])
		result["win"] = result["outcome_roll"] < result["win_chance"]
		rate(result)
	var before = rank_name()
	state()["matches"] += 1
	state()["wins"] += int(result["win"])
	state()["rating"] = maxi(0, state()["rating"] + result.get("rating_delta", 25 if result["win"] else -12))
	state()["last_match"] = result.duplicate(true)
	state()["last_match"].merge({"rank_before": before, "rank_after": rank_name()})
	state()["battle"] = null
	return commit(previous)
