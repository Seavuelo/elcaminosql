extends Control

const State = preload("res://scripts/study_state.gd")
const Room = preload("res://scripts/room_view.gd")
const Avatar = preload("res://scripts/avatar_view.gd")
const Worker = preload("res://scripts/sql_worker.gd")
const Layout = preload("res://scripts/room_layout.gd")
const AppIcon = preload("res://scripts/app_icon.gd")
const UI = preload("res://scripts/ui_kit.gd")
const Brand = preload("res://scripts/brand.gd")
const FrontMenu = preload("res://scripts/front_menu.gd")
const Campaign = preload("res://scripts/campaign.gd")
const School = preload("res://scripts/school_view.gd")
const Lecture = preload("res://scripts/lecture_view.gd")
const Audio = preload("res://scripts/audio_service.gd")
const Course = preload("res://scripts/course_data.gd")
const Kashut = preload("res://scripts/kashut_view.gd")
const Notebook = preload("res://scripts/notebook_view.gd")
const Workbench = preload("res://scripts/sql_workbench.gd")
const NexoGame = preload("res://scripts/nexo_game.gd")
const NexoView = preload("res://scripts/nexo_view.gd")
const Settings = preload("res://scripts/settings_view.gd")
const LeagueGame = preload("res://scripts/league_game.gd")
const LeagueView = preload("res://scripts/league_view.gd")
const DataTable = preload("res://scripts/table_view.gd")
const INK = Color("243e39")
const MUTED = Color("64746a")
const GREEN = Color("316b59")
const CREAM = Color("f5efe3")
const GOLD = Color("dcb878")

var state
var room
var overlay: Control
var screen = "room"
var footer: Label
var summary: Label
var day_label: Label
var furniture_list: VBoxContainer
var decorate_button: Button
var light_button: Button
var save_button: Button
var side_filler: Control
var front: Control
var campaign
var sidebar: PanelContainer
var audio
var lecture_view
var chapter_caption: Label
var active_tool
var decorate_toolbar: Button
var league
var application_active = true
var world_toolbar: HBoxContainer
var world_caption: Label
var missions_button: Button
var mission_time = 0.0

func _ready() -> void:
	var args = OS.get_cmdline_user_args()
	if "--sql-worker" in args:
		var index = args.find("--sql-worker")
		if index + 1 < args.size():
			Worker.run_file(args[index + 1])
		get_tree().quit()
		return
	var test_dir = ""
	if ("--self-test" in args or "--visual-check" in args) and "--test-dir" in args:
		test_dir = args[args.find("--test-dir") + 1]
	state = State.new(test_dir)
	if test_dir.is_empty():
		state.import_profile()
	if test_dir.is_empty(): Settings.apply_window(state.data["settings"])
	campaign = Campaign.new(state)
	league = LeagueGame.new(state)
	audio = Audio.new()
	audio.store = state
	add_child(audio)
	get_tree().auto_accept_quit = false
	build_theme()
	build_room()
	if not state.notice.is_empty():
		footer.text = state.notice
	if "--self-test" in args:
		call_deferred("run_self_test")
	else:
		show_front_menu()
		if test_dir.is_empty() and not state.data["settings"]["creator_note_seen"]: show_creator_note()

func style(color: Color, radius: int = 12) -> StyleBoxFlat:
	var box = StyleBoxFlat.new()
	box.bg_color = color
	box.set_corner_radius_all(radius)
	box.content_margin_left = 16
	box.content_margin_right = 16
	box.content_margin_top = 12
	box.content_margin_bottom = 12
	return box

func build_theme() -> void:
	theme = UI.theme()

func label(parent: Node, text: String, font_size: int = 16, color: Color = INK) -> Label:
	var control = Label.new()
	control.text = text
	control.add_theme_font_size_override("font_size", font_size)
	control.add_theme_color_override("font_color", color)
	if font_size >= 24:
		control.add_theme_font_override("font", UI.weight(UI.TITLE, 600))
	parent.add_child(control)
	return control

func paragraph(parent: Node, text: String, font_size: int = 16, color: Color = INK) -> Label:
	var control = label(parent, text, font_size, color)
	control.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return control

func button(parent: Node, text: String, callback: Callable, accent: bool = false) -> Button:
	return UI.action(parent, text, callback, accent)

func spacer(parent: Node) -> Control:
	var control = Control.new()
	control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(control)
	return control

