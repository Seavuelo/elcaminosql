extends VBoxContainer

const UI = preload("res://scripts/ui_kit.gd")
const Logic = preload("res://scripts/model_logic.gd")
const Edges = preload("res://scripts/model_edges.gd")
const Lecture = preload("res://scripts/lecture_view.gd")
const Notebook = preload("res://scripts/notebook_view.gd")
var store
var campaign
var audio
var model
var graph: GraphEdit
var edges
var nodes: Dictionary = {}
var status: Label
var mode_label: Label
var relational_mode = false
var dialog: Control
var form_error: Label
var draft: Dictionary = {}
var attr_index = -1
var attr_fields: Dictionary = {}
var form_body: VBoxContainer
var detail: Label
var document = ""
var form_actions: HBoxContainer

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	model = Logic.new(campaign.progress()["model"])
	var toolbar = HBoxContainer.new()
	toolbar.add_theme_constant_override("separation", 7)
	add_child(toolbar)
	for item in [["Nueva\ntabla", entity_form], ["Relaciones", relations_form], ["Tarea\nactual", task_form], ["Lógico /\nrelacional", toggle_model], ["Generar\nSQL", sql_form], ["Comprobar", verify_model], ["Cuaderno", notebook_form]]:
		var button = UI.action(toolbar, item[0], item[1], item[0] == "Nueva\ntabla")
		button.add_theme_font_size_override("font_size", 14)
		button.custom_minimum_size.y = 50
	UI.fill(toolbar)
	mode_label = UI.text(toolbar, "MODELO LÓGICO", 12, UI.COPPER)
	graph = GraphEdit.new()
	graph.size_flags_vertical = Control.SIZE_EXPAND_FILL
	graph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	graph.zoom_min = 0.15
	graph.zoom_max = 2
	graph.show_minimap_button = true
	graph.minimap_enabled = false
	graph.show_arrange_button = false
	graph.connection_lines_curvature = 0
	graph.add_theme_stylebox_override("panel", UI.box(Color("e8eddf"), 12, 0))
	graph.add_theme_color_override("grid_minor", Color("d6dfcf"))
	graph.add_theme_color_override("grid_major", Color("b9c8b4"))
	add_child(graph)
	edges = Edges.new()
	edges.graph = graph
	graph.add_child(edges)
	graph.connection_request.connect(func(from, _port, to, _target):
		if not relational_mode:
			relation_form({"source": nodes.find_key(graph.get_node(NodePath(from))), "target": nodes.find_key(graph.get_node(NodePath(to)))})
	)
	graph.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed and not relational_mode:
			var id = edges.pick(event.position)
			for relation in model.data["relations"]:
				if relation["id"] == id:
					relation_form(relation)
	)
	graph.end_node_move.connect(save_positions)
	status = UI.text(self, "Arrastra las tablas para ordenarlas, une sus conectores o abre Relaciones, rueda para acercar y botón central para mover el lienzo", 13, UI.MUTED, true)
	rebuild_graph()

func persist() -> bool:
	var previous = store.data.duplicate(true)
	campaign.progress()["model"] = model.data.duplicate(true)
	if not store.save():
		store.data = previous
		model.data = campaign.progress()["model"].duplicate(true)
		status.text = store.notice
		return false
	return true

func save_positions() -> void:
	if relational_mode:
		return
	for name in nodes:
		var item = model.entity(name)
		item["x"] = nodes[name].position_offset.x
		item["y"] = nodes[name].position_offset.y
	persist()

