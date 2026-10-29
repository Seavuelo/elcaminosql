extends RefCounted

const Layout = preload("res://scripts/room_layout.gd")
const Course = preload("res://scripts/course_data.gd")
var directory = "user://"
var data: Dictionary
var notice = ""
var recovery_blocked = false

func parse_file(path: String) -> Variant:
	var parser = JSON.new()
	return restore_numbers(parser.data) if parser.parse(FileAccess.get_file_as_string(path)) == OK else null

static func restore_numbers(value: Variant) -> Variant:
	# JSON pierde la distinción entre enteros y decimales, los identificadores necesitan enteros estables
	if value is float and is_finite(value) and floor(value) == value and absf(value) < 9007199254740992:
		return int(value)
	if value is Dictionary:
		for key in value: value[key] = restore_numbers(value[key])
	elif value is Array:
		for index in range(value.size()): value[index] = restore_numbers(value[index])
	return value

func _init(test_directory: String = "") -> void:
	if not test_directory.is_empty():
		directory = test_directory
	data = {"schema": 1, "player_name": "Estudiante", "year": 1, "skin": 0, "hair": 0,
		"shirt": 0, "day": 1, "night": false, "items": Layout.initial(),
		"completed": [], "reputation": 0, "likes": 0, "imported": false}
	for suffix in ["", ".bak"]:
		var path = directory.path_join("study.json" + suffix)
		if not FileAccess.file_exists(path):
			continue
		var parsed = parse_file(path)
		if valid(parsed):
			data = parsed
			upgrade()
			if suffix == ".bak":
				notice = "Recuperamos el último respaldo de tu habitación"
			return
		# Un archivo dañado queda disponible para recuperar sus datos manualmente
		if DirAccess.copy_absolute(ProjectSettings.globalize_path(path), ProjectSettings.globalize_path(path + ".damaged")) != OK:
			recovery_blocked = true
		notice = "El guardado no se pudo leer, se conserva para revisión"
	upgrade()

func upgrade() -> void:
	var defaults = {
		"campaign": {"started": false, "phase": "intro", "year": 1, "day": 1, "location": "home",
			"lectures": [], "tasks": [], "sql_history": [], "quizzes": {}, "exams": {}, "grades": [],
			"attempts": {"1": 1, "2": 1, "3": 1, "4": 1}, "model": {"entities": [], "relations": []},
			"model_tested": "", "ready_to_leave": false, "prologue_read": false, "lecture_pages": {}, "seen_days": [],
			"legacy_base": false, "reset_year4": false, "drafts": {}, "departures": {}, "seen_missions": {}},
		"settings": {"music_volume": 0.18, "sfx_volume": 0.7, "narration_volume": 0.85, "narration_enabled": true,
			"screen_mode": "windowed", "resolution": [1280, 800], "creator_note_seen": false},
		"league": {"xp": 0, "rewards": [], "rating": 0, "matches": 0, "wins": 0, "god": "astra", "strategy": "safe", "relic": "lens",
			"upgrades": {"vision": 0, "mechanics": 0, "positioning": 0, "macro": 0}, "mastery": {}, "battle": null, "last_match": null},
		"nexo": {"contacts": [], "responses": {}, "completed_cases": {}, "messages_read": [], "posts": [], "recommendations": [], "reputation_sources": {}, "onboarded": false},
		"career": {"project": "", "defended": false, "choice": ""}, "activities": {"completed": [], "investigations": {}}, "relationships": {}, "money": 0, "income_sources": [], "personal_notes": "", "sandbox_history": [],
		"furniture_level": {"bed": 1, "desk": 0}, "legacy_progress_imported": false,
		"hair_style": 0, "eye_color": 0, "pants_color": 0, "shoe_color": 0, "clothing_style": 0, "shoe_style": 0, "backpack_color": 0,
	}
	for key in defaults:
		if not data.has(key):
			data[key] = defaults[key].duplicate(true) if defaults[key] is Dictionary or defaults[key] is Array else defaults[key]
		elif data[key] is Dictionary and defaults[key] is Dictionary:
			for field in defaults[key]:
				if not data[key].has(field):
					var value = defaults[key][field]
					data[key][field] = value.duplicate(true) if value is Dictionary or value is Array else value
	for god in Course.all().get("league", {}).get("gods", {}):
		if not data["league"]["mastery"].has(god):
			data["league"]["mastery"][god] = 0

