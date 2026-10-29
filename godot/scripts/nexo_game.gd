extends RefCounted
const Course = preload("res://scripts/course_data.gd")
var store
var content: Dictionary
var notice = ""
func _init(save_system) -> void:
	store = save_system
	content = JSON.parse_string(FileAccess.get_file_as_string("res://data/nexo.json"))
func state() -> Dictionary: return store.data["nexo"]
func post(id: String) -> Dictionary:
	for item in content["posts"]:
		if item["id"] == id: return item
	return {}
func available(item: Dictionary) -> bool:
	return item["lesson"] in store.data["campaign"]["lectures"]
func preview(id: String, choice: int) -> Dictionary:
	var item = post(id)
	if item.is_empty() or not available(item) or choice < 0 or choice >= item["options"].size(): return {}
	var option = item["options"][choice]
	return {"score": option[1], "feedback": option[2], "choice": choice}
func publish(id: String, choice: int) -> bool:
	if state()["responses"].has(id): notice = "Tu respuesta ya está publicada, puedes seguir revisando las otras opciones sin volver a ganar recompensas"; return false
	var response = preview(id, choice)
	if response.is_empty(): notice = "Primero revisa la clase relacionada y elige una respuesta"; return false
	var previous = store.data.duplicate(true)
	var item = post(id)
	var year = clampi(int(store.data["campaign"]["year"]), 1, 4)
	var likes = [10, 80, 135, 280][year - 1] + int(response["score"]) * 3 + absi(id.hash()) % 9 if response["score"] > 0 else 0
	response.merge({"likes": likes, "author": item["author"], "year": year, "text": item["options"][choice][0]})
	state()["responses"][id] = response
	store.data["reputation"] = maxi(0, int(store.data["reputation"]) + int(response["score"]))
	store.data["likes"] += likes
	state()["reputation_sources"]["post:" + id] = response["score"]
	if item["author"] not in state()["contacts"]: state()["contacts"].append(item["author"])
	var friendship = int(store.data["relationships"].get(item["author"], 0))
	store.data["relationships"][item["author"]] = maxi(0, friendship + (2 if response["score"] > 0 else -1))
	if response["score"] >= 2:
		store.award_xp(100, "nexo:" + id)
		store.reward_money(2, "nexo:" + id)
	recommend_help()
	notice = "Respuesta publicada, revisa la explicación para entender qué aporta tu solución"
	if not store.save():
		store.data = previous
		notice = store.notice
		return false
	return true

func case_available(item: Dictionary) -> bool:
	if item.has("evidence") and not store.data["activities"]["investigations"].get(item["evidence"], {}).get("diagnosed", false): return false
	return available(item) and (item.get("previous", "").is_empty() or state()["completed_cases"].has(item["previous"]))
func complete_case(id: String, query: String) -> bool:
	var item = preload("res://scripts/nexo_sql.gd").case_data(id)
	if item.is_empty() or not case_available(item) or state()["completed_cases"].has(id):
		notice = "Este encargo todavía no está disponible o ya fue entregado"
		return false
	var previous = store.data.duplicate(true)
	state()["completed_cases"][id] = {"query": query, "project": item["project"], "stage": item["stage"], "author": item["author"]}
	store.data["reputation"] += int(item["reputation"])
	state()["reputation_sources"]["case:" + id] = item["reputation"]
	store.award_xp(int(item["xp"]), "case:" + id)
	store.reward_money(int(item["money"]), "case:" + id)
	store.data["relationships"][item["author"]] = int(store.data["relationships"].get(item["author"], 0)) + 3
	if item["author"] not in state()["contacts"]: state()["contacts"].append(item["author"])
	if int(item["stage"]) == 4 or item.get("recommendation", false):
		state()["recommendations"].append({"id": item["project"], "author": item["author"], "text": item.get("recommendation_text", "Me ayudó a construir y comprobar el proyecto durante la carrera, explica sus decisiones y revisa los datos antes de entregar")})
	recommend_help()
	notice = "Encargo entregado, tu proyecto avanzó y la ayuda quedó registrada"
	if not store.save():
		store.data = previous
		notice = store.notice
		return false
	return true

func recommend_help() -> void:
	var count = state()["completed_cases"].size()
	for response in state()["responses"].values():
		if response.get("score", 0) >= 2: count += 1
	if count < 10: return
	for record in state()["recommendations"]:
		if record["id"] == "marco_10_ayudas": return
	state()["recommendations"].append({"id": "marco_10_ayudas", "author": "marco", "text": "Ha ayudado a sus compañeros en diez ocasiones, comprueba sus resultados y comparte lo que aprende, recomiendo su disposición para colaborar"})
	store.data["reputation"] += 5
	state()["reputation_sources"]["recommendation:marco"] = 5