func rebuild_graph() -> void:
	for node in nodes.values():
		graph.remove_child(node)
		node.queue_free()
	nodes.clear()
	var source = model.data["entities"]
	var relation_list = model.data["relations"]
	if relational_mode:
		var result = model.relational()
		if result.is_empty():
			relational_mode = false
			status.text = model.error
		else:
			source = result["tables"]
			relation_list = []
			for table in source:
				for foreign in table["foreign_keys"]:
					relation_list.append({"id": foreign["name"] + table["name"], "name": foreign["name"], "source": foreign["table"], "target": table["name"], "kind": "1:N", "source_optional": false, "target_optional": true, "identifying": table["columns"].any(func(a): return a.get("generated", false) and a.get("uid", false))})
	mode_label.text = "MODELO RELACIONAL" if relational_mode else "MODELO LÓGICO"
	for index in range(source.size()):
		var item: Dictionary = source[index]
		var node = GraphNode.new()
		node.name = "Table" + str(index)
		node.title = item["name"]
		node.custom_minimum_size.x = 350
		node.position_offset = Vector2(item.get("x", 60 + index * 540), item.get("y", 70 + index % 2 * 130))
		node.add_theme_stylebox_override("panel", UI.box(UI.WHITE, 10, 14))
		node.add_theme_stylebox_override("panel_selected", UI.box(Color("e2ebd7"), 10, 14))
		node.add_theme_stylebox_override("titlebar", UI.box(UI.GREEN, 10, 12))
		node.add_theme_stylebox_override("titlebar_selected", UI.box(UI.DEEP, 10, 12))
		node.add_theme_color_override("title_color", UI.WHITE)
		graph.add_child(node)
		nodes[item["name"]] = node
		var attrs: Array = item["columns"] if relational_mode else item["attributes"]
		if attrs.is_empty():
			UI.text(node, "Añade atributos en Propiedades", 14, UI.MUTED)
		for attr in attrs:
			var row = HBoxContainer.new()
			node.add_child(row)
			UI.text(row, "UID" if attr.get("uid", false) else "FK" if attr.get("generated", false) else "*" if attr.get("mandatory", false) else "○", 11, UI.COPPER).custom_minimum_size.x = 30
			UI.text(row, attr["name"], 15, UI.INK).size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var kind: String = attr["type"]
			if kind == "VARCHAR": kind += "(" + str(attr.get("length", 80)) + ")"
			if kind == "NUMERIC": kind += "(%s,%s)" % [attr.get("precision", 10), attr.get("scale", 2)]
			UI.text(row, kind, 12, UI.MUTED)
		if not relational_mode:
			UI.action(node, "Propiedades", entity_form.bind(item["name"])).custom_minimum_size.y = 32
		else:
			for foreign in item["foreign_keys"]:
				UI.text(node, "FK → " + foreign["table"] + " (" + ", ".join(foreign["columns"]) + ")", 12, UI.GREEN, true)
		node.set_slot(0, true, 0, UI.COPPER, true, 0, UI.GREEN)
		for title_control in node.get_titlebar_hbox().get_children():
			if title_control is Label:
				title_control.add_theme_color_override("font_color", UI.WHITE)
				title_control.add_theme_font_override("font", UI.weight(UI.BODY, 650))
		node.reset_size()
	edges.nodes = nodes
	edges.relations = relation_list
	graph.get_menu_hbox().get_parent().add_theme_stylebox_override("panel", UI.box(Color("f4eedf"), 8, 6))
	if not source.is_empty() and not relational_mode:
		status.text = "UID identifica cada fila, * indica obligatorio y ○ opcional, haz clic en una relación para editarla"
	if source.is_empty():
		status.text = "Tu lienzo está listo, empieza con Nueva tabla y representa una sola cosa, por ejemplo ESTUDIANTE"

func open_form(title: String, subtitle: String = "") -> VBoxContainer:
	close_form()
	dialog = Control.new()
	dialog.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	get_tree().current_scene.add_child(dialog)
	var shade = ColorRect.new()
	shade.color = Color(0.03, 0.09, 0.07, 0.8)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dialog.add_child(shade)
	var margin = UI.margin(dialog, 48)
	var panel = PanelContainer.new()
	margin.add_child(panel)
	var column = VBoxContainer.new()
	panel.add_child(column)
	var header = HBoxContainer.new()
	column.add_child(header)
	UI.heading(header, "Taller de datos", title, subtitle).size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.action(header, "Volver al lienzo", close_form)
	form_body = UI.scroll(column)
	form_error = UI.text(column, "", 14, UI.RED, true)
	form_actions = HBoxContainer.new()
	column.add_child(form_actions)
	return form_body

func close_form() -> void:
	if is_instance_valid(dialog):
		dialog.get_parent().remove_child(dialog)
		dialog.queue_free()
	dialog = null

func handle_escape() -> bool:
	if is_instance_valid(dialog):
		close_form()
		return true
	return false

