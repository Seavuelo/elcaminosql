extends Node
const Course = preload("res://scripts/course_data.gd")
const State = preload("res://scripts/study_state.gd")
var app
var checks = []
func check(value: bool, description: String):
	checks.append({"ok": value, "description": description})
	print(("PASS " if value else "FAIL ") + description)
func capture(name: String):
	await get_tree().process_frame
	await get_tree().process_frame
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		check(get_viewport().get_texture().get_image().save_png(app.state.directory.path_join(name + ".png")) == OK, "Captura " + name)
func run(game):
	app = game
	get_tree().create_timer(80).timeout.connect(func(): get_tree().quit(1))
	check(ClassDB.class_exists("SQLite"), "SQLite nativo disponible sin Python")
	check(app.state.new_run({"player_name": "Prueba portátil"}), "Partida nueva aislada")
	app.enter_world()
	app.application_active = false
	await capture("01-habitacion")
	var lessons = 0
	var clips = {}
	for year in range(5):
		for day in range(1, 6):
			var lesson = Course.lesson(year, day)
			check(not lesson.is_empty(), "Clase %s/%s incluida" % [year, day])
			lessons += 1
			for board in lesson:
				for part in board.get("speech_parts", []):
					if not part.get("audio", "").is_empty(): clips[part["audio"]] = true
	for path in clips: check(ResourceLoader.exists(path), "Audio " + path.get_file())
	check(clips.size() == 287, "Las 287 narraciones aprobadas están incluidas")
	for file in ["nexo.json", "activities.json", "defense.json", "university.sql", "credits.txt", "portfolio/verificar.py"]:
		check(not FileAccess.get_file_as_string("res://data/" + file).is_empty(), "Contenido " + file)
	check(not FileAccess.get_file_as_string("res://addons/godot-sqlite/LICENSE.md").is_empty(), "Licencia SQLite")
	for method in ["show_phone", "show_nexo", "show_league", "show_home_desktop", "show_home_shop", "show_notebook", "show_activities", "show_modeler", "show_career", "show_settings", "show_help"]:
		app.call(method)
		await capture(method)
		check(is_instance_valid(app.overlay), "Interfaz " + method)
	app.show_lecture(0, 1)
	await capture("clase-introductoria")
	app.close_overlay()
	app.campaign.progress()["lectures"].append("1_2")
	app.show_nexo_case("almacen_1")
	var view = app.active_tool
	if view.service.pid > 0: await view.service.finished
	view.editor.text = "SELECT nombre, stock FROM producto WHERE stock <= 5"
	view.run_query(true)
	await view.service.finished
	check(not app.state.data["nexo"]["completed_cases"].has("almacen_1"), "El límite incorrecto no entrega el encargo")
	view.editor.text = "SELECT nombre, stock FROM producto WHERE stock < 5"
	view.run_query(true)
	await view.service.finished
	check(app.state.data["nexo"]["completed_cases"].has("almacen_1"), "Consulta validada por el proceso SQLite exportado")
	var xp = app.state.data["league"]["xp"]
	view.run_query(true)
	await view.service.finished
	check(app.state.data["league"]["xp"] == xp, "Recompensa única")
	check(view.service.pid == -1, "Proceso SQL finalizado")
	app.close_overlay()
	var restored = State.new(app.state.directory)
	check(restored.data["nexo"]["completed_cases"].has("almacen_1"), "Entrega conservada al recargar")
	var failed = checks.filter(func(item): return not item["ok"])
	var report = FileAccess.open(app.state.directory.path_join("report.json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"success": failed.is_empty(), "version": ProjectSettings.get_setting("application/config/version"), "checks": checks}, "\t"))
	report.close()
	app.audio.queue_free()
	await get_tree().create_timer(0.15).timeout
	get_tree().quit(0 if failed.is_empty() else 1)
