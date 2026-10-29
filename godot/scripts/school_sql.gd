extends RefCounted

const Course = preload("res://scripts/course_data.gd")

static func single_statement(query: String) -> Dictionary:
	if query.is_empty() or query.length() > 32000:
		return {"ok": false, "error": "Escribe una sentencia SQL de hasta 32000 caracteres"}
	var mode = "normal"
	var clean = ""
	var semicolons = []
	var index = 0
	while index < query.length():
		var c = query[index]
		var next = query[index + 1] if index + 1 < query.length() else ""
		if mode == "line":
			if c == "\n":
				mode = "normal"
			clean += " "
		elif mode == "block":
			if c == "*" and next == "/":
				mode = "normal"
				index += 1
			clean += " "
		elif mode in ["'", "\"", "`", "]"]:
			if c == mode:
				if next == mode and mode != "]":
					index += 1
				else:
					mode = "normal"
		else:
			if c == "-" and next == "-":
				mode = "line"
				index += 1
				clean += " "
			elif c == "/" and next == "*":
				mode = "block"
				index += 1
				clean += " "
			elif c in ["'", "\"", "`", "["]:
				mode = "]" if c == "[" else c
				clean += " Q "
			else:
				clean += c
				if c == ";":
					semicolons.append({"clean": clean.length() - 1, "source": index})
		index += 1
	if mode not in ["normal", "line"]:
		return {"ok": false, "error": "Revisa las comillas o el comentario que quedó abierto"}
	if semicolons.size() > 1 or (semicolons.size() == 1 and not clean.substr(semicolons[0]["clean"] + 1).strip_edges().is_empty()):
		return {"ok": false, "error": "Ejecuta una sentencia a la vez, puedes repartirla en varias líneas"}
	var forbidden = RegEx.new()
	forbidden.compile("(?i)\\b(ATTACH|DETACH|PRAGMA|VACUUM|LOAD_EXTENSION|READFILE|WRITEFILE|TRIGGER)\\b")
	if forbidden.search(clean) != null:
		return {"ok": false, "error": "Esta instrucción no pertenece al entorno de práctica, trabaja con las tablas del catálogo"}
	var tokens = RegEx.new()
	tokens.compile("[A-Za-z_][A-Za-z_0-9]*")
	var first = tokens.search(clean)
	var keyword = first.get_string().to_upper() if first != null else ""
	var sql = query.strip_edges()
	if semicolons.size() == 1:
		# Los comentarios posteriores se conservan, envolver la consulta exige quitar solo el delimitador
		var position = int(semicolons[0]["source"])
		sql = query.substr(0, position) + query.substr(position + 1)
	return {"ok": true, "sql": sql, "keyword": keyword}

static func open_memory():
	var db = ClassDB.instantiate("SQLite")
	db.path = ":memory:"
	db.default_extension = ""
	db.verbosity_level = 0
	if not db.open_db():
		return null
	db.enable_load_extension(false)
	return db

static func authority(id: String) -> Dictionary:
	if id.begins_with("exam_"):
		var parts = id.split("_")
		if parts.size() != 4 or not parts[1].is_valid_int() or not parts[3].is_valid_int():
			return {}
		var list = Course.exams(int(parts[1]))
		return list[int(parts[3])] if int(parts[3]) >= 0 and int(parts[3]) < list.size() else {}
	return Course.task(id)