func field(parent: Node, title: String, value: String, help: String, placeholder: String = "") -> LineEdit:
	var group = VBoxContainer.new()
	group.add_theme_constant_override("separation", 5)
	parent.add_child(group)
	var row = HBoxContainer.new()
	group.add_child(row)
	UI.text(row, title, 14)
	UI.fill(row)
	var hint = UI.action(row, "?", func(): detail.text = help)
	hint.tooltip_text = help
	hint.custom_minimum_size = Vector2(28, 28)
	hint.add_theme_stylebox_override("normal", UI.box(Color("e2e8d7"), 14, 3))
	var input = LineEdit.new()
	input.text = value
	input.set_meta("model_field", title)
	input.placeholder_text = placeholder
	group.add_child(input)
	return input

func help_label(parent: Node) -> void:
	detail = UI.text(parent, "Pulsa ? para ver una explicación de cada campo", 14, UI.GREEN, true)

func entity_form(old: String = "", keep_draft: bool = false) -> void:
	if not keep_draft:
		draft = model.entity(old).duplicate(true) if not old.is_empty() else {"name": "", "attributes": [], "x": 60 + model.data["entities"].size() * 540, "y": 60 + model.data["entities"].size() % 2 * 120}
	var body = open_form("Propiedades de la tabla", "Nombra la entidad en singular, cada atributo representa un dato de esa entidad")
	var tabs = TabContainer.new()
	tabs.custom_minimum_size.y = 370
	body.add_child(tabs)
	var general = VBoxContainer.new()
	general.name = "General"
	tabs.add_child(general)
	var name_input = field(general, "Nombre de la entidad", draft["name"], "Usa singular y mayúsculas, ESTUDIANTE representa a cada estudiante, no escribas espacios, tildes ni ñ, usa _ como en ORDEN_COMPRA", "ESTUDIANTE")
	name_input.text_changed.connect(func(value): draft["name"] = value)
	UI.text(general, "Sin espacios, tildes ni ñ, separa palabras con _, máximo 40 caracteres", 14, UI.MUTED, true)
	var attributes = VBoxContainer.new()
	attributes.name = "Atributos"
	tabs.add_child(attributes)
	var list = VBoxContainer.new()
	list.add_theme_constant_override("separation", 5)
	attributes.add_child(list)
	for index in range(draft["attributes"].size()):
		var attr = draft["attributes"][index]
		var row = HBoxContainer.new()
		list.add_child(row)
		UI.text(row, attr["name"] + "  ·  " + attr["type"] + ("  ·  UID primario" if attr.get("uid", false) else "  ·  Obligatorio" if attr.get("mandatory", false) else "  ·  Opcional"), 15, UI.INK, true)
		UI.compact(UI.action(row, "Editar", func(): attr_index = index; fill_attribute(draft["attributes"][index])))
		UI.compact(UI.action(row, "Quitar", func(): draft["attributes"].remove_at(index); attr_index = -1; entity_form(old, true)))
	var editor_card = UI.card(attributes, Color("e8eddf"))
	UI.text(editor_card, "AÑADIR O EDITAR ATRIBUTO", 12, UI.COPPER)
	var grid = GridContainer.new()
	grid.columns = 2
	editor_card.add_child(grid)
	var left = VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_child(left)
	var right = VBoxContainer.new()
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_child(right)
	attr_fields = {}
	attr_fields["name"] = field(left, "Nombre del atributo", "", "Sin espacios, tildes ni ñ, ejemplos: id, nombre, fecha_nacimiento", "id")
	UI.text(right, "Tipo de origen", 14)
	var type = OptionButton.new()
	for label in Logic.TYPES: type.add_item(label)
	right.add_child(type)
	attr_fields["type"] = type
	attr_fields["length"] = field(left, "Longitud de VARCHAR", "80", "Cantidad máxima de caracteres, VARCHAR(1) admite A pero rechaza Ana, VARCHAR(80) admite hasta 80 y VARCHAR(100) hasta 100, escribir un nombre corto no rellena lo que sobra")
	var numbers = HBoxContainer.new()
	right.add_child(numbers)
	attr_fields["precision"] = field(numbers, "Precisión", "10", "Total de dígitos de NUMERIC, NUMERIC(5,2) admite 123,45 pero no 1234,56")
	attr_fields["scale"] = field(numbers, "Escala", "2", "Dígitos decimales incluidos en la precisión, para un identificador entero puedes usar escala 0")
	for spec in [["uid", "UID primario", "Identifica de forma única cada fila, no admite duplicados ni NULL, varios UID forman una clave compuesta"], ["mandatory", "Obligatorio", "La fila necesita un valor, si no está marcado el atributo puede ser NULL, una clave primaria siempre es obligatoria"]]:
		var check = CheckBox.new()
		check.text = spec[1]
		check.tooltip_text = spec[2]
		editor_card.add_child(check)
		attr_fields[spec[0]] = check
	attr_fields["uid"].toggled.connect(func(value):
		if value: attr_fields["mandatory"].button_pressed = true
	)
	var add_attr = UI.action(form_actions, "Guardar atributo y añadir otro", func():
		draft["name"] = name_input.text
		if collect_attribute():
			attr_index = -1
			entity_form(old, true)
	, true)
	add_attr.visible = keep_draft
	tabs.tab_changed.connect(func(index): add_attr.visible = index == 1)
	var update_type = func():
		attr_fields["length"].editable = type.selected == 0
		attr_fields["precision"].editable = type.selected == 1
		attr_fields["scale"].editable = type.selected == 1
	type.item_selected.connect(func(_index): update_type.call())
	update_type.call()
	help_label(body)
	var actions = form_actions
	UI.action(actions, "Guardar tabla", func():
		draft["name"] = name_input.text
		if not attr_fields["name"].text.strip_edges().is_empty() and not collect_attribute():
			return
		if model.save_entity(draft, old) and persist():
			close_form()
			rebuild_graph()
			status.text = "Tabla guardada, puedes abrir sus propiedades cuando quieras"
		else:
			form_error.text = model.error if not model.error.is_empty() else store.notice
	, true)
	if not old.is_empty():
		UI.action(actions, "Eliminar tabla", func(): confirm_delete_entity(old))
	if keep_draft:
		tabs.current_tab = 1
	else:
		name_input.grab_focus()
	attr_index = -1

