extends Control
const UI = preload("res://scripts/ui_kit.gd")
const Terrain = preload("res://scripts/league_terrain.gd")
var league
var terrain
var textures = {}
var feedback = ""
var feedback_time = 0.0
var feedback_good = false
signal attempted(result)
func _ready() -> void:
	custom_minimum_size = Vector2(400, 250)
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	focus_mode = Control.FOCUS_ALL
	terrain = Terrain.new()
	terrain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(terrain)
	for god in league.content["gods"]:
		textures[god] = load("res://assets/league/" + god + ".png")
func _process(delta: float) -> void:
	feedback_time = maxf(0, feedback_time - delta)
	queue_redraw()
func notify(result: Dictionary) -> void:
	feedback = result.get("text", "")
	feedback_good = result.get("success", false)
	feedback_time = 2.4
func battle() -> Dictionary:
	return league.state()["battle"] if league.state()["battle"] != null else {}
func champion(position: Vector2, god: String, allied: bool, health: float, main: bool = false) -> void:
	var scale = terrain.bounds().size.x / 800
	var radius = (16 if main else 10) * scale
	var color = Color("8dd9b5") if allied else Color("e89f9b")
	draw_circle(position + Vector2(0, 4) * scale, radius, Color(0.03, 0.09, 0.07, 0.5))
	draw_arc(position, radius + 2 * scale, 0, TAU, 28, color, (2.3 if main else 1.2) * scale, true)
	if textures.get(god) != null:
		draw_texture_rect(textures[god], Rect2(position - Vector2(radius, radius * 1.6), Vector2(radius * 2, radius * 2.18)), false)
	var bar = Rect2(position + Vector2(-radius, -radius * 1.95), Vector2(radius * 2, 3.5 * scale))
	draw_rect(bar.grow(scale), Color("152c28"))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(health, 0.05, 1), bar.size.y)), color)