func build_room() -> void:
	var background = ColorRect.new()
	background.color = CREAM
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	var margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + edge, 24)
	add_child(margin)
	var column = VBoxContainer.new()
	margin.add_child(column)
	var header = HBoxContainer.new()
	column.add_child(header)
	var wordmark = Brand.new()
	wordmark.custom_minimum_size = Vector2(320, 40)
	header.add_child(wordmark)
	spacer(header)
	chapter_caption = label(header, "Tu hogar  /  Un lugar para volver", 13, MUTED)
	var bar = HBoxContainer.new()
	world_toolbar = bar
	column.add_child(bar)
	world_caption = label(bar, "Un lugar para aprender y hacerlo tuyo", 17)
	spacer(bar)
	var phone_button = button(bar, "Teléfono", show_phone, true)
	phone_button.icon = load("res://assets/ui/phone.svg")
	decorate_toolbar = button(bar, "Decorar", toggle_decorate)
	missions_button = button(bar, "Tareas", show_missions)
	button(bar, "Controles", show_help)
	var body = HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(body)
	room = Room.new()
	room.state = state
	room.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	room.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(room)
	room.message.connect(set_message)
	room.changed.connect(refresh_summary)
	room.nearby_changed.connect(func(_id, text): set_message("" if text.is_empty() else "E  ·  " + text))
	room.interacted.connect(interact_room)
	var side = PanelContainer.new()
	sidebar = side
	side.custom_minimum_size.x = 280
	body.add_child(side)
	var side_column = VBoxContainer.new()
	side.add_child(side_column)
	var identity = HBoxContainer.new()
	side_column.add_child(identity)
	var avatar = Avatar.new()
	avatar.profile = state.data
	avatar.custom_minimum_size = Vector2(54, 70)
	identity.add_child(avatar)
	var names = VBoxContainer.new()
	names.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	identity.add_child(names)
	paragraph(names, state.data["player_name"], 21)
	label(names, "Tu habitación", 14, MUTED)
	day_label = label(side_column, "", 14, MUTED)
	decorate_button = button(side_column, "Decorar habitación", toggle_decorate, true)
	furniture_list = VBoxContainer.new()
	furniture_list.add_theme_constant_override("separation", 5)
	var furniture_scroll = ScrollContainer.new()
	furniture_scroll.name = "FurnitureScroll"
	furniture_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	furniture_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	furniture_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	side_column.add_child(furniture_scroll)
	furniture_scroll.add_child(furniture_list)
	light_button = button(side_column, "Cambiar luz", toggle_night)
	save_button = button(side_column, "Guardar", save_room)
	summary = paragraph(side_column, "", 14)
	side_filler = Control.new()
	side_filler.size_flags_vertical = Control.SIZE_EXPAND_FILL
	side_column.add_child(side_filler)
	paragraph(side_column, "Los cambios se guardan al colocar cada objeto", 12, MUTED)
	footer = paragraph(column, "WASD para moverte, acércate al escritorio o a la cama para interactuar", 14, MUTED)
	footer.custom_minimum_size.y = 38
	refresh_summary()

func refresh_summary() -> void:
	sidebar.visible = room.editing
	decorate_toolbar.visible = not room is School
	world_caption.text = "Taller de fundamentos" if room is School and campaign.year() == 0 else "Laboratorio de la facultad" if room is School else "Un lugar para aprender y hacerlo tuyo"
	chapter_caption.text = ("Semana introductoria" if campaign.year() == 0 else "Año " + str(campaign.year())) + "  /  Día " + str(campaign.day())
	if campaign.progress()["phase"] == "graduated": chapter_caption.text = "Carrera completada  /  Tu siguiente capítulo"
	day_label.text = "Una tarde en casa  /  " + ("Luz de noche" if state.data["night"] else "Luz de día")
	summary.text = "Carlos está esperando tu ayuda con el stock del almacén" if state.data["completed"].is_empty() else "Primer encargo completado\n+2 reputación en Nexo\nUna planta para tu habitación"
	for child in furniture_list.get_children():
		furniture_list.remove_child(child)
		child.queue_free()
	furniture_list.get_parent().visible = room.editing
	decorate_button.text = "Terminar decoración" if room.editing else "Decorar habitación"
	for control in [light_button, save_button, summary, side_filler]:
		control.visible = not room.editing
	if room.editing:
		label(furniture_list, "ELIGE UN MUEBLE", 12, MUTED)
		for id in state.data["items"]:
			var item_button = button(furniture_list, Layout.CATALOG[id]["name"], room.select_item.bind(id))
			item_button.custom_minimum_size.y = 28
			item_button.add_theme_font_size_override("font_size", 14)
			for mode in ["normal", "hover", "pressed"]:
				var compact = style(Color("e7e7d7") if mode == "normal" else Color("d8dfc9"))
				compact.content_margin_top = 4
				compact.content_margin_bottom = 4
				item_button.add_theme_stylebox_override(mode, compact)
		var actions = HBoxContainer.new()
		furniture_list.add_child(actions)
		button(actions, "Girar", room.rotate_selected).size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button(actions, "Cancelar", room.cancel_move).size_flags_horizontal = Control.SIZE_EXPAND_FILL

func set_message(text: String) -> void:
	footer.text = text

func interact_room(id: String) -> void:
	if id == "desk":
		show_home_desktop()
	elif id == "bed":
		var column = modal("Un descanso merecido", "Guarda tus avances antes de terminar la jornada")
		screen = "rest"
		paragraph(column, "Mañana será otro día para aprender y seguir con tus proyectos" if campaign.progress()["ready_to_leave"] else "Aún puedes terminar tus actividades en la facultad, descansar te permitirá retomar esta misma jornada", 19)
		button(column, "Dormir y guardar", func():
			if campaign.sleep():
				close_overlay()
				refresh_summary()
				audio.sfx("bell")
			else:
				set_message(state.notice), true)
	elif id == "door":
		if campaign.progress()["phase"] == "graduated": show_career()
		else: show_school_arrival()
	elif id == "lamp":
		toggle_night()

func show_front_menu() -> void:
	close_overlay()
	if is_instance_valid(front):
		front.queue_free()
	room.visible = false
	room.enabled = false
	front = FrontMenu.new()
	front.store = state
	add_child(front)
	front.continue_game.connect(enter_world)
	front.new_game.connect(confirm_new_game)
	front.settings.connect(show_settings)
	front.credits.connect(show_licenses)
	front.quit_game.connect(func(): get_tree().quit())
	audio.set_context("menu")
	screen = "menu"
	world_toolbar.visible = false

