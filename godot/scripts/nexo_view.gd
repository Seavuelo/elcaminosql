extends VBoxContainer
signal case_requested(id)
signal career_requested
const UI = preload("res://scripts/ui_kit.gd")
const Avatar = preload("res://scripts/avatar_view.gd")
const Course = preload("res://scripts/course_data.gd")
var game
var body: VBoxContainer
var status: Label
var selected = -1
var publish_button: Button
var navigation: HBoxContainer
func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	var banner = UI.card(self, UI.GREEN)
	banner.get_parent().add_theme_stylebox_override("panel", UI.box(UI.GREEN, 16, 12))
	var row = HBoxContainer.new()
	banner.add_child(row)
	var avatar = Avatar.new()
	avatar.profile = game.store.data
	avatar.custom_minimum_size = Vector2(56, 64)
	row.add_child(avatar)
	var info = VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(info)
	UI.text(info, game.store.data["player_name"], 26, UI.WHITE).add_theme_font_override("font", UI.weight(UI.TITLE, 650))
	var phase = game.store.data["campaign"]["phase"]
	var chapter = "Carrera completada" if phase == "graduated" else "Semana introductoria" if phase == "intro" else "Año %s" % int(game.store.data["campaign"]["year"])
	UI.text(info, "Ingeniería Informática  ·  " + chapter, 15, Color("d9e4cd"))
	navigation = HBoxContainer.new()
	add_child(navigation)
	UI.action(navigation, "Comunidad", feed, true)
	UI.action(navigation, "Mi perfil", profile)
	UI.action(navigation, "Contactos", contacts)
	UI.action(navigation, "Mensajes", inbox)
	UI.action(navigation, "Proyectos", projects)
	body = VBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(body)
	status = UI.text(self, "Tu reputación profesional y la XP para Liga son cosas distintas, aquí importa cómo ayudas a otras personas", 13, UI.MUTED, true)
	if game.state()["onboarded"]: feed()
	else: welcome()
func welcome() -> void:
	var list = clear_body()
	UI.heading(list, "Tu primer perfil", "Tu camino profesional empieza aquí", "No necesitas saberlo todo para aportar, empieza por una duda que puedas explicar bien")
	for item in [["Ayuda con lo que entiendes", "En Comunidad puedes revisar respuestas antes de publicarlas, una explicación útil vale más que aparentar que lo sabes todo"], ["Construye algo que puedas mostrar", "Los encargos llegan a Mensajes a medida que aprendes, prueba tus consultas sin riesgo y guarda los proyectos terminados en tu portafolio"], ["Cuida a las personas de tu red", "Tus ayudas suman contactos y recomendaciones, la reputación de Nexo, la XP de Liga y el dinero para tu casa se muestran por separado"]]:
		var card = UI.card(list, Color("e7e9da"))
		UI.text(card, item[0], 23, UI.GREEN)
		UI.text(card, item[1], 17, UI.INK, true)
	UI.action(list, "Empezar con mi perfil", func():
		game.state()["onboarded"] = true
		if not game.store.save():
			game.state()["onboarded"] = false
			status.text = game.store.notice
			return
		feed()
	, true)
func clear_body() -> VBoxContainer:
	for child in body.get_children():
		body.remove_child(child)
		child.queue_free()
	return UI.scroll(body)
func author(id: String) -> String:
	if id == "marco": return "Profesor Marco"
	if id == "equipo_datos": return "Equipo de apoyo académico"
	for peer in Course.all()["peers"]:
		if peer["id"] == id: return peer["name"]
	return id.capitalize()
func feed() -> void:
	select_page("Comunidad")
	var list = clear_body()
	UI.heading(list, "Nexo", "Lo que estamos construyendo", "Un caso pequeño también sirve para pensar como alguien que trabaja con datos")
	var count = 0
	for item in game.content["posts"]:
		if not game.available(item): continue
		count += 1
		var answered = game.state()["responses"].has(item["id"])
		var card = UI.card(list, Color("e6eadb") if answered else Color("eee5d1"))
		UI.text(card, author(item["author"]) + "  ·  Tu comunidad", 13, UI.COPPER)
		UI.text(card, item["title"], 24, UI.GREEN, true)
		UI.text(card, item["text"], 17, UI.INK, true)
		UI.action(card, "Ver mi respuesta" if answered else "Pensar una respuesta", detail.bind(item["id"]), not answered)
	if count == 0:
		var card = UI.card(list, Color("e6eadb"))
		UI.text(card, "Tu red empieza con lo que vas aprendiendo", 24, UI.GREEN, true)
		UI.text(card, "Después de las clases aparecerán publicaciones relacionadas con esas ideas, puedes hablar con tus compañeros para conectar con ellos desde el primer día", 19, UI.INK, true)
