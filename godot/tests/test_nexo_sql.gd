extends SceneTree
const SQL = preload("res://scripts/nexo_sql.gd")
const Nexo = preload("res://scripts/nexo_game.gd")
const State = preload("res://scripts/study_state.gd")
var failures = []
var checks = 0
func check(value: bool, message: String):
	checks += 1
	if not value: failures.append(message)
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-nexo-sql").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Proyectos de prueba"})
	var game = Nexo.new(store)
	check(not game.case_available(SQL.case_data("almacen_1")), "Los encargos requieren su clase")
	for item in game.content["cases"]: store.data["campaign"]["lectures"].append(item["lesson"])
	for evidence in ["reservas", "totales"]: store.data["activities"]["investigations"][evidence] = {"read": [], "diagnosed": true}
	check(not game.case_available(SQL.case_data("almacen_2")), "La siguiente etapa requiere la entrega anterior")
	for item in game.content["cases"]:
		var request = {"case_id": item["id"], "query": item["sql"]}
		var result = SQL.evaluate(request)
		check(result.get("ok", false) and result.get("correct", false) and result.get("passed") == 3, "Tres conjuntos de datos válidos: " + item["id"])
		check(game.complete_case(item["id"], item["sql"]), "Guardar etapa " + item["id"])
		var before = store.data.duplicate(true)
		check(not game.complete_case(item["id"], item["sql"]) and before == store.data, "Sin recompensas repetidas: " + item["id"])
		var inspect = SQL.evaluate({"case_id": item["id"], "action": "catalog"})
		check(inspect.get("ok", false) and not inspect["catalog"].is_empty(), "Catálogo completo: " + item["id"])
	check(game.state()["recommendations"].size() == 5, "Completar proyectos, un encargo y diez ayudas produce recomendaciones sin duplicarlas")
	check(store.data["campaign"]["sql_history"].is_empty(), "Los proyectos no modifican la base académica")
	var wrong = SQL.evaluate({"case_id": "almacen_1", "query": "SELECT nombre,stock FROM producto WHERE stock <= 5"})
	check(wrong["ok"] and not wrong["correct"], "Rechazar la inclusión incorrecta del límite")
	var alternative = SQL.evaluate({"case_id": "almacen_1", "query": "select stock, nombre from producto where 5 > stock"})
	check(alternative.get("correct", false), "Aceptar otra sintaxis y otro orden de columnas")
	for query in ["DELETE FROM producto", "ATTACH DATABASE 'otro.db' AS otro", "SELECT * FROM producto; DELETE FROM producto", "SELECT load_extension('x')"]:
		check(not SQL.evaluate({"case_id": "almacen_1", "query": query}).get("ok", false), "Proteger un encargo de lectura")
	wrong = SQL.evaluate({"case_id": "almacen_2", "query": "UPDATE producto SET stock=stock+8"})
	check(wrong["ok"] and not wrong["correct"], "Un UPDATE sin WHERE no cumple el encargo")
	check(SQL.evaluate({"case_id": "almacen_2", "query": SQL.case_data("almacen_2")["sql"]})["correct"], "Un intento incorrecto no contamina la prueba siguiente")
	var inspected = SQL.evaluate({"case_id": "almacen_2", "query": "SELECT * FROM producto"})
	check(inspected.get("inspection", false) and not inspected["correct"], "Explorar una tabla no entrega el encargo")
	print(JSON.stringify({"module": "nexo_sql", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
