extends HBoxContainer

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
const Figure = preload("res://scripts/learning_figure.gd")
const Lecture = preload("res://scripts/lecture_view.gd")
var store
var entries: Array = []
var filtered: Array = []
var search: LineEdit
var section: OptionButton
var list: VBoxContainer
var detail: VBoxContainer
var personal: TextEdit

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	var navigation = VBoxContainer.new()
	navigation.custom_minimum_size.x = 290
	add_child(navigation)
	search = LineEdit.new()
	search.placeholder_text = "Buscar en tus apuntes"
	search.text_changed.connect(func(_text): refresh())
	navigation.add_child(search)
	section = OptionButton.new()
	for text in ["Todo", "Bases", "Modelo", "Año 1", "Año 2", "Año 3", "Año 4", "Mis notas"]:
		section.add_item(text)
	section.item_selected.connect(func(_index): refresh())
	navigation.add_child(section)
	list = UI.scroll(navigation)
	list.add_theme_constant_override("separation", 4)
	detail = UI.scroll(self)
	for item in Course.all()["notes"]:
		entries.append({"section": "Modelo" if item[0] >= 3 else "Bases", "title": item[1], "body": item[2], "diagram": item[3], "keywords": item[4], "sql": ""})
	for key in Course.all()["demonstrations"]:
		for item in Course.all()["demonstrations"][key]:
			entries.append({"section": "Año " + key.split("_")[0], "title": item["title"],
				"body": item["speech"] + "\n\n" + item["explanation"] + "\n\n" + item["check"],
				"diagram": item.get("diagram", ""), "keywords": key, "sql": item["sql"]})
	for day in Course.all()["foundation"]:
		for item in Course.all()["foundation"][day]["pages"]:
			entries.append({"section": "Bases", "title": item["title"], "body": item["body"], "diagram": "", "keywords": "introduccion " + day, "sql": item["sql"]})
	refresh()

func normalized(value: String) -> String:
	value = value.to_lower()
	for pair in [["á", "a"], ["é", "e"], ["í", "i"], ["ó", "o"], ["ú", "u"], ["ü", "u"]]:
		value = value.replace(pair[0], pair[1])
	return value

func clear_detail() -> void:
	for child in detail.get_children():
		detail.remove_child(child)
		child.queue_free()

func refresh() -> void:
	clear_detail()
	for child in list.get_children():
		list.remove_child(child)
		child.queue_free()
	filtered = []
	var selected = section.get_item_text(section.selected)
	if selected == "Mis notas":
		UI.heading(detail, "Cuaderno personal", "Tus propias palabras", "Se guardan mientras escribes")
		personal = TextEdit.new()
		personal.custom_minimum_size.y = 430
		personal.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
		personal.text = store.data["personal_notes"]
		personal.text_changed.connect(func(): store.data["personal_notes"] = personal.text; store.save())
		detail.add_child(personal)
		return
	var query = normalized(search.text)
	for entry in entries:
		if selected != "Todo" and selected != entry["section"]:
			continue
		if not query.is_empty() and query not in normalized(entry["title"] + " " + entry["body"] + " " + entry["keywords"] + " " + entry["sql"]):
			continue
		filtered.append(entry)
		var button = UI.action(list, entry["title"], show_entry.bind(filtered.size() - 1))
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.add_theme_font_size_override("font_size", 14)
	if not filtered.is_empty():
		show_entry(0)
	else:
		UI.heading(detail, "Tu cuaderno", "No encontramos esa palabra", "Prueba con otra palabra o busca en todas las secciones")

func show_entry(index: int) -> void:
	clear_detail()
	if index < 0 or index >= filtered.size():
		return
	var entry: Dictionary = filtered[index]
	for i in range(list.get_child_count()):
		list.get_child(i).add_theme_stylebox_override("normal", UI.box(Color("d5e1ce") if i == index else Color("e9e9dc"), 8, 11))
	UI.heading(detail, entry["section"], entry["title"])
	UI.text(detail, entry["body"], 18, UI.INK, true)
	if not entry["diagram"].is_empty():
		var figure = Figure.new()
		figure.kind = entry["diagram"]
		detail.add_child(figure)
	if not entry["sql"].is_empty():
		var code = CodeEdit.new()
		code.editable = false
		code.text = entry["sql"]
		code.syntax_highlighter = Lecture.highlighter()
		code.custom_minimum_size.y = 180
		detail.add_child(code)