func detail(id: String) -> void:
	var item = game.post(id)
	var list = clear_body()
	selected = -1
	UI.heading(list, author(item["author"]), item["title"], item["text"])
	var group = ButtonGroup.new()
	for index in range(item["options"].size()):
		var button = UI.action(list, item["options"][index][0], func():
			selected = index
			if is_instance_valid(publish_button): publish_button.disabled = game.state()["responses"].has(id)
		)
		button.toggle_mode = true
		button.button_group = group
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	var feedback = UI.text(list, "Elige una opción, puedes revisar tu razonamiento antes de publicar", 17, UI.GREEN, true)
	var existing = game.state()["responses"].get(id, {})
	if not existing.is_empty():
		feedback.text = "Tu respuesta  ·  " + existing["text"] + "\n\n" + existing["feedback"]
	var actions = HBoxContainer.new()
	body.add_child(actions)
	UI.action(actions, "Revisar mi razonamiento", func():
		var result = game.preview(id, selected)
		feedback.text = "Primero elige una respuesta" if result.is_empty() else result["feedback"] + "\n\nEsta revisión es de práctica y no cambia tu reputación"
		list.get_parent().call_deferred("ensure_control_visible", feedback)
	)
	var publish = UI.action(actions, "Publicar respuesta", func():
		if game.publish(id, selected):
			detail(id)
		status.text = game.notice
	, true)
	publish_button = publish
	publish.disabled = selected < 0 or not existing.is_empty()
	UI.action(actions, "Volver", feed)
func profile() -> void:
	select_page("Mi perfil")
	var list = clear_body()
	UI.heading(list, "Mi perfil", "Lo que has aportado")
	UI.text(list, "%s reputación  ·  %s %s  ·  %s reacciones" % [int(game.store.data["reputation"]), game.state()["contacts"].size(), "contacto" if game.state()["contacts"].size() == 1 else "contactos", int(game.store.data["likes"])], 20, UI.GREEN, true)
	if game.state()["responses"].is_empty():
		UI.text(list, "Todavía no publicas una respuesta, tu primera ayuda puede empezar con una duda que entiendas bien", 19, UI.MUTED, true)
	for id in game.state()["responses"]:
		var record = game.state()["responses"][id]
		var card = UI.card(list, Color("e6eadb"))
		UI.text(card, game.post(id)["title"], 22, UI.GREEN, true)
		UI.text(card, record["text"], 17, UI.INK, true)
		UI.text(card, "%s reacciones  ·  %s%s reputación" % [int(record["likes"]), "+" if record["score"] > 0 else "", int(record["score"])], 14, UI.COPPER)
		UI.action(card, "Ver explicación", detail.bind(id))
func contacts() -> void:
	select_page("Contactos")
	var list = clear_body()
	UI.heading(list, "Tu red", "Las personas detrás de los datos")
	if game.state()["contacts"].is_empty():
		UI.text(list, "Todavía no has conectado con nadie, habla con tus compañeros en la sala o ayuda con una publicación", 20, UI.MUTED, true)
	for id in game.state()["contacts"]:
		var card = UI.card(list, Color("e6eadb"))
		var row = HBoxContainer.new()
		card.add_child(row)
		if id == "equipo_datos":
			UI.text(row, "SQL", 28, UI.GREEN).custom_minimum_size = Vector2(68, 80)
		else:
			var avatar = Avatar.new()
			avatar.profile = Course.peer_profile(id)
			avatar.custom_minimum_size = Vector2(68, 80)
			row.add_child(avatar)
		var info = VBoxContainer.new()
		row.add_child(info)
		UI.text(info, author(id), 24, UI.GREEN)
		UI.text(info, "Equipo con el que colaboraste" if id == "equipo_datos" else "Tu compañero de facultad" if id not in ["moshi", "sofia", "camila", "valentina"] else "Tu compañera de facultad", 15, UI.MUTED)
		UI.text(info, "Relación  ·  %s" % int(game.store.data["relationships"].get(id, 0)), 14, UI.COPPER)

