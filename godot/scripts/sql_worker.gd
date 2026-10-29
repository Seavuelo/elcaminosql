extends RefCounted

static func run_file(request_path: String) -> void:
	var request = JSON.parse_string(FileAccess.get_file_as_string(request_path))
	var result = {"ok": false, "error": "No se pudo leer la consulta"}
	if request is Dictionary and request.get("kind") == "nexo":
		result = preload("res://scripts/nexo_sql.gd").evaluate(request)
	elif request is Dictionary and request.get("query") is String:
		result = preload("res://scripts/school_sql.gd").evaluate(request, request_path)
	elif request is Dictionary and request.get("action") == "catalog":
		result = preload("res://scripts/school_sql.gd").evaluate(request, request_path)
	var output = FileAccess.open(request_path + ".result", FileAccess.WRITE)
	if output != null:
		output.store_string(JSON.stringify(result))
		output.close()
