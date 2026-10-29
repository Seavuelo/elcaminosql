extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Career = preload("res://scripts/career.gd")
var failures = []
var checks = 0
func check(value, message):
	checks += 1
	if not value: failures.append(message)
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-career").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Mi camino"})
	var career = Career.new(store)
	check(career.opportunities().is_empty(), "No hay ofertas antes de completar la carrera")
	store.data["campaign"]["phase"] = "graduated"
	check(career.opportunities().size() == 1, "Siempre existe una forma de empezar sin reputación acumulada")
	check(not career.defend("almacen", [1,0,2]), "La defensa necesita el proyecto completo")
	store.data["nexo"]["completed_cases"]["almacen_4"] = {"query": "SELECT 1"}
	check(not career.defend("almacen", [0,0,2]), "Una defensa equivocada ofrece retroalimentación")
	check(career.defend("almacen", [1,0,2]), "Defender decisiones correctas")
	var previous = store.data.duplicate(true)
	check(career.defend("almacen", [1,0,2]) and previous == store.data, "La defensa no duplica recompensas")
	check(career.opportunities().size() == 2, "El almacén completo abre un camino propio")
	store.data["nexo"]["completed_cases"]["tutorias_4"] = {"query": "SELECT 1"}
	store.data["reputation"] = 40
	store.data["relationships"]["moshi"] = 12
	check(career.opportunities().size() == 3, "La relación y el proyecto abren la recomendación de Moshi")
	check(career.choose("lumina") and store.data["career"]["choice"] == "lumina", "Elegir una oportunidad")
	check(not career.choose("inexistente"), "Rechazar una oportunidad inexistente")
	var restored = State.new(folder)
	check(restored.data["career"] == store.data["career"], "El proyecto y la elección se conservan")
	store.recovery_blocked = true
	previous = store.data.duplicate(true)
	check(not career.choose("facultad") and previous == store.data, "Fallo de guardado revierte la decisión")
	print(JSON.stringify({"module": "career", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