func inbox() -> void:
	select_page("Mensajes")
	var list = clear_body()
	if game.store.data["campaign"]["phase"] == "graduated":
		var opportunity = UI.card(list, Color("e6eadb"))
		UI.text(opportunity, "Tu siguiente paso", 24, UI.GREEN)
		UI.text(opportunity, "Terminaste la carrera, tus proyectos y recomendaciones pueden abrir distintas oportunidades, siempre puedes comenzar con el equipo de la facultad", 17, UI.INK, true)
		UI.action(opportunity, "Ver mis oportunidades", func(): career_requested.emit(), true)
	UI.heading(list, "Bandeja de entrada", "Una mano para avanzar", "Los encargos aparecen después de aprender lo necesario y avanzar la etapa anterior")
	var count = 0
	for item in game.content.get("cases", []):
		if not game.case_available(item): continue
		count += 1
		var completed = game.state()["completed_cases"].has(item["id"])
		var card = UI.card(list, Color("e6eadb") if completed else Color("eee5d1"))
		UI.text(card, author(item["author"]) + ("  ·  Encargo puntual" if item.get("recommendation", false) else "  ·  Etapa %s de 4" % int(item["stage"])), 13, UI.COPPER)
		UI.text(card, item["title"], 23, UI.GREEN, true)
		UI.text(card, item["text"], 17, UI.INK, true)
		UI.text(card, "Entregado" if completed else "%s XP para Liga  /  %s reputación  /  $%s para tu casa" % [int(item["xp"]), int(item["reputation"]), int(item["money"])], 13, UI.MUTED, true)
		UI.action(card, "Revisar mi solución" if completed else "Abrir encargo", func(): case_requested.emit(item["id"]), not completed)
	if count == 0:
		UI.text(list, "Todavía no hay encargos para tus clases actuales, tus compañeros traerán dudas cuando ya tengas las herramientas para resolverlas", 20, UI.MUTED, true)
func projects() -> void:
	select_page("Proyectos")
	var list = clear_body()
	UI.heading(list, "Paso a paso", "Proyectos que crecen contigo")
	for project in [["almacen", "El almacén de Carlos"], ["tutorias", "La agenda de Moshi"], ["biblioteca", "La biblioteca de Sofía"]]:
		var card = UI.card(list, Color("e6eadb"))
		UI.text(card, project[1], 24, UI.GREEN)
		var completed = 0
		var next = {}
		for item in game.content.get("cases", []):
			if item["project"] != project[0]: continue
			if game.state()["completed_cases"].has(item["id"]): completed += 1
			elif game.case_available(item): next = item
		if completed > 0: UI.action(card, "Exportar para mi portafolio", export_project.bind(project[0]))
		UI.text(card, "%s de 4 etapas completadas" % completed, 16, UI.COPPER)
		var bar = ProgressBar.new()
		bar.max_value = 4
		bar.value = completed
		bar.show_percentage = false
		bar.custom_minimum_size.y = 10
		card.add_child(bar)
		if not next.is_empty():
			UI.action(card, "Continuar  ·  " + next["title"], func(): case_requested.emit(next["id"]), true)
		else:
			UI.text(card, "Proyecto completo, tu ayuda se convirtió en una recomendación" if completed == 4 else "La próxima etapa llegará con nuevas materias, puedes seguir aprendiendo a tu ritmo", 16, UI.MUTED, true)
	for record in game.state()["recommendations"]:
		var card = UI.card(list, Color("eee0bd"))
		UI.text(card, "Recomendación de " + author(record["author"]), 20, UI.GREEN, true)
		UI.text(card, record["text"], 17, UI.INK, true)

func select_page(title: String) -> void:
	UI.select_nav(navigation, title)

func export_project(project: String) -> void:
	var picker = FileDialog.new()
	picker.title = "Elige dónde guardar tu proyecto"
	picker.file_mode = FileDialog.FILE_MODE_OPEN_DIR
	picker.access = FileDialog.ACCESS_FILESYSTEM
	add_child(picker)
	picker.dir_selected.connect(func(path):
		var result = preload("res://scripts/portfolio.gd").export_project(game.store, project, path)
		status.text = "Proyecto exportado en " + result["path"] if result["ok"] else result["error"]
		picker.queue_free()
	)
	picker.canceled.connect(picker.queue_free)
	picker.popup_centered_ratio(0.75)
