extends VBoxContainer
const UI = preload("res://scripts/ui_kit.gd")
const Career = preload("res://scripts/career.gd")
const Avatar = preload("res://scripts/avatar_view.gd")
var store
var career
var body: VBoxContainer
var actions: HBoxContainer
var status: Label
var navigation: HBoxContainer
var answers = [-1,-1,-1]
func _ready():
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	career = Career.new(store)
	var nav = HBoxContainer.new()
	navigation = nav
	add_child(nav)
	UI.action(nav, "Mi cierre de carrera", overview, true)
	UI.action(nav, "Presentar mi proyecto", projects)
	UI.action(nav, "Mi próximo paso", paths)
	body = VBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(body)
	actions = HBoxContainer.new()
	add_child(actions)
	status = UI.text(self, "Tu aprendizaje y tu trabajo comprobado también forman parte de esta historia", 14, UI.MUTED, true)
	overview()
func clear() -> VBoxContainer:
	for host in [body, actions]:
		for child in host.get_children(): host.remove_child(child); child.queue_free()
	return UI.scroll(body)
func graduated() -> bool:
	return store.data["campaign"]["phase"] == "graduated"
func overview():
	UI.select_nav(navigation, "Mi cierre de carrera")
	var list = clear()
	if not graduated():
		UI.heading(list, "Tu camino", "Cada clase construye algo", "El cierre de carrera y las oportunidades estarán disponibles después de completar cuarto año")
		UI.text(list, "Mientras tanto puedes crear proyectos, ayudar a tus compañeros y preparar tu portafolio", 21, UI.GREEN, true)
		return
	var card = UI.card(list, UI.GREEN)
	var row = HBoxContainer.new()
	card.add_child(row)
	var avatar = Avatar.new()
	avatar.profile = store.data
	avatar.custom_minimum_size = Vector2(110, 135)
	row.add_child(avatar)
	var words = VBoxContainer.new()
	words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(words)
	UI.text(words, "CUATRO AÑOS, UN CAMINO PROPIO", 13, UI.GOLD)
	UI.text(words, store.data["player_name"], 40, UI.WHITE).add_theme_font_override("font", UI.weight(UI.TITLE, 650))
	UI.text(words, "De tu primera consulta a resolver problemas con datos", 20, UI.PAPER, true)
	var crest = TextureRect.new()
	crest.texture = load("res://icon.svg")
	crest.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	crest.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	crest.custom_minimum_size = Vector2(96, 96)
	row.add_child(crest)
	UI.text(list, "Lo que aprendiste no cabe solamente en una nota, también está en las decisiones que sabes explicar y en el trabajo que puedes mostrar", 21, UI.INK, true)
	var summary = HBoxContainer.new()
	list.add_child(summary)
	for metric in [[str(store.data["nexo"]["completed_cases"].size()), "encargos completados"], [str(store.data["nexo"]["contacts"].size()), "personas en tu red"], [str(store.data["nexo"]["recommendations"].size()), "recomendaciones"]]:
		var tile = UI.card(summary, Color("e5ead9"))
		tile.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
		UI.text(tile, metric[0], 32, UI.GREEN)
		UI.text(tile, metric[1], 15, UI.MUTED, true)
	UI.text(list, "Proyecto presentado  ·  " + store.data["career"]["project"].capitalize() if store.data["career"]["defended"] else "Puedes presentar uno de tus proyectos completos y explicar cómo comprobaste sus resultados", 18, UI.GREEN, true)
	var choice = store.data["career"]["choice"]
	for path in career.opportunities():
		if path["id"] == choice:
			UI.heading(list, "El siguiente capítulo", path["title"], path["text"])
	UI.action(actions, "Revisar mis oportunidades", paths, true)
func projects():
	UI.select_nav(navigation, "Presentar mi proyecto")
	var list = clear()
	UI.heading(list, "Un trabajo que puedes explicar", "Tu proyecto final", "Elige un proyecto completo y defiende tres de sus decisiones, puedes revisar tus apuntes antes de presentarlo")
	for item in [["almacen", "El almacén de Carlos"], ["tutorias", "La agenda de Moshi"], ["biblioteca", "La biblioteca de Sofía"]]:
		var button = UI.action(list, item[1], defense.bind(item[0]), true)
		button.disabled = not graduated() or not career.completed(item[0])
		if button.disabled: UI.text(list, "Requiere terminar la carrera y las cuatro etapas del proyecto", 14, UI.MUTED)
func defense(project: String):
	UI.select_nav(navigation, "Presentar mi proyecto")
	answers = [-1,-1,-1]
	var list = clear()
	UI.heading(list, "Presentación del proyecto", {"almacen": "Almacén", "tutorias": "Tutorías", "biblioteca": "Biblioteca"}.get(project, project.capitalize()), "Explica las decisiones, una buena solución también puede defenderse con palabras claras")
	var grid = GridContainer.new()
	grid.columns = 3
	list.add_child(grid)
	for index in range(career.questions[project].size()):
		var question = career.questions[project][index]
		var card = UI.card(grid, Color("eee5d0"))
		card.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
		UI.text(card, "DECISIÓN " + str(index + 1), 12, UI.COPPER)
		UI.text(card, question["q"], 20, UI.GREEN, true)
		var group = ButtonGroup.new()
		for option in range(question["options"].size()):
			var button = UI.action(card, question["options"][option], func(): answers[index] = option)
			button.toggle_mode = true
			button.button_group = group
			button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			button.add_theme_font_size_override("font_size", 15)
	UI.action(actions, "Presentar mis decisiones", func():
		var success = career.defend(project, answers)
		status.text = career.notice
		if success: overview()
	, true)
func paths():
	UI.select_nav(navigation, "Mi próximo paso")
	var list = clear()
	UI.heading(list, "Después de la universidad", "No todas las puertas se abren igual", "Tus proyectos y tus contactos crean alternativas, siempre hay una forma de comenzar")
	if not graduated():
		UI.text(list, "Primero termina cuarto año, todavía hay mucho que puedes construir en la facultad", 21, UI.MUTED, true)
	for path in career.opportunities():
		var card = UI.card(list, Color("e5ead9"))
		UI.text(card, path["title"], 25, UI.GREEN, true)
		UI.text(card, path["text"], 19, UI.INK, true)
		var chosen = store.data["career"]["choice"] == path["id"]
		var button = UI.action(card, "Mi próximo paso" if chosen else "Elegir este camino", func():
			if career.choose(path["id"]): overview()
			status.text = career.notice
		, not chosen)
		button.disabled = chosen