func fill_attribute(attr: Dictionary) -> void:
	for key in ["name", "length", "precision", "scale"]:
		attr_fields[key].text = str(attr.get(key, 80 if key == "length" else 10 if key == "precision" else 2))
	attr_fields["type"].select(Logic.TYPES.find(attr["type"]))
	attr_fields["type"].item_selected.emit(Logic.TYPES.find(attr["type"]))
	attr_fields["uid"].button_pressed = attr.get("uid", false)
	attr_fields["mandatory"].button_pressed = attr.get("mandatory", false)
	attr_fields["name"].grab_focus()

func collect_attribute() -> bool:
	var item = {}
	for key in ["name", "length", "precision", "scale"]:
		item[key] = attr_fields[key].text
	item["type"] = Logic.TYPES[attr_fields["type"].selected]
	for key in ["uid", "mandatory"]: item[key] = attr_fields[key].button_pressed
	item = model.attribute(item)
	if item.is_empty():
		form_error.text = model.error
		return false
	for index in range(draft["attributes"].size()):
		if index != attr_index and draft["attributes"][index]["name"].to_lower() == item["name"].to_lower():
			form_error.text = "Ya existe un atributo con ese nombre"
			return false
	if attr_index < 0:
		draft["attributes"].append(item)
	else:
		draft["attributes"][attr_index] = item
	return true

func confirm_delete_entity(name: String) -> void:
	var body = open_form("Eliminar " + name, "Esta acción quita la tabla del modelo lógico")
	UI.text(body, "Si tiene relaciones, debes quitarlas primero para no dejar referencias sueltas", 18, UI.INK, true)
	UI.action(body, "Confirmar eliminación", func():
		if model.delete_entity(name) and persist():
			close_form()
			rebuild_graph()
		else:
			form_error.text = model.error
	)

func relations_form() -> void:
	var body = open_form("Relaciones", "Una relación explica cómo se conectan dos entidades")
	for relation in model.data["relations"]:
		UI.action(body, relation["source"] + " → " + relation["target"] + "  ·  " + relation["kind"] + "  ·  " + relation["name"], relation_form.bind(relation))
	var add = UI.action(body, "Crear relación", relation_form, true)
	add.disabled = model.data["entities"].is_empty()
	if add.disabled:
		UI.text(body, "Primero crea las entidades que quieres relacionar", 18, UI.MUTED, true)

