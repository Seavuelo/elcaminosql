extends SceneTree
const State = preload("res://scripts/study_state.gd")
const League = preload("res://scripts/league_game.gd")
var checks = 0
var failures = []
func check(value: bool, description: String) -> void:
	checks += 1
	if not value: failures.append(description)
func _initialize() -> void:
	var folder = ProjectSettings.globalize_path("res://../.preview/test-league").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Prueba de Liga"})
	var game = League.new(store)
	check(game.rank_name() == "Unranked", "El jugador empieza sin clasificar")
	check(not game.buy("vision") and game.state()["xp"] == 0, "No se compran aumentos sin XP")
	store.award_xp(10000, "fixture")
	check(game.buy("vision") and game.level("vision") == 1 and game.state()["xp"] == 9900, "Una compra descuenta exactamente su precio")
	store.recovery_blocked = true
	var previous = store.data.duplicate(true)
	check(not game.buy("vision") and store.data == previous, "Una compra fallida revierte XP y nivel")
	store.recovery_blocked = false
	check(game.choose("god", "nix") and game.choose("strategy", "flank") and game.choose("relic", "fang"), "Cambiar los tres componentes de la combinación")
	check(game.buy("mastery") and game.level("mastery") == 1, "Entrenar maestría del dios elegido")
	game.choose("god", "astra")
	check(game.level("mastery") == 0, "La maestría no se comparte con otro dios")
	var weak = game.preparation()["chance"]
	for key in game.KEYS:
		if key == "mastery": game.state()["mastery"][game.state()["god"]] = 10
		else: game.state()["upgrades"][key] = 10
	check(game.preparation()["chance"] > weak and game.preparation()["chance"] <= 0.85, "Los aumentos mejoran la preparación sin garantizar una victoria")
	check(not game.buy("vision"), "Nivel 10 es el límite")
	for seed_value in range(30):
		var result = game.simulate(seed_value)
		var sums = [0, 0, 0]
		var last = -1.0
		for event in result["events"]:
			check(event["time"] >= last, "El relato está ordenado cronológicamente")
			last = event["time"]
			for index in range(3): sums[index] += event.get(["k", "d", "a"][index], 0)
		check(sums == [result["kills"], result["deaths"], result["assists"]], "Las estadísticas coinciden con lo ocurrido en la partida")
		check(game.simulate(seed_value) == result, "La semilla produce un relato reproducible")
	var balance = game.state()["xp"]
	check(game.start_battle(14), "Iniciar partida")
	check(not game.start_battle(15) and not game.choose("god", "bront") and not game.buy("macro"), "No se superponen partidas ni se cambia la combinación en curso")
	var battle = game.state()["battle"]
	check(battle["windows"].size() in [2, 3], "Solo dos o tres oportunidades por partida")
	var cue = battle["windows"][0]
	check(is_equal_approx(float(cue["window"]), 1.3) and is_equal_approx(float(cue["radius"]), 23), "A nivel máximo la ventana dura 1,3 segundos y el círculo aumenta")
	battle["elapsed"] = cue["at"] + cue["windup"] + cue["window"] * 0.5
	var attempt = game.attempt_timing()
	check(attempt["success"] and attempt["perfect"], "Una pulsación centrada en la ventana es perfecta")
	check(game.attempt_timing().is_empty(), "La misma oportunidad no se premia dos veces")
	game.update(100)
	check(game.state()["battle"] == null and game.state()["matches"] == 1, "La partida termina y actualiza la clasificación")
	check(game.state()["xp"] == balance, "Las partidas no generan XP para farmear")
	for seed_value in [16, 17]: game.start_battle(seed_value); game.update(100)
	check(game.rank_name() != "Unranked", "Tras tres partidas aparece el rango")
	check(game.start_battle(19), "Iniciar una partida que se guardará a mitad")
	game.update(6)
	store.save()
	var restored = State.new(folder)
	var resumed = League.new(restored)
	check(resumed.state()["battle"]["elapsed"] == 6 and resumed.state()["battle"]["seed"] == 19, "Cargar conserva el tiempo, la semilla y el relato de la partida")
	resumed.update(100)
	check(resumed.state()["matches"] == 4, "Reanudar registra un único resultado")
	var live = resumed.state()["last_match"]
	var score = [0, 0, 0]
	for event in live["events"]:
		for index in range(3): score[index] += int(event.get(["k", "d", "a"][index], 0))
	check(score == [int(live["kills"]), int(live["deaths"]), int(live["assists"])], "Las oportunidades conservan un marcador coherente al finalizar")
	print(JSON.stringify({"module": "league", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