func _draw() -> void:
	if terrain == null or league == null: return
	var rect = terrain.bounds()
	var scale = rect.size.x / 800
	var match_state = battle()
	var result: Dictionary = match_state.get("result", league.state().get("last_match", {})) if not match_state.is_empty() else league.state().get("last_match", {}) if league.state().get("last_match") != null else {}
	var elapsed = float(match_state.get("elapsed", 0))
	var gods = league.content["gods"].keys()
	for i in range(12):
		var t = fmod(elapsed * 0.035 + i * 0.13, 1.0)
		var lane = i % 3
		var p = terrain.route(lane, t if i < 6 else 1 - t)
		var color = Color("91bdb0") if i < 6 else Color("c28d8b")
		draw_circle(p, 3.5 * scale, color)
		draw_line(p, p + Vector2(3, -4) * scale, color.lightened(0.25), scale)
	for i in range(8):
		var allied = i < 4
		var lane = i % 3
		var travel = 0.28 + sin(elapsed * 0.13 + i * 2.1) * 0.14
		var p = terrain.route(lane, travel if allied else 1 - travel) + Vector2(sin(elapsed + i) * 4, cos(elapsed * 0.8 + i) * 3) * scale
		champion(p, gods[(i + 1) % gods.size()], allied, 0.7 + sin(elapsed * 0.2 + i) * 0.25)
	var tower_count = 0
	for event in result.get("events", []):
		if event["time"] <= elapsed and event["type"] == "objective" and event.get("objective", "") == "torre": tower_count += 1
	for i in range(6):
		if i >= 3 and i - 3 < tower_count: continue
		var p = terrain.route(i % 3, 0.30 if i < 3 else 0.70)
		var color = Color("84bdac") if i < 3 else Color("c58e89")
		draw_rect(Rect2(p + Vector2(-8, -14) * scale, Vector2(16, 22) * scale), Color("807e6c"))
		draw_rect(Rect2(p + Vector2(-10, -16) * scale, Vector2(20, 6) * scale), color)
		draw_circle(p + Vector2(0, -20) * scale, 4 * scale, color.lightened(0.35))
	var previous = {"time": 0.0, "pos": [0.08, 0.88], "type": "info"}
	var next = {}
	for event in result.get("events", []):
		if event["time"] <= elapsed: previous = event
		else: next = event; break
	if next.is_empty(): next = previous
	var from = Vector2(previous["pos"][0], previous["pos"][1])
	var target = Vector2(next["pos"][0], next["pos"][1])
	var progress = clampf((elapsed - float(previous["time"])) / maxf(0.2, float(next["time"]) - float(previous["time"])), 0, 1)
	var hero = terrain.point(from.lerp(target, smoothstep(0, 1, progress)))
	var dead = previous["type"] == "death" and elapsed - float(previous["time"]) < 0.7
	if not dead:
		champion(hero, result.get("god", league.state()["god"]), true, 0.35 if previous["type"] == "death" else 0.85, true)
	var age = elapsed - float(previous["time"])
	if age >= 0 and age < 0.85 and previous["type"] in ["kill", "assist", "death", "objective"]:
		var p = terrain.point(from)
		var color = Color("eed69e") if previous["type"] != "death" else Color("e9a7a2")
		draw_arc(p, (15 + age * 35) * scale, -PI * 0.7, PI * 0.7, 32, Color(color, 1 - age), 2 * scale, true)
		for i in range(6):
			var angle = i * TAU / 6 + age * 2
			var offset = Vector2(cos(angle), sin(angle)) * (12 + age * 36) * scale
			draw_line(p + offset, p + offset * 1.2, Color(color, 1 - age), 2 * scale, true)
	for i in range(8):
		var t = fmod(elapsed * 0.07 + i * 0.14, 1)
		var p = terrain.point(Vector2(0.38 + t * 0.25, t))
		draw_line(p, p + Vector2(9, 0) * scale, Color(0.75, 0.91, 0.82, 0.24), scale, true)
	var cue = league.current_cue()
	if not cue.is_empty():
		var p = terrain.point(Vector2(cue["pos"][0], cue["pos"][1]))
		var radius = float(cue["radius"]) * rect.size.x / 304
		var timing = (elapsed - float(cue["at"]) - float(cue["windup"])) / float(cue["window"])
		draw_circle(p, radius * 1.9, Color(0.03, 0.10, 0.09, 0.80))
		draw_arc(p, radius * 1.35, 0, TAU, 64, Color(0.5, 0.85, 0.68, 0.52), radius * 0.40, true)
		var ring = radius * (2.0 - timing * 1.2) if timing >= 0 else radius * (2 - timing * 0.16)
		draw_arc(p, ring, 0, TAU, 64, Color("f4db9f") if timing < 0.15 else Color("c5f5d5"), 3 * scale, true)
		draw_circle(p, 3 * scale, Color("f1dfb8"))
		var caption = "PREPÁRATE" if timing < 0 else "AHORA"
		draw_string(UI.weight(UI.BODY, 700), p + Vector2(-40 * scale, radius * 2.2 + 18 * scale), caption, HORIZONTAL_ALIGNMENT_CENTER, 80 * scale, 12 * scale, Color("fff3d1"))
	if feedback_time > 0:
		var box = Rect2(rect.position + Vector2(20, rect.size.y - 48), Vector2(rect.size.x - 40, 36))
		draw_style_box(UI.box(Color("e9ddbc") if feedback_good else Color("e6c8b6"), 9, 8), box)
		var point = clampi(16, 12, int(rect.size.x / 42))
		draw_string(UI.BODY, box.position + Vector2(10, 24), feedback, HORIZONTAL_ALIGNMENT_CENTER, box.size.x - 20, point, UI.INK)
func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var rect = terrain.bounds()
		if rect.has_point(event.position) and not league.current_cue().is_empty():
			var result = league.attempt_timing((event.position - rect.position) / rect.size)
			notify(result)
			attempted.emit(result)
			accept_event()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_SPACE and not league.current_cue().is_empty():
		var result = league.attempt_timing()
		notify(result)
		attempted.emit(result)
		accept_event()
