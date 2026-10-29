extends RefCounted

const Course = preload("res://scripts/course_data.gd")
var store

func _init(save_system) -> void:
	store = save_system

func progress() -> Dictionary:
	return store.data["campaign"]

func commit(previous: Dictionary) -> bool:
	if store.save():
		return true
	store.data = previous
	return false

func year() -> int:
	return 0 if progress()["phase"] == "intro" else int(progress()["year"])

func day() -> int:
	return int(progress()["day"])

func day_key() -> String:
	return Course.key(year(), day())

func lecture_done() -> bool:
	return day_key() in progress()["lectures"]

func complete_lecture(lesson_year: int = -1, lesson_day: int = -1) -> bool:
	if lesson_year < 0: lesson_year = year()
	if lesson_day < 0: lesson_day = day()
	if Course.lesson(lesson_year, lesson_day).is_empty(): return false
	var id = Course.key(lesson_year, lesson_day)
	if id in progress()["lectures"]: return true
	var previous = store.data.duplicate(true)
	progress()["lectures"].append(id)
	store.award_xp(50, "lecture_" + id)
	return commit(previous)

func current_task_id() -> String:
	if year() == 0 or day() == 5:
		return ""
	for index in range(Course.tasks(year(), day()).size()):
		var id = day_key() + "_" + str(index)
		if id not in progress()["tasks"]:
			return id
	return ""

func complete_task(id: String) -> bool:
	if id != current_task_id() or Course.task(id).is_empty():
		return false
	var previous = store.data.duplicate(true)
	progress()["tasks"].append(id)
	if Course.task(id)["is_write"]:
		progress()["sql_history"].append(id)
	store.award_xp(100, "exercise_" + id)
	return commit(previous)

func quiz_record() -> Dictionary:
	return progress()["quizzes"].get(str(day()), {})

func record_quiz(answers: Array) -> bool:
	var questions = Course.quiz(day())
	if year() != 0 or answers.size() != questions.size():
		return false
	var previous_state = store.data.duplicate(true)
	var score = 0
	for i in range(questions.size()):
		if int(answers[i]) == int(questions[i]["answer"]):
			score += 1
	var old: Dictionary = quiz_record()
	var previous = int(old.get("best", 0))
	var best = maxi(score, previous)
	var granted = int(old.get("xp_granted", 0))
	var total = int(Course.all()["kashut_rewards"][best])
	progress()["quizzes"][str(day())] = {"answers": answers, "score": score, "best": best, "reviewed": score == 10, "xp_granted": maxi(total, granted)}
	store.award_xp(maxi(0, total - granted), "kashut_%s_best_%s" % [day(), best])
	return commit(previous_state)

func review_quiz() -> bool:
	if quiz_record().is_empty():
		return false
	var previous = store.data.duplicate(true)
	quiz_record()["reviewed"] = true
	return commit(previous)

func exam() -> Dictionary:
	var id = str(year()) + "_" + str(progress()["attempts"].get(str(year()), 1))
	if not progress()["exams"].has(id):
		progress()["exams"][id] = {"answers": [], "finished": false, "grade": 1.0, "score": 0}
	return progress()["exams"][id]

func record_exam(correct: bool, query: String, feedback: String, history_id: String = "") -> bool:
	if year() == 0 or day() != 5 or exam()["finished"]:
		return false
	var previous = store.data.duplicate(true)
	var record = exam()
	record["answers"].append({"correct": correct, "query": query, "feedback": feedback})
	if correct:
		record["score"] += 1
		if not history_id.is_empty() and history_id not in progress()["sql_history"]:
			progress()["sql_history"].append(history_id)
	if record["answers"].size() == Course.exams(year()).size():
		record["finished"] = true
		var ratio = float(record["score"]) / Course.exams(year()).size()
		record["grade"] = snappedf(1 + 5 * ratio if ratio <= 0.6 else 4 + 7.5 * (ratio - 0.6), 0.1)
		progress()["grades"].append({"year": year(), "attempt": progress()["attempts"].get(str(year()), 1), "grade": record["grade"]})
		if record["grade"] >= 4:
			store.award_xp(1000, "exam_" + str(year()))
	return commit(previous)

