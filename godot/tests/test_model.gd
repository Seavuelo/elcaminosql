extends SceneTree
const Model = preload("res://scripts/model_logic.gd")
var checks = 0
var failures = []
func check(value: bool, description: String) -> void:
	checks += 1
	if not value:
		failures.append(description)
func attr(name: String, type: String = "NUMERIC", uid: bool = false, mandatory: bool = false) -> Dictionary:
	return {"name": name, "type": type, "uid": uid, "mandatory": mandatory, "length": 80, "precision": 10, "scale": 0 if uid else 2}
func fixture():
	var model = Model.new()
	model.save_entity({"name": "ESTUDIANTE", "attributes": [attr("id", "NUMERIC", true), attr("nombre", "VARCHAR", false, true), attr("promedio")], "x": 60, "y": 60})
	model.save_entity({"name": "TUTORIA", "attributes": [attr("id", "NUMERIC", true), attr("tema", "VARCHAR")], "x": 470, "y": 180})
	model.save_relation({"name": "TIENE_TUTORIA", "source": "ESTUDIANTE", "target": "TUTORIA", "kind": "1:N", "transfer_key": true, "source_optional": false, "target_optional": true, "transferable": true})
	return model
func database(model):
	var db = ClassDB.instantiate("SQLite")
	db.path = ":memory:"
	db.verbosity_level = 0
	db.open_db()
	db.query("PRAGMA foreign_keys=ON")
	for sql in model.statements(): check(db.query(sql), "DDL válido: " + db.error_message)
	return db
func _initialize() -> void:
	var model = fixture()
	check(model.verify(true)["ok"], "El taller acepta Moshi, dos tutorías y rechaza PK duplicada, NULL y FK inexistente")
	check(not model.save_entity({"name": "OTRA", "attributes": [attr("x"), attr("X")]}), "Atributos repetidos se rechazan ignorando mayúsculas")
	for name in ["con espacio", "niño", "café", "1tabla", "a-b", "", "a".repeat(41)]:
		check(not Model.identifier(name), "Identificador rechazado: " + name)
	check(model.save_entity({"name": "alumno", "attributes": model.entity("ESTUDIANTE")["attributes"]}, "ESTUDIANTE"), "Se puede renombrar una entidad")
	check(model.data["relations"][0]["source"] == "ALUMNO", "El cambio de nombre se propaga a la relación")
	check(not model.delete_entity("ALUMNO"), "No se borra una entidad que aún tiene relaciones")
	model = fixture()
	model.data["relations"][0]["kind"] = "N:M"
	var result = model.relational()
	check(result["tables"].size() == 3, "N:M crea la tabla intermedia")
	var bridge = result["tables"][2]
	check(bridge["columns"].filter(func(a): return a["uid"]).size() == 2, "La tabla intermedia tiene UID compuesto")
	check(bridge["foreign_keys"].size() == 2, "La tabla intermedia conserva ambas FK")
	check(model.verify()["ok"], "SQL N:M ejecutable")
	model.data["relations"][0]["target"] = "ESTUDIANTE"
	check(model.verify()["ok"], "Una autorrelación N:M genera referencias de origen y destino diferentes")
	model = fixture()
	model.data["relations"][0]["kind"] = "1:1"
	var db = database(model)
	check(db.query("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)"), "Insertar estudiante")
	check(db.query("INSERT INTO TUTORIA VALUES(1,'Claves',1)"), "Primera asociación 1:1")
	check(not db.query("INSERT INTO TUTORIA VALUES(2,'Tipos',1)"), "UNIQUE impide dos destinos para el mismo origen en 1:1")
	db.close_db()
	model = fixture()
	model.data["relations"][0]["transferable"] = false
	db = database(model)
	db.query("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8),(2,'Carlos',5)")
	db.query("INSERT INTO TUTORIA VALUES(1,'Claves',1)")
	check(not db.query("UPDATE TUTORIA SET estudiante_id=2 WHERE id=1"), "La relación no transferible impide reasignar el origen")
	db.close_db()
	model = fixture()
	model.data["relations"][0]["identifying"] = true
	model.save_entity({"name": "MATERIAL", "attributes": [attr("id", "NUMERIC", true)]})
	model.save_relation({"name": "USA_MATERIAL", "source": "TUTORIA", "target": "MATERIAL", "kind": "1:N", "identifying": true})
	result = model.relational()
	check(result["tables"][2]["columns"].filter(func(a): return a["uid"]).size() == 3, "Las identificadoras propagan la clave compuesta de los antecesores")
	check(model.verify()["ok"], "Las claves compuestas generadas referencian el UID completo")
	model.save_relation({"name": "CICLO", "source": "MATERIAL", "target": "ESTUDIANTE", "kind": "1:N", "identifying": true})
	check(model.relational().is_empty() and "ciclo" in model.error, "Se rechaza un ciclo identificador sin recursión infinita")
	model = fixture()
	var relation = model.data["relations"][0].duplicate(true)
	relation["name"] = "TIENE_APOYO"
	relation.erase("id")
	check(model.save_relation(relation), "Dos relaciones entre las mismas entidades son válidas")
	check(model.verify()["ok"], "Dos relaciones generan columnas FK diferenciadas")
	model = Model.new()
	model.save_entity({"name": "EVENTO", "attributes": [attr("id", "INTEGER", true), attr("fecha", "DATE"), {"name": "codigo", "type": "VARCHAR", "length": 3}, {"name": "monto", "type": "NUMERIC", "precision": 5, "scale": 2}]})
	db = database(model)
	check(db.query("INSERT INTO EVENTO VALUES(1,'2024-02-29','ABC',999.99)"), "Fecha bisiesta, texto al límite y NUMERIC(5,2) válidos")
	for sql in ["INSERT INTO EVENTO VALUES(2,'2023-02-29','ABC',1)", "INSERT INTO EVENTO VALUES(2,'2024-01-01','ABCD',1)", "INSERT INTO EVENTO VALUES(2,'2024-01-01','ABC',1000)", "INSERT INTO EVENTO VALUES(2,'2024-01-01','ABC',1.123)", "INSERT INTO EVENTO VALUES(2,'2024-01-01','ABC','hola')"]:
		check(not db.query(sql), "Rechazo de dato inválido: " + sql)
	check(db.query("INSERT INTO EVENTO VALUES(2,NULL,NULL,NULL)"), "Atributos opcionales conservan NULL")
	db.close_db()
	print(JSON.stringify({"module": "model", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
