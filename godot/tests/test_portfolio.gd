extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Nexo = preload("res://scripts/nexo_game.gd")
const Portfolio = preload("res://scripts/portfolio.gd")
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-portfolio")
	DirAccess.make_dir_recursive_absolute(folder)
	var store = State.new(folder.path_join("state"))
	store.new_run({"player_name": "Persona de prueba"})
	var game = Nexo.new(store)
	for item in game.content["cases"]: store.data["campaign"]["lectures"].append(item["lesson"])
	for item in game.content["cases"]: game.complete_case(item["id"], item["sql"])
	var failures = []
	var paths = []
	for project in ["almacen", "tutorias", "biblioteca"]:
		var result = Portfolio.export_project(store, project, folder)
		if not result["ok"]:
			failures.append(result)
			continue
		paths.append(result["path"])
		for file in ["README.md", "proyecto.db", "modelo.json", "inicio.sql", "consultas.sql", "verificar.py", "soluciones.json", "pruebas.json"]:
			if not FileAccess.file_exists(result["path"].path_join(file)): failures.append(project + ": falta " + file)
	var out = FileAccess.open(folder.path_join("exports.json"), FileAccess.WRITE)
	out.store_string(JSON.stringify(paths))
	out.close()
	print(JSON.stringify({"module": "portfolio", "exports": paths.size(), "failures": failures}))
	quit(0 if failures.is_empty() else 1)