func award_xp(amount: int, source: String) -> int:
	if amount <= 0 or source in data["league"]["rewards"]:
		return 0
	data["league"]["xp"] += amount
	data["league"]["rewards"].append(source)
	return amount

func reward_money(amount: int, source: String) -> int:
	if amount <= 0 or source in data["income_sources"]:
		return 0
	data["money"] += amount
	data["income_sources"].append(source)
	return amount

func new_run(profile: Dictionary) -> bool:
	var previous = data.duplicate(true)
	data = {"schema": 1, "player_name": "Estudiante", "year": 1, "skin": 0, "hair": 0, "shirt": 0,
		"day": 1, "night": false, "items": Layout.starter(), "completed": [], "reputation": 0, "likes": 0, "imported": true}
	upgrade()
	data["furniture_level"] = {"bed": 0, "desk": 0}
	data["settings"] = previous["settings"].duplicate(true)
	data.merge(profile, true)
	data["campaign"]["started"] = true
	data["legacy_progress_imported"] = true
	if not save():
		data = previous
		return false
	return true

func valid(value: Variant) -> bool:
	if not value is Dictionary or value.get("schema") != 1:
		return false
	if not value.get("player_name") is String or value["player_name"].length() > 40:
		return false
	if not value.get("completed") is Array or not value.get("night") is bool or not value.get("imported") is bool:
		return false
	for key in ["year", "skin", "hair", "shirt", "day", "reputation", "likes"]:
		var number = value.get(key)
		if not (number is float or number is int) or not is_finite(float(number)) or number < 0 or number > 100000:
			return false
	return Layout.valid(value.get("items")) and valid_extras(value)

static func number(value: Variant, minimum: float, maximum: float) -> bool:
	return (value is float or value is int) and is_finite(float(value)) and float(value) >= minimum and float(value) <= maximum

