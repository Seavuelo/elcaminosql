extends "res://scripts/room_view.gd"

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
var campaign
var seats: Array = []
var actors: Array = []
var day_closed = false
var room_width = 14
var room_depth = 12
var teacher_desk = Vector2(6, 0)

func _ready() -> void:
	is_classroom = true
	super._ready()
	if campaign.year() == 0:
		room_width = 13
		room_depth = 10
		teacher_desk = Vector2(5, 0)
		seats = [Vector2(1, 3), Vector2(6, 3), Vector2(1, 6), Vector2(6, 6), Vector2(9, 8)]
	else:
		for y in [3, 6, 9]:
			for x in [1, 5, 9]:
				seats.append(Vector2(x, y))
	player = Vector2(0.35, room_depth - 1.35)
	var peers = []
	for peer in Course.all()["peers"]:
		if campaign.year() == 0 and peer["id"] in ["moshi", "carlos", "sofia", "matias"]:
			peers.append(peer)
		elif campaign.year() > 0 and campaign.year() >= peer["first_year"] and campaign.year() <= peer["last_year"]:
			peers.append(peer)
	for index in range(peers.size()):
		var peer: Dictionary = peers[index]
		var profile = {"skin": 0, "hair": 0, "shirt": 0, "skin_rgb": peer["skin"], "hair_rgb": peer["hair"],
			"shirt_rgb": peer["shirt"], "eyes_rgb": peer["eyes"], "pants_rgb": peer["pants"], "shoes_rgb": peer["shoes"],
			"hair_style": peer["hair_style"], "clothing_style": 1 if peer["id"] == "moshi" else 0, "show_backpack": false}
		actors.append({"id": peer["id"], "name": peer["name"], "profile": profile, "seat": index,
			"cell": seats[index] + Vector2(1.5, 1.5), "phase": campaign.progress()["departures"].get(campaign.day_key(), {}).get(peer["id"], "studying"), "timer": 0.0, "path": []})

func zoom() -> float:
	return minf(size.x / ((room_width + room_depth) * 34 + 100), size.y / ((room_width + room_depth) * 17 + 218))

func origin() -> Vector2:
	var scale = zoom()
	return Vector2(size.x * 0.5 - (room_width - room_depth) * 17 * scale, (size.y - ((room_width + room_depth) * 17 + 132) * scale) * 0.5 + 134 * scale)

func occupied(point: Vector2) -> bool:
	if point.x < 0.2 or point.y < 0.2 or point.x > room_width - 0.2 or point.y > room_depth - 0.2:
		return true
	if Rect2(teacher_desk + Vector2(0, 0.1), Vector2(3, 0.9)).grow(0.15).has_point(point) or point.distance_to((teacher_desk + Vector2(1.6, 1.65))) < 0.55:
		return true
	for seat in seats:
		if Rect2(seat, Vector2(3, 1)).grow(0.12).has_point(point):
			return true
		if Rect2(seat + Vector2(1.12, 1.18), Vector2(0.72, 0.72)).has_point(point):
			return true
	return false

func update_nearby() -> void:
	var point = player + Vector2(0.5, 0.5)
	var closest = ""
	var title = ""
	if point.distance_to((teacher_desk + Vector2(1.6, 1.65))) < 1.8:
		closest = "teacher"
		title = "Hablar con Marco"
	var pc = Rect2(seats.back(), Vector2(3, 1))
	var nearest = Vector2(clampf(point.x, pc.position.x, pc.end.x), clampf(point.y, pc.position.y, pc.end.y))
	if point.distance_to(nearest) < 1.35:
		closest = "pc"
		title = "Usar tu computador"
	var best = 1.35
	for actor in actors:
		if actor["phase"] == "gone":
			continue
		var length = point.distance_to(actor["cell"])
		if length < best:
			best = length
			closest = "peer:" + actor["id"]
			title = "Hablar con " + actor["name"]
	if point.distance_to(Vector2(0.8, room_depth - 0.8)) < 1.5:
		closest = "exit"
		title = "Salir de la sala"
	if closest != nearby:
		nearby = closest
		nearby_changed.emit(closest, title)

