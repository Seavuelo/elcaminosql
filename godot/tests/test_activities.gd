extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Activities = preload("res://scripts/activities.gd")
const Nexo = preload("res://scripts/nexo_game.gd")
const SQL = preload("res://scripts/nexo_sql.gd")
var checks = 0
var failures = []
func check(value, message):
	checks += 1
	if not value: failures.append(message)
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-activities").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Investigar"})
	var game = Activities.new(store)
	check(not game.check_puzzle("filtro", [1,4]), "El desafío requiere su clase")
	for item in game.content["puzzles"]: store.data["campaign"]["lectures"].append(item["lesson"])
	for item in game.content["investigations"]: store.data["campaign"]["lectures"].append(item["lesson"])
	check(not game.check_puzzle("filtro", [1,2,4]), "El filtro excluye correctamente el límite")
	for item in game.content["puzzles"]:
		var answer = item["correct"].map(func(value): return int(value))
		check(game.check_puzzle(item["id"], answer), "Completar " + item["id"])
		var before = store.data.duplicate(true)
		check(game.check_puzzle(item["id"], answer) and before == store.data, "No repetir recompensas")
	var nexo = Nexo.new(store)
	for item in game.content["investigations"]:
		check(not nexo.case_available(SQL.case_data(item["case_id"])), "La corrección necesita diagnóstico")
		check(not game.diagnose(item["id"], int(item["answer"])), "El diagnóstico requiere los documentos")
		for doc in item["docs"]: check(game.read_document(item["id"], doc["id"]), "Documento guardado")
		check(not game.diagnose(item["id"], 0), "Una causa incorrecta no desbloquea el encargo")
		check(game.diagnose(item["id"], int(item["answer"])), "Diagnóstico correcto")
		check(nexo.case_available(SQL.case_data(item["case_id"])), "El diagnóstico abre la corrección")
		var task = SQL.case_data(item["case_id"])
		check(SQL.evaluate({"case_id": task["id"], "query": task["sql"]}).get("correct", false), "La solución funciona en tres conjuntos de datos")
	var restored = State.new(folder)
	check(restored.data["activities"] == store.data["activities"], "Lecturas, desafíos y diagnósticos se conservan")
	print(JSON.stringify({"module": "activities", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