func enter_world() -> void:
	close_overlay()
	if is_instance_valid(front):
		remove_child(front)
		front.queue_free()
	front = null
	world_toolbar.visible = true
	room.visible = true
	room.enabled = true
	refresh_summary()
	screen = "room"
	if campaign.progress()["location"] == "school":
		if not room is School:
			show_school_arrival()
		else:
			screen = "school"
			audio.set_context("exam" if campaign.day() == 5 else "study")
	else:
		if room is School: switch_world(false)
		audio.set_context("study")

func confirm_new_game() -> void:
	if not state.data["campaign"]["started"]:
		show_character_editor()
		return
	var column = modal("¿Comenzar una nueva historia?", "Tu progreso actual será reemplazado, puedes seguir con tu historia usando Continuar")
	screen = "new_game_confirm"
	button(column, "Volver", close_overlay).grab_focus()
	button(column, "Comenzar nueva historia", show_character_editor)

func show_character_editor() -> void:
	var column = modal("Tu ficha de matrícula", "Dale tu estilo al personaje que te acompañará durante la carrera")
	screen = "character"
	var name_row = HBoxContainer.new()
	column.add_child(name_row)
	var name_field = LineEdit.new()
	name_field.max_length = 30
	name_field.placeholder_text = "Tu nombre"
	name_field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_row.add_child(name_field)
	var gender = OptionButton.new()
	for word in ["Alumno", "Alumna", "Estudiante"]:
		gender.add_item(word)
	gender.custom_minimum_size.x = 200
	name_row.add_child(gender)
	var profile = state.data.duplicate(true)
	var row = HBoxContainer.new()
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	row.add_theme_constant_override("separation", 30)
	column.add_child(row)
	var portrait_column = VBoxContainer.new()
	portrait_column.custom_minimum_size.x = 250
	row.add_child(portrait_column)
	var preview = Avatar.new()
	preview.profile = profile
	preview.size_flags_vertical = Control.SIZE_EXPAND_FILL
	preview.custom_minimum_size = Vector2(240, 270)
	portrait_column.add_child(preview)
	button(portrait_column, "Girar personaje", func():
		var directions = ["down", "left", "up", "right"]
		preview.facing = directions[(directions.find(preview.facing) + 1) % directions.size()]
		preview.queue_redraw())
	var options = GridContainer.new()
	options.columns = 2
	options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	options.add_theme_constant_override("h_separation", 24)
	options.add_theme_constant_override("v_separation", 14)
	row.add_child(options)
	var fields = {"skin": ["Tono de piel", "skin_tones"], "hair": ["Color de pelo", "hair_colors"], "hair_style": ["Peinado", "hair_styles"],
		"eye_color": ["Ojos", "eye_colors"], "shirt": ["Color de ropa", "shirt_colors"], "clothing_style": ["Ropa", "clothing_styles"],
		"pants_color": ["Pantalones", "pants_colors"], "shoe_color": ["Color de zapatos", "shoe_colors"], "shoe_style": ["Zapatos", "shoe_styles"], "backpack_color": ["Mochila", "backpack_colors"]}
	for key in fields:
		var field = VBoxContainer.new()
		field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		field.add_theme_constant_override("separation", 6)
		options.add_child(field)
		UI.text(field, fields[key][0], 14, UI.MUTED)
		var choice = OptionButton.new()
		choice.custom_minimum_size = Vector2(240, 42)
		choice.set_meta("field", key)
		var choices: Array = Course.appearance()[fields[key][1]]
		for option in choices:
			choice.add_item(option[0] if option is Array else option)
		choice.select(clampi(int(profile.get(key, 0)), 0, choices.size() - 1))
		choice.item_selected.connect(func(index): profile[key] = index; preview.queue_redraw())
		field.add_child(choice)
	var error = UI.text(column, "", 14, UI.RED, true)
	button(column, "Preparar mi primer día", func():
		var player_name = name_field.text.strip_edges()
		if player_name.is_empty():
			error.text = "Escribe el nombre que aparecerá en tu carnet"
			name_field.grab_focus()
			return
		var selected = {"player_name": player_name, "gender": ["male", "female", "neutral"][gender.selected]}
		for key in fields:
			selected[key] = profile[key]
		if state.new_run(selected):
			show_admission(0)
		else:
			error.text = state.notice, true)
	name_field.grab_focus()

func show_admission(index: int) -> void:
	var pages: Array = preload("res://scripts/course_data.gd").all()["prologue"]
	if index >= pages.size():
		state.data["campaign"]["prologue_read"] = true
		state.save()
		enter_world()
		return
	var page: Dictionary = pages[index]
	var column = modal(page["title"].capitalize(), "Facultad de Ingeniería Informática")
	screen = "admission"
	var row = HBoxContainer.new()
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(row)
	var art = preload("res://scripts/admission_art.gd").new()
	art.page = index
	art.size_flags_vertical = Control.SIZE_EXPAND_FILL
	row.add_child(art)
	var text_column = UI.scroll(row)
	UI.text(text_column, page["text"], 23, UI.INK, true)
	button(column, "Continuar" if index + 1 < pages.size() else "Mi primer día", show_admission.bind(index + 1), true)