func relation_form(value: Dictionary = {}) -> void:
	var relation = value.duplicate(true)
	var body = open_form("Propiedades de la relación", "El origen aporta su clave, el destino recibe la referencia cuando eliges pasar UID")
	var name_input = field(body, "Nombre de la relación", relation.get("name", ""), "Sin espacios ni tildes, para muchos a muchos este nombre será el de la tabla intermedia", "TIENE_TUTORIA")
	var endpoints = HBoxContainer.new()
	body.add_child(endpoints)
	var fields = {}
	for endpoint in ["source", "target"]:
		var column = VBoxContainer.new()
		column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		endpoints.add_child(column)
		UI.text(column, "Entidad de origen" if endpoint == "source" else "Entidad de destino", 14)
		var choice = OptionButton.new()
		for index in range(model.data["entities"].size()):
			choice.add_item(model.data["entities"][index]["name"])
			if model.data["entities"][index]["name"] == relation.get(endpoint, ""):
				choice.select(index)
		column.add_child(choice)
		fields[endpoint] = choice
		fields[endpoint + "_role"] = field(column, "Nombre de origen" if endpoint == "source" else "Nombre de destino", relation.get(endpoint + "_role", "tiene" if endpoint == "source" else "pertenece"), "Se lee como una frase, ESTUDIANTE tiene TUTORIA, TUTORIA pertenece a ESTUDIANTE")
	UI.text(body, "Cardinalidad", 14)
	var kind = OptionButton.new()
	for label in ["1:1  ·  Uno a uno", "1:N  ·  Uno a muchos", "N:M  ·  Muchos a muchos"]: kind.add_item(label)
	kind.select(maxi(0, ["1:1", "1:N", "N:M"].find(relation.get("kind", "1:N"))))
	body.add_child(kind)
	var explanation = UI.text(body, "", 15, UI.GREEN, true)
	var describe = func():
		explanation.text = ["Cada origen se asocia con un único destino, se genera una FK con UNIQUE, no hace falta una tercera tabla", "Un origen puede tener varios destinos, su UID pasa al destino como FK, no hace falta una tercera tabla", "Cada lado admite varios del otro, se genera una tabla intermedia con las dos referencias como clave primaria compuesta"][kind.selected]
	kind.item_selected.connect(func(_index): describe.call())
	describe.call()
	for spec in [
		["transfer_key", "Pasar UID primario como clave foránea", "Genera columnas FK en el destino y comprueba que exista el origen, sin esta casilla la asociación queda solo en el dibujo"],
		["transferable", "Transferible", "Permite cambiar la referencia a otro origen, si se desmarca se genera una restricción para impedir reasignar una referencia ya informada"],
		["source_optional", "Origen opcional", "El destino puede existir sin un origen, su FK admite NULL, la línea se muestra punteada"],
		["target_optional", "Destino opcional", "El origen puede existir sin tener hijos, desmarcarlo expresa una regla que debe validar el proceso, una FK sola no obliga a tener hijos"],
		["identifying", "Con identificación", "La clave del origen pasa a formar parte del UID del destino, solo se transfieren sus claves, los demás atributos permanecen en su entidad"]]:
		var check = CheckBox.new()
		check.text = spec[1]
		check.tooltip_text = spec[2]
		check.button_pressed = relation.get(spec[0], spec[0] in ["transfer_key", "transferable", "target_optional"])
		body.add_child(check)
		fields[spec[0]] = check
		UI.text(body, spec[2], 13, UI.MUTED, true)
	help_label(body)
	var actions = form_actions
	UI.action(actions, "Guardar relación", func():
		relation["name"] = name_input.text
		for endpoint in ["source", "target"]:
			relation[endpoint] = fields[endpoint].get_item_text(fields[endpoint].selected)
			relation[endpoint + "_role"] = fields[endpoint + "_role"].text
		relation["kind"] = ["1:1", "1:N", "N:M"][kind.selected]
		for key in ["transfer_key", "transferable", "source_optional", "target_optional", "identifying"]:
			relation[key] = fields[key].button_pressed
		if model.save_relation(relation) and persist():
			close_form()
			rebuild_graph()
		else:
			form_error.text = model.error if not model.error.is_empty() else store.notice
	, true)
	if relation.has("id"):
		UI.action(actions, "Eliminar relación", func():
			model.data["relations"].erase(value)
			if persist(): close_form(); rebuild_graph()
		)

func toggle_model() -> void:
	relational_mode = not relational_mode
	rebuild_graph()
	if relational_mode:
		status.text = "Vista generada desde tu modelo lógico, vuelve a Lógico para editar entidades y relaciones"

