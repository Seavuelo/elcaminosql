extends RefCounted
const SQL = preload("res://scripts/school_sql.gd")
static func export_project(store, project: String, parent: String) -> Dictionary:
	var content = JSON.parse_string(FileAccess.get_file_as_string("res://data/nexo.json"))
	var cases = []
	var solutions = {}
	for item in content["cases"]:
		if item["project"] == project and store.data["nexo"]["completed_cases"].has(item["id"]):
			cases.append(item)
			solutions[item["id"]] = store.data["nexo"]["completed_cases"][item["id"]]["query"]
	if cases.is_empty(): return {"ok": false, "error": "Completa al menos una etapa para exportar tu trabajo"}
	cases.sort_custom(func(a,b): return a["stage"] < b["stage"])
	var folder = parent.path_join("ElCaminoSQL-" + project + "-" + Crypto.new().generate_random_bytes(4).hex_encode())
	if DirAccess.make_dir_recursive_absolute(folder) != OK: return {"ok": false, "error": "No se pudo crear la carpeta del proyecto"}
	var db = SQL.open_memory()
	if db == null: return {"ok": false, "error": "No se pudo preparar la base exportable"}
	var ok = db.query(cases[0]["fixtures"][0])
	var queries = PackedStringArray()
	var readme = "# " + project.capitalize() + "\n\nProyecto educativo de " + store.data["player_name"] + ", realizado en El Camino SQL\n\nLos datos son ficticios, las consultas son las entregadas por el jugador\n\n## Qué resuelve\n\n"
	for item in cases:
		var query = solutions[item["id"]]
		ok = ok and db.query(query)
		queries.append("-- Etapa %s: %s\n%s" % [int(item["stage"]), item["title"], query])
		readme += "### " + item["title"] + "\n\n" + item["objective"] + "\n\n"
	var model = SQL.catalog(db)
	for table in model:
		db.query("PRAGMA foreign_key_list(" + SQL.quoted(table["name"]) + ")")
		table["foreign_keys"] = db.query_result.duplicate(true)
	if ok: ok = db.backup_to(folder.path_join("proyecto.db"))
	db.close_db()
	if not ok: return {"ok": false, "error": "No se pudo reconstruir el proyecto, conserva tu partida y revisa las consultas"}
	readme += "## Archivos\n\n- proyecto.db contiene el estado final y se abre con cualquier herramienta compatible con SQLite\n- inicio.sql contiene el esquema y los datos iniciales\n- consultas.sql documenta las consultas en orden, para reproducirlas parte de inicio.sql, no las vuelvas a ejecutar sobre el estado final\n- soluciones.json conserva tus consultas y pruebas.json contiene tres conjuntos de datos por etapa\n\n## Comprobar\n\nCon Python 3 instalado, ejecuta python verificar.py desde esta carpeta, no necesita paquetes adicionales\n\nLas pruebas verifican resultados y cambios, no comparan el texto de las consultas\n\n## Alcance\n\nEste proyecto incluye " + str(cases.size()) + " etapas completadas, puedes ampliarlo con nuevos requisitos y datos\n"
	var files = {"README.md": readme, "modelo.json": JSON.stringify(model, "  "), "inicio.sql": cases[0]["fixtures"][0], "consultas.sql": "\n\n".join(queries), "soluciones.json": JSON.stringify(solutions, "  "), "pruebas.json": JSON.stringify(cases, "  "), "verificar.py": FileAccess.get_file_as_string("res://data/portfolio/verificar.py")}
	for name in files:
		var file = FileAccess.open(folder.path_join(name), FileAccess.WRITE)
		if file == null: return {"ok": false, "error": "No se pudo completar el archivo " + name + ", la carpeta parcial se conserva"}
		file.store_string(files[name])
		file.close()
	return {"ok": true, "path": folder}
