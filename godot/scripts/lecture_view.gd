extends VBoxContainer

signal completed

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
const Figure = preload("res://scripts/learning_figure.gd")
const Table = preload("res://scripts/table_view.gd")
const Avatar = preload("res://scripts/avatar_view.gd")
var store
var audio
var year = 0
var day = 1
var index = 0
var boards: Array = []
var canvas: VBoxContainer
var speech: RichTextLabel
var position_label: Label
var progress_bar: ProgressBar
var previous: Button
var following: Button
var voice_button: Button
var transcript_button: Button
var transcript = false
var spoken_part = 0
var code_view: CodeEdit
var figure_view

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	boards = Course.lesson(year, day)
	index = clampi(int(store.data["campaign"]["lecture_pages"].get(Course.key(year, day), 0)), 0, maxi(0, boards.size() - 1))
	var board = PanelContainer.new()
	board.size_flags_vertical = Control.SIZE_EXPAND_FILL
	board.add_theme_stylebox_override("panel", UI.box(Color("1f473b"), 12, 22))
	add_child(board)
	canvas = VBoxContainer.new()
	canvas.add_theme_constant_override("separation", 12)
	board.add_child(canvas)
	var caption_panel = PanelContainer.new()
	caption_panel.add_theme_stylebox_override("panel", UI.box(Color("eee7d5"), 12, 14))
	add_child(caption_panel)
	var caption = HBoxContainer.new()
	caption_panel.add_child(caption)
	var portrait = Avatar.new()
	portrait.profile = {"skin": 0, "hair": 1, "shirt": 5, "hair_style": 0, "clothing_style": 4, "glasses": true}
	portrait.custom_minimum_size = Vector2(76, 94)
	caption.add_child(portrait)
	var words = VBoxContainer.new()
	words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	caption.add_child(words)
	UI.text(words, "PROFESOR MARCO", 12, UI.COPPER)
	var scroller = ScrollContainer.new()
	scroller.custom_minimum_size.y = 106
	scroller.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	words.add_child(scroller)
	speech = RichTextLabel.new()
	speech.fit_content = true
	speech.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	speech.add_theme_color_override("default_color", UI.INK)
	speech.add_theme_font_size_override("normal_font_size", 17)
	scroller.add_child(speech)
	var navigation = HBoxContainer.new()
	add_child(navigation)
	previous = UI.action(navigation, "Anterior", step.bind(-1))
	voice_button = UI.action(navigation, "", toggle_voice)
	UI.action(navigation, "Repetir voz", repeat_voice)
	transcript_button = UI.action(navigation, "Ver texto completo", func(): transcript = not transcript; update_caption())
	UI.fill(navigation)
	position_label = UI.text(navigation, "", 14, UI.MUTED)
	following = UI.action(navigation, "Continuar", step.bind(1), true)
	progress_bar = ProgressBar.new()
	progress_bar.custom_minimum_size.y = 4
	progress_bar.show_percentage = false
	progress_bar.add_theme_stylebox_override("background", UI.box(Color("dce0ce"), 2, 0))
	progress_bar.add_theme_stylebox_override("fill", UI.box(UI.COPPER, 2, 0))
	add_child(progress_bar)
	if audio != null: audio.speech_changed.connect(on_speech_changed)
	show_board()

