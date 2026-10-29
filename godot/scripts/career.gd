extends RefCounted
var store
var notice = ""
var questions: Dictionary
func _init(save_system):
	store = save_system
	questions = JSON.parse_string(FileAccess.get_file_as_string("res://data/defense.json"))
func completed(project: String) -> bool:
	return store.data["nexo"]["completed_cases"].has(project + "_4")
func defend(project: String, answers: Array) -> bool:
	if store.data["campaign"]["phase"] != "graduated" or not questions.has(project) or not completed(project): notice = "Termina la carrera y las cuatro etapas del proyecto para presentarlo"; return false
	if answers.size() != questions[project].size() or answers.any(func(value): return not (value is int or value is float) or value < 0): notice = "Responde las tres preguntas"; return false
	for index in range(answers.size()):
		if int(answers[index]) != int(questions[project][index]["answer"]): notice = questions[project][index]["feedback"]; return false
	if store.data["career"]["defended"]: notice = "Tu proyecto ya fue presentado, puedes seguir repasando sus decisiones"; return true
	var previous = store.data.duplicate(true)
	store.data["career"].merge({"project": project, "defended": true}, true)
	store.award_xp(500, "capstone")
	store.reward_money(40, "capstone")
	store.data["reputation"] += 10
	if not store.save(): store.data = previous; notice = store.notice; return false
	notice = "Proyecto presentado, tus decisiones y sus pruebas ya forman parte de tu portafolio"
	return true
func opportunities() -> Array:
	if store.data["campaign"]["phase"] != "graduated": return []
	var paths = [{"id": "facultad", "title": "Apoyo de datos en la facultad", "text": "Marco te propone colaborar con el equipo de apoyo, empezarás con reportes y revisión de datos, con alguien del equipo acompañando tus primeras entregas"}]
	if completed("almacen"):
		paths.append({"id": "almacen", "title": "Hacer crecer el almacén con Carlos", "text": "Carlos quiere seguir trabajando contigo, el almacén ahora tiene datos que puede usar para decidir compras y entender sus ventas, te invita a ocuparte de sus próximos reportes"})
	if completed("tutorias") and store.data["reputation"] >= 35 and store.data["relationships"].get("moshi", 0) >= 9:
		paths.append({"id": "lumina", "title": "Una práctica por recomendación de Moshi", "text": "Moshi conoció al equipo de Lúmina y mostró el proyecto que construyeron, te invitan a conversar sobre una práctica en análisis de datos, tu trabajo comprobado abrió esa puerta"})
	return paths
func choose(id: String) -> bool:
	if not opportunities().any(func(path): return path["id"] == id): return false
	var previous = store.data.duplicate(true)
	store.data["career"]["choice"] = id
	if not store.save(): store.data = previous; notice = store.notice; return false
	notice = "Tu próximo paso quedó elegido, todavía puedes volver a casa, revisar tus proyectos y compartir lo que aprendiste"
	return true
