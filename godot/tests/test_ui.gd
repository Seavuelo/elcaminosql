extends SceneTree
var app
var checks = 0
var failures = []
func _initialize():
	create_timer(12).timeout.connect(func(): print("UI_TEST_TIMEOUT"); quit(1))
	call_deferred("run")
func check(value: bool, description: String):
	checks += 1
	if not value:
		failures.append(description)
		print("FAILED ", description)
func find_button(node: Node, text: String) -> Button:
	if node is Button and node.text == text: return node
	for child in node.get_children():
		var found = find_button(child, text)
		if found != null: return found
	return null
func find_field(node: Node, text: String) -> LineEdit:
	if node is LineEdit and node.get_meta("model_field", "") == text: return node
	for child in node.get_children():
		var found = find_field(child, text)
		if found != null: return found
	return null
func key(code: Key):
	var event = InputEventKey.new()
	event.pressed = true
	event.keycode = code
	event.physical_keycode = code
	app._input(event)
func type_text(field: LineEdit, value: String):
	field.grab_focus()
	field.clear()
	for character in value:
		var event = InputEventKey.new()
		event.pressed = true
		event.unicode = character.unicode_at(0)
		event.keycode = OS.find_keycode_from_string(character.to_upper())
		event.physical_keycode = event.keycode
		root.push_input(event)
	await process_frame
func run():
	app = load("res://scenes/main.tscn").instantiate()
	root.add_child(app)
	current_scene = app
	app.application_active = false
	check(app.screen == "menu", "El juego abre en la portada")
	app.show_creator_note()
	app.close_overlay()
	check(app.state.data["settings"]["creator_note_seen"], "La nota del creador queda marcada después de leerla")
	app.state.new_run({"player_name": "Persona nueva"})
	app.show_admission(0)
	key(KEY_ESCAPE)
	check(app.screen == "room" and app.room.enabled, "Esc permite salir del prólogo sin cerrar el juego")
	check(app.world_toolbar.visible, "Los controles vuelven al entrar al mundo")
	var old_position = app.room.player
	var click = InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = Vector2(300, 300)
	app.room._gui_input(click)
	check(app.room.player == old_position and app.room.path.is_empty(), "El clic no mueve al personaje")
	app.room.player = Vector2(-0.1, 6.7)
	app.room.update_nearby()
	app.room.interact()
	check(app.screen == "school" and app.room.seats.size() == 5 and app.room.actors.size() == 4, "La puerta lleva a una sala introductoria con cinco puestos")
	check(app.room.occupied(app.room.teacher_desk + Vector2(1.6, 1.65)), "El cuerpo del profesor tiene colisión")
	check(app.campaign.unread_missions(), "Una tarea nueva tiene aviso")
	app.campaign.read_missions()
	check(not app.campaign.unread_missions(), "Leer una tarea detiene su aviso")
	app.show_school_desktop()
	check(find_button(app.overlay, "Kashut") == null, "Las actividades se explican antes de abrirlas")
	app.close_overlay()
	app.show_lecture()
	check(not app.world_toolbar.visible, "Controles y tareas se ocultan durante las clases")
	var parts = app.lecture_view.boards[0]["speech_parts"].size()
	app.audio.stop_voice()
	check(app.lecture_view.boards[0]["speech_parts"].size() == parts and parts > 0, "Parar la voz no vacía el contenido de la clase")
	key(KEY_ESCAPE)
	check(not app.campaign.lecture_done() and app.room.enabled, "Esc conserva una clase pendiente y vuelve al aula")
	app.campaign.complete_lecture()
	check(app.campaign.unread_missions(), "Completar la clase anuncia la actividad siguiente")
	app.show_modeler()
	var view = app.active_tool
	view.entity_form()
	await process_frame
	await process_frame
	await type_text(find_field(view.dialog, "Nombre de la entidad"), "ESTUDIANTE")
	check(view.draft["name"] == "ESTUDIANTE" and app.screen == "modeler", "Se puede escribir ESTUDIANTE sin que la T abra tareas")
	var tabs = view.dialog.find_children("*", "TabContainer", true, false)[0]
	tabs.current_tab = 1
	await type_text(view.attr_fields["name"], "id")
	view.attr_fields["type"].select(1)
	view.attr_fields["type"].item_selected.emit(1)
	view.attr_fields["uid"].button_pressed = true
	check(not view.attr_fields["length"].editable and view.attr_fields["precision"].editable, "Los campos de tamaño dependen del tipo elegido")
	find_button(view.dialog, "Guardar atributo y añadir otro").pressed.emit()
	check(view.draft["attributes"].size() == 1 and view.attr_fields["name"].text.is_empty(), "Guardar atributo permite añadir el siguiente inmediatamente")
	check(app.campaign.progress()["model"]["entities"].is_empty(), "El borrador no reemplaza el modelo antes de guardar la tabla")
	find_button(view.dialog, "Guardar tabla").pressed.emit()
	if view.model.entity("ESTUDIANTE").is_empty():
		print("FORM_ERROR ", view.form_error.text, " DRAFT ", JSON.stringify(view.draft))
		app.free()
		quit(1)
		return
	check(view.model.entity("ESTUDIANTE")["attributes"][0]["uid"] and not is_instance_valid(view.dialog), "El botón guarda entidad, atributos y UID")
	view.entity_form("ESTUDIANTE")
	key(KEY_ESCAPE)
	check(app.screen == "modeler" and not is_instance_valid(view.dialog), "El primer Esc cierra propiedades y conserva el lienzo")
	key(KEY_ESCAPE)
	check(app.screen == "school", "El segundo Esc vuelve al aula")
	var school = app.room
	app.room.departure("moshi")
	check(app.campaign.progress()["departures"][app.campaign.day_key()]["moshi"] == "packing", "Moshi empieza a ordenar sus cosas y se guarda su despedida")
	app.show_front_menu()
	app.enter_world()
	check(app.room == school, "Continuar conserva los actores y su animación en el aula")
	app.show_front_menu()
	app.state.new_run({"player_name": "Nueva historia"})
	app.enter_world()
	check(app.room.get_script() != load("res://scripts/school_view.gd") and app.screen == "room", "Una partida nueva desde el aula empieza en casa")
	app.show_settings()
	check(app.active_tool.resolution.item_count >= 5, "Los ajustes incluyen las resoluciones principales")
	check(not app.world_toolbar.visible, "Los controles del mundo se ocultan en ajustes")
	app.close_overlay()
	app.campaign.progress()["lectures"].append("3_1")
	app.show_activities()
	app.active_tool.puzzle("prediccion", true)
	var prediction = app.active_tool
	find_button(prediction, "total 4  /  registrados 3  /  devueltos 2").button_pressed = true
	check(prediction.answers == [2], "La elección del reto registra una sola alternativa")
	find_button(prediction, "Comprobar mi solución").pressed.emit()
	check("prediccion" in app.state.data["activities"]["completed"], "El botón comprueba la predicción y guarda su recompensa")
	app.show_nexo()
	find_button(app.active_tool, "Empezar con mi perfil").pressed.emit()
	check(app.state.data["nexo"]["onboarded"], "La bienvenida de Nexo se completa y persiste")
	app.close_overlay()
	app.show_league()
	app.active_tool.start_match()
	check(app.league.state()["battle"] != null, "El teléfono inicia una partida nativa de Liga")
	app.close_overlay()
	app.league.update(100)
	check(app.league.state()["last_match"] != null, "La simulación puede completarse fuera del teléfono")
	app.free()
	await process_frame
	await create_timer(0.15).timeout
	print(JSON.stringify({"module": "ui", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