func task_form() -> void:
	var body = open_form("Tu tarea de hoy")
	if campaign.year() != 0 or campaign.day() < 2:
		UI.text(body, "No tienes una tarea de modelamiento pendiente, puedes experimentar libremente", 20, UI.GREEN, true)
		return
	for item in campaign.model_checklist():
		UI.text(body, ("Listo  ·  " if item[1] else "Pendiente  ·  ") + item[0], 19, UI.GREEN if item[1] else UI.INK, true)

func sql_form() -> void:
	var statements = model.statements()
	if statements.is_empty():
		status.text = model.error
		return
	document = "PRAGMA foreign_keys=ON;\n\n" + "\n\n".join(statements)
	var body = open_form("SQL de tu modelo", "El diseño se convierte en instrucciones reales de SQLite")
	var code = CodeEdit.new()
	code.text = document
	code.editable = false
	code.custom_minimum_size.y = 340
	code.syntax_highlighter = Lecture.highlighter()
	body.add_child(code)
	for warning in model.relational()["warnings"]:
		UI.text(body, warning, 14, UI.COPPER, true)
	var row = HBoxContainer.new()
	body.add_child(row)
	UI.action(row, "Copiar SQL", func(): DisplayServer.clipboard_set(document))
	UI.action(row, "Exportar SQL y modelo", export_model, true)

func export_model() -> void:
	var picker = FileDialog.new()
	picker.title = "Guardar mi modelo"
	picker.file_mode = FileDialog.FILE_MODE_SAVE_FILE
	picker.access = FileDialog.ACCESS_FILESYSTEM
	picker.filters = PackedStringArray(["*.sql ; Modelo SQLite"])
	picker.current_file = "mi_modelo.sql"
	add_child(picker)
	picker.file_selected.connect(func(path):
		var sql_file = FileAccess.open(path, FileAccess.WRITE)
		if sql_file == null:
			form_error.text = "No se pudo guardar el SQL, elige una carpeta con permiso de escritura"
		else:
			sql_file.store_string(document)
			sql_file.close()
			var json_file = FileAccess.open(path.get_basename() + ".modelo.json", FileAccess.WRITE)
			if json_file == null:
				form_error.text = "SQL guardado, no se pudo guardar el archivo del modelo"
			else:
				json_file.store_string(JSON.stringify(model.data, "  "))
				json_file.close()
				form_error.text = "Modelo y SQL guardados en " + path.get_base_dir()
		picker.queue_free()
	)
	picker.canceled.connect(picker.queue_free)
	picker.popup_centered_ratio(0.75)

func verify_model() -> void:
	var workshop = campaign.year() == 0 and campaign.day() >= 4
	var result = model.verify(workshop)
	var body = open_form("Comprobación del modelo", "Se usa una base temporal, tu base de clases conserva sus datos")
	if not result["ok"]:
		UI.text(body, "Todavía hay algo que revisar", 24, UI.RED)
		UI.text(body, result["error"], 18, UI.INK, true)
		if workshop:
			UI.text(body, "Las pruebas esperan ESTUDIANTE(id, nombre, promedio) y TUTORIA(id, tema), si añadiste otros campos obligatorios necesitarán valores de prueba", 15, UI.MUTED, true)
		return
	var previous = store.data.duplicate(true)
	campaign.progress()["model_tested"] = JSON.stringify(model.data)
	if not store.save():
		store.data = previous
		form_error.text = store.notice
		return
	UI.text(body, "Tu modelo se pudo construir correctamente", 24, UI.GREEN)
	UI.text(body, "%s tablas reales creadas, claves y referencias comprobadas" % result["tables"].size(), 18, UI.INK, true)
	if workshop:
		UI.text(body, "Moshi tiene dos tutorías, ambas conservan su propio ID y apuntan a la misma estudiante", 18, UI.INK, true)
	for check in result["checks"]:
		UI.text(body, check, 18, UI.GREEN, true)
	for warning in result["warnings"]:
		UI.text(body, warning, 15, UI.COPPER, true)
	if audio != null: audio.sfx("success")

func notebook_form() -> void:
	var body = open_form("Cuaderno de modelamiento")
	var view = Notebook.new()
	view.store = store
	view.custom_minimum_size.y = 430
	body.add_child(view)

func _exit_tree() -> void:
	if is_instance_valid(dialog):
		dialog.queue_free()
	dialog = null
