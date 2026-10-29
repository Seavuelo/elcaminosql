extends Control
const UI = preload("res://scripts/ui_kit.gd")
var graph: GraphEdit
var relations: Array = []
var nodes: Dictionary = {}
var segments: Array = []
signal selected(id)

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func _process(_delta: float) -> void:
	queue_redraw()

func endpoint(node: GraphNode, output: bool) -> Vector2:
	var port = node.get_output_port_position(0) if output else node.get_input_port_position(0)
	return node.position + port * node.scale

func end_mark(point: Vector2, direction: Vector2, many: bool, optional: bool, identifying: bool) -> void:
	var normal = direction.orthogonal()
	if many:
		for offset in [-7, 0, 7]:
			draw_line(point, point + direction * 14 + normal * offset, UI.GREEN, 2, true)
	else:
		draw_line(point + direction * 10 - normal * 7, point + direction * 10 + normal * 7, UI.GREEN, 2, true)
	if optional:
		draw_arc(point + direction * 23, 5, 0, TAU, 20, UI.GREEN, 1.8, true)
	else:
		draw_line(point + direction * 22 - normal * 7, point + direction * 22 + normal * 7, UI.GREEN, 2, true)
	if identifying:
		draw_line(point + direction * 32 - normal * 6, point + direction * 32 + normal * 6, UI.COPPER, 2.5, true)

func _draw() -> void:
	segments.clear()
	for relation in relations:
		if not nodes.has(relation["source"]) or not nodes.has(relation["target"]):
			continue
		var start = endpoint(nodes[relation["source"]], true)
		var end = endpoint(nodes[relation["target"]], false)
		var points = PackedVector2Array()
		if start.distance_to(end) < 20 or relation["source"] == relation["target"]:
			points = PackedVector2Array([start, start + Vector2(55, 0), start + Vector2(55, -100), end + Vector2(-45, -100), end + Vector2(-45, 0), end])
		else:
			var mid = (start.x + end.x) / 2
			points = PackedVector2Array([start, Vector2(mid, start.y), Vector2(mid, end.y), end])
		for index in range(points.size() - 1):
			if relation.get("source_optional", false):
				draw_dashed_line(points[index], points[index + 1], UI.GREEN, 2, 7, true, true)
			else:
				draw_line(points[index], points[index + 1], UI.GREEN, 2, true)
			segments.append({"id": relation["id"], "a": points[index], "b": points[index + 1]})
		end_mark(start, Vector2.RIGHT, relation["kind"] == "N:M", relation.get("source_optional", false), false)
		end_mark(end, Vector2.LEFT, relation["kind"] != "1:1", relation.get("target_optional", true), relation.get("identifying", false))
		var center = (points[1] + points[-2]) / 2
		var label = relation["name"] + "  " + relation["kind"]
		var width = UI.BODY.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x
		var anchor = center
		for offset in [Vector2.ZERO, Vector2(0, 40), Vector2(0, -40), Vector2(0, 80), Vector2(0, -80), Vector2(0, 120), Vector2(0, -120), Vector2(0, 180), Vector2(0, -180)]:
			var test_rect = Rect2(anchor + offset - Vector2(width / 2 + 5, 12), Vector2(width + 10, 22))
			var overlaps = false
			for node in nodes.values():
				if test_rect.intersects(Rect2(node.position, node.size * node.scale).grow(7)):
					overlaps = true
			if not overlaps:
				center = anchor + offset
				break
		if center != anchor:
			draw_dashed_line(anchor, center, Color(UI.GREEN, 0.45), 1, 4, true, true)
		draw_style_box(UI.box(UI.WHITE, 6, 4), Rect2(center - Vector2(width / 2 + 5, 12), Vector2(width + 10, 22)))
		draw_string(UI.BODY, center + Vector2(-width / 2, 4), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, UI.GREEN)

func pick(point: Vector2) -> String:
	for segment in segments:
		if Geometry2D.get_closest_point_to_segment(point, segment["a"], segment["b"]).distance_to(point) < 10:
			return segment["id"]
	return ""
