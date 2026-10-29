extends PanelContainer
const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
var store
func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_theme_stylebox_override("panel", UI.box(Color("f5efd9"), 10, 38))
	var scroll = UI.scroll(self)
	UI.heading(scroll, "Gracias por estar aquí", "Una nota de Sebastián")
	UI.text(scroll, Course.all()["creator_note"], 21, UI.INK, true)
	resized.connect(queue_redraw)
func _draw() -> void:
	draw_line(Vector2(24, 12), Vector2(24, size.y - 12), Color("d7a391"), 1)
	for y in range(36, int(size.y) - 12, 30):
		draw_circle(Vector2(10, y), 3, Color("92866b"))
func _exit_tree() -> void:
	if store != null:
		store.data["settings"]["creator_note_seen"] = true
		store.save()