func valid_extras(value: Dictionary) -> bool:
	for field in ["campaign", "settings", "league", "nexo", "relationships", "furniture_level", "activities", "career"]:
		if value.has(field) and not value[field] is Dictionary:
			return false
	for field in ["sandbox_history", "income_sources"]:
		if value.has(field) and (not value[field] is Array or value[field].size() > 20000):
			return false
	if value.has("personal_notes") and (not value["personal_notes"] is String or value["personal_notes"].length() > 1000000):
		return false
	if value.has("money") and not number(value["money"], 0, 1000000000):
		return false
	var settings: Dictionary = value.get("settings", {})
	for field in ["music_volume", "sfx_volume", "narration_volume"]:
		if settings.has(field) and not number(settings[field], 0, 1):
			return false
	if settings.has("narration_enabled") and not settings["narration_enabled"] is bool:
		return false
	if settings.has("screen_mode") and settings["screen_mode"] not in ["windowed", "borderless", "fullscreen"]:
		return false
	if settings.has("resolution"):
		var resolution = settings["resolution"]
		if not resolution is Array or resolution.size() != 2 or not number(resolution[0], 640, 7680) or not number(resolution[1], 480, 4320):
			return false
	var current: Dictionary = value.get("campaign", {})
	if current.has("phase") and current["phase"] not in ["intro", "career", "graduated"]:
		return false
	for field in ["year", "day"]:
		if current.has(field) and (not number(current[field], 1, 4 if field == "year" else 5) or int(current[field]) != current[field]):
			return false
	for field in ["lectures", "tasks", "sql_history", "grades", "seen_days"]:
		if current.has(field) and (not current[field] is Array or current[field].size() > 20000):
			return false
	for field in ["lectures", "tasks", "sql_history", "seen_days"]:
		for item in current.get(field, []):
			if not item is String or item.length() > 100:
				return false
	for field in ["quizzes", "exams", "attempts", "lecture_pages", "drafts", "departures", "seen_missions"]:
		if current.has(field) and not current[field] is Dictionary:
			return false
	for record in current.get("grades", []):
		if not record is Dictionary or not number(record.get("year"), 1, 4) or not number(record.get("attempt"), 1, 100000) or not number(record.get("grade"), 1, 7):
			return false
	for record in current.get("quizzes", {}).values():
		if not record is Dictionary or not record.get("answers", []) is Array or record.get("answers", []).size() > 10:
			return false
	for record in current.get("exams", {}).values():
		if not record is Dictionary or not record.get("answers", []) is Array or record.get("answers", []).size() > 5:
			return false
		for answer in record.get("answers", []):
			if not answer is Dictionary:
				return false
	if current.has("model"):
		var design = current["model"]
		if not design is Dictionary or not design.get("entities") is Array or not design.get("relations") is Array or design["entities"].size() > 200 or design["relations"].size() > 500:
			return false
		var logic = preload("res://scripts/model_logic.gd").new()
		for entity in design["entities"]:
			if not entity is Dictionary or not entity.get("name") is String or not entity.get("attributes") is Array or entity["attributes"].size() > 200:
				return false
			for attr in entity["attributes"]:
				if not attr is Dictionary or not attr.get("name") is String:
					return false
			for coordinate in ["x", "y"]:
				if entity.has(coordinate) and not number(entity[coordinate], -100000, 100000):
					return false
			if not logic.save_entity(entity):
				return false
		for relation in design["relations"]:
			if not relation is Dictionary or not relation.get("name") is String or not relation.get("id") is String or not logic.save_relation(relation):
				return false
	var league: Dictionary = value.get("league", {})
	for field in ["xp", "rating", "matches", "wins"]:
		if league.has(field) and not number(league[field], 0, 1000000000):
			return false
	for field in ["upgrades", "mastery"]:
		if league.has(field):
			if not league[field] is Dictionary:
				return false
			for level in league[field].values():
				if not number(level, 0, 10) or int(level) != level:
					return false
	if league.has("rewards") and not league["rewards"] is Array:
		return false
	var nexo: Dictionary = value.get("nexo", {})
	if nexo.has("onboarded") and not nexo["onboarded"] is bool: return false
	for field in ["contacts", "messages_read", "posts", "recommendations"]:
		if nexo.has(field) and not nexo[field] is Array:
			return false
	for field in ["responses", "reputation_sources", "completed_cases"]:
		if nexo.has(field) and not nexo[field] is Dictionary:
			return false
	var activities: Dictionary = value.get("activities", {})
	if activities.has("completed") and not activities["completed"] is Array:
		return false
	for id in activities.get("completed", []):
		if not id is String: return false
	if activities.has("investigations") and not activities["investigations"] is Dictionary:
		return false
	for record in activities.get("investigations", {}).values():
		if not record is Dictionary or not record.get("read") is Array or not record.get("diagnosed") is bool:
			return false
		for id in record["read"]:
			if not id is String: return false
	var career: Dictionary = value.get("career", {})
	for field in ["project", "choice"]:
		if career.has(field) and not career[field] is String: return false
	if career.has("defended") and not career["defended"] is bool: return false
	for level in value.get("furniture_level", {}).values():
		if not number(level, 0, 1) or int(level) != level: return false
	for relationship in value.get("relationships", {}).values():
		if not number(relationship, 0, 1000000): return false
	return true

func save() -> bool:
	if recovery_blocked:
		notice = "No se pudo respaldar el archivo dañado, se conserva sin reemplazarlo"
		return false
	if not valid(data):
		notice = "Hay datos de la partida que necesitan revisión"
		return false
	var path = ProjectSettings.globalize_path(directory.path_join("study.json"))
	if DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK:
		notice = "No se pudo crear la carpeta de guardado"
		return false
	var file = FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if file == null:
		notice = "No se pudo escribir el guardado"
		return false
	file.store_string(JSON.stringify(data, "\t"))
	file.flush()
	var write_error = file.get_error()
	file.close()
	if write_error != OK:
		notice = "No se pudo completar el guardado"
		return false
	if FileAccess.file_exists(path):
		var old = parse_file(path)
		if valid(old) and DirAccess.copy_absolute(path, path + ".bak") != OK:
			notice = "No se pudo conservar el respaldo anterior"
			return false
	if DirAccess.rename_absolute(path + ".tmp", path) != OK:
		notice = "No se pudo reemplazar el guardado anterior"
		return false
	notice = "Partida guardada"
	return true

