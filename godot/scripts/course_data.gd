extends RefCounted

static var content: Dictionary = {}

static func all() -> Dictionary:
	if content.is_empty():
		var file = FileAccess.get_file_as_string("res://data/course.json")
		var parser = JSON.new()
		if parser.parse(file) == OK and parser.data is Dictionary:
			content = parser.data
	return content

static func key(year: int, day: int) -> String:
	return "%s_%s" % [year, day]

static func tasks(year: int, day: int) -> Array:
	return all().get("tasks", {}).get(key(year, day), [])

static func lesson(year: int, day: int) -> Array:
	return all().get("boards", {}).get(key(year, day), [])

static func task(id: String) -> Dictionary:
	var parts = id.split("_")
	if parts.size() != 3 or not parts[0].is_valid_int() or not parts[1].is_valid_int() or not parts[2].is_valid_int():
		return {}
	var list = tasks(int(parts[0]), int(parts[1]))
	return list[int(parts[2])] if int(parts[2]) >= 0 and int(parts[2]) < list.size() else {}

static func quiz(day: int) -> Array:
	return all().get("quiz", {}).get(str(day), [])

static func exams(year: int) -> Array:
	return all().get("exams", {}).get(str(year), [])

static func appearance() -> Dictionary:
	return all().get("appearance", {})

static func peer_profile(id: String) -> Dictionary:
	for peer in all().get("peers", []):
		if peer["id"] == id or peer["name"] == id:
			return {"skin": 0, "hair": 0, "shirt": 0, "skin_rgb": peer["skin"], "hair_rgb": peer["hair"],
				"shirt_rgb": peer["shirt"], "eyes_rgb": peer["eyes"], "pants_rgb": peer["pants"], "shoes_rgb": peer["shoes"],
				"hair_style": peer["hair_style"], "clothing_style": 1 if peer["id"] == "moshi" else 0, "show_backpack": false}
	return {"skin": 0, "hair": 0, "shirt": 0}

static func color(option: String, index: int, fallback: Color = Color.WHITE) -> Color:
	var choices: Array = appearance().get(option, [])
	if choices.is_empty():
		return fallback
	var rgb: Array = choices[clampi(index, 0, choices.size() - 1)][1]
	return Color(float(rgb[0]) / 255, float(rgb[1]) / 255, float(rgb[2]) / 255)
