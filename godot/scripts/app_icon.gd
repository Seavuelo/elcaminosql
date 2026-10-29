extends Button

var kind = "nexo"

func _draw() -> void:
	var p = Vector2(size.x * 0.5, 48)
	if kind == "nexo":
		var color = Color("e8e8c7")
		for offset in [Vector2(-27, 15), Vector2(27, 15), Vector2(0, -21)]:
			draw_line(p, p + offset, color, 4, true)
			draw_circle(p + offset, 8, color)
		draw_circle(p, 11, Color("d8b77a"))
	else:
		draw_colored_polygon(PackedVector2Array([p + Vector2(-32, -30), p + Vector2(32, -30), p + Vector2(27, 11), p + Vector2(0, 35), p + Vector2(-27, 11)]), Color("796348"))
		draw_colored_polygon(PackedVector2Array([p + Vector2(-24, -23), p + Vector2(24, -23), p + Vector2(20, 8), p + Vector2(0, 27), p + Vector2(-20, 8)]), Color("f3dc9e"))
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -18), p + Vector2(15, 2), p + Vector2(0, 20), p + Vector2(-15, 2)]), Color("b7634b"))
		draw_line(p + Vector2(0, -18), p + Vector2(0, 20), Color("efb886"), 2)
