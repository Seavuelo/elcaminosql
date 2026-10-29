extends VBoxContainer
const UI = preload("res://scripts/ui_kit.gd")
const Logic = preload("res://scripts/activities.gd")
const Table = preload("res://scripts/table_view.gd")
const Lecture = preload("res://scripts/lecture_view.gd")
var store
var game
var body: VBoxContainer
var status: Label
var answers: Array = []
var order: Array = []
var action_bar: HBoxContainer
var navigation: HBoxContainer
signal case_requested(id)
func _ready():
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	game = Logic.new(store)
	navigation = HBoxContainer.new()
	add_child(navigation)
	UI.action(navigation, "Desafíos de bolsillo", puzzles, true)
	UI.action(navigation, "Mesa de investigación", investigations)
	body = VBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(body)
	action_bar = HBoxContainer.new()
	add_child(action_bar)
	status = UI.text(self, "Puedes practicar sin perder reputación, las recompensas se conceden una sola vez", 14, UI.MUTED, true)
	puzzles()
func clear() -> VBoxContainer:
	for child in action_bar.get_children(): action_bar.remove_child(child); child.queue_free()
	for child in body.get_children(): body.remove_child(child); child.queue_free()
	return UI.scroll(body)
func puzzles():
	select_mode(true)
	var list = clear()
	UI.heading(list, "Ponlo a prueba", "Piensa con las manos", "Filtra, ordena, relaciona y comprueba lo que hará una consulta")
	for item in game.content["puzzles"]:
		var card = UI.card(list, Color("e5ead9"))
		UI.text(card, item["title"], 24, UI.GREEN)
		UI.text(card, item["description"], 17, UI.INK, true)
		var start = UI.action(card, "Practicar otra vez" if item["id"] in store.data["activities"]["completed"] else "Abrir desafío", puzzle.bind(item["id"], true), true)
		start.disabled = not game.available(item)
		if start.disabled: UI.text(card, "Disponible después de la clase relacionada", 14, UI.MUTED)
func row_text(row: Array) -> String:
	var values = PackedStringArray()
	for value in row: values.append("NULL" if value == null else str(int(value)) if value is float and value == floor(value) else str(value))
	return "  /  ".join(values)
func puzzle(id: String, reset: bool = false):
	select_mode(true)
	var item = game.item(id, "puzzles")
	if not game.available(item): return
	if reset:
		answers = []
		order = range(item["rows"].size())
		if id == "claves": answers.resize(item["rows"].size()); answers.fill(-1)
	var list = clear()
	UI.heading(list, "Desafío de bolsillo", item["title"], item["description"])
	var code = CodeEdit.new()
	code.text = item["sql"]
	code.editable = false
	code.custom_minimum_size.y = maxi(65, (item["sql"].count("\n") + 1) * 24 + 32)
	code.syntax_highlighter = Lecture.highlighter()
	list.add_child(code)
	if id == "claves":
		UI.text(list, "Estudiantes  ·  " + "    |    ".join(item["parents"].map(func(row): return row_text(row))), 17, UI.GREEN, true)
	var rows_parent = GridContainer.new()
	rows_parent.columns = 2 if id == "filtro" else 1
	rows_parent.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_child(rows_parent)
	var choices = ButtonGroup.new()
	for position in range(order.size()):
		var index = order[position]
		var row = item["rows"][index]
		if id == "filtro" or item.get("kind", "") == "choice":
			var button = UI.action(rows_parent, row_text(row), func(): pass)
			button.toggle_mode = true
			if item.get("kind", "") == "choice": button.button_group = choices
			button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			button.button_pressed = index in answers
			button.toggled.connect(func(on):
				if item.get("kind", "") == "choice":
					if on: answers = [index]
					return
				if on and index not in answers: answers.append(index)
				elif not on: answers.erase(index)
			)
		else:
			var card = UI.card(rows_parent, Color("eee5d0"))
			card.get_parent().add_theme_stylebox_override("panel", UI.box(Color("eee5d0"), 14, 12))
			card.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var controls = HBoxContainer.new()
			card.add_child(controls)
			UI.text(controls, row_text(row), 19, UI.INK, true)
			if id == "orden":
				for delta in [-1, 1]:
					var move = UI.compact(UI.action(controls, "↑" if delta < 0 else "↓", func():
						var other = position + delta
						var old = order[position]
						order[position] = order[other]
						order[other] = old
						puzzle(id)
					))
					move.disabled = position + delta < 0 or position + delta >= order.size()
			else:
				var select = OptionButton.new()
				select.add_item("Elige estudiante")
				for parent in item["parents"]: select.add_item(row_text(parent))
				select.select(int(answers[index]) + 1)
				select.item_selected.connect(func(value): answers[index] = value - 1)
				controls.add_child(select)
	var feedback = UI.text(list, "", 18, UI.GREEN, true)
	UI.action(action_bar, "Comprobar mi solución", func():
		var correct = game.check_puzzle(id, order if id == "orden" else answers)
		feedback.text = game.notice
		feedback.add_theme_color_override("font_color", UI.GREEN if correct else UI.RED)
		list.get_parent().call_deferred("ensure_control_visible", feedback)
	, true)
