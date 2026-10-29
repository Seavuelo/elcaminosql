extends Control

signal changed
signal message(text: String)
signal interacted(id: String)
signal nearby_changed(id: String, label: String)

const Layout = preload("res://scripts/room_layout.gd")
const Character = preload("res://scripts/character_art.gd")
var state
var editing = false
var selected = ""
var candidate: Dictionary = {}
var player = Vector2(5, 6)
var path: Array[Vector2i] = []
var elapsed = 0.0
var glow: PointLight2D
var enabled = true
var nearby = ""
var facing = "down"
var moving = false
var is_classroom = false

func _ready() -> void:
	clip_contents = true
	mouse_default_cursor_shape = Control.CURSOR_ARROW
	focus_mode = Control.FOCUS_ALL
	light_mask = 2
	var gradient = Gradient.new()
	gradient.colors = PackedColorArray([Color(1, 0.79, 0.47, 0.8), Color(1, 0.79, 0.47, 0)])
	var texture = GradientTexture2D.new()
	texture.gradient = gradient
	texture.width = 256
	texture.height = 256
	texture.fill = GradientTexture2D.FILL_RADIAL
	texture.fill_from = Vector2(0.5, 0.5)
	texture.fill_to = Vector2(1, 0.5)
	glow = PointLight2D.new()
	glow.texture = texture
	glow.range_item_cull_mask = 2
	glow.energy = 0.48
	add_child(glow)
	if state != null and occupied(player + Vector2(0.5, 0.5)):
		for y in range(7, -1, -1):
			for x in range(10):
				if not occupied(Vector2(x + 0.5, y + 0.5)):
					player = Vector2(x, y)
					return

func zoom() -> float:
	return minf(size.x / 690.0, size.y / 535.0)

func origin() -> Vector2:
	var scale = zoom()
	return Vector2(size.x * 0.5 - 34 * scale, (size.y - 455 * scale) * 0.5 + 142 * scale)

func iso(cell: Vector2) -> Vector2:
	return Vector2((cell.x - cell.y) * 34, (cell.x + cell.y) * 17)

func cell_at(point: Vector2) -> Vector2i:
	var p = (point - origin()) / zoom()
	return Vector2i(floori((p.x / 34 + p.y / 17) / 2), floori((p.y / 17 - p.x / 34) / 2))

func select_item(id: String) -> void:
	if not state.data["items"].has(id):
		return
	editing = true
	selected = id
	candidate = state.data["items"][id].duplicate(true)
	message.emit("Mueve el cursor y haz clic para colocar, R para girar, Esc para cancelar")

func cancel_move() -> void:
	selected = ""
	candidate.clear()
	message.emit("Movimiento cancelado")

func rotate_selected() -> void:
	if not selected.is_empty():
		candidate["rotated"] = not candidate["rotated"]

func place_selected() -> bool:
	if selected.is_empty() or not Layout.can_place(state.data["items"], selected, candidate):
		return false
	if Layout.footprint(selected, candidate).has_point(Vector2i(0, 7)):
		return false
	if selected != "rug" and Layout.footprint(selected, candidate).has_point(Vector2i((player + Vector2(0.5, 0.5)).floor())):
		return false
	var trial = state.data["items"].duplicate(true)
	trial[selected] = candidate.duplicate(true)
	if not Layout.accessible(trial):
		return false
	var previous = state.data["items"][selected].duplicate(true)
	state.data["items"][selected] = candidate.duplicate(true)
	if not state.save():
		state.data["items"][selected] = previous
		message.emit(state.notice)
		return false
	selected = ""
	candidate.clear()
	path.clear()
	changed.emit()
	message.emit("Mueble colocado y guardado")
	return true

