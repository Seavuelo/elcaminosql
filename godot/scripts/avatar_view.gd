extends Control

const Character = preload("res://scripts/character_art.gd")
var profile: Dictionary
var facing = "down"

func _draw() -> void:
	var scale = minf(4.0, minf(size.x / 30.0, size.y / 65.0))
	var center = Vector2(size.x * 0.5, size.y * 0.5 + 26 * scale)
	draw_circle(size * 0.5, minf(size.x, minf(size.y, 260)) * 0.46, Color("e8cfa6"))
	if not profile.is_empty():
		Character.paint(self, center, profile, scale, 0, facing)
