extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Campaign = preload("res://scripts/campaign.gd")
const Course = preload("res://scripts/course_data.gd")
const Model = preload("res://scripts/model_logic.gd")
var checks = 0
var failures = []
func check(value: bool, description: String) -> void:
	checks += 1
	if not value: failures.append(description)
func write_json(path: String, value: Dictionary) -> void:
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(value))
	file.close()
func attr(name: String, type: String = "NUMERIC", uid: bool = false, mandatory: bool = false) -> Dictionary:
	return {"name": name, "type": type, "uid": uid, "mandatory": mandatory, "length": 80, "precision": 10, "scale": 0 if uid else 2}
func fixture():
	var model = Model.new()
	model.save_entity({"name": "ESTUDIANTE", "attributes": [attr("id", "NUMERIC", true), attr("nombre", "VARCHAR", false, true), attr("promedio")], "x": 60, "y": 60})
	model.save_entity({"name": "TUTORIA", "attributes": [attr("id", "NUMERIC", true), attr("tema", "VARCHAR")], "x": 470, "y": 180})
	model.save_relation({"name": "TIENE_TUTORIA", "source": "ESTUDIANTE", "target": "TUTORIA", "kind": "1:N", "transfer_key": true, "source_optional": false, "target_optional": true, "transferable": true})
	return model

