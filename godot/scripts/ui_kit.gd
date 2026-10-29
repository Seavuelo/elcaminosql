extends RefCounted

const BODY = preload("res://assets/fonts/inter.ttf")
const TITLE = preload("res://assets/fonts/fraunces.ttf")
const CODE = preload("res://assets/fonts/jetbrainsmono.ttf")
const INK = Color("253d36")
const MUTED = Color("677369")
const GREEN = Color("295e4c")
const DEEP = Color("183e34")
const PAPER = Color("f4eedf")
const WHITE = Color("fffaf0")
const GOLD = Color("d9b77c")
const COPPER = Color("a96c43")
const RED = Color("a44b46")

static func weight(font: Font, value: int) -> FontVariation:
	var variation = FontVariation.new()
	variation.base_font = font
	variation.variation_opentype = {TextServerManager.get_primary_interface().name_to_tag("wght"): value}
	return variation

static func box(color: Color = WHITE, radius: int = 16, padding: int = 20) -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(radius)
	style.set_content_margin_all(padding)
	return style

static func theme() -> Theme:
	var result = Theme.new()
	result.default_font = BODY
	result.default_font_size = 16
	for control in ["Label", "Button", "CheckBox", "OptionButton", "LineEdit", "Tree", "TabContainer", "RichTextLabel"]:
		result.set_color("font_color", control, INK)
	result.set_stylebox("panel", "PanelContainer", box())
	result.set_constant("separation", "VBoxContainer", 14)
	result.set_constant("separation", "HBoxContainer", 14)
	result.set_stylebox("normal", "Button", box(Color("e8e9dc"), 10, 13))
	result.set_stylebox("hover", "Button", box(Color("dce3cf"), 10, 13))
	result.set_stylebox("pressed", "Button", box(GOLD, 10, 13))
	var focus = box(Color(0, 0, 0, 0), 10, 0)
	focus.border_color = COPPER
	focus.set_border_width_all(3)
	result.set_stylebox("focus", "Button", focus)
	result.set_color("font_hover_color", "Button", INK)
	result.set_color("font_pressed_color", "Button", INK)
	result.set_color("font_focus_color", "Button", INK)
	result.set_color("font_disabled_color", "Button", MUTED)
	result.set_stylebox("disabled", "Button", box(Color("e3e3d7"), 10, 13))
	result.set_color("font_placeholder_color", "LineEdit", MUTED)
	result.set_color("caret_color", "LineEdit", GREEN)
	result.set_stylebox("panel", "ItemList", box(Color("e7e8db"), 10, 10))
	result.set_stylebox("selected", "ItemList", box(Color("c8d9c0"), 6, 8))
	result.set_stylebox("selected_focus", "ItemList", box(Color("c8d9c0"), 6, 8))
	result.set_color("font_color", "ItemList", INK)
	result.set_color("font_selected_color", "ItemList", GREEN)
	result.set_stylebox("panel", "PopupMenu", box(WHITE, 10, 10))
	result.set_stylebox("hover", "PopupMenu", box(Color("dce3cf"), 6, 8))
	result.set_color("font_color", "PopupMenu", INK)
	result.set_color("font_hover_color", "PopupMenu", GREEN)
	result.set_stylebox("normal", "LineEdit", box(Color("ecebdf"), 8, 12))
	result.set_stylebox("focus", "LineEdit", box(Color("e1e9d7"), 8, 12))
	result.set_stylebox("normal", "CodeEdit", box(Color("17312f"), 10, 16))
	result.set_stylebox("focus", "CodeEdit", box(Color("17312f"), 10, 16))
	result.set_font("font", "CodeEdit", CODE)
	result.set_stylebox("read_only", "CodeEdit", box(Color("17312f"), 10, 16))
	result.set_color("font_readonly_color", "CodeEdit", Color("ece9d8"))
	result.set_color("font_color", "CodeEdit", Color("ece9d8"))
	result.set_color("caret_color", "CodeEdit", Color("f3d7a0"))
	result.set_color("line_number_color", "CodeEdit", Color("91a79b"))
	result.set_stylebox("panel", "Tree", box(Color("efeddf"), 10, 12))
	result.set_stylebox("panel", "TabContainer", box(WHITE, 10, 12))
	for type in ["TabContainer", "TabBar"]:
		result.set_stylebox("tab_selected", type, box(GREEN, 8, 12))
		result.set_stylebox("tab_unselected", type, box(Color("e4e7d7"), 8, 12))
		result.set_color("font_selected_color", type, WHITE)
		result.set_color("font_unselected_color", type, INK)
	result.set_stylebox("background", "ProgressBar", box(Color("d9dfcd"), 5, 0))
	result.set_stylebox("fill", "ProgressBar", box(GREEN, 5, 0))
	return result

