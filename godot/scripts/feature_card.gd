extends Button
const UI = preload("res://scripts/ui_kit.gd")
var title = ""
var description = ""
var kind = "sql"
var primary = false
var action: Callable
var title_font = UI.weight(UI.BODY, 650)
func _ready():
	custom_minimum_size = Vector2(220, 132)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	accessibility_name = title
	tooltip_text = description
	pressed.connect(func():
		for audio in get_tree().get_nodes_in_group("game_audio"): audio.sfx("key")
		if action.is_valid(): action.call()
	)
	for item in [["normal", UI.GREEN if primary else Color("e7e9da")], ["hover", UI.GREEN.lightened(0.1) if primary else Color("d9e3ce")], ["pressed", UI.DEEP if primary else Color("d2dcbf")]]:
		add_theme_stylebox_override(item[0], UI.box(item[1], 16, 16))
func _draw():
	var accent = UI.GOLD if primary else UI.COPPER
	var foreground = UI.WHITE if primary else UI.INK
	var muted = Color("d8e3cd") if primary else UI.MUTED
	var center = Vector2(40, 45)
	draw_circle(center, 25, Color("376e59") if primary else Color("dce3cc"))
	if kind == "nexo":
		for delta in [Vector2(-13, 9), Vector2(13, 9), Vector2(0,-13)]:
			draw_line(center,center+delta,accent,2,true)
			draw_circle(center+delta,4,accent)
		draw_circle(center,5,accent)
	elif kind in ["sql", "grades"]:
		for i in range(3):
			var height = 10 + i*5
			draw_rect(Rect2(center + Vector2(-14+i*10,12-height),Vector2(6,height)),accent)
	elif kind in ["notebook", "library"]:
		for i in range(3):
			draw_rect(Rect2(center+Vector2(-14+i*10,-15),Vector2(8,29)),accent.lightened(i*0.1))
			draw_line(center+Vector2(-12+i*10,-9),center+Vector2(-8+i*10,-9),UI.PAPER,1)
	elif kind == "model":
		for delta in [Vector2(-12,-10),Vector2(13,-8),Vector2(0,13)]:
			draw_line(center,center+delta,accent,2,true)
			draw_rect(Rect2(center+delta-Vector2(6,4),Vector2(12,8)),accent)
	elif kind == "home":
		draw_polyline(PackedVector2Array([center+Vector2(-17,0),center+Vector2(0,-15),center+Vector2(17,0)]),accent,3,true)
		draw_rect(Rect2(center+Vector2(-12,-2),Vector2(24,17)),accent,false,2)
		draw_rect(Rect2(center+Vector2(-3,5),Vector2(6,10)),accent)
	elif kind == "career":
		draw_colored_polygon(PackedVector2Array([center+Vector2(-19,-4),center+Vector2(0,-14),center+Vector2(19,-4),center+Vector2(0,6)]),accent)
		draw_line(center+Vector2(-12,3),center+Vector2(-12,12),accent,3)
		draw_line(center+Vector2(12,3),center+Vector2(12,12),accent,3)
	else:
		draw_arc(center,15,0,TAU,32,accent,2,true)
		draw_arc(center,8,0,TAU,24,accent,2,true)
		draw_circle(center,3,accent)
	var point = 18
	while point>14 and title_font.get_string_size(title,HORIZONTAL_ALIGNMENT_LEFT,-1,point).x>size.x-90: point-=1
	draw_string(title_font,Vector2(76,35),title,HORIZONTAL_ALIGNMENT_LEFT,-1,point,foreground)
	var y=59.0
	for line in UI.wrapped_lines(description,size.x-92,UI.BODY,14):
		draw_string(UI.BODY,Vector2(76,y),line,HORIZONTAL_ALIGNMENT_LEFT,-1,14,muted)
		y+=19
