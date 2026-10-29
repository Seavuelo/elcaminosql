extends ScrollContainer

const UI = preload("res://scripts/ui_kit.gd")
var dark = false
var grid: GridContainer

func display(value: Variant) -> String:
	if value == null:
		return "NULL"
	if value is float and is_finite(value) and value == floor(value) and absf(value) < 9007199254740992:
		return str(int(value))
	return str(value)

func set_data(columns: Array, rows: Array) -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()
	grid = GridContainer.new()
	grid.columns = maxi(1, columns.size())
	grid.add_theme_constant_override("h_separation", 1)
	grid.add_theme_constant_override("v_separation", 1)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(grid)
	var widths = []
	for i in range(columns.size()):
		var width = UI.BODY.get_string_size(str(columns[i]), HORIZONTAL_ALIGNMENT_LEFT, -1, 15).x + 26
		for row in rows:
			var value = row.get(columns[i]) if row is Dictionary else row[i]
			width = maxf(width, UI.BODY.get_string_size(display(value), HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 24)
		widths.append(clampf(width, 100, 290))
		cell(str(columns[i]), widths[i], true, false)
	for index in range(rows.size()):
		var row = rows[index]
		for i in range(columns.size()):
			var value = row.get(columns[i]) if row is Dictionary else row[i]
			cell(display(value), widths[i], false, index % 2 == 1)
	if rows.is_empty() and not columns.is_empty():
		for i in range(columns.size()):
			cell("Sin filas" if i == 0 else "", widths[i], false, false)

func cell(value: String, width: float, header: bool, alternate: bool) -> void:
	var panel = PanelContainer.new()
	var color = Color("345c4d") if dark else Color("dce5d4")
	if not header:
		color = (Color("22483c") if alternate else Color("274f42")) if dark else (Color("f1f0e5") if alternate else Color("f8f5ea"))
	var style = UI.box(color, 0, 10)
	panel.add_theme_stylebox_override("panel", style)
	grid.add_child(panel)
	var text = UI.text(panel, value, 15 if header else 16, UI.PAPER if dark else UI.GREEN if header else UI.INK, true)
	text.custom_minimum_size.x = width
	if header:
		text.add_theme_font_override("font", UI.weight(UI.BODY, 650))