func investigations():
	select_mode(false)
	var list = clear()
	UI.heading(list, "Apoyo a la facultad", "Sobre la mesa", "Lee los registros, explica el problema y después comprueba tu solución con SQL")
	for item in game.content["investigations"]:
		var card = UI.card(list, Color("e9dfc7"))
		UI.text(card, item["title"], 25, UI.GREEN, true)
		UI.text(card, item["subtitle"], 16, UI.MUTED, true)
		UI.text(card, "%s de %s documentos revisados" % [game.record(item["id"])["read"].size(), item["docs"].size()], 14, UI.COPPER)
		var open = UI.action(card, "Investigar el caso", investigation.bind(item["id"]), true)
		open.disabled = not game.available(item)
		if open.disabled: UI.text(card, "Disponible cuando hayas visto la materia necesaria", 14, UI.MUTED)
func investigation(id: String):
	select_mode(false)
	var item = game.item(id, "investigations")
	if not game.available(item): return
	var list = clear()
	UI.heading(list, "Carpeta de investigación", item["title"], item["subtitle"])
	for doc in item["docs"]:
		var seen = doc["id"] in game.record(id)["read"]
		UI.action(list, ("Revisado  ·  " if seen else "Documento  ·  ") + doc["title"], document.bind(id, doc["id"]))
	UI.text(list, "¿Qué explica mejor el problema?", 22, UI.GREEN)
	for index in range(item["options"].size()):
		var button = UI.action(list, item["options"][index], func():
			game.diagnose(id, index)
			status.text = game.notice
			investigation(id)
		)
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if game.record(id)["diagnosed"]:
		UI.text(list, item["feedback"], 18, UI.GREEN, true)
		UI.action(list, "Comprobar la corrección en SQL", func(): case_requested.emit(item["case_id"]), true)
func document(id: String, document_id: String):
	select_mode(false)
	var item = game.item(id, "investigations")
	if not game.read_document(id, document_id): status.text = game.notice; return
	var doc = {}
	for candidate in item["docs"]:
		if candidate["id"] == document_id: doc = candidate
	var list = clear()
	UI.heading(list, "Documento del caso", doc["title"])
	UI.text(list, doc["body"], 21, UI.INK, true)
	if doc.has("columns"):
		var table = Table.new()
		table.custom_minimum_size.y = 170
		list.add_child(table)
		table.set_data(doc["columns"], doc["rows"])
	if doc.has("code"):
		var code = CodeEdit.new()
		code.text = doc["code"]
		code.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
		code.editable = false
		code.custom_minimum_size.y = maxi(115, (doc["code"].count("\n") + 1) * 24 + 32)
		code.syntax_highlighter = Lecture.highlighter()
		list.add_child(code)
	if item.has("source"):
		UI.text(list, "Caso ficticio inspirado en una discusión técnica pública de la comunidad PostgreSQL", 14, UI.MUTED, true)
		UI.action(list, "Consultar la fuente", func(): OS.shell_open(item["source"]))
	UI.action(list, "Volver a los documentos", investigation.bind(id), true)

func select_mode(challenge: bool):
	UI.select_nav(navigation, "Desafíos de bolsillo" if challenge else "Mesa de investigación")