func show_school_arrival() -> void:
	var previous = state.data.duplicate(true)
	state.data["campaign"]["location"] = "school"
	if not state.save():
		state.data = previous
		set_message(state.notice)
		return
	switch_world(true)
	show_day_card()

func switch_world(school: bool) -> void:
	close_overlay()
	var host = room.get_parent()
	var position = room.get_index()
	host.remove_child(room)
	room.queue_free()
	room = School.new() if school else Room.new()
	room.state = state
	if school:
		room.campaign = campaign
	room.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	room.size_flags_vertical = Control.SIZE_EXPAND_FILL
	host.add_child(room)
	host.move_child(room, position)
	room.nearby_changed.connect(func(_id, text): set_message("" if text.is_empty() else "E  ·  " + text))
	room.interacted.connect(interact_school if school else interact_room)
	room.message.connect(set_message)
	room.changed.connect(refresh_summary)
	room.enabled = true
	refresh_summary()
	audio.set_context("exam" if school and campaign.day() == 5 else "study")
	screen = "school" if school else "room"

func show_day_card() -> void:
	if campaign.day_key() in campaign.progress()["seen_days"]:
		return
	campaign.progress()["seen_days"].append(campaign.day_key())
	state.save()
	var curtain = ColorRect.new()
	curtain.color = UI.DEEP
	curtain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(curtain)
	var center = CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	curtain.add_child(center)
	var column = VBoxContainer.new()
	center.add_child(column)
	var heading = UI.text(column, "Semana introductoria" if campaign.year() == 0 else "Año " + str(campaign.year()), 40, UI.PAPER)
	heading.add_theme_font_override("font", UI.weight(UI.TITLE, 600))
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var topic = UI.text(column, Course.lesson(campaign.year(), campaign.day())[0]["title"], 20, UI.PAPER, true)
	topic.custom_minimum_size.x = 640
	topic.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.text(column, "DÍA " + str(campaign.day()), 18, UI.GOLD).horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	room.enabled = false
	var tween = create_tween()
	tween.tween_interval(2)
	tween.tween_property(curtain, "modulate:a", 0.0, 0.45)
	tween.tween_callback(func(): curtain.queue_free(); room.enabled = overlay == null and not is_instance_valid(front))

func interact_school(id: String) -> void:
	if id == "teacher":
		if not campaign.lecture_done():
			show_lecture()
		elif campaign.can_finish():
			var column = modal("Profesor Marco", "Buen trabajo por hoy")
			UI.text(column, "Ya terminaste las actividades, puedes quedarte practicando o despedirte de tus compañeros antes de volver a casa", 21, UI.INK, true)
			button(column, "Gracias, profe", func(): campaign.close_class(); close_overlay(), true)
		else:
			var column = modal("Profesor Marco", "Las actividades siguen en tu computador")
			var pending = campaign.missions().filter(func(item): return not item["done"])
			UI.text(column, pending[0]["detail"] if not pending.is_empty() else "Revisa las tareas en tu computador", 22, UI.INK, true)
			button(column, "Voy a mi computador", close_overlay, true)
	elif id == "pc":
		show_school_desktop()
	elif id == "exit":
		if campaign.leave_school():
			switch_world(false)
	elif id.begins_with("peer:"):
		show_peer(id.trim_prefix("peer:"))

func show_peer(id: String) -> void:
	var peer = {}
	for candidate in Course.all()["peers"]:
		if candidate["id"] == id:
			peer = candidate
	if peer.is_empty():
		return
	var after = campaign.can_finish()
	var words = ""
	if campaign.year() == 0:
		words = Course.all()["intro_dialogues"][peer["name"]]["after" if after else "before"][campaign.day() - 1]
	else:
		words = peer["after" if after else "before"].get(campaign.day_key(), "¿Cómo vas con la clase? Podemos revisar los apuntes antes de irnos")
	var column = modal(peer["name"], "Tu compañera de curso" if id in ["moshi", "sofia", "camila", "valentina"] else "Tu compañero de curso")
	screen = "peer"
	UI.text(column, words, 23, UI.INK, true)
	var community = NexoGame.new(state)
	for item in community.content["posts"]:
		if item["author"] == id and community.available(item) and not community.state()["responses"].has(item["id"]):
			button(column, "Ayudar con su duda", func(): show_nexo(); active_tool.detail(item["id"]), true)
			break
	for item in community.content.get("cases", []):
		if item["author"] == id and community.case_available(item) and not community.state()["completed_cases"].has(item["id"]):
			button(column, "Ayudar con su proyecto", show_nexo_case.bind(item["id"]), true)
			break
	if id not in state.data["nexo"]["contacts"]:
		button(column, "Agregar a Nexo", func():
			state.data["nexo"]["contacts"].append(id)
			state.save()
			show_peer(id), true)
	else:
		UI.text(column, "Ya están conectados en Nexo", 14, UI.GREEN)
	button(column, "Nos vemos", func():
		close_overlay()
		if after and room is School:
			room.departure(id))

