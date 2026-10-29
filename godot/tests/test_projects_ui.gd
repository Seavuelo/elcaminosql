extends SceneTree
var app
var failures = []
func _initialize():
	create_timer(55).timeout.connect(func(): print("PROJECT_TEST_TIMEOUT"); quit(1))
	call_deferred("run")
func run():
	app = load("res://scenes/main.tscn").instantiate()
	root.add_child(app)
	current_scene = app
	app.state.new_run({"player_name": "Lucía"})
	app.enter_world()
	app.application_active = false
	var content = JSON.parse_string(FileAccess.get_file_as_string("res://data/nexo.json"))
	for item in content["cases"]: app.campaign.progress()["lectures"].append(item["lesson"])
	for evidence in ["reservas", "totales"]: app.state.data["activities"]["investigations"][evidence] = {"read": [], "diagnosed": true}
	app.show_nexo()
	app.active_tool.inbox()
	for item in content["cases"]:
		app.show_nexo_case(item["id"])
		var view = app.active_tool
		if view.service.pid > 0: await view.service.finished
		if item["id"] == "equipo_agenda":
			view.run_query(true)
			await view.service.finished
			if app.state.data["nexo"]["completed_cases"].has(item["id"]): failures.append("La consulta defectuosa fue aceptada")
		view.editor.text = item["sql"]
		view.run_query(true)
		await view.service.finished
		if not app.state.data["nexo"]["completed_cases"].has(item["id"]): failures.append({"id": item["id"], "status": view.status.text})
	app.show_nexo()
	app.active_tool.projects()
	app.active_tool.contacts()
	app.free()
	await create_timer(0.15).timeout
	print(JSON.stringify({"module": "projects_ui", "deliveries": content["cases"].size(), "failures": failures}))
	quit(0 if failures.is_empty() else 1)
