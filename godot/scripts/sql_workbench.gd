extends VBoxContainer

signal finished_day

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
const Service = preload("res://scripts/sql_service.gd")
const Table = preload("res://scripts/table_view.gd")
const Lecture = preload("res://scripts/lecture_view.gd")
const Notebook = preload("res://scripts/notebook_view.gd")
var store
var campaign
var audio
var sandbox = false
var case_id = ""
var nexo
var service
var task: Dictionary = {}
var active_id = ""
var exam_mode = false
var pending = ""
var sent_query = ""
var editor: CodeEdit
var output
var result_title: Label
var status: Label
var objective: Label
var task_title: Label
var catalog_column: VBoxContainer
var run_button: Button
var submit_button: Button
var hint_button: Button
var hint_level = 0
var hint_box: RichTextLabel
var notes_layer: PanelContainer

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	service = Service.new()
	service.directory = store.directory
	service.finished.connect(receive)
	add_child(service)
	var task_panel = UI.card(self, Color("e7e8d8"))
	task_title = UI.text(task_panel, "", 20, UI.GREEN, true)
	task_title.add_theme_font_override("font", UI.weight(UI.BODY, 650))
	objective = UI.text(task_panel, "", 16, UI.INK, true)
	var workspace = HSplitContainer.new()
	workspace.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(workspace)
	var left = VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.custom_minimum_size.x = 480
	workspace.add_child(left)
	editor = CodeEdit.new()
	editor.gutters_draw_line_numbers = true
	editor.syntax_highlighter = Lecture.highlighter()
	editor.size_flags_vertical = Control.SIZE_EXPAND_FILL
	editor.custom_minimum_size.y = 142
	editor.add_theme_font_size_override("font_size", 18)
	left.add_child(editor)
	var sidebar = VBoxContainer.new()
	sidebar.custom_minimum_size.x = 240
	workspace.add_child(sidebar)
	UI.text(sidebar, "CATÁLOGO DE TU BASE", 12, UI.COPPER)
	catalog_column = UI.scroll(sidebar)
	var actions = HBoxContainer.new()
	add_child(actions)
	run_button = UI.action(actions, "Probar consulta", run_query.bind(false))
	submit_button = UI.action(actions, "Entregar", run_query.bind(true), true)
	hint_button = UI.action(actions, "Pista", hint)
	UI.action(actions, "Cuaderno", open_notes)
	hint_box = RichTextLabel.new()
	hint_box.fit_content = true
	hint_box.custom_minimum_size.y = 70
	hint_box.visible = false
	var hint_scroll = ScrollContainer.new()
	hint_scroll.name = "HintScroll"
	hint_scroll.custom_minimum_size.y = 100
	hint_scroll.visible = false
	hint_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hint_scroll.add_child(hint_box)
	add_child(hint_scroll)
	status = UI.text(self, "Puedes probar antes de entregar, los errores de sintaxis no consumen una respuesta", 14, UI.MUTED, true)
	result_title = UI.text(self, "RESULTADO DE TU CONSULTA", 12, UI.COPPER)
	output = Table.new()
	output.custom_minimum_size.y = 130
	output.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(output)
	load_task()
	pending = "catalog"
	set_busy(true)
	var payload = context()
	payload["action"] = "catalog"
	service.start_job(payload)

func context() -> Dictionary:
	if not case_id.is_empty(): return {"kind": "nexo", "case_id": case_id, "case_history": nexo.state()["completed_cases"].keys()}
	return {"kind": "school", "history": campaign.progress()["sql_history"], "legacy_base": campaign.progress().get("legacy_base", false),
		"reset_year4": campaign.progress().get("reset_year4", false), "sandbox": sandbox,
		"sandbox_history": store.data["sandbox_history"] if sandbox else []}

