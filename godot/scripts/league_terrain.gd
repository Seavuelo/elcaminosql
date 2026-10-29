extends Control
var paths = [
	[Vector2(0.08, 0.88), Vector2(0.08, 0.15), Vector2(0.91, 0.15), Vector2(0.92, 0.12)],
	[Vector2(0.08, 0.88), Vector2(0.92, 0.12)],
	[Vector2(0.08, 0.88), Vector2(0.90, 0.88), Vector2(0.92, 0.12)]
]
func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	show_behind_parent = true
	resized.connect(queue_redraw)
func bounds() -> Rect2:
	var width = minf(size.x - 24, (size.y - 24) * 304.0 / 154)
	var dimensions = Vector2(width, width * 154.0 / 304)
	return Rect2((size - dimensions) / 2, dimensions)
func point(value: Vector2) -> Vector2: return bounds().position + bounds().size * value
func route(index: int, progress: float) -> Vector2:
	var points = paths[index]
	var length = 0.0
	for i in range(points.size() - 1): length += points[i].distance_to(points[i + 1])
	var distance = clampf(progress, 0, 1) * length
	for i in range(points.size() - 1):
		var segment = points[i].distance_to(points[i + 1])
		if distance <= segment: return point(points[i].lerp(points[i + 1], distance / segment))
		distance -= segment
	return point(points[-1])
func _draw() -> void:
	var rect = bounds()
	if rect.size.x <= 0: return
	var scale = rect.size.x / 800
	var style = StyleBoxFlat.new()
	style.bg_color = Color("213e38")
	style.set_corner_radius_all(18)
	style.border_color = Color("82714d")
	style.set_border_width_all(2)
	draw_style_box(style, rect.grow(5))
	var rng = RandomNumberGenerator.new()
	rng.seed = 54377
	for i in range(580):
		var p = rect.position + Vector2(rng.randf(), rng.randf()) * rect.size
		draw_circle(p, rng.randf_range(1, 4) * scale, Color("345342") if i % 2 else Color("294b40"))
	var river = PackedVector2Array()
	for p in [Vector2(0.35, 0), Vector2(0.41, 0), Vector2(0.46, 0.25), Vector2(0.60, 0.62), Vector2(0.66, 1), Vector2(0.60, 1), Vector2(0.54, 0.62), Vector2(0.40, 0.25)]: river.append(point(p))
	draw_colored_polygon(river, Color("2c6662"))
	var stream = PackedVector2Array()
	for p in [Vector2(0.365, 0), Vector2(0.39, 0), Vector2(0.445, 0.25), Vector2(0.58, 0.62), Vector2(0.645, 1), Vector2(0.62, 1), Vector2(0.56, 0.62), Vector2(0.42, 0.25)]: stream.append(point(p))
	draw_colored_polygon(stream, Color("3b7770"))
	for path in paths:
		var points = PackedVector2Array()
		for p in path: points.append(point(p))
		draw_polyline(points, Color("344639"), 30 * scale, true)
		draw_polyline(points, Color("9b9673"), 19 * scale, true)
		draw_polyline(points, Color("b8ad83"), 11 * scale, true)
	for i in range(190):
		var p = Vector2(rng.randf_range(0.14, 0.87), rng.randf_range(0.21, 0.78))
		var clear = absf(p.y - (1 - p.x)) < 0.09 or absf(p.x - (0.38 + p.y * 0.25)) < 0.045
		if clear: continue
		var at = point(p)
		var radius = rng.randf_range(8, 16) * scale
		draw_circle(at + Vector2(3, 5) * scale, radius, Color("18342f"))
		draw_line(at + Vector2(0, 7) * scale, at - Vector2(0, 7) * scale, Color("6e6949"), 3 * scale)
		draw_colored_polygon(PackedVector2Array([at + Vector2(-radius, 1), at + Vector2(0, -radius * 1.6), at + Vector2(radius, 1)]), Color("3a6347") if i % 2 else Color("4b7451"))
		draw_line(at + Vector2(-radius * 0.4, -radius * 0.4), at + Vector2(0, -radius * 1.5), Color("719166"), scale)
	for at in [Vector2(0.32, 0.51), Vector2(0.69, 0.48)]:
		var p = point(at)
		draw_arc(p, 23 * scale, 0, TAU, 32, Color("7c8d74"), 4 * scale, true)
		draw_circle(p, 15 * scale, Color("29433a"))
	for side in range(2):
		var p = point(Vector2(0.08, 0.88) if side == 0 else Vector2(0.92, 0.12))
		var color = Color("79d6bb") if side == 0 else Color("e7a2a0")
		draw_circle(p + Vector2(0, 3), 24 * scale, Color("716f59"))
		draw_arc(p, 29 * scale, 0, TAU, 40, color.darkened(0.3), 2 * scale, true)
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -29) * scale, p + Vector2(13, -4) * scale, p + Vector2(0, 12) * scale, p + Vector2(-13, -4) * scale]), color)
		draw_line(p + Vector2(0, -26) * scale, p + Vector2(0, 8) * scale, color.lightened(0.45), 2 * scale)