func import_profile(path: String = "") -> bool:
	if data["imported"] and data["legacy_progress_imported"]:
		return false
	if path.is_empty():
		path = OS.get_environment("USERPROFILE").path_join(".config/sql-quest/savegame.json")
	if not FileAccess.file_exists(path):
		return false
	var old = parse_file(path)
	if not old is Dictionary or not old.get("player_name") is String:
		return false
	data["player_name"] = old["player_name"].strip_edges().left(40)
	for keys in [["current_year", "year", 1, 4], ["skin_tone", "skin", 0, 5], ["hair_color", "hair", 0, 8], ["shirt_color", "shirt", 0, 8]]:
		var value = old.get(keys[0], keys[2])
		if (value is float or value is int) and is_finite(float(value)):
			data[keys[1]] = clampi(int(value), keys[2], keys[3])
	data["imported"] = true
	if not data["campaign"]["started"] and old.get("has_save", false):
		import_legacy_progress(old)
		import_legacy_database(path.get_base_dir().path_join("universidad.db"))
		var config_path = path.get_base_dir().path_join("config.json")
		if FileAccess.file_exists(config_path):
			var settings = parse_file(config_path)
			if settings is Dictionary:
				for key in data["settings"]:
					if settings.has(key) and typeof(settings[key]) == typeof(data["settings"][key]):
						data["settings"][key] = settings[key]
	data["legacy_progress_imported"] = true
	return save()

func import_legacy_database(path: String) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var destination = ProjectSettings.globalize_path(directory.path_join("legacy-university.db"))
	if DirAccess.make_dir_recursive_absolute(destination.get_base_dir()) != OK:
		return false
	var source = ClassDB.instantiate("SQLite")
	source.path = path
	source.default_extension = ""
	source.read_only = true
	source.verbosity_level = 0
	if not source.open_db():
		return false
	var success: bool = source.backup_to(destination)
	source.close_db()
	if success:
		data["campaign"]["legacy_base"] = true
		data["campaign"]["sql_history"] = []
	return success

func import_legacy_progress(old: Dictionary) -> void:
	var current: Dictionary = data["campaign"]
	current["started"] = true
	current["year"] = clampi(int(old.get("current_year", 1)), 1, 4)
	var foundation: Dictionary = old.get("foundation", {"completed": true})
	current["phase"] = "career" if foundation.get("completed", true) else "intro"
	if old.get("is_graduated", false):
		current["phase"] = "graduated"
	current["day"] = clampi(int(foundation.get("day", 1)) if current["phase"] == "intro" else int(old.get("current_day", 1)), 1, 5)
	current["model"] = foundation.get("logical_model", {"entities": [], "relations": []}).duplicate(true)
	current["quizzes"] = foundation.get("kashut", {}).duplicate(true)
	for day_key in foundation.get("lectures", {}):
		if foundation["lectures"][day_key]:
			current["lectures"].append("0_" + str(day_key))
	for y in range(1, current["year"] + 1):
		for d in range(1, 6):
			var completed_day = y < current["year"] or (current["phase"] != "intro" and d < current["day"])
			var active = y == current["year"] and d == current["day"] and current["phase"] != "intro"
			if completed_day or (active and old.get("lecture_done_for_day", false)):
				current["lectures"].append(Course.key(y, d))
			var list = Course.tasks(y, d)
			var count = list.size() if completed_day or (active and old.get("day_task_completed", false)) else int(old.get("current_task_idx", 0)) if active else 0
			for index in range(mini(count, list.size())):
				var id = Course.key(y, d) + "_" + str(index)
				current["tasks"].append(id)
				if list[index]["is_write"]:
					current["sql_history"].append(id)
	if old.get("year_attempts") is Dictionary:
		current["attempts"].merge(old["year_attempts"], true)
	if current["day"] == 5 and old.get("exam_active", false):
		var answers = []
		for i in range(int(old.get("exam_q_index", 0))):
			answers.append({"correct": null, "recovered": true, "query": "", "feedback": "El guardado anterior conserva el puntaje total, no el resultado de cada pregunta"})
		current["exams"][str(current["year"]) + "_" + str(current["attempts"].get(str(current["year"]), 1))] = {
			"answers": answers, "finished": old.get("exam_finished", false), "grade": old.get("exam_final_grade", 1.0), "score": old.get("exam_score", 0)}
	if old.get("league") is Dictionary:
		data["league"].merge(old["league"], true)
	data["personal_notes"] = old.get("personal_notes", "")
	for key in ["hair_style", "eye_color", "pants_color", "shoe_color", "clothing_style", "shoe_style", "backpack_color"]:
		if old.get(key) is int or old.get(key) is float:
			data[key] = clampi(int(old[key]), 0, 20)
	upgrade()
