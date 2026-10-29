extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Nexo = preload("res://scripts/nexo_game.gd")
var failures = []
var checks = 0
func check(value: bool, message: String):
	checks += 1
	if not value: failures.append(message)
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-nexo").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Prueba de Nexo"})
	var game = Nexo.new(store)
	check(not game.publish("caja_negativa", 1), "El caso no se publica antes de aprender su concepto")
	for item in game.content["posts"]: store.data["campaign"]["lectures"].append(item["lesson"])
	var before = store.data.duplicate(true)
	check(game.preview("caja_negativa", 1)["score"] == 3 and store.data == before, "La revisión de práctica no consume ni concede recursos")
	check(game.publish("caja_negativa", 1), "Publicar una ayuda correcta")
	check(store.data["reputation"] == 3 and store.data["league"]["xp"] == 100 and store.data["money"] == 2, "Reputación, XP y dinero se registran por separado")
	before = store.data.duplicate(true)
	check(not game.publish("caja_negativa", 1) and store.data == before, "No se duplican premios al responder de nuevo")
	check("carlos" in game.state()["contacts"] and store.data["relationships"]["carlos"] == 2, "La ayuda conecta con el autor y mejora la relación")
	store.recovery_blocked = true
	before = store.data.duplicate(true)
	check(not game.publish("codigos_inicio", 0) and store.data == before, "Un fallo de guardado revierte respuesta y recompensas")
	store.recovery_blocked = false
	check(not game.publish("codigos_inicio", 99), "Rechazar opciones inexistentes")
	check(game.publish("codigos_inicio", 0), "Ayudar a Moshi")
	check(game.publish("juegos_identidad", 2) and store.data["reputation"] == 5, "Una respuesta incorrecta tiene una consecuencia pequeña y acotada")
	var restored = State.new(folder)
	check(restored.data["nexo"] == State.restore_numbers(store.data["nexo"].duplicate(true)), "Respuestas y contactos sobreviven a la carga")
	for item in game.content["posts"]:
		check(item["options"].size() >= 4 and item["options"].any(func(option): return option[1] >= 2), "Cada caso ofrece alternativas y una explicación útil")
	print(JSON.stringify({"module": "nexo", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