static func highlighter() -> CodeHighlighter:
	var syntax = CodeHighlighter.new()
	syntax.function_color = Color("e5c48b")
	syntax.member_variable_color = Color("ede7d2")
	syntax.number_color = Color("edbb79")
	syntax.symbol_color = Color("ed9e8e")
	syntax.add_color_region("'", "'", Color("a8d6a1"))
	syntax.add_color_region("--", "", Color("8fae9a"), true)
	for word in ["SELECT", "DISTINCT", "FROM", "WHERE", "AND", "OR", "NOT", "NULL", "IS", "ORDER", "BY", "ASC", "DESC", "LIMIT", "OFFSET", "AS", "WITH", "IN", "JOIN", "LEFT", "INNER", "ON", "GROUP", "HAVING", "COUNT", "SUM", "AVG", "MIN", "MAX", "CREATE", "TABLE", "INDEX", "VIEW", "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "PRIMARY", "FOREIGN", "KEY", "REFERENCES", "CHECK", "UNIQUE", "BETWEEN", "INTEGER", "TEXT", "REAL", "NUMERIC", "VARCHAR", "DATE", "BLOB", "CASE", "WHEN", "THEN", "ELSE", "END"]:
		syntax.add_keyword_color(word, Color("98c8e2"))
		syntax.add_keyword_color(word.to_lower(), Color("98c8e2"))
	return syntax

func show_board() -> void:
	code_view = null
	figure_view = null
	spoken_part = 0
	for child in canvas.get_children():
		canvas.remove_child(child)
		child.queue_free()
	if boards.is_empty():
		return
	var board: Dictionary = boards[index]
	var title = UI.text(canvas, board.get("chalk_title", board["title"]), 27, Color("ecdfba"), true)
	title.add_theme_font_override("font", UI.weight(UI.TITLE, 600))
	if not board.get("chalk_body", "").is_empty():
		UI.text(canvas, board["chalk_body"], 18, Color("c5d3bd"), true)
	var row = HBoxContainer.new()
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	canvas.add_child(row)
	var code: String = board.get("code_example", "")
	if not code.is_empty():
		var editor = CodeEdit.new()
		code_view = editor
		editor.editable = false
		editor.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
		editor.syntax_highlighter = highlighter()
		editor.text = code
		editor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		editor.size_flags_vertical = Control.SIZE_EXPAND_FILL
		editor.custom_minimum_size.y = 135
		editor.add_theme_font_size_override("font_size", 19)
		editor.add_theme_color_override("caret_color", Color.TRANSPARENT)
		row.add_child(editor)
	if not board.get("table_columns", []).is_empty():
		var table = Table.new()
		table.dark = true
		table.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		table.size_flags_vertical = Control.SIZE_EXPAND_FILL
		table.custom_minimum_size.y = 135
		row.add_child(table)
		table.set_data(board["table_columns"], board["table_rows"])
	elif board.has("illustration"):
		var figure = Figure.new()
		figure_view = figure
		figure.kind = board["illustration"]
		figure.dark = true
		figure.profile = store.data
		figure.variant = index % 3
		figure.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		figure.size_flags_vertical = Control.SIZE_EXPAND_FILL
		row.add_child(figure)
	update_caption()
	previous.disabled = index == 0
	following.text = "Terminar clase" if index == boards.size() - 1 else "Continuar"
	position_label.text = "%s / %s" % [index + 1, boards.size()]
	progress_bar.value = float(index + 1) / boards.size() * 100
	voice_button.text = "Voz activada" if store.data["settings"]["narration_enabled"] else "Voz desactivada"
	store.data["campaign"]["lecture_pages"][Course.key(year, day)] = index
	store.save()
	if audio != null:
		audio.sfx("chalk")
		audio.speak(board["speech_parts"])

func step(direction: int) -> void:
	if direction > 0 and index == boards.size() - 1:
		completed.emit()
		return
	index = clampi(index + direction, 0, maxi(0, boards.size() - 1))
	show_board()

func toggle_voice() -> void:
	store.data["settings"]["narration_enabled"] = not store.data["settings"]["narration_enabled"]
	store.save()
	voice_button.text = "Voz activada" if store.data["settings"]["narration_enabled"] else "Voz desactivada"
	update_caption()
	if audio != null:
		audio.apply_settings()
		if store.data["settings"]["narration_enabled"]:
			repeat_voice()

func repeat_voice() -> void:
	if audio != null and not boards.is_empty():
		audio.speak(boards[index]["speech_parts"])

func _exit_tree() -> void:
	if is_instance_valid(audio):
		if audio.speech_changed.is_connected(on_speech_changed): audio.speech_changed.disconnect(on_speech_changed)
		audio.stop_voice()

func on_speech_changed(part: int) -> void:
	spoken_part = part
	update_caption()
	if boards.is_empty(): return
	var parts: Array = boards[index]["speech_parts"]
	if part < 0 or part >= parts.size(): return
	var focus = int(parts[part].get("focus", 0))
	if is_instance_valid(code_view):
		for line in range(code_view.get_line_count()): code_view.set_line_background_color(line, Color.TRANSPARENT)
		if focus >= 0 and focus < code_view.get_line_count(): code_view.set_line_background_color(focus, Color("345b48"))
	if is_instance_valid(figure_view):
		figure_view.variant = focus
		figure_view.queue_redraw()
func update_caption() -> void:
	if not is_instance_valid(speech) or boards.is_empty(): return
	var parts: Array = boards[index]["speech_parts"]
	var show_all = transcript or not store.data["settings"]["narration_enabled"]
	if show_all:
		var lines = PackedStringArray()
		for part in parts: lines.append(part["text"].replace("\n", " "))
		speech.text = "\n\n".join(lines)
	else:
		speech.text = parts[clampi(spoken_part, 0, maxi(0, parts.size() - 1))]["text"] if not parts.is_empty() else ""
	transcript_button.disabled = not store.data["settings"]["narration_enabled"]
	transcript_button.text = "Texto completo" if transcript_button.disabled else "Seguir la voz" if transcript else "Ver texto completo"
