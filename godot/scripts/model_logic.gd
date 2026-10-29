extends RefCounted

const TYPES = ["VARCHAR", "NUMERIC", "DATE", "INTEGER", "REAL", "BLOB"]
var data: Dictionary
var error = ""

func _init(value: Dictionary = {}) -> void:
	data = value.duplicate(true) if not value.is_empty() else {"entities": [], "relations": []}

static func identifier(value: String) -> bool:
	var pattern = RegEx.new()
	pattern.compile("^[A-Za-z][A-Za-z0-9_]{0,39}$")
	return pattern.search(value) != null

static func quoted(value: String) -> String:
	return '"' + value.replace('"', '""') + '"'

func entity(value: String) -> Dictionary:
	for item in data["entities"]:
		if item["name"] == value:
			return item
	return {}

func attribute(value: Dictionary) -> Dictionary:
	var item = value.duplicate(true)
	item["name"] = str(item.get("name", "")).strip_edges()
	if not identifier(item["name"]):
		error = "Usa letras sin tildes ni ñ, números y _, sin espacios, empieza con una letra, máximo 40 caracteres"
		return {}
	if item.get("type", "") not in TYPES:
		error = "Elige un tipo de origen disponible"
		return {}
	for field in ["length", "precision", "scale"]:
		var number = item.get(field, 80 if field == "length" else (10 if field == "precision" else 2))
		if not str(number).is_valid_float() or float(number) != floor(float(number)):
			error = "Longitud, precisión y escala deben ser números enteros"
			return {}
		item[field] = int(number)
	if item["length"] < 1 or item["length"] > 4000:
		error = "La longitud de VARCHAR debe estar entre 1 y 4000"
		return {}
	if item["precision"] < 1 or item["precision"] > 15 or item["scale"] < 0 or item["scale"] > mini(6, item["precision"]):
		error = "Usa precisión de 1 a 15 y escala entre 0 y 6, sin superar la precisión"
		return {}
	item["uid"] = bool(item.get("uid", false))
	item["mandatory"] = bool(item.get("mandatory", false)) or item["uid"]
	return item

func save_entity(value: Dictionary, old: String = "") -> bool:
	error = ""
	var item = value.duplicate(true)
	item["name"] = str(item.get("name", "")).strip_edges().to_upper()
	if not identifier(item["name"]):
		error = "El nombre empieza con una letra, sin espacios, tildes ni ñ, usa _ para separar palabras, máximo 40 caracteres"
		return false
	if not entity(item["name"]).is_empty() and item["name"] != old:
		error = "Ya existe una entidad con ese nombre"
		return false
	var names = []
	var attrs = []
	for value_attr in item.get("attributes", []):
		var attr = attribute(value_attr)
		if attr.is_empty():
			return false
		if attr["name"].to_lower() in names:
			error = "Los atributos de una entidad no pueden repetir el nombre"
			return false
		names.append(attr["name"].to_lower())
		attrs.append(attr)
	item["attributes"] = attrs
	var current = entity(old)
	if current.is_empty():
		data["entities"].append(item)
	else:
		data["entities"][data["entities"].find(current)] = item
		for relation in data["relations"]:
			for endpoint in ["source", "target"]:
				if relation[endpoint] == old:
					relation[endpoint] = item["name"]
	return true

func delete_entity(value: String) -> bool:
	for relation in data["relations"]:
		if value in [relation["source"], relation["target"]]:
			error = "Quita primero las relaciones de esta entidad"
			return false
	data["entities"].erase(entity(value))
	return true

func save_relation(value: Dictionary) -> bool:
	error = ""
	var item = value.duplicate(true)
	item["name"] = str(item.get("name", "")).strip_edges().to_upper()
	if not identifier(item["name"]):
		error = "El nombre de la relación debe comenzar con una letra, usa _ sin espacios, tildes ni ñ, máximo 40 caracteres"
		return false
	if entity(item.get("source", "")).is_empty() or entity(item.get("target", "")).is_empty():
		error = "Selecciona dos entidades existentes"
		return false
	if item.get("kind", "") not in ["1:1", "1:N", "N:M"]:
		error = "Elige una cardinalidad disponible"
		return false
	for field in ["source_optional", "target_optional", "identifying", "transfer_key", "transferable"]:
		item[field] = bool(item.get(field, field in ["target_optional", "transfer_key", "transferable"]))
	if item["identifying"] and (item["source_optional"] or not item["transfer_key"]):
		error = "Una relación identificadora necesita un origen obligatorio y debe transferir su clave"
		return false
	for relation in data["relations"]:
		if relation["name"] == item["name"] and relation["id"] != item.get("id", ""):
			error = "Ya existe una relación con ese nombre"
			return false
	if not item.has("id"):
		item["id"] = Crypto.new().generate_random_bytes(12).hex_encode()
	for index in range(data["relations"].size()):
		if data["relations"][index]["id"] == item["id"]:
			data["relations"][index] = item
			return true
	data["relations"].append(item)
	return true