func show_school_desktop() -> void:
	if not campaign.lecture_done():
		var column = modal("Antes de comenzar", "Marco está preparando la clase")
		UI.text(column, "Primero acércate al profesor para escuchar la explicación, después tendrás las actividades disponibles en tu computador", 22, UI.INK, true)
		button(column, "Voy a hablar con Marco", close_overlay, true)
		return
	var column = modal("Tu espacio de estudio", "Primero comprende la idea, después compruébala con tus datos")
	screen = "desktop"
	var list = UI.scroll(column)
	UI.heading(list, "Clase de hoy", Course.lesson(campaign.year(), campaign.day())[0]["title"])
	var grid = GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 14)
	grid.add_theme_constant_override("v_separation", 14)
	list.add_child(grid)
	var entries = [["Repasar la clase", "Vuelve a la pizarra de Marco y escucha la explicación", "library", show_lecture]]
	if campaign.year() == 0:
		entries.append(["Kashut", "Diez preguntas para descubrir qué entendiste y qué repasar", "activities", show_kashut])
		if campaign.day() >= 2: entries.append(["Taller de modelamiento", "Construye tu modelo y revisa la tarea actual", "model", show_modeler])
	else:
		entries.append(["Evaluación del viernes" if campaign.day() == 5 else "Laboratorio SQL", "Prueba tus consultas y entrega cuando estés conforme", "sql", show_course_sql])
	entries.append_array([["Cuaderno y apuntes", "Consulta explicaciones, dibujos y tus notas", "notebook", show_notebook], ["Tu partida actual", "Revisa tus notas y el camino que llevas recorrido", "grades", show_grades]])
	for entry in entries:
		var card = preload("res://scripts/feature_card.gd").new()
		card.title = entry[0]
		card.description = entry[1]
		card.kind = entry[2]
		card.primary = entry[2] in ["sql", "activities"]
		card.action = entry[3]
		grid.add_child(card)
	if campaign.year() == 0 and campaign.day() >= 2:
		var requirements = campaign.model_checklist()
		var count = requirements.filter(func(item): return item[1]).size()
		UI.text(list, "Taller  ·  %s de %s requisitos listos" % [count, requirements.size()], 17, UI.GREEN, true)
	if campaign.can_finish():
		UI.text(list, "Actividades completadas, habla con Marco para cerrar la jornada y vuelve a casa por la puerta cuando quieras", 19, UI.GREEN, true)

func show_lecture(lesson_year: int = -1, lesson_day: int = -1) -> void:
	if lesson_year < 0: lesson_year = campaign.year()
	if lesson_day < 0: lesson_day = campaign.day()
	var current = lesson_year == campaign.year() and lesson_day == campaign.day()
	var column = modal("La clase de Marco", ("Semana introductoria" if lesson_year == 0 else "Año " + str(lesson_year)) + "  /  Día " + str(lesson_day))
	screen = "lecture"
	lecture_view = Lecture.new()
	lecture_view.store = state
	lecture_view.audio = audio
	lecture_view.year = lesson_year
	lecture_view.day = lesson_day
	column.add_child(lecture_view)
	lecture_view.completed.connect(func():
		if not current:
			if campaign.complete_lecture(lesson_year, lesson_day): show_library()
			else: set_message(state.notice)
		elif campaign.complete_lecture():
			close_overlay()
			audio.sfx("success"))

func show_kashut() -> void:
	var column = modal("Kashut", "Diez preguntas para comprobar lo que entendiste")
	screen = "kashut"
	var view = Kashut.new()
	view.store = state
	view.campaign = campaign
	view.audio = audio
	view.day = campaign.day()
	column.add_child(view)
	view.closed.connect(close_overlay)
	active_tool = view

func show_notebook() -> void:
	var column = modal("Tu cuaderno", "Ideas, ejemplos y tus propios apuntes")
	screen = "notebook"
	var view = Notebook.new()
	view.store = state
	column.add_child(view)
	active_tool = view

func show_grades() -> void:
	var column = modal("Mis notas", "Cada intento forma parte de lo que aprendiste")
	screen = "grades"
	var rows = []
	for record in campaign.progress()["grades"]:
		rows.append([record["year"], record["attempt"], "%.1f" % float(record["grade"]), "Aprobado" if record["grade"] >= 4 else "Para reforzar"])
	if rows.is_empty():
		UI.text(column, "Tus primeras notas aparecerán después de la evaluación del viernes", 20, UI.GREEN, true)
	else:
		var table = DataTable.new()
		table.size_flags_vertical = Control.SIZE_EXPAND_FILL
		column.add_child(table)
		table.set_data(["Año", "Intento", "Nota", "Resultado"], rows)

func show_course_sql(free: bool = false) -> void:
	var column = modal("Tu laboratorio", "Una consulta puede escribirse de distintas maneras, lo importante es lo que hace")
	screen = "course_sql"
	var view = Workbench.new()
	view.store = state
	view.campaign = campaign
	view.audio = audio
	view.sandbox = free
	column.add_child(view)
	active_tool = view

func show_modeler() -> void:
	var column = modal("Mi modelo de datos", "Diseña la información y comprueba cómo se relaciona")
	screen = "modeler"
	var script = load("res://scripts/modeler_view.gd")
	if script == null:
		close_overlay()
		set_message("No se pudo abrir el modelo de datos")
		return
	var view = script.new()
	view.store = state
	view.campaign = campaign
	view.audio = audio
	column.add_child(view)
	active_tool = view