static func text(parent: Node, value: String, size: int = 16, color: Color = INK, wrap: bool = false) -> Label:
	var label = Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	if wrap:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(label)
	return label

static func heading(parent: Node, eyebrow: String, title: String, subtitle: String = "") -> VBoxContainer:
	var column = VBoxContainer.new()
	column.add_theme_constant_override("separation", 5)
	parent.add_child(column)
	text(column, eyebrow.to_upper(), 12, COPPER)
	var title_label = text(column, title, 32, GREEN, true)
	title_label.add_theme_font_override("font", weight(TITLE, 600))
	if not subtitle.is_empty():
		text(column, subtitle, 15, MUTED, true)
	return column

static func action(parent: Node, title: String, callback: Callable, primary: bool = false) -> Button:
	var button = Button.new()
	button.text = title
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	button.custom_minimum_size.y = 46
	if primary:
		button.add_theme_stylebox_override("normal", box(GREEN, 10, 13))
		button.add_theme_stylebox_override("hover", box(GREEN.lightened(0.1), 10, 13))
		button.add_theme_color_override("font_color", WHITE)
		button.add_theme_color_override("font_hover_color", Color.WHITE)
		button.add_theme_color_override("font_focus_color", Color.WHITE)
	button.pressed.connect(func():
		for audio in button.get_tree().get_nodes_in_group("game_audio"):
			audio.sfx("key")
		callback.call()
	)
	parent.add_child(button)
	return button

static func wrapped_lines(value: String, width: float, font: Font, point: int) -> PackedStringArray:
	var lines = PackedStringArray()
	var line = ""
	for word in value.split(" "):
		var next = word if line.is_empty() else line + " " + word
		if not line.is_empty() and font.get_string_size(next, HORIZONTAL_ALIGNMENT_LEFT, -1, point).x > width:
			lines.append(line)
			line = word
		else:
			line = next
	if not line.is_empty():
		lines.append(line)
	return lines

static func card(parent: Node, color: Color = WHITE) -> VBoxContainer:
	var panel = PanelContainer.new()
	panel.add_theme_stylebox_override("panel", box(color))
	parent.add_child(panel)
	var column = VBoxContainer.new()
	panel.add_child(column)
	return column

static func margin(parent: Node, padding: int = 28) -> MarginContainer:
	var margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + edge, padding)
	parent.add_child(margin)
	return margin

static func fill(parent: Node, vertical: bool = false) -> Control:
	var spacer = Control.new()
	if vertical:
		spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	else:
		spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(spacer)
	return spacer

static func scroll(parent: Node) -> VBoxContainer:
	var scroll = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	parent.add_child(scroll)
	var column = VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(column)
	return column

static func compact(button: Button) -> Button:
	button.custom_minimum_size.y = 34
	button.add_theme_font_size_override("font_size", 14)
	for state in ["normal", "hover", "pressed", "disabled"]:
		var style = button.get_theme_stylebox(state).duplicate()
		style.set_content_margin_all(8)
		button.add_theme_stylebox_override(state, style)
	return button

static func select_nav(parent: HBoxContainer, title: String) -> void:
	for button in parent.get_children():
		if not button is Button: continue
		var active = button.text == title
		button.add_theme_stylebox_override("normal", box(GREEN if active else Color("e8e9dc"), 10, 13))
		button.add_theme_stylebox_override("hover", box(GREEN.lightened(0.1) if active else Color("dce3cf"), 10, 13))
		for key in ["font_color", "font_hover_color", "font_focus_color"]:
			button.add_theme_color_override(key, WHITE if active else INK)