func table_for(item: Dictionary) -> Dictionary:
	return {"name": item["name"], "columns": item["attributes"].duplicate(true), "foreign_keys": [], "unique": [], "x": item.get("x", 0), "y": item.get("y", 0)}

func parent_first(name: String, visiting: Array, built: Array, tables: Dictionary) -> bool:
	if name in built:
		return true
	if name in visiting:
		error = "Las relaciones identificadoras no pueden formar un ciclo"
		return false
	visiting.append(name)
	for relation in data["relations"]:
		if relation["target"] == name and relation.get("identifying", false) and relation["kind"] != "N:M":
			if not parent_first(relation["source"], visiting, built, tables):
				return false
			if not transfer(relation, tables[relation["source"]], tables[name], prefix_for(relation), true):
				return false
	visiting.erase(name)
	built.append(name)
	return true

func prefix_for(relation: Dictionary) -> String:
	var count = 0
	for other in data["relations"]:
		if other["source"] == relation["source"] and other["target"] == relation["target"] and other["kind"] != "N:M":
			count += 1
	return relation["name"] + "_" + relation["source"] if count > 1 else relation["source"]

func transfer(relation: Dictionary, source: Dictionary, target: Dictionary, prefix: String, identifying: bool = false, optional: bool = false) -> bool:
	var primary = source["columns"].filter(func(item): return item.get("uid", false))
	if primary.is_empty():
		error = "Falta un UID primario en " + source["name"]
		return false
	var fields = []
	var target_columns = []
	for attr in primary:
		var label = prefix + "_" + attr["name"]
		if attr["name"] == attr["name"].to_lower():
			label = label.to_lower()
		var existing = {}
		for field in target["columns"]:
			if field["name"].to_lower() == label.to_lower():
				existing = field
		if not existing.is_empty() and existing["type"] != attr["type"]:
			error = "La columna " + label + " ya existe con otro tipo"
			return false
		if existing.is_empty():
			existing = attr.duplicate(true)
			existing.merge({"name": label, "uid": identifying, "mandatory": not optional, "generated": true}, true)
			target["columns"].append(existing)
		existing["uid"] = existing.get("uid", false) or identifying
		existing["mandatory"] = existing.get("mandatory", false) or not optional or identifying
		fields.append(existing["name"])
		target_columns.append(attr["name"])
	var duplicate = false
	for foreign in target["foreign_keys"]:
		if foreign["name"] == relation["name"] and foreign["table"] == source["name"]:
			duplicate = true
	if not duplicate:
		target["foreign_keys"].append({"name": relation["name"], "columns": fields, "table": source["name"], "target_columns": target_columns, "transferable": relation.get("transferable", true)})
	if relation["kind"] == "1:1" and fields not in target["unique"]:
		target["unique"].append(fields)
	return true

func relational() -> Dictionary:
	error = ""
	if data["entities"].is_empty():
		error = "Crea una entidad antes de convertir el modelo"
		return {}
	var tables = {}
	for item in data["entities"]:
		tables[item["name"]] = table_for(item)
	var built = []
	for item in data["entities"]:
		if not parent_first(item["name"], [], built, tables):
			return {}
	var warnings = []
	for relation in data["relations"]:
		if not relation.get("transfer_key", true):
			warnings.append(relation["name"] + ": asociación solo lógica, no genera FK ni integridad automática")
			continue
		var source = tables[relation["source"]]
		var target = tables[relation["target"]]
		if relation["kind"] == "N:M":
			if tables.has(relation["name"]):
				error = "El nombre de la tabla intermedia coincide con una entidad, cambia el nombre de la relación"
				return {}
			var bridge = table_for({"name": relation["name"], "attributes": [], "x": (float(source["x"]) + float(target["x"])) / 2, "y": maxf(float(source["y"]), float(target["y"])) + 260})
			var same = source["name"] == target["name"]
			if not transfer(relation, source, bridge, source["name"] + ("_ORIGEN" if same else ""), true) or not transfer(relation, target, bridge, target["name"] + ("_DESTINO" if same else ""), true):
				return {}
			tables[relation["name"]] = bridge
		elif not relation.get("identifying", false):
			if not transfer(relation, source, target, prefix_for(relation), false, relation.get("source_optional", false)):
				return {}
		if not relation.get("target_optional", true):
			warnings.append(relation["name"] + ": exigir al menos un hijo requiere validación del proceso, una FK sola no garantiza esa participación mínima")
	for table in tables.values():
		if table["columns"].is_empty() or table["columns"].filter(func(a): return a.get("uid", false)).is_empty():
			error = "Define atributos y un UID primario en " + table["name"]
			return {}
	return {"tables": tables.values(), "warnings": warnings}