func show_home_desktop() -> void:
	var column = modal("Tu escritorio", "Un lugar para experimentar y avanzar con tus proyectos")
	screen = "home_desktop"
	var list = UI.scroll(column)
	var grid = GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 14)
	grid.add_theme_constant_override("v_separation", 14)
	list.add_child(grid)
	for entry in [
		["Nexo", "Contactos, encargos y proyectos que crecen contigo", "nexo", show_nexo],
		["Laboratorio libre", "Tu propia base para experimentar sin afectar las clases", "sql", show_course_sql.bind(true)],
		["Tu cuaderno", "Explicaciones, ejemplos y tus apuntes personales", "notebook", show_notebook],
		["Desafíos e investigación", "Filtra, ordena y encuentra errores siguiendo las pistas", "activities", show_activities],
		["Muebles y equipo", "Convierte el trabajo de tus proyectos en un espacio propio", "home", show_home_shop],
		["Tu modelo de datos", "Diseña entidades, relaciones y comprueba tus claves", "model", show_modeler],
		["Biblioteca de clases", "Vuelve a escuchar a Marco y repasa a tu ritmo", "library", show_library],
		["Tu partida actual", "Consulta tus notas y los intentos que forman tu camino", "grades", show_grades],
		["Tu siguiente capítulo", "Presenta un proyecto y revisa tus oportunidades", "career", show_career]]:
		var card = preload("res://scripts/feature_card.gd").new()
		card.title = entry[0]
		card.description = entry[1]
		card.kind = entry[2]
		card.primary = entry[2] == "nexo"
		card.action = entry[3]
		grid.add_child(card)

func show_library() -> void:
	var column = modal("Tu biblioteca de clases", "Puedes volver a escuchar los fundamentos y repasar lo que ya estudiaste")
	screen = "library"
	var list = UI.scroll(column)
	for year in range(5):
		UI.heading(list, "Fundamentos" if year == 0 else "Carrera", "Semana introductoria" if year == 0 else "Año " + str(year))
		for day in range(1, 6):
			var available = year == 0 or year <= int(campaign.progress()["year"])
			var title = Course.lesson(year, day)[0]["title"]
			var button = button(list, "Día %s  ·  %s" % [day, title], show_lecture.bind(year, day))
			button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			button.disabled = not available

func show_skip_intro() -> void:
	var column = modal("Los fundamentos son opcionales", "Puedes entrar al primer año y volver a estas clases desde tu escritorio")
	screen = "skip_intro"
	UI.text(column, "Si estás empezando desde cero, los cinco días de fundamentos te ayudarán a comprender los datos, sus tipos, las claves y las relaciones", 22, UI.INK, true)
	button(column, "Seguir con los fundamentos", close_overlay, true).grab_focus()
	button(column, "Entrar al primer año", func():
		if campaign.skip_intro():
			close_overlay()
			if campaign.progress()["location"] == "school":
				switch_world(true)
				show_day_card()
			else:
				refresh_summary()
		else: set_message(state.notice)
	)

func show_creator_note() -> void:
	var column = modal("Antes de empezar", "Un juego personal hecho por Seavuelo")
	screen = "creator_note"
	var note = preload("res://scripts/creator_note_view.gd").new()
	note.store = state
	column.add_child(note)
	button(column, "Gracias, vamos a jugar", close_overlay, true)

func show_missions() -> void:
	var column = modal("Tu próxima meta", "Cada actividad aparece cuando llega su momento")
	screen = "missions"
	campaign.read_missions()
	var list = UI.scroll(column)
	for item in campaign.missions():
		var card = UI.card(list, Color("e1e8d6") if item["done"] else Color("eee2c7"))
		UI.text(card, ("Listo  ·  " if item["done"] else "Pendiente  ·  ") + item["title"], 21, UI.GREEN if item["done"] else UI.INK, true)
		UI.text(card, item["detail"], 16, UI.MUTED, true)

func show_pause() -> void:
	var column = modal("Un momento de calma", "Tu historia se guarda en este equipo")
	screen = "pause"
	button(column, "Seguir jugando", close_overlay, true).grab_focus()
	button(column, "Ajustes", show_settings)
	if campaign.year() == 0: button(column, "Semana introductoria opcional", show_skip_intro)
	button(column, "Volver a la portada", show_front_menu)
	button(column, "Guardar y salir", func():
		if state.save(): get_tree().quit()
		else: set_message(state.notice)
	)

func show_career() -> void:
	var column = modal("Tu siguiente capítulo", "El trabajo que hiciste también habla por ti")
	screen = "career"
	var view = preload("res://scripts/career_view.gd").new()
	view.store = state
	column.add_child(view)
	active_tool = view

func show_activities() -> void:
	var column = modal("Otra forma de aprender", "Pequeños desafíos y problemas que necesitan una mirada más atenta")
	screen = "activities"
	var view = preload("res://scripts/activities_view.gd").new()
	view.store = state
	view.case_requested.connect(show_nexo_case)
	column.add_child(view)
	active_tool = view

func show_home_shop() -> void:
	var column = modal("Un hogar que crece contigo", "Madera, plantas y un rincón para tus próximos proyectos")
	screen = "home_shop"
	var view = preload("res://scripts/home_shop_view.gd").new()
	view.store = state
	view.player = room.player
	view.purchased.connect(func(): room.queue_redraw(); refresh_summary())
	column.add_child(view)
	active_tool = view