func walk_to(cell: Vector2i) -> void:
	var grid = AStarGrid2D.new()
	grid.region = Rect2i(Vector2i.ZERO, Layout.SIZE)
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	grid.update()
	for id in state.data["items"]:
		if id != "rug":
			grid.fill_solid_region(Layout.footprint(id, state.data["items"][id]), true)
	if not grid.region.has_point(cell) or grid.is_point_solid(cell):
		return
	var start = Vector2i(player.floor())
	path = grid.get_id_path(start, cell)
	if not path.is_empty():
		path.remove_at(0)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and not selected.is_empty():
		var cell = cell_at(event.position)
		candidate["cell"] = [cell.x, cell.y]
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_RIGHT:
			cancel_move()
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if not selected.is_empty():
				if not place_selected():
					message.emit("Busca un lugar libre dentro de la habitación, deja espacio para tu personaje")
			elif editing:
				var cell = cell_at(event.position)
				for id in state.data["items"]:
					if id != "rug" and Layout.footprint(id, state.data["items"][id]).has_point(cell):
						select_item(id)
						return
			else:
				grab_focus()

func _process(delta: float) -> void:
	if state == null:
		return
	elapsed += delta
	moving = false
	if enabled and not editing and is_visible_in_tree():
		var direction = Vector2(float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
			float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
		if not direction.is_zero_approx():
			path.clear()
			move_keyboard(direction, delta)
	if not path.is_empty() and not editing and enabled and is_visible_in_tree():
		player = player.move_toward(Vector2(path[0]), delta * 3.5)
		moving = true
		if player.is_equal_approx(Vector2(path[0])):
			path.remove_at(0)
	if state.data["items"].has("lamp"):
		var lamp = Layout.footprint("lamp", state.data["items"]["lamp"])
		glow.position = origin() + (iso(Vector2(lamp.position) + Vector2(0.5, 0.5)) + Vector2(0, -74)) * zoom()
	glow.texture_scale = 2.1 * zoom()
	glow.enabled = state.data["night"] and state.data["items"].has("lamp")
	update_nearby()
	queue_redraw()

func occupied(point: Vector2) -> bool:
	if point.x < 0.18 or point.y < 0.18 or point.x > 9.82 or point.y > 7.82:
		return true
	for id in state.data["items"]:
		if id != "rug" and Rect2(Layout.footprint(id, state.data["items"][id])).grow(0.12).has_point(point):
			return true
	return false

func move_keyboard(direction: Vector2, delta: float) -> void:
	# La transformación inversa conserva WASD en direcciones de pantalla
	var screen_direction = direction.normalized()
	var step = Vector2(screen_direction.x + screen_direction.y, screen_direction.y - screen_direction.x) * delta * 2.5
	var target = player + Vector2(0.5, 0.5)
	if not occupied(target + Vector2(step.x, 0)):
		player.x += step.x
		moving = true
	if not occupied(player + Vector2(0.5, 0.5) + Vector2(0, step.y)):
		player.y += step.y
		moving = true
	facing = "right" if absf(direction.x) > absf(direction.y) and direction.x > 0 else "left" if absf(direction.x) > absf(direction.y) else "down" if direction.y > 0 else "up"

func update_nearby() -> void:
	var closest = ""
	var distance = 1.5
	var point = player + Vector2(0.5, 0.5)
	for id in ["bed", "desk", "lamp"]:
		if not state.data["items"].has(id):
			continue
		var area = Rect2(Layout.footprint(id, state.data["items"][id]))
		var nearest = Vector2(clampf(point.x, area.position.x, area.end.x), clampf(point.y, area.position.y, area.end.y))
		var length = point.distance_to(nearest)
		if length < distance:
			distance = length
			closest = id
	if point.distance_to(Vector2(0.8, 7.2)) < 1.3:
		closest = "door"
	if closest != nearby:
		nearby = closest
		var labels = {"bed": "Descansar", "desk": "Usar el computador", "lamp": "Cambiar la luz", "door": "Ir a la universidad", "": ""}
		nearby_changed.emit(nearby, labels[nearby])

func interact() -> void:
	if enabled and not editing and not nearby.is_empty():
		interacted.emit(nearby)

func quad(cell: Vector2, dimensions: Vector2, height: float = 0) -> PackedVector2Array:
	var lift = Vector2(0, -height)
	return PackedVector2Array([iso(cell) + lift, iso(cell + Vector2(dimensions.x, 0)) + lift,
		iso(cell + dimensions) + lift, iso(cell + Vector2(0, dimensions.y)) + lift])

func box(cell: Vector2, dimensions: Vector2, height: float, color: Color, base_height: float = 0) -> void:
	var top = quad(cell, dimensions, height)
	var bottom = quad(cell, dimensions, base_height)
	draw_colored_polygon(PackedVector2Array([top[1], top[2], bottom[2], bottom[1]]), color.darkened(0.24))
	draw_colored_polygon(PackedVector2Array([top[2], top[3], bottom[3], bottom[2]]), color.darkened(0.37))
	draw_colored_polygon(top, color)
	draw_polyline(PackedVector2Array([top[0], top[1], top[2], top[3], top[0]]), color.lightened(0.12), 1, true)

func wall(a: Vector2, b: Vector2, low: float, high: float, color: Color) -> void:
	draw_colored_polygon(PackedVector2Array([iso(a) + Vector2(0, -low), iso(b) + Vector2(0, -low),
		iso(b) + Vector2(0, -high), iso(a) + Vector2(0, -high)]), color)

func draw_furniture(id: String, item: Dictionary, ghost: bool = false) -> void:
	var area = Layout.footprint(id, item)
	var cell = Vector2(area.position)
	var dimensions = Vector2(area.size)
	if ghost:
		var valid = Layout.can_place(state.data["items"], id, item)
		if area.has_point(Vector2i(0, 7)):
			valid = false
		if id != "rug" and area.has_point(Vector2i(player.floor())):
			valid = false
		if valid:
			var trial = state.data["items"].duplicate(true)
			trial[id] = item
			valid = Layout.accessible(trial)
		if valid:
			draw_furniture(id, item)
		draw_colored_polygon(quad(cell, dimensions, 1), Color(0.3, 0.85, 0.68, 0.55) if valid else Color(0.9, 0.35, 0.3, 0.6))
		return
	if id == "rug":
		draw_colored_polygon(quad(cell, dimensions, 1), Color("ac6155"))
		draw_polyline(quad(cell + Vector2(0.12, 0.12), dimensions - Vector2(0.24, 0.24), 2), Color("e8b790"), 2, true)
		for i in range(1, 5):
			var p = iso(cell + dimensions * i / 5.0)
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -5), p + Vector2(9, 0), p + Vector2(0, 5), p + Vector2(-9, 0)]), Color("ddaa81"))
	elif id == "bed":
		if int(state.data["furniture_level"].get("bed", 1)) == 0:
			box(cell + Vector2(0.08, 0.08), dimensions - Vector2(0.16, 0.16), 9, Color("e0d1b3"))
			box(cell + Vector2(0.12, 0.7), dimensions - Vector2(0.24, 0.82), 12, Color("8eaaa0"), 9)
			box(cell + Vector2(0.2, 0.12), Vector2(dimensions.x - 0.4, 0.45), 15, Color("fff0cf"), 9)
			return
		box(cell, dimensions, 16, Color("80583f"))
		box(cell + Vector2(0.08, 0.08), dimensions - Vector2(0.16, 0.16), 27, Color("f0dfbf"), 16)
		box(cell + Vector2(0.12, 0.75), dimensions - Vector2(0.24, 0.87), 32, Color("7eaca2"), 27)
		box(cell + Vector2(0.18, 0.14), Vector2(dimensions.x - 0.36, 0.48), 35, Color("fff1d4"), 27)
		for stripe in range(3):
			draw_line(iso(cell + Vector2(0.2, 1.0 + stripe * 0.3)) + Vector2(0, -33), iso(cell + Vector2(dimensions.x - 0.2, 1.0 + stripe * 0.3)) + Vector2(0, -33), Color("b4d0b1"), 2, true)
	elif id == "desk":
		for corner in [Vector2.ZERO, Vector2(dimensions.x - 0.2, 0), Vector2(0, dimensions.y - 0.2), dimensions - Vector2(0.2, 0.2)]:
			box(cell + corner, Vector2(0.16, 0.16), 48, Color("6d5144"))
		box(cell, dimensions, 51, Color("c89c68"), 46)
		var pc = iso(cell + dimensions * 0.5) + Vector2(0, -56)
		draw_colored_polygon(PackedVector2Array([pc + Vector2(-19, -3), pc + Vector2(8, -3), pc + Vector2(18, 3), pc + Vector2(-10, 3)]), Color("a3aba2"))
		draw_rect(Rect2(pc + Vector2(-17, -27), Vector2(29, 25)), Color("3b4b4b"))
		draw_rect(Rect2(pc + Vector2(-14, -24), Vector2(23, 18)), Color("183c42"))
		for line in range(3):
			draw_line(pc + Vector2(-11, -20 + line * 4), pc + Vector2(5 - line * 3, -20 + line * 4), Color("78caba"), 1)
		if not is_classroom and int(state.data["furniture_level"].get("desk", 0)) >= 1:
			draw_rect(Rect2(pc + Vector2(-25, -41), Vector2(48, 29)), Color("354c48"))
			draw_rect(Rect2(pc + Vector2(-22, -38), Vector2(42, 23)), Color("193f42"))
			for line in range(4): draw_line(pc + Vector2(-18, -33 + line * 4), pc + Vector2(8 - line * 3, -33 + line * 4), Color("9ed4be"), 1)
			draw_line(pc + Vector2(0, -12), pc + Vector2(0, -5), Color("435953"), 4)
			draw_rect(Rect2(pc + Vector2(27, -25), Vector2(14, 25)), Color("45554d"))
			draw_arc(pc + Vector2(34, -16), 4, 0, TAU, 16, Color("d5b57a"), 1, true)
			draw_rect(Rect2(pc + Vector2(-17, -2), Vector2(30, 5)), Color("c4c9b0"))
		var mug = iso(cell + Vector2(0.4, 0.5)) + Vector2(0, -56)
		draw_circle(mug, 4, Color("ebe0bd"))
		draw_arc(mug + Vector2(4, 0), 3, -PI * 0.5, PI * 0.5, 8, Color("ebe0bd"), 2)
	elif id == "chair":
		box(cell + Vector2(0.15, 0.15), dimensions - Vector2(0.3, 0.3), 19, Color("7a5846"))
		box(cell + Vector2(0.05, 0.05), dimensions - Vector2(0.1, 0.1), 26, Color("b27956"), 19)
		wall(cell, cell + Vector2(dimensions.x, 0), 23, 59, Color("9c6c4d"))
		wall(cell + Vector2(0.13, 0), cell + Vector2(dimensions.x - 0.13, 0), 33, 54, Color("d1a575"))
	elif id == "shelf":
		box(cell, dimensions, 93, Color("80634d"))
		for row in range(3):
			for book in range(7):
				var p = iso(cell + Vector2(dimensions.x * (book + 0.6) / 8, dimensions.y))
				var color = [Color("c48762"), Color("839987"), Color("e0bb78"), Color("788898")][book % 4]
				draw_line(p + Vector2(0, -12 - row * 27), p + Vector2(0, -31 - row * 27), color, 5)
			wall(cell + Vector2(0, dimensions.y), cell + dimensions, 9 + row * 27, 12 + row * 27, Color("af8962"))
	elif id == "lamp":
		var p = iso(cell + Vector2(0.5, 0.5))
		draw_circle(p, 9, Color("655248"))
		draw_line(p, p + Vector2(0, -93), Color("806c58"), 4, true)
		draw_colored_polygon(PackedVector2Array([p + Vector2(-11, -112), p + Vector2(11, -112), p + Vector2(18, -87), p + Vector2(-18, -87)]), Color("efd49b"))
		draw_line(p + Vector2(-17, -87), p + Vector2(17, -87), Color("fff0b6"), 3)
	elif id == "plant":
		var p = iso(cell + Vector2(0.5, 0.5))
		box(cell + Vector2(0.2, 0.2), Vector2(0.6, 0.6), 18, Color("bf7857"))
		for i in range(6):
			var end = p + Vector2(sin(i * 2.4) * 17, -34 - (i % 3) * 9)
			draw_line(p + Vector2(0, -16), end, Color("4e6b43"), 2, true)
			draw_colored_polygon(PackedVector2Array([end, end + Vector2(-8, -9), end + Vector2(1, -16), end + Vector2(6, -6)]), Color("7e9f65") if i % 2 else Color("a0b878"))

	elif id == "sofa":
		box(cell, dimensions, 19, Color("547166"))
		box(cell + Vector2(0.08, 0.08), dimensions - Vector2(0.16, 0.16), 28, Color("a9bb9b"), 19)
		wall(cell, cell + Vector2(dimensions.x, 0), 25, 60, Color("829a7f"))
		for side in [0.0, dimensions.x - 0.25]:
			box(cell + Vector2(side, 0), Vector2(0.25, dimensions.y), 40, Color("7b987f"), 19)
		var middle = iso(cell + dimensions * 0.5)
		draw_line(middle + Vector2(0, -29), middle + Vector2(12, -22), Color("5f806e"), 2)
	elif id in ["coffee_table", "chest"]:
		var high = 36 if id == "chest" else 25
		box(cell + Vector2(0.12, 0.12), dimensions - Vector2(0.24, 0.24), high, Color("8d674c"))
		box(cell, dimensions, high + 4, Color("c49d71"), high)
		var center = iso(cell + dimensions * 0.5) + Vector2(0, -high - 6)
		if id == "chest":
			draw_rect(Rect2(center + Vector2(-3, 4), Vector2(6, 8)), Color("dfbd7f"))
		else:
			draw_circle(center + Vector2(-12, 0), 6, Color("efe1bd"))
			draw_rect(Rect2(center + Vector2(5, -5), Vector2(16, 9)), Color("6b8e7a"))
	elif id == "aquarium":
		box(cell, dimensions, 32, Color("86684f"))
		box(cell + Vector2(0.08, 0.08), dimensions - Vector2(0.16, 0.16), 65, Color("78b5b2"), 32)
		box(cell, dimensions, 68, Color("d6d8b9"), 65)
		var center = iso(cell + dimensions * 0.5) + Vector2(0, -48)
		for i in range(3):
			var fish = center + Vector2(sin(elapsed * 0.6 + i * 2) * 15, i * 6 - 7)
			draw_colored_polygon(PackedVector2Array([fish + Vector2(-5, 0), fish + Vector2(3, -3), fish + Vector2(7, 0), fish + Vector2(3, 3)]), Color("e6ad70"))
		for i in range(4):
			draw_line(center + Vector2(-20 + i * 7, 14), center + Vector2(-22 + i * 7, 2 - i * 2), Color("407e66"), 2, true)
	elif id == "bonsai":
		var center = iso(cell + Vector2(0.5, 0.5))
		box(cell + Vector2(0.12, 0.12), Vector2(0.76, 0.76), 15, Color("bc8560"))
		draw_polyline(PackedVector2Array([center + Vector2(0, -14), center + Vector2(-6, -30), center + Vector2(4, -46)]), Color("7f6748"), 5, true)
		for offset in [Vector2(4, -47), Vector2(-9, -35), Vector2(14, -35)]:
			draw_circle(center + offset, 11, Color("6c9470"))
			draw_arc(center + offset, 8, PI, TAU, 12, Color("a9ba80"), 2, true)