static func quoted_list(fields: Array) -> String:
	var values = PackedStringArray()
	for field in fields:
		values.append(quoted(str(field)))
	return ", ".join(values)

static func sql_for(table: Dictionary) -> String:
	var parts = PackedStringArray()
	var primary = []
	for attr in table["columns"]:
		var type = attr["type"]
		var column = quoted(attr["name"])
		var text = column + " " + ("TEXT" if type in ["VARCHAR", "DATE"] else type)
		if attr.get("mandatory", false) or attr.get("uid", false):
			text += " NOT NULL"
		if attr.get("uid", false):
			primary.append(attr["name"])
		if type == "VARCHAR":
			text += " CHECK(length(%s) <= %s)" % [column, attr.get("length", 80)]
		elif type == "DATE":
			text += " CHECK(%s IS NULL OR (length(%s) = 10 AND date(%s, '+0 days') IS NOT NULL AND date(%s, '+0 days') = %s))" % [column, column, column, column, column]
		elif type == "NUMERIC":
			text += " CHECK(%s IS NULL OR (typeof(%s) IN ('integer','real') AND abs(%s) < %s AND abs(%s-round(%s,%s)) < 0.000000001))" % [column, column, column, str(int(pow(10, attr.get("precision", 10) - attr.get("scale", 2)))), column, column, attr.get("scale", 2)]
		parts.append(text)
	parts.append("PRIMARY KEY (" + quoted_list(primary) + ")")
	for fields in table["unique"]:
		parts.append("UNIQUE (" + quoted_list(fields) + ")")
	for foreign in table["foreign_keys"]:
		parts.append("CONSTRAINT " + quoted(foreign["name"]) + " FOREIGN KEY (" + quoted_list(foreign["columns"]) + ") REFERENCES " + quoted(foreign["table"]) + " (" + quoted_list(foreign["target_columns"]) + ")")
	return "CREATE TABLE " + quoted(table["name"]) + " (\n  " + ",\n  ".join(parts) + "\n);"

func statements() -> PackedStringArray:
	var model = relational()
	var result = PackedStringArray()
	if model.is_empty():
		return result
	for table in model["tables"]:
		result.append(sql_for(table))
	for table in model["tables"]:
		for index in range(table["foreign_keys"].size()):
			var foreign = table["foreign_keys"][index]
			if foreign["transferable"]:
				continue
			var known = PackedStringArray()
			var changed = PackedStringArray()
			for field in foreign["columns"]:
				known.append("OLD." + quoted(field) + " IS NOT NULL")
				changed.append("OLD." + quoted(field) + " IS NOT NEW." + quoted(field))
			result.append("CREATE TRIGGER " + quoted("LOCK_" + table["name"] + "_" + str(index)) + " BEFORE UPDATE OF " + quoted_list(foreign["columns"]) + " ON " + quoted(table["name"]) + " WHEN (" + " AND ".join(known) + ") AND (" + " OR ".join(changed) + ") BEGIN SELECT RAISE(ABORT, 'Relacion no transferible'); END;")
	return result

func verify(workshop: bool = false) -> Dictionary:
	var sql = statements()
	if sql.is_empty():
		return {"ok": false, "error": error}
	var db = ClassDB.instantiate("SQLite")
	db.path = ":memory:"
	db.verbosity_level = 0
	if not db.open_db():
		return {"ok": false, "error": "No se pudo abrir la base temporal"}
	var checks = []
	var failure = ""
	if not db.query("PRAGMA foreign_keys=ON"):
		failure = db.error_message
	for statement in sql:
		if failure.is_empty() and not db.query(statement):
			failure = db.error_message
	if workshop and failure.is_empty():
		for query in ["INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(1,'Moshi',6.8)", "INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(1,1,'Modelo relacional')", "INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(2,1,'Claves')"]:
			if not db.query(query):
				failure = db.error_message
		for check in [["PK repetida", "INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(1,'Otro',5)"], ["Nombre obligatorio", "INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(2,NULL,5)"], ["FK inexistente", "INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(3,999,'Sin dueño')"]]:
			if not failure.is_empty():
				break
			if db.query(check[1]):
				failure = check[0] + " no fue rechazado, revisa las restricciones"
			else:
				checks.append(check[0] + ": rechazado correctamente")
	if failure.is_empty() and (not db.query("PRAGMA foreign_key_check") or not db.query_result.is_empty()):
		failure = "Hay referencias que no corresponden a una fila existente"
	db.close_db()
	return {"ok": failure.is_empty(), "error": failure, "checks": checks, "tables": relational().get("tables", []), "warnings": relational().get("warnings", [])}