func show_settings() -> void:
	var column = modal("A tu manera", "Elige cómo quieres ver y escuchar tu historia")
	screen = "settings"
	var view = Settings.new()
	view.store = state
	view.audio = audio
	column.add_child(view)
	active_tool = view

func toggle_decorate() -> void:
	if room is School:
		return
	room.editing = not room.editing
	room.path.clear()
	room.cancel_move()
	refresh_summary()
	set_message("Elige un mueble, muévelo con el cursor y haz clic para colocarlo" if room.editing else "Muévete con WASD, acércate a un objeto y pulsa E")

func toggle_night() -> void:
	state.data["night"] = not state.data["night"]
	save_room()
	refresh_summary()

func save_room() -> void:
	state.save()
	set_message(state.notice)

func close_overlay() -> void:
	if is_instance_valid(overlay):
		remove_child(overlay)
		overlay.queue_free()
	overlay = null
	active_tool = null
	screen = "school" if room is School else "room"
	room.enabled = not is_instance_valid(front)
	world_toolbar.visible = not is_instance_valid(front)

func modal(title: String, subtitle: String) -> VBoxContainer:
	close_overlay()
	room.path.clear()
	room.enabled = false
	world_toolbar.visible = false
	overlay = Control.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(overlay)
	var shade = ColorRect.new()
	shade.color = Color(0.04, 0.10, 0.09, 0.79)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.add_child(shade)
	var center = MarginContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge in ["left", "right"]:
		center.add_theme_constant_override("margin_" + edge, 40)
	for edge in ["top", "bottom"]:
		center.add_theme_constant_override("margin_" + edge, 28)
	overlay.add_child(center)
	var panel = PanelContainer.new()
	center.add_child(panel)
	var column = VBoxContainer.new()
	column.add_theme_constant_override("separation", 8)
	panel.add_child(column)
	var header = HBoxContainer.new()
	column.add_child(header)
	label(header, title, 26, GREEN)
	spacer(header)
	button(header, "Cerrar", close_overlay)
	paragraph(column, subtitle, 14, MUTED)
	return column

func show_phone() -> void:
	var column = modal("Tu teléfono", "Tus contactos, tus proyectos y una partida cuando necesitas una pausa")
	screen = "phone"
	var center = CenterContainer.new()
	center.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(center)
	var device = PanelContainer.new()
	device.custom_minimum_size = Vector2(440, 510)
	var frame = UI.box(Color("263c37"), 34, 12)
	frame.border_color = Color("7f8f7e")
	frame.set_border_width_all(2)
	device.add_theme_stylebox_override("panel", frame)
	center.add_child(device)
	var glass = PanelContainer.new()
	glass.add_theme_stylebox_override("panel", UI.box(Color("365f50"), 26, 20))
	device.add_child(glass)
	var home = VBoxContainer.new()
	glass.add_child(home)
	var top = HBoxContainer.new()
	home.add_child(top)
	var time = Time.get_time_dict_from_system()
	UI.text(top, "%02d:%02d" % [time["hour"], time["minute"]], 18, UI.WHITE)
	UI.fill(top)
	UI.text(top, "● ● ●   100%", 12, Color("cad8bf"))
	UI.fill(home, true)
	var greeting = UI.text(home, "Un mundo en tu bolsillo", 25, UI.WHITE, true)
	greeting.add_theme_font_override("font", UI.weight(UI.TITLE, 600))
	UI.text(home, state.data["player_name"], 15, Color("d6dfc7"))
	var apps = HBoxContainer.new()
	home.add_child(apps)
	var nexo = button(apps, "\n\n\nNEXO\nConecta y comparte", show_nexo, true)
	nexo.set_script(AppIcon)
	nexo.custom_minimum_size = Vector2(178, 180)
	nexo.add_theme_font_size_override("font_size", 15)
	nexo.add_theme_stylebox_override("normal", UI.box(Color("214c40"), 20, 12))
	var game = button(apps, "\n\n\nLIGA DE DIOSES\nTu próxima jugada", show_league)
	game.set_script(AppIcon)
	game.kind = "league"
	game.custom_minimum_size = Vector2(178, 180)
	game.add_theme_font_size_override("font_size", 15)
	game.add_theme_stylebox_override("normal", UI.box(UI.GOLD, 20, 12))
	var stats = HBoxContainer.new()
	home.add_child(stats)
	var learning = UI.card(stats, Color("284c40"))
	learning.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.text(learning, "%s XP" % int(state.data["league"]["xp"]), 18, UI.GOLD)
	UI.text(learning, "Para tus aumentos", 12, Color("d6dfc7"))
	var social = UI.card(stats, Color("284c40"))
	social.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.text(social, "%s contactos" % state.data["nexo"]["contacts"].size(), 18, UI.WHITE)
	UI.text(social, "En tu red Nexo", 12, Color("d6dfc7"))
	UI.fill(home, true)
	var indicator = CenterContainer.new()
	home.add_child(indicator)
	var line = ColorRect.new()
	line.color = Color("c9d6bd")
	line.custom_minimum_size = Vector2(78, 3)
	indicator.add_child(line)

func show_league() -> void:
	var column = modal("Tu pausa entre clases", "Liga de Dioses  /  Un poco de estrategia también viene bien")
	screen = "league"
	var view = LeagueView.new()
	view.league = league
	view.audio = audio
	column.add_child(view)
	active_tool = view

