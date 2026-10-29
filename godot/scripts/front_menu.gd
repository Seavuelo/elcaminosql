extends Control

signal continue_game
signal new_game
signal settings
signal credits
signal quit_game

const UI = preload("res://scripts/ui_kit.gd")
const Brand = preload("res://scripts/brand.gd")
const Room = preload("res://scripts/room_view.gd")
var store

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var background = ColorRect.new()
	background.color = UI.DEEP
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	var row = HBoxContainer.new()
	UI.margin(self, 42).add_child(row)
	row.add_theme_constant_override("separation", 38)
	var left = VBoxContainer.new()
	left.custom_minimum_size.x = 366
	left.add_theme_constant_override("separation", 18)
	row.add_child(left)
	UI.text(left, "UNA VIDA ENTRE DATOS", 12, UI.GOLD)
	UI.fill(left, true)
	var brand = Brand.new()
	brand.large = true
	brand.light = true
	brand.custom_minimum_size = Vector2(350, 190)
	left.add_child(brand)
	UI.text(left, "Aprende, conecta y construye tu camino", 19, UI.PAPER, true)
	UI.text(left, "De tu primera clase a los proyectos que compartirás con el mundo", 15, Color("b1c4ac"), true)
	var continue_button = UI.action(left, "Continuar mi historia", func(): continue_game.emit(), true)
	continue_button.disabled = not store.data["campaign"]["started"]
	var new_button = UI.action(left, "Comenzar una nueva historia", func(): new_game.emit())
	var lower = HBoxContainer.new()
	left.add_child(lower)
	UI.action(lower, "Ajustes", func(): settings.emit()).size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.action(lower, "Créditos", func(): credits.emit()).size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.action(left, "Salir", func(): quit_game.emit())
	UI.fill(left, true)
	UI.text(left, "Creado por Seavuelo  ·  Siempre gratuito", 12, Color("b1c4ac"))
	var scene = VBoxContainer.new()
	scene.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(scene)
	var preview = Room.new()
	preview.state = store
	preview.enabled = false
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	preview.size_flags_vertical = Control.SIZE_EXPAND_FILL
	preview.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scene.add_child(preview)
	var caption = UI.text(scene, "Un lugar para volver, algo nuevo por aprender", 14, Color("c9d3b8"))
	caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if not continue_button.disabled:
		continue_button.grab_focus()
	else:
		new_button.grab_focus()