func model_checklist() -> Array:
	var model: Dictionary = progress()["model"]
	var entities: Array = model.get("entities", [])
	var student = {}
	var tutoring = {}
	for entity in entities:
		if entity.get("name", "").to_upper() == "ESTUDIANTE":
			student = entity
		if entity.get("name", "").to_upper() == "TUTORIA":
			tutoring = entity
	var attrs = {}
	for attribute in student.get("attributes", []):
		attrs[attribute["name"].to_lower()] = attribute
	var result = []
	if day() >= 2:
		result.append(["Crear ESTUDIANTE", not student.is_empty()])
		result.append(["Añadir id numérico", attrs.has("id") and attrs["id"]["type"] in ["NUMERIC", "INTEGER", "REAL"]])
		result.append(["Añadir nombre como VARCHAR", attrs.has("nombre") and attrs["nombre"]["type"] == "VARCHAR"])
		result.append(["Añadir promedio numérico", attrs.has("promedio") and attrs["promedio"]["type"] in ["NUMERIC", "INTEGER", "REAL"]])
	if day() >= 3:
		result.append(["Marcar id como UID primario", attrs.get("id", {}).get("uid", false)])
		result.append(["Marcar nombre como obligatorio", attrs.get("nombre", {}).get("mandatory", false)])
	if day() >= 4:
		var tutor_attrs = {}
		for attribute in tutoring.get("attributes", []):
			tutor_attrs[attribute["name"].to_lower()] = attribute
		result.append(["Crear TUTORIA", not tutoring.is_empty()])
		result.append(["Añadir TUTORIA.id como UID", tutor_attrs.get("id", {}).get("uid", false)])
		result.append(["Añadir TUTORIA.tema como texto", tutor_attrs.get("tema", {}).get("type") == "VARCHAR"])
		var relation_ok = false
		for relation in model.get("relations", []):
			if relation.get("source") == "ESTUDIANTE" and relation.get("target") == "TUTORIA" and relation.get("kind") == "1:N" and relation.get("transfer_key", false):
				relation_ok = true
		result.append(["Relacionar ESTUDIANTE con TUTORIA y pasar UID", relation_ok])
	if day() == 5:
		result.append(["Generar y comprobar el modelo relacional", progress().get("model_tested", "") == JSON.stringify(model) and not progress().get("model_tested", "").is_empty()])
	return result

func can_finish() -> bool:
	if not lecture_done():
		return false
	if year() == 0:
		if quiz_record().is_empty() or not quiz_record().get("reviewed", false):
			return false
		for item in model_checklist():
			if not item[1]:
				return false
		return true
	return exam()["finished"] if day() == 5 else current_task_id().is_empty()

func close_class() -> bool:
	if not can_finish():
		return false
	var previous = store.data.duplicate(true)
	progress()["ready_to_leave"] = true
	return commit(previous)

func leave_school() -> bool:
	var previous = store.data.duplicate(true)
	progress()["location"] = "home"
	return commit(previous)