func _draw() -> void:
	if state == null:
		return
	draw_style_box(panel_style(), Rect2(Vector2.ZERO, size))
	draw_set_transform(origin(), 0, Vector2.ONE * zoom())
	var night: bool = state.data["night"]
	var left = Color("a3b4a0") if not night else Color("677c78")
	var right = Color("c6cbb0") if not night else Color("81908b")
	wall(Vector2.ZERO, Vector2(0, 8), 0, 132, left)
	wall(Vector2.ZERO, Vector2(10, 0), 0, 132, right)
	wall(Vector2(0, 0), Vector2(0, 8), 128, 136, left.lightened(0.14))
	wall(Vector2(0, 0), Vector2(10, 0), 128, 136, right.lightened(0.14))
	wall(Vector2(5.4, 0), Vector2(8.8, 0), 49, 113, Color("725c4b"))
	wall(Vector2(5.55, 0), Vector2(8.65, 0), 53, 109, Color("b8d4ca") if not night else Color("4b697c"))
	wall(Vector2(6.98, 0), Vector2(7.13, 0), 52, 111, Color("e6d8b8"))
	wall(Vector2(5.5, 0), Vector2(8.7, 0), 78, 82, Color("e6d8b8"))
	wall(Vector2(0, 2), Vector2(0, 4.5), 60, 109, Color("856247"))
	draw_door(6.25)
	for i in range(3):
		wall(Vector2(0, 2.2 + i * 0.68), Vector2(0, 2.75 + i * 0.68), 72 - i * 4, 99 - i * 4, Color("eac77b") if i != 1 else Color("eee4c4"))
	for y in range(8):
		for x in range(10):
			var cell = Vector2(x, y)
			var color = Color("bb956d") if (x + y) % 2 else Color("c6a078")
			if night:
				color = color.darkened(0.20)
			draw_colored_polygon(quad(cell, Vector2.ONE), color)
			draw_polyline(quad(cell, Vector2.ONE), color.darkened(0.15), 0.7, true)
			draw_line(iso(cell + Vector2(0.08, 0.4)), iso(cell + Vector2(0.9, 0.4)), color.darkened(0.05), 1)
	wall(Vector2(0, 8), Vector2(10, 8), -10, 0, Color("735c49"))
	wall(Vector2(10, 0), Vector2(10, 8), -10, 0, Color("947252"))
	if editing:
		for y in range(9):
			draw_line(iso(Vector2(0, y)), iso(Vector2(10, y)), Color(1, 0.95, 0.8, 0.22), 1)
		for x in range(11):
			draw_line(iso(Vector2(x, 0)), iso(Vector2(x, 8)), Color(1, 0.95, 0.8, 0.22), 1)
	var items: Dictionary = state.data["items"]
	if items.has("rug"): draw_furniture("rug", items["rug"])
	var order: Array = items.keys().filter(func(id): return id != "rug")
	order.append("player")
	order.sort_custom(func(a, b): return depth(a) < depth(b))
	for id in order:
		if id == "player":
			Character.paint(self, origin() + iso(player + Vector2(0.5, 0.5)) * zoom(), state.data, zoom(), sin(elapsed * 13) * 2 if moving else 0, facing)
			draw_set_transform(origin(), 0, Vector2.ONE * zoom())
		else:
			draw_furniture(id, items[id])
	if not selected.is_empty():
		draw_furniture(selected, candidate, true)
	draw_set_transform(Vector2.ZERO)

func depth(id: String) -> float:
	if id == "player":
		return player.x + player.y + 1.0
	var area = Layout.footprint(id, state.data["items"][id])
	return float(area.end.x + area.end.y) - 0.1

func draw_door(y: float) -> void:
	wall(Vector2(0, y), Vector2(0, y + 1.45), 0, 103, Color("76553e"))
	wall(Vector2(0, y + 0.09), Vector2(0, y + 1.36), 1, 98, Color("b48c61"))
	wall(Vector2(0, y + 0.2), Vector2(0, y + 1.25), 45, 88, Color("c49d71"))
	var handle = iso(Vector2(0, y + 1.14)) + Vector2(3, -43)
	draw_circle(handle, 3, Color("e8cd91"))

func panel_style() -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = Color("263e3e") if state.data["night"] else Color("405e57")
	style.set_corner_radius_all(22)
	return style