func load_task() -> void:
	exam_mode = case_id.is_empty() and not sandbox and campaign.day() == 5
	if not case_id.is_empty():
		task = preload("res://scripts/nexo_sql.gd").case_data(case_id)
		active_id = "case:" + case_id
		task_title.text = task["title"]
		objective.text = task["objective"]
	elif sandbox:
		active_id = "sandbox"
		task = {}
		task_title.text = "Tu base de experimentación"
		objective.text = "Prueba estructuras y consultas en una copia independiente, tus ejercicios del curso se conservan"
	elif exam_mode:
		var record = campaign.exam()
		if record["finished"]:
			show_exam_result()
			return
		var index = record["answers"].size()
		task = Course.exams(campaign.year())[index]
		active_id = "exam_%s_%s_%s" % [campaign.year(), campaign.progress()["attempts"].get(str(campaign.year()), 1), index]
		task_title.text = "Examen  ·  Pregunta %s de 5" % [index + 1]
		objective.text = task["objective"]
	else:
		active_id = campaign.current_task_id()
		task = Course.task(active_id)
		task_title.text = task.get("title", "Actividades del día completadas")
		objective.text = task.get("objective", "Puedes seguir practicando, cuando quieras terminar habla con Marco y vuelve a casa por la puerta")
	editor.text = campaign.progress()["drafts"].get(active_id, task.get("broken_sql", ""))
	editor.placeholder_text = "Escribe aquí tu consulta SQL"
	editor.editable = true
	hint_button.visible = not exam_mode and not task.is_empty()
	submit_button.visible = not sandbox and not task.is_empty()
	hint_box.get_parent().visible = false
	if not case_id.is_empty() and nexo.state()["completed_cases"].has(case_id):
		submit_button.visible = false
		status.text = "Encargo entregado, puedes seguir probando sin repetir las recompensas"
	hint_level = 0

func set_busy(value: bool) -> void:
	run_button.disabled = value
	submit_button.disabled = value

func run_query(submit: bool) -> void:
	if service.pid > 0 or is_instance_valid(notes_layer):
		return
	pending = "submit" if submit else "practice"
	sent_query = editor.text
	var payload = context()
	payload["query"] = sent_query
	payload["task_id"] = "" if sandbox else active_id
	set_busy(true)
	status.text = "Comprobando tu consulta…"
	service.start_job(payload)

func receive(result: Dictionary) -> void:
	set_busy(false)
	if result.has("catalog") and (not task.get("is_write", false) or pending in ["catalog", "inspect"] or (pending == "submit" and result.get("correct", false))):
		show_catalog(result["catalog"])
	if not result.get("ok", false):
		status.text = result.get("error", "No se pudo ejecutar la consulta")
		status.add_theme_color_override("font_color", UI.RED)
		if audio != null: audio.sfx("error")
		return
	if pending == "catalog":
		if not case_id.is_empty():
			output.set_data(result.get("columns", []), result.get("rows", []))
			result_title.text = "VISTA DE EJEMPLO  ·  " + result["catalog"][0]["name"] if not result.get("catalog", []).is_empty() else "VISTA DE EJEMPLO"
		status.text = "Tu base está lista, revisa el objetivo y los nombres del catálogo"
		return
	result_title.text = "MUESTRA DE LA TABLA" if pending == "inspect" else "RESULTADO DE TU CONSULTA"
	output.set_data(result.get("columns", []), result.get("rows", []))
	status.add_theme_color_override("font_color", UI.GREEN if result.get("correct", false) else UI.MUTED)
	if not case_id.is_empty():
		status.text = result.get("feedback", "Consulta ejecutada")
		if pending == "submit" and result.get("correct", false):
			if nexo.complete_case(case_id, sent_query):
				status.text = "Encargo completado  ·  +%s XP  ·  +%s reputación  ·  $%s" % [task["xp"], task["reputation"], task["money"]]
				submit_button.visible = false
				if audio != null: audio.sfx("success")
			else: status.text = nexo.notice
	elif sandbox:
		if result.get("sandbox_write", false):
			store.data["sandbox_history"].append(sent_query)
			store.save()
		status.text = "Cambio guardado en tu base libre" if result.get("sandbox_write", false) else "%s filas en el resultado" % result.get("rows", []).size()
	elif pending == "inspect":
		status.text = "Esta es una muestra de la tabla, tu consulta del editor se conserva"
	elif pending == "submit":
		var correct = result.get("correct", false)
		if exam_mode:
			if campaign.record_exam(correct, sent_query, result.get("feedback", ""), active_id if correct and task.get("is_write", false) else ""):
				status.text = "Respuesta entregada"
				load_task()
			else:
				status.text = store.notice
		elif correct:
			if campaign.complete_task(active_id):
				status.text = "¡Ejercicio completado! +100 XP para Liga de Dioses"
				if audio != null: audio.sfx("success")
				load_task()
			else:
				status.text = store.notice
		else:
			status.text = result.get("feedback", "Revisa el resultado antes de entregar")
	else:
		status.text = ("La solución cumple el objetivo, puedes entregarla" if result.get("correct", false) else result.get("feedback", "Consulta ejecutada"))
		if task.get("is_write", false) and result.get("correct", false):
			status.text = "Los cambios cumplen el objetivo, se confirmarán al entregar"
		if result.get("inspection", false):
			status.text = "Puedes explorar los datos, la tarea de escritura sigue pendiente"

