extends Control

const UI = preload("res://scripts/ui_kit.gd")
var large = false
var light = false

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func _draw() -> void:
	var ink = UI.WHITE if light else UI.GREEN
	var serif = UI.weight(UI.TITLE, 650)
	if large:
		draw_string(serif, Vector2(0, 61), "El Camino", HORIZONTAL_ALIGNMENT_LEFT, -1, 64, ink)
		draw_string(UI.weight(UI.BODY, 750), Vector2(0, 151), "SQL", HORIZONTAL_ALIGNMENT_LEFT, -1, 88, UI.GOLD)
		draw_line(Vector2(3, 181), Vector2(311, 181), UI.COPPER, 1, true)
		draw_circle(Vector2(320, 181), 3, UI.GOLD)
	else:
		draw_texture_rect(preload("res://icon.svg"), Rect2(0, 0, 38, 38), false)
		draw_string(serif, Vector2(48, 29), "El Camino SQL", HORIZONTAL_ALIGNMENT_LEFT, -1, 27, ink)