static func initialize(db, request: Dictionary, folder: String) -> bool:
	if request.get("legacy_base", false) and not request.get("sandbox", false):
		if not db.restore_from(folder.path_join("legacy-university.db")):
			return false
	elif not db.query(FileAccess.get_file_as_string("res://data/university.sql")):
		return false
	if request.get("reset_year4", false):
		db.query("DROP VIEW IF EXISTS vista_honor")
		db.query("DROP INDEX IF EXISTS idx_carrera")
	for id in ([] if request.get("sandbox", false) else request.get("history", [])):
		if not id is String:
			return false
		var exercise = authority(id)
		if exercise.is_empty() or not exercise.get("is_write", false) or not db.query(exercise["sql"]):
			return false
	if request.get("sandbox", false):
		if request.get("sandbox_history", []).size() > 500:
			return false
		for previous in request.get("sandbox_history", []):
			var safe = single_statement(previous)
			if not safe["ok"] or safe["keyword"] not in ["CREATE", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP"] or not db.query(safe["sql"]):
				return false
	db.query("PRAGMA foreign_keys=ON")
	return true

static func quoted(value: String) -> String:
	return '"' + value.replace('"', '""') + '"'

static func read(db, query: String) -> Dictionary:
	var checked = single_statement(query)
	if not checked["ok"]:
		return checked
	if checked["keyword"] not in ["SELECT", "WITH", "EXPLAIN"]:
		return {"ok": false, "error": "Esta actividad es de lectura, los cambios se habilitan solo en una tarea autorizada o en tu base libre"}
	var columns = []
	var rows = []
	if checked["keyword"] == "EXPLAIN":
		if not db.query(checked["sql"]):
			return {"ok": false, "error": db.error_message}
		rows = db.query_result.duplicate(true)
		columns = rows[0].keys() if not rows.is_empty() else []
	else:
		if not db.query("CREATE TEMP VIEW __student_result AS\n" + checked["sql"] + "\n"):
			return {"ok": false, "error": db.error_message}
		if not db.query("PRAGMA table_info(__student_result)"):
			return {"ok": false, "error": db.error_message}
		for field in db.query_result:
			columns.append(field["name"])
		db.query("PRAGMA query_only=ON")
		var success = db.query("SELECT * FROM __student_result LIMIT 1001")
		rows = db.query_result.duplicate(true)
		var error: String = db.error_message
		db.query("PRAGMA query_only=OFF")
		db.query("DROP VIEW __student_result")
		if not success:
			return {"ok": false, "error": error}
	if rows.size() > 1000:
		return {"ok": false, "error": "El resultado supera las mil filas, reduce los cruces o utiliza un filtro y LIMIT"}
	return {"ok": true, "columns": columns, "rows": rows}

static func catalog(db) -> Array:
	db.query("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name")
	var names = db.query_result.duplicate(true)
	var result = []
	for table in names:
		db.query("PRAGMA table_info(" + quoted(table["name"]) + ")")
		result.append({"name": table["name"], "columns": db.query_result.duplicate(true)})
	return result

static func snapshot(db) -> Array:
	db.query("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")
	var objects = db.query_result.duplicate(true)
	var result = []
	for object in objects:
		var name: String = object["name"]
		db.query("PRAGMA index_xinfo(" + quoted(name) + ")" if object["type"] == "index" else "PRAGMA table_info(" + quoted(name) + ")")
		var fields: Array = db.query_result.duplicate(true)
		var rows = []
		var keys = []
		if object["type"] != "index":
			if not db.query("SELECT * FROM " + quoted(name)):
				return [{"invalid": true, "name": name}]
			for row in db.query_result:
				rows.append(JSON.stringify(row))
			rows.sort()
			db.query("PRAGMA foreign_key_list(" + quoted(name) + ")")
			keys = db.query_result.duplicate(true)
		result.append({"kind": object["type"], "name": name, "fields": fields, "rows": rows, "keys": keys})
	return result

static func compare(actual: Dictionary, expected: Dictionary, ordered: bool) -> Dictionary:
	if actual["columns"].size() != expected["columns"].size():
		return {"correct": false, "feedback": "Revisa las columnas solicitadas, el resultado debe contener %s" % ", ".join(expected["columns"])}
	var mapping = []
	var normalized = []
	for column in actual["columns"]:
		normalized.append(str(column).to_lower())
	for index in range(expected["columns"].size()):
		var found = normalized.find(str(expected["columns"][index]).to_lower())
		mapping.append(found if found >= 0 else index)
	var actual_rows = []
	var expected_rows = []
	for pair in [[actual, actual_rows, true], [expected, expected_rows, false]]:
		for row in pair[0]["rows"]:
			var values = []
			for index in range(expected["columns"].size()):
				var column = pair[0]["columns"][mapping[index] if pair[2] else index]
				var value = row[column]
				values.append(snappedf(float(value), 0.01) if value is float or value is int else value)
			pair[1].append(JSON.stringify(values))
	if not ordered:
		actual_rows.sort()
		expected_rows.sort()
	if actual_rows == expected_rows:
		return {"correct": true, "feedback": "El resultado cumple lo solicitado"}
	return {"correct": false, "feedback": "Revisa las filas, los valores y los límites del filtro" + (", también el orden y los desempates" if ordered else "")}

static func evaluate(request: Dictionary, request_path: String) -> Dictionary:
	var db = open_memory()
	if db == null:
		return {"ok": false, "error": "No se pudo preparar SQLite"}
	if not initialize(db, request, request_path.get_base_dir()):
		db.close_db()
		return {"ok": false, "error": "No se pudo reconstruir tu base de práctica, se conservaron los datos guardados"}
	var catalog_data = catalog(db)
	if request.get("action") == "catalog":
		db.close_db()
		return {"ok": true, "catalog": catalog_data}
	var query: String = request.get("query", "")
	var checked = single_statement(query)
	if not checked["ok"]:
		db.close_db()
		return checked
	var exercise = authority(request.get("task_id", ""))
	var sandbox = request.get("sandbox", false)
	if sandbox:
		if checked["keyword"] in ["SELECT", "WITH", "EXPLAIN"]:
			var result = read(db, query)
			result["catalog"] = catalog_data
			db.close_db()
			return result
		if checked["keyword"] not in ["CREATE", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP"]:
			db.close_db()
			return {"ok": false, "error": "Usa una instrucción SQL de lectura o modelamiento en tu base libre"}
		var success = db.query(checked["sql"])
		var error: String = db.error_message
		catalog_data = catalog(db)
		db.close_db()
		return {"catalog": catalog_data, "ok": success, "error": error, "sandbox_write": success, "columns": ["Estado"], "rows": [{"Estado": "Cambio aplicado en tu base libre"}]}
	if exercise.get("is_write", false):
		if checked["keyword"] in ["SELECT", "EXPLAIN"]:
			var inspection = read(db, query)
			inspection["inspection"] = true
			inspection["catalog"] = catalog_data
			db.close_db()
			return inspection
		if checked["keyword"] not in ["CREATE", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "WITH"]:
			db.close_db()
			return {"ok": false, "error": "Esta tarea necesita una operación de escritura"}
		var baseline = request_path + ".baseline.db"
		if not db.backup_to(baseline):
			db.close_db()
			return {"ok": false, "error": "No se pudo preparar la comprobación de tus cambios"}
		var reference = open_memory()
		if reference == null or not reference.restore_from(baseline):
			db.close_db()
			return {"ok": false, "error": "No se pudo preparar la base de referencia"}
		var expected_ok = reference.query(exercise["sql"])
		var actual_ok = db.query(checked["sql"])
		var error: String = db.error_message
		var correct = expected_ok and actual_ok and snapshot(db) == snapshot(reference)
		catalog_data = catalog(db)
		reference.close_db()
		db.close_db()
		return {"ok": actual_ok, "error": error, "correct": correct, "write_validated": correct, "catalog": catalog_data,
			"feedback": "Los cambios coinciden con lo solicitado" if correct else "Los cambios no coinciden con el encargo, tu base se conserva para que puedas corregirlos",
			"columns": ["Comprobación"], "rows": [{"Comprobación": "Cambios correctos" if correct else "Cambios sin confirmar"}]}
	var actual = read(db, query)
	if actual["ok"] and not exercise.is_empty():
		var expected = read(db, exercise["sql"])
		if not expected["ok"]:
			actual = {"ok": false, "error": "La consulta de referencia necesita revisar su base de práctica"}
		else:
			actual.merge(compare(actual, expected, "ORDER BY" in exercise["sql"].to_upper()), true)
	actual["catalog"] = catalog_data
	db.close_db()
	return actual