func show_catalog(tables: Array) -> void:
	for child in catalog_column.get_children():
		catalog_column.remove_child(child)
		child.queue_free()
	for table in tables:
		var button = UI.action(catalog_column, table["name"], inspect_table.bind(table["name"]))
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		for column in table["columns"]:
			UI.text(catalog_column, column["name"] + "  ·  " + column["type"], 12, UI.MUTED, true)

func inspect_table(name: String) -> void:
	if service.pid > 0:
		return
	pending = "inspect"
	var payload = context()
	if not case_id.is_empty(): payload["action"] = "inspect"
	payload["query"] = "SELECT * FROM " + '"' + name.replace('"', '""') + '" LIMIT 30'
	set_busy(true)
	service.start_job(payload)

func hint() -> void:
	if exam_mode or task.is_empty():
		return
	hint_box.get_parent().visible = true
	hint_box.visible = true
	hint_box.text = task["hints"][mini(hint_level, 2)]
	hint_level = mini(2, hint_level + 1)
	hint_button.text = "Siguiente pista" if hint_level < 2 else "Solución explicada"

func open_notes() -> void:
	if is_instance_valid(notes_layer):
		return
	notes_layer = PanelContainer.new()
	notes_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	notes_layer.add_theme_stylebox_override("panel", UI.box(UI.PAPER, 12, 22))
	get_tree().current_scene.add_child(notes_layer)
	var column = VBoxContainer.new()
	notes_layer.add_child(column)
	var row = HBoxContainer.new()
	column.add_child(row)
	UI.heading(row, "Siempre a mano", "Tu cuaderno")
	UI.fill(row)
	UI.action(row, "Volver a mi consulta", handle_escape)
	var notes = Notebook.new()
	notes.store = store
	column.add_child(notes)

func handle_escape() -> bool:
	if not is_instance_valid(notes_layer):
		return false
	notes_layer.queue_free()
	notes_layer = null
	return true

func show_exam_result() -> void:
	task = {}
	task_title.text = "Evaluación terminada"
	var record = campaign.exam()
	objective.text = "%s de 5 respuestas correctas  ·  Nota %.1f  ·  %s" % [int(record["score"]), float(record["grade"]), "Aprobado" if record["grade"] >= 4 else "Volveremos a practicar este año"]
	editor.visible = false
	run_button.visible = false
	submit_button.visible = false
	hint_button.visible = false
	var rows = []
	for index in range(record["answers"].size()):
		var answer: Dictionary = record["answers"][index]
		rows.append([index + 1, "Recuperada" if answer.get("recovered", false) else "Correcta" if answer["correct"] else "Para revisar", answer.get("feedback", "")])
	output.set_data(["Pregunta", "Resultado", "Retroalimentación"], rows)

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and not is_instance_valid(notes_layer):
		if event.ctrl_pressed and event.keycode == KEY_ENTER:
			run_query(event.shift_pressed and not sandbox)
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_F1:
			open_notes()
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_F3:
			hint()
			get_viewport().set_input_as_handled()

func _exit_tree() -> void:
	if is_instance_valid(notes_layer):
		notes_layer.queue_free()
	if is_instance_valid(editor):
		campaign.progress()["drafts"][active_id] = editor.text
		store.save()
