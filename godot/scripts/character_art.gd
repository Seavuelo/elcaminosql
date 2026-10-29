extends RefCounted

const Course = preload("res://scripts/course_data.gd")

static func color(data: Dictionary, rgb_key: String, palette: String, index_key: String, fallback: Color) -> Color:
	if data.get(rgb_key) is Array and data[rgb_key].size() == 3:
		var rgb: Array = data[rgb_key]
		return Color(float(rgb[0]) / 255, float(rgb[1]) / 255, float(rgb[2]) / 255)
	return Course.color(palette, int(data.get(index_key, 0)), fallback)

static func paint(canvas: CanvasItem, center: Vector2, data: Dictionary, scale: float = 1.0, stride: float = 0.0, facing: String = "down") -> void:
	var skin = color(data, "skin_rgb", "skin_tones", "skin", Color("efc69e"))
	var hair = color(data, "hair_rgb", "hair_colors", "hair", Color("654531"))
	var shirt = color(data, "shirt_rgb", "shirt_colors", "shirt", Color("4e8594"))
	var eyes = color(data, "eyes_rgb", "eye_colors", "eye_color", Color("6e713f"))
	var pants = color(data, "pants_rgb", "pants_colors", "pants_color", Color("384351"))
	var shoes = color(data, "shoes_rgb", "shoe_colors", "shoe_color", Color("343239"))
	var backpack = Course.color("backpack_colors", int(data.get("backpack_color", 0)))
	var hair_style = int(data.get("hair_style", 0))
	var clothing = int(data.get("clothing_style", 0))
	var side_view = facing in ["left", "right"]
	var sleeve = clothing in [1, 2, 4, 5, 6, 7]
	canvas.draw_set_transform(center, 0, Vector2.ONE * scale)
	var shadow = PackedVector2Array()
	for point in range(20):
		var angle = point / 20.0 * TAU
		shadow.append(Vector2(cos(angle) * 11, sin(angle) * 4 - 1))
	canvas.draw_colored_polygon(shadow, Color(0, 0, 0, 0.13))
	if hair_style == 1:
		canvas.draw_rect(Rect2(-11, -51, 23, 31), hair.darkened(0.12))
	for side in [-1, 1]:
		var x = side * 4 - 3 if not side_view else side * 2 - 2
		var leg = Rect2(x, -14 + (0 if data.get("packing", false) else stride * side), 6, 13)
		canvas.draw_rect(leg, pants.darkened(0.1 if side < 0 else 0.0))
		canvas.draw_rect(Rect2(leg.position + Vector2(-1, 10), Vector2(8, 4)), shoes)
		if int(data.get("shoe_style", 0)) == 1:
			canvas.draw_rect(Rect2(leg.position + Vector2(-1, 7), Vector2(7, 4)), shoes)
		else:
			canvas.draw_line(leg.position + Vector2(0, 12), leg.position + Vector2(6, 12), shoes.lightened(0.3), 1)
	canvas.draw_rect(Rect2(-9, -33, 18, 21), shirt.darkened(0.15))
	canvas.draw_rect(Rect2(-7, -33, 12, 18), shirt)
	for side in [-1, 1]:
		var x = -12 if side < 0 else 8
		var offset = stride * side * 0.5
		canvas.draw_rect(Rect2(x, -29 + offset, 5, 14), shirt.darkened(0.1 if side > 0 else 0.0) if sleeve else skin)
		canvas.draw_rect(Rect2(x, -29 + offset, 5, 6), shirt)
		canvas.draw_rect(Rect2(x, -17 + offset, 5, 5), skin)
	if clothing == 3:
		for y in [-28, -23, -18]:
			canvas.draw_rect(Rect2(-7, y, 14, 2), shirt.lightened(0.4))
	elif clothing in [2, 5, 7]:
		canvas.draw_rect(Rect2(-3, -32, 7, 19), Color("e8ddbf"))
		canvas.draw_line(Vector2(-4, -32), Vector2(-4, -13), shirt.darkened(0.3), 1)
	elif clothing == 4:
		for y in [-27, -22, -17]:
			canvas.draw_circle(Vector2(0, y), 1, shirt.darkened(0.45))
	elif clothing == 1:
		canvas.draw_line(Vector2(-4, -30), Vector2(-2, -23), shirt.lightened(0.55), 1)
		canvas.draw_line(Vector2(4, -30), Vector2(2, -23), shirt.lightened(0.55), 1)
	canvas.draw_rect(Rect2(-8, -49, 17, 18), skin)
	canvas.draw_rect(Rect2(7, -43, 4, 7), skin.darkened(0.08))
	if hair_style != 3:
		canvas.draw_rect(Rect2(-10, -52, 19, 8), hair)
		canvas.draw_rect(Rect2(-10, -45, 5, 11), hair)
		canvas.draw_rect(Rect2(6, -46, 4, 6), hair.darkened(0.1))
		canvas.draw_rect(Rect2(-7, -52, 13, 3), hair.lightened(0.12))
	else:
		canvas.draw_rect(Rect2(-8, -50, 17, 3), hair.darkened(0.08))
	if hair_style == 2:
		for x in [-8, -2, 4]:
			canvas.draw_rect(Rect2(x, -55 - (x % 3), 6, 6), hair)
	elif hair_style == 4:
		for x in [-8, -3, 2, 7]:
			canvas.draw_circle(Vector2(x, -50), 4, hair)
			canvas.draw_circle(Vector2(x, -52), 2, hair.lightened(0.08))
	if facing == "up":
		canvas.draw_rect(Rect2(-8, -46, 17, 14 if hair_style != 1 else 26), hair)
		canvas.draw_line(Vector2(-6, -41), Vector2(7, -41), hair.lightened(0.08), 2)
		if data.get("show_backpack", true) and hair_style != 1:
			canvas.draw_rect(Rect2(-7, -30, 14, 16), backpack.darkened(0.25))
			canvas.draw_rect(Rect2(-5, -29, 10, 12), backpack)
	elif side_view:
		var side = -1 if facing == "left" else 1
		canvas.draw_rect(Rect2(-9 if side > 0 else 4, -46, 6, 13 if hair_style != 1 else 26), hair)
		canvas.draw_rect(Rect2(5 if side > 0 else -6, -41, 2, 3), eyes)
		canvas.draw_rect(Rect2(8 if side > 0 else -11, -39, 3, 4), skin)
	else:
		canvas.draw_rect(Rect2(-2, -41, 2, 3), eyes)
		canvas.draw_rect(Rect2(5, -41, 2, 3), eyes)
		canvas.draw_line(Vector2(1, -35), Vector2(4, -35), skin.darkened(0.3), 1)
		if data.get("glasses", false):
			canvas.draw_rect(Rect2(-4, -43, 6, 6), Color("403c36"), false, 1)
			canvas.draw_rect(Rect2(3, -43, 6, 6), Color("403c36"), false, 1)
			canvas.draw_line(Vector2(2, -40), Vector2(3, -40), Color("403c36"), 1)
	canvas.draw_line(Vector2(-5, -31), Vector2(5, -31), shirt.lightened(0.2), 2)
