extends RefCounted
const SQL = preload("res://scripts/school_sql.gd")
static func case_data(id: String) -> Dictionary:
	var content = JSON.parse_string(FileAccess.get_file_as_string("res://data/nexo.json"))
	for item in content.get("cases", []):
		if item["id"] == id: return item
	return {}
static func evaluate(request: Dictionary) -> Dictionary:
	var task = case_data(request.get("case_id", ""))
	if task.is_empty(): return {"ok": false, "error": "No se encontró este encargo"}
	var checked = SQL.single_statement(request.get("query", ""))
	if request.get("action") != "catalog" and not checked["ok"]: return checked
	var report = {"ok": true, "correct": true, "passed": 0, "total": task["fixtures"].size(), "columns": [], "rows": [], "catalog": []}
	for index in range(task["fixtures"].size()):
		var db = SQL.open_memory()
		if db == null: return {"ok": false, "error": "No se pudo preparar la copia del encargo"}
		if not db.query(task["fixtures"][index]):
			db.close_db()
			return {"ok": false, "error": "No se pudo preparar la información de prueba"}
		db.query("PRAGMA foreign_keys=ON")
		for previous_id in request.get("case_history", []):
			var previous = case_data(previous_id)
			if previous.is_empty() or previous["project"] != task["project"] or not previous["is_write"]: continue
			var inspecting = request.get("action") in ["catalog", "inspect"] or checked.get("keyword", "") in ["SELECT", "EXPLAIN"]
			if int(previous["stage"]) < int(task["stage"]) or (previous_id == task["id"] and inspecting):
				if not db.query(previous["sql"]):
					db.close_db()
					return {"ok": false, "error": "No se pudo reconstruir la etapa anterior del proyecto"}
		if index == 0: report["catalog"] = SQL.catalog(db)
		if request.get("action") == "catalog":
			if not report["catalog"].is_empty():
				var sample = SQL.read(db, "SELECT * FROM " + SQL.quoted(report["catalog"][0]["name"]) + " LIMIT 8")
				report["columns"] = sample.get("columns", [])
				report["rows"] = sample.get("rows", [])
			db.close_db()
			return report
		var inspect = request.get("action") == "inspect" or (task["is_write"] and checked["keyword"] in ["SELECT", "EXPLAIN"])
		var actual = {}
		var correct = false
		if not task["is_write"] or inspect:
			actual = SQL.read(db, request["query"])
			if actual["ok"] and not inspect:
				var expected = SQL.read(db, task["sql"])
				if expected["ok"]: correct = SQL.compare(actual, expected, "ORDER BY" in task["sql"].to_upper())["correct"]
		else:
			var reference = SQL.open_memory()
			if reference == null:
				db.close_db()
				return {"ok": false, "error": "No se pudo preparar la comprobación"}
			var expected_ok = reference.query(task["fixtures"][index]) and reference.query("PRAGMA foreign_keys=ON")
			for previous_id in request.get("case_history", []):
				var previous = case_data(previous_id)
				if not previous.is_empty() and previous["project"] == task["project"] and previous["is_write"] and int(previous["stage"]) < int(task["stage"]):
					expected_ok = expected_ok and reference.query(previous["sql"])
			expected_ok = expected_ok and reference.query(task["sql"])
			var permitted = checked["keyword"] in ["CREATE", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "WITH"]
			var success = permitted and db.query(checked["sql"])
			actual = {"ok": success, "error": db.error_message if permitted else "Este encargo necesita una instrucción de escritura", "columns": ["Comprobación"], "rows": [{"Comprobación": "Cambio probado en una copia temporal"}]}
			correct = expected_ok and success and SQL.snapshot(db) == SQL.snapshot(reference)
			reference.close_db()
		if index == 0:
			report["columns"] = actual.get("columns", [])
			report["rows"] = actual.get("rows", [])
		db.close_db()
		if not actual["ok"]: return actual
		if inspect:
			report["inspection"] = true
			report["correct"] = false
			report["feedback"] = "Esta es una muestra, tu solución y el encargo siguen pendientes"
			return report
		if correct: report["passed"] += 1
		else: report["correct"] = false
	report["feedback"] = "Tu solución supera los %s casos de prueba" % report["total"] if report["correct"] else "Superaste %s de %s casos, revisa los límites, los empates, los NULL y las filas que deben conservarse" % [report["passed"], report["total"]]
	return report