func show_nexo() -> void:
	var column = modal("Nexo", "Tu red empieza con las personas a quienes ayudas")
	screen = "nexo"
	var view = NexoView.new()
	view.game = NexoGame.new(state)
	view.case_requested.connect(show_nexo_case)
	view.career_requested.connect(show_career)
	column.add_child(view)
	active_tool = view

func show_nexo_case(id: String) -> void:
	var game = NexoGame.new(state)
	var task = preload("res://scripts/nexo_sql.gd").case_data(id)
	if task.is_empty() or not game.case_available(task): return
	var column = modal("Tu encargo de Nexo", "Prueba en una copia, comprueba los límites y entrega cuando estés conforme")
	screen = "nexo_sql"
	var view = Workbench.new()
	view.store = state
	view.campaign = campaign
	view.audio = audio
	view.case_id = id
	view.nexo = game
	column.add_child(view)
	active_tool = view
	UI.action(column, "Volver a Nexo", show_nexo)

func show_help() -> void:
	var column = modal("Controles", "Explora la facultad, estudia a tu ritmo y vuelve a casa al terminar la jornada")
	screen = "help"
	for text in ["CAMINAR  /  WASD mueve al personaje por la habitación", "INTERACTUAR  /  Acércate a un objeto y presiona E", "DECORAR  /  Elige un mueble en el panel, mueve el cursor y haz clic para colocarlo", "GIRAR Y CANCELAR  /  R para girar, Esc o clic derecho para cancelar el movimiento", "COMPUTADOR  /  Prueba y entrega consultas SQL", "TELÉFONO  /  Tus contactos, proyectos y juegos"]:
		paragraph(column, text, 18)
	paragraph(column, "En la facultad, Tareas muestra tu siguiente objetivo, sus avisos dejan de parpadear después de revisarlos", 15, MUTED)
	button(column, "Licencias y componentes", show_licenses)

func show_licenses() -> void:
	var column = modal("Licencias", "Godot y el complemento SQLite conservan sus avisos originales")
	screen = "licenses"
	var text = TextEdit.new()
	text.editable = false
	text.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text.text = Engine.get_license_text() + "\n\nGODOT-SQLITE\n\n" + FileAccess.get_file_as_string("res://addons/godot-sqlite/LICENSE.md")
	text.text += "\n\nGODOT THIRD-PARTY COPYRIGHTS\n" + JSON.stringify(Engine.get_copyright_info(), "\t")
	text.text += "\n\nGODOT THIRD-PARTY LICENSES\n" + JSON.stringify(Engine.get_license_info(), "\t")
	text.text += "\n\nMÚSICA Y NARRACIÓN\n" + FileAccess.get_file_as_string("res://data/credits.txt")
	for font in ["inter", "fraunces", "jetbrainsmono"]:
		text.text += "\n\n" + font.to_upper() + "\n" + FileAccess.get_file_as_string("res://assets/fonts/" + font + "-OFL.txt")
	column.add_child(text)

func _input(event: InputEvent) -> void:
	if state == null or not event is InputEventKey or not event.pressed or event.echo:
		return
	if screen == "admission" and event.keycode == KEY_ESCAPE:
		state.data["campaign"]["prologue_read"] = true
		state.save()
		enter_world()
		get_viewport().set_input_as_handled()
		return
	if screen == "lecture" and is_instance_valid(lecture_view):
		if event.keycode in [KEY_SPACE, KEY_ENTER, KEY_RIGHT]:
			lecture_view.step(1)
			get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_LEFT:
			lecture_view.step(-1)
			get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_F7:
			lecture_view.toggle_voice()
			get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_F8:
			lecture_view.repeat_voice()
			get_viewport().set_input_as_handled()
			return
	if event.keycode == KEY_ESCAPE:
		if is_instance_valid(active_tool) and active_tool.has_method("handle_escape") and active_tool.handle_escape():
			get_viewport().set_input_as_handled()
			return
		if overlay != null:
			close_overlay()
		elif not room.selected.is_empty():
			room.cancel_move()
		elif room.editing:
			toggle_decorate()
		elif not is_instance_valid(front):
			show_pause()
		get_viewport().set_input_as_handled()
	elif overlay == null and event.keycode == KEY_R and room.editing:
		room.rotate_selected()
		get_viewport().set_input_as_handled()
	elif overlay == null and event.physical_keycode == KEY_E:
		room.interact()
		get_viewport().set_input_as_handled()

func _process(delta: float) -> void:
	mission_time += delta
	if is_instance_valid(missions_button) and world_toolbar.visible:
		var unread = campaign.unread_missions()
		missions_button.text = "Tareas  ●" if unread else "Tareas"
		missions_button.modulate.a = 0.78 + sin(mission_time * 3) * 0.22 if unread else 1.0
	if league != null and application_active and not is_instance_valid(front):
		league.update(delta, screen == "league" and is_instance_valid(active_tool) and active_tool.phase == "battle")

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT: application_active = false
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN: application_active = true
	if what == NOTIFICATION_WM_CLOSE_REQUEST and state != null:
		if state.save():
			get_tree().quit()
		else:
			set_message(state.notice + ", el juego sigue abierto para que puedas intentarlo otra vez")

func run_self_test() -> void:
	var test_script = load("res://tests/smoke.gd")
	if test_script == null or not test_script.can_instantiate():
		get_tree().quit(1)
		return
	var test = test_script.new()
	add_child(test)
	await test.run(self)