func sleep() -> bool:
	var previous = store.data.duplicate(true)
	if not progress()["ready_to_leave"]:
		store.data["night"] = false
		return commit(previous)
	if day() < 5:
		progress()["day"] += 1
	elif year() == 0:
		progress()["phase"] = "career"
		progress()["year"] = 1
		progress()["day"] = 1
	elif exam()["grade"] < 4:
		var current_year = year()
		progress()["attempts"][str(current_year)] = int(progress()["attempts"].get(str(current_year), 1)) + 1
		progress()["lectures"] = progress()["lectures"].filter(func(id): return not id.begins_with(str(current_year) + "_"))
		progress()["tasks"] = progress()["tasks"].filter(func(id): return not id.begins_with(str(current_year) + "_"))
		progress()["sql_history"] = progress()["sql_history"].filter(func(id): return not id.begins_with(str(current_year) + "_") and not id.begins_with("exam_" + str(current_year) + "_"))
		if current_year == 2:
			progress()["legacy_base"] = false
		elif current_year == 4:
			progress()["reset_year4"] = true
		progress()["day"] = 1
	elif year() < 4:
		progress()["year"] += 1
		progress()["day"] = 1
	else:
		progress()["phase"] = "graduated"
	progress()["ready_to_leave"] = false
	progress()["location"] = "home"
	store.data["night"] = false
	store.data["year"] = progress()["year"]
	return commit(previous)

func missions() -> Array:
	if progress()["phase"] == "graduated":
		return [{"id": "graduate", "title": "Tu siguiente paso", "detail": "Revisa tus proyectos y las oportunidades que llegan por Nexo", "done": false}]
	var result = []
	if progress()["location"] == "home" and not progress()["ready_to_leave"]:
		result.append({"id": "school", "title": "Ir a la universidad", "detail": "Acércate a la puerta de tu habitación y pulsa E", "done": false})
	result.append({"id": "lecture", "title": "Hablar con Marco para empezar la clase", "detail": "El profesor te espera junto a la pizarra", "done": lecture_done()})
	if lecture_done():
		if year() == 0:
			var record = quiz_record()
			var complete = record.get("answers", []).size() == 10
			result.append({"id": "kashut", "title": "Ir al computador para hacer Kashut", "detail": "Usa tu equipo y responde las diez preguntas", "done": complete})
			if complete:
				result.append({"id": "review", "title": "Revisar las respuestas", "detail": "Termina el repaso, si acertaste todas puedes salir del podio", "done": record.get("reviewed", false)})
			if record.get("reviewed", false) and day() >= 2:
				var finished = true
				for item in model_checklist(): finished = finished and item[1]
				result.append({"id": "model", "title": "Tarea del modelador en tu computador", "detail": "Abre el taller, Tarea actual muestra lo que necesitas construir", "done": finished})
		elif day() == 5:
			result.append({"id": "exam", "title": "La evaluación del viernes", "detail": "Cinco desafíos, puedes probar antes de entregar", "done": exam()["finished"]})
		else:
			var total = Course.tasks(year(), day()).size()
			var completed = 0
			for index in range(total):
				if day_key() + "_" + str(index) in progress()["tasks"]: completed += 1
			result.append({"id": "sql", "title": "Ejercicios de SQL", "detail": "%s de %s terminados, revisa el objetivo en tu computador" % [completed, total], "done": completed == total})
	if can_finish():
		result.append({"id": "close", "title": "Hablar con Marco para cerrar la jornada", "detail": "Todavía puedes practicar y ayudar a tus compañeros", "done": progress()["ready_to_leave"]})
	if progress()["ready_to_leave"]:
		result.append({"id": "home", "title": "Volver a casa y descansar", "detail": "Sal por la puerta de la sala, la cama permite comenzar el siguiente día", "done": false})
	return result

func unread_missions() -> bool:
	var seen = progress()["seen_missions"].get(day_key(), [])
	for item in missions():
		if not item["done"] and item["id"] not in seen: return true
	return false

func read_missions() -> bool:
	var previous = store.data.duplicate(true)
	var seen = progress()["seen_missions"].get(day_key(), [])
	for item in missions():
		if item["id"] not in seen: seen.append(item["id"])
	progress()["seen_missions"][day_key()] = seen
	return commit(previous)

func skip_intro() -> bool:
	if year() != 0: return false
	var previous = store.data.duplicate(true)
	progress().merge({"phase": "career", "year": 1, "day": 1, "ready_to_leave": false}, true)
	return commit(previous)