func departure(id: String) -> void:
	for actor in actors:
		if actor["id"] == id and actor["phase"] == "studying":
			var previous = state.data.duplicate(true)
			var record = campaign.progress()["departures"].get(campaign.day_key(), {})
			record[id] = "packing"
			campaign.progress()["departures"][campaign.day_key()] = record
			if state.save():
				actor["phase"] = "packing"
				actor["timer"] = 0.0
			else:
				state.data = previous
				message.emit(state.notice)

func exit_path(start: Vector2i) -> Array[Vector2i]:
	var grid = AStarGrid2D.new()
	grid.region = Rect2i(0, 0, room_width, room_depth)
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	grid.update()
	for seat in seats:
		grid.fill_solid_region(Rect2i(Vector2i(seat), Vector2i(3, 1)), true)
	grid.set_point_solid(start, false)
	return grid.get_id_path(start, Vector2i(0, room_depth - 1))

func _process(delta: float) -> void:
	if campaign == null:
		return
	elapsed += delta
	moving = false
	if enabled:
		var direction = Vector2(float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
			float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
		if not direction.is_zero_approx():
			move_keyboard(direction, delta)
		for actor in actors:
			actor["timer"] += delta
			if actor["phase"] == "packing" and actor["timer"] > 1.6:
				actor["phase"] = "leaving"
				actor["path"] = exit_path(Vector2i(actor["cell"]))
			elif actor["phase"] == "leaving":
				if actor["path"].is_empty():
					actor["phase"] = "gone"
					campaign.progress()["departures"][campaign.day_key()][actor["id"]] = "gone"
					if not state.save(): message.emit(state.notice)
				else:
					var target = Vector2(actor["path"][0]) + Vector2(0.5, 0.5)
					actor["cell"] = actor["cell"].move_toward(target, delta * 2.4)
					if actor["cell"].distance_to(target) < 0.02:
						actor["path"].remove_at(0)
	glow.enabled = false
	update_nearby()
	queue_redraw()

func _draw() -> void:
	if campaign == null:
		return
	draw_style_box(panel_style(), Rect2(Vector2.ZERO, size))
	draw_set_transform(origin(), 0, Vector2.ONE * zoom())
	wall(Vector2.ZERO, Vector2(0, room_depth), 0, 132, Color("b0b9a3"))
	wall(Vector2.ZERO, Vector2(room_width, 0), 0, 132, Color("d4d3b5"))
	wall(Vector2(2, 0), Vector2(room_width - 2.5, 0), 47, 126, Color("876446"))
	wall(Vector2(2.15, 0), Vector2(room_width - 2.65, 0), 51, 122, Color("214b40"))
	for y in range(room_depth):
		for x in range(room_width):
			var color = Color("c0a484") if (x + y) % 2 else Color("c8ae8b")
			draw_colored_polygon(quad(Vector2(x, y), Vector2.ONE), color)
			draw_polyline(quad(Vector2(x, y), Vector2.ONE), color.darkened(0.09), 0.7, true)
	wall(Vector2(0, room_depth), Vector2(room_width, room_depth), -10, 0, Color("846b52"))
	wall(Vector2(room_width, 0), Vector2(room_width, room_depth), -10, 0, Color("9e8060"))
	wall(Vector2(0, 2), Vector2(0, 5), 48, 117, Color("e8dcc0"))
	wall(Vector2(0, 2.1), Vector2(0, 4.9), 52, 113, Color("a6c6bd"))
	wall(Vector2(0, 3.4), Vector2(0, 3.55), 50, 115, Color("f0e8cf"))
	draw_door(room_depth - 1.7)
	var base = Transform2D(0, Vector2.ONE * zoom(), 0, origin())
	draw_set_transform_matrix(base * Transform2D(Vector2(1, 0.5), Vector2(0, 1), iso(Vector2(2.4, 0)) + Vector2(0, -110)))
	draw_string(UI.CODE, Vector2.ZERO, "PROFESOR MARCO", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("d4e1c4"))
	var topic: String = Course.lesson(campaign.year(), campaign.day())[0].get("chalk_title", "Bases de datos")
	var line = 0
	for text in UI.wrapped_lines(topic, (room_width - 4.8) * 34, UI.CODE, 11):
		draw_string(UI.CODE, Vector2(0, 21 + line * 15), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("c7d9bf"))
		line += 1
	draw_set_transform(origin(), 0, Vector2.ONE * zoom())
	draw_furniture("desk", {"cell": [int(teacher_desk.x), 0], "rotated": false})
	var teacher = {"skin": 0, "hair": 1, "shirt": 5, "pants_color": 1, "shoe_color": 0, "hair_style": 0, "clothing_style": 4, "glasses": true, "show_backpack": false}
	Character.paint(self, origin() + iso((teacher_desk + Vector2(1.6, 1.65))) * zoom(), teacher, zoom() * 1.07)
	draw_set_transform(origin(), 0, Vector2.ONE * zoom())
	var order: Array = []
	for index in range(seats.size()):
		var seat: Vector2 = seats[index]
		order.append({"kind": "desk", "index": index, "depth": seat.x + seat.y + 2.0})
		order.append({"kind": "chair", "index": index, "depth": seat.x + seat.y + 2.8})
	for index in range(actors.size()):
		var actor = actors[index]
		if actor["phase"] != "gone":
			order.append({"kind": "actor", "index": index, "depth": actor["cell"].x + actor["cell"].y})
	order.append({"kind": "player", "depth": player.x + player.y + 1})
	order.sort_custom(func(a, b): return a["depth"] < b["depth"])
	for item in order:
		if item["kind"] == "desk":
			var seat: Vector2 = seats[item["index"]]
			draw_furniture("desk", {"cell": [int(seat.x), int(seat.y)], "rotated": false})
			if item["index"] < actors.size() and actors[item["index"]]["phase"] in ["leaving", "gone"]:
				var pc = iso(seat + Vector2(1.5, 0.5)) + Vector2(-14, -80)
				draw_rect(Rect2(pc, Vector2(23, 18)), Color("283a36"))
		elif item["kind"] == "chair":
			var seat: Vector2 = seats[item["index"]] + Vector2(1, 1)
			draw_furniture("chair", {"cell": [int(seat.x), int(seat.y)], "rotated": false})
		elif item["kind"] == "actor":
			var actor = actors[item["index"]]
			var direction = "up" if actor["phase"] == "studying" else "right" if actor["phase"] == "packing" else "down"
			actor["profile"]["packing"] = actor["phase"] == "packing"
			var stride = sin(elapsed * 17) * 2.2 if actor["phase"] in ["packing", "leaving"] else 0.0
			Character.paint(self, origin() + iso(actor["cell"]) * zoom() + Vector2(0, -12 if actor["phase"] in ["studying", "packing"] else 0) * zoom(), actor["profile"], zoom(), stride, direction)
		else:
			Character.paint(self, origin() + iso(player + Vector2(0.5, 0.5)) * zoom(), state.data, zoom(), sin(elapsed * 13) * 2 if moving else 0, facing)
		draw_set_transform(origin(), 0, Vector2.ONE * zoom())
	draw_set_transform(Vector2.ZERO)
	if not campaign.lecture_done() or (campaign.can_finish() and not campaign.progress()["ready_to_leave"]):
		var at = origin() + (iso(teacher_desk + Vector2(1.6, 1.65)) + Vector2(0, -76)) * zoom()
		draw_circle(at, 11 * zoom(), Color(UI.GOLD, 0.78 + sin(elapsed * 3) * 0.22))
		var font = UI.weight(UI.BODY, 750)
		var point_size = 17 * zoom()
		var width = font.get_string_size("!", HORIZONTAL_ALIGNMENT_LEFT, -1, point_size).x
		draw_string(font, at + Vector2(-width / 2, point_size * 0.35), "!", HORIZONTAL_ALIGNMENT_LEFT, -1, point_size, UI.DEEP)
