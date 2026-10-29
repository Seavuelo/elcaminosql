extends RefCounted
var store
var content: Dictionary
var notice = ""
func _init(save_system):
	store = save_system
	content = JSON.parse_string(FileAccess.get_file_as_string("res://data/activities.json"))
func item(id: String, section: String) -> Dictionary:
	for entry in content[section]:
		if entry["id"] == id: return entry
	return {}
func available(entry: Dictionary) -> bool:
	return entry.get("lesson", "") in store.data["campaign"]["lectures"]
func check_puzzle(id: String, answer: Array) -> bool:
	var entry = item(id, "puzzles")
	if entry.is_empty() or not available(entry): return false
	var expected = []
	for value in entry["correct"]: expected.append(int(value))
	var actual = answer.duplicate()
	if id == "filtro": actual.sort(); expected.sort()
	if actual != expected: notice = entry["explanation"]; return false
	if id in store.data["activities"]["completed"]:
		notice = "Correcto, ya completaste esta actividad, puedes practicar sin repetir recompensas"
		return true
	var previous = store.data.duplicate(true)
	store.data["activities"]["completed"].append(id)
	store.award_xp(100, "puzzle:" + id)
	store.reward_money(4, "puzzle:" + id)
	if not store.save(): store.data = previous; notice = store.notice; return false
	notice = "¡Completado! +100 XP para Liga y $4 para tu habitación\n\n" + entry["explanation"]
	return true
func record(id: String) -> Dictionary:
	return store.data["activities"]["investigations"].get(id, {"read": [], "diagnosed": false})
func read_document(id: String, document: String) -> bool:
	var entry = item(id, "investigations")
	if entry.is_empty() or not available(entry) or not entry["docs"].any(func(doc): return doc["id"] == document): return false
	var previous = store.data.duplicate(true)
	var state = record(id)
	if document not in state["read"]: state["read"].append(document)
	store.data["activities"]["investigations"][id] = state
	if not store.save(): store.data = previous; notice = store.notice; return false
	return true
func diagnose(id: String, choice: int) -> bool:
	var entry = item(id, "investigations")
	if entry.is_empty() or not available(entry) or record(id)["read"].size() != entry["docs"].size():
		notice = "Revisa los tres documentos antes de decidir qué ocurrió"
		return false
	if choice != int(entry["answer"]): notice = entry["feedback"]; return false
	var previous = store.data.duplicate(true)
	var state = record(id)
	state["diagnosed"] = true
	store.data["activities"]["investigations"][id] = state
	if not store.save(): store.data = previous; notice = store.notice; return false
	notice = entry["feedback"]
	return true