func _initialize() -> void:
	var folder = ProjectSettings.globalize_path("res://../.preview/test-campaign").path_join(str(Time.get_ticks_usec()))
	DirAccess.make_dir_recursive_absolute(folder)
	var store = State.new(folder.path_join("save"))
	check(store.new_run({"player_name": "Prueba"}), "Crear partida aislada")
	var campaign = Campaign.new(store)
	for day in range(1, 6):
		check(campaign.year() == 0 and campaign.day() == day, "La introducción conserva el día correcto")
		check(not campaign.can_finish(), "La jornada no acaba sin sus actividades")
		check(campaign.complete_lecture(), "Terminar clase introductoria")
		var answers = []
		for question in Course.quiz(day): answers.append(question["answer"])
		check(campaign.record_quiz(answers), "Guardar diez respuestas Kashut")
		var xp = store.data["league"]["xp"]
		check(campaign.record_quiz(answers) and store.data["league"]["xp"] == xp, "Repetir Kashut no duplica XP")
		if day >= 2:
			var model = fixture()
			campaign.progress()["model"] = model.data.duplicate(true)
			if day == 5:
				check(not campaign.can_finish(), "El último taller requiere comprobar el modelo")
				campaign.progress()["model_tested"] = JSON.stringify(model.data)
		check(campaign.can_finish() and campaign.close_class(), "Todas las actividades permiten cerrar la clase")
		check(campaign.leave_school() and campaign.sleep(), "Salir a casa y dormir avanza el día")
	check(campaign.year() == 1 and campaign.day() == 1, "La introducción desemboca en primer año")
	for year in range(1, 5):
		for day in range(1, 6):
			check(campaign.year() == year and campaign.day() == day, "Calendario completo: año %s día %s" % [year, day])
			check(campaign.complete_lecture(), "Completar clase")
			if day < 5:
				while not campaign.current_task_id().is_empty():
					var task_id = campaign.current_task_id()
					check(campaign.complete_task(task_id), "Entregar ejercicio " + task_id)
			else:
				for index in range(5): check(campaign.record_exam(true, "SELECT 1", "Correcto"), "Guardar respuesta de examen")
				check(is_equal_approx(float(campaign.exam()["grade"]), 7.0), "Cinco respuestas correctas reciben 7,0")
			check(campaign.close_class() and campaign.leave_school() and campaign.sleep(), "Cerrar jornada académica")
	check(campaign.progress()["phase"] == "graduated", "Los cuatro años terminan en graduación")
	check(campaign.progress()["tasks"].size() == 64 and campaign.progress()["grades"].size() == 4, "Se conservan los 64 ejercicios y cuatro notas")
	var restored = State.new(folder.path_join("save"))
	check(restored.data == State.restore_numbers(store.data.duplicate(true)), "Recuperación completa del progreso desde disco")
	check(Campaign.new(restored).exam()["finished"], "Cargar una partida no crea otro intento de examen por un decimal en el ID")
	check(Campaign.new(restored).model_checklist()[-1][1], "La comprobación del modelo sigue válida después de cargar")
	var previous = store.data.duplicate(true)
	store.data["campaign"]["day"] = "mal"
	check(not store.save(), "Se rechaza un calendario inválido sin reemplazar el guardado")
	store.data = previous
	var damaged = previous.duplicate(true)
	damaged["campaign"]["model"]["entities"][0]["attributes"][0]["type"] = "SQL_DESCONOCIDO"
	check(not store.valid(damaged), "Un modelo dañado no entra en el guardado")
	store.recovery_blocked = true
	previous = store.data.duplicate(true)
	check(not campaign.leave_school() and store.data == previous, "Fallo de escritura revierte ubicación")
	store.data["campaign"]["ready_to_leave"] = true
	previous = store.data.duplicate(true)
	check(not campaign.sleep() and store.data == previous, "Fallo de escritura revierte cambio de jornada")
	store.recovery_blocked = false
	var repeat_store = State.new(folder.path_join("repeat"))
	repeat_store.new_run({"player_name": "Otro intento"})
	var repeat_course = Campaign.new(repeat_store)
	repeat_course.progress().merge({"phase": "career", "year": 2, "day": 5, "ready_to_leave": true, "tasks": ["1_1_0", "2_1_0"], "sql_history": ["2_1_0"], "legacy_base": true}, true)
	for index in range(5): repeat_course.record_exam(index < 2, "SELECT 1", "Para revisar")
	check(repeat_course.exam()["grade"] < 4 and repeat_course.sleep(), "Un examen no aprobado permite repetir")
	check(repeat_course.year() == 2 and repeat_course.day() == 1 and repeat_course.progress()["attempts"]["2"] == 2, "El segundo intento vuelve al inicio del mismo año")
	check("1_1_0" in repeat_course.progress()["tasks"] and "2_1_0" not in repeat_course.progress()["tasks"], "Repetir conserva los años anteriores")
	check(not repeat_course.progress()["legacy_base"] and repeat_course.progress()["sql_history"].is_empty(), "Repetir segundo año reinicia la base de escritura")
	var original = folder.path_join("universidad.db")
	var db = ClassDB.instantiate("SQLite")
	db.path = original
	db.verbosity_level = 0
	check(db.open_db(), "Crear base antigua de prueba")
	db.query("CREATE TABLE recuerdo(id INTEGER PRIMARY KEY, texto TEXT)")
	db.query("INSERT INTO recuerdo VALUES(1,'Cambio personal conservado')")
	db.close_db()
	var original_hash = FileAccess.get_sha256(original)
	write_json(folder.path_join("savegame.json"), {"player_name": "Moshi", "has_save": true, "current_year": 2, "current_day": 2, "current_task_idx": 1, "foundation": {"completed": true}, "personal_notes": "Apunte personal"})
	var imported = State.new(folder.path_join("imported"))
	check(imported.import_profile(folder.path_join("savegame.json")), "Importar partida y práctica antiguas")
	check(imported.data["campaign"]["legacy_base"] and imported.data["campaign"]["sql_history"].is_empty(), "La copia restaurada no vuelve a ejecutar cambios anteriores")
	check(FileAccess.get_sha256(original) == original_hash, "La base antigua queda idéntica byte a byte")
	db.path = ":memory:"
	db.open_db()
	check(db.restore_from(folder.path_join("imported/legacy-university.db")), "Restaurar la copia de práctica")
	check(db.query("SELECT texto FROM recuerdo") and db.query_result[0]["texto"] == "Cambio personal conservado", "La importación conserva cambios personales de la base")
	db.close_db()
	print(JSON.stringify({"module": "campaign", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
