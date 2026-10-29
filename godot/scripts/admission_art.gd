extends Control
const UI = preload("res://scripts/ui_kit.gd")
const Character = preload("res://scripts/character_art.gd")
var page = 0
var elapsed = 0.0
func _ready():
	custom_minimum_size = Vector2(360,330)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
func _process(delta):
	elapsed += delta
	if page == 1: queue_redraw()
func _draw():
	var scale = minf(size.x/360.0,size.y/330.0)
	draw_set_transform((size-Vector2(360,330)*scale)/2,0,Vector2.ONE*scale)
	draw_circle(Vector2(180,165),145,Color("e7dfc3"))
	if page == 0:
		draw_style_box(UI.box(Color("d7b97f"),12,0),Rect2(55,115,250,160))
		draw_colored_polygon(PackedVector2Array([Vector2(55,115),Vector2(180,35),Vector2(305,115)]),Color("ba945c"))
		draw_style_box(UI.box(Color("fff6df"),7,0),Rect2(86,69,188,175))
		for i in range(5): draw_line(Vector2(108,113+i*18),Vector2(251-i%2*27,113+i*18),Color("b6b99b"),3,true)
		draw_colored_polygon(PackedVector2Array([Vector2(55,125),Vector2(180,205),Vector2(305,125),Vector2(305,275),Vector2(55,275)]),Color("dfc18a"))
		draw_line(Vector2(55,275),Vector2(155,192),Color("bf9d63"),2,true)
		draw_line(Vector2(305,275),Vector2(205,192),Color("bf9d63"),2,true)
		draw_circle(Vector2(180,207),23,UI.COPPER)
		draw_arc(Vector2(180,207),17,0,TAU,40,UI.GOLD,2,true)
		draw_string(UI.weight(UI.BODY,700),Vector2(166,213),"SQL",HORIZONTAL_ALIGNMENT_LEFT,-1,14,UI.WHITE)
	elif page == 1:
		draw_style_box(UI.box(Color("ac8057"),7,0),Rect2(28,233,304,20))
		draw_rect(Rect2(49,253,12,52),Color("795b46"))
		draw_rect(Rect2(298,253,12,52),Color("795b46"))
		draw_style_box(UI.box(Color("455c52"),10,0),Rect2(69,70,213,148))
		draw_style_box(UI.box(Color("193e37"),5,0),Rect2(79,80,193,124))
		for i in range(6):
			var width = [125,83,144,65,118,93][i]
			draw_line(Vector2(94,100+i*16),Vector2(94+width,100+i*16),UI.GOLD if i==0 else Color("a0c9ad"),3,true)
		if int(elapsed*2)%2==0: draw_line(Vector2(194,180),Vector2(194,191),UI.PAPER,2)
		draw_colored_polygon(PackedVector2Array([Vector2(69,218),Vector2(282,218),Vector2(304,236),Vector2(47,236)]),Color("aeb8a1"))
		draw_style_box(UI.box(Color("718578"),4,0),Rect2(136,222,75,10))
		draw_style_box(UI.box(Color("ebe2c4"),9,0),Rect2(307,207,17,23))
		draw_line(Vector2(315,212),Vector2(315,217),UI.COPPER,2)
	elif page == 2:
		draw_style_box(UI.box(Color("244f40"),8,0),Rect2(38,44,285,125))
		draw_string(UI.weight(UI.TITLE,650),Vector2(60,83),"Aprender y comprobar",HORIZONTAL_ALIGNMENT_LEFT,-1,22,UI.PAPER)
		draw_string(UI.BODY,Vector2(60,116),"Aprobación: desde 4,0",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("b5d9ad"))
		draw_string(UI.BODY,Vector2(60,145),"Bajo 4,0: volver a practicar",HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("edc28c"))
		Character.paint(self,(size-Vector2(360,330)*scale)/2+Vector2(180,306)*scale,{"skin":0,"hair":1,"shirt":5,"hair_style":0,"clothing_style":4,"glasses":true,"show_backpack":false},2.25*scale)
	else:
		draw_style_box(UI.box(Color("bbc5a9"),5,0),Rect2(56,108,250,167))
		draw_colored_polygon(PackedVector2Array([Vector2(37,110),Vector2(181,44),Vector2(324,110)]),UI.GREEN)
		for x in [77,246]:
			for y in [133,186]:
				draw_rect(Rect2(x,y,35,30),Color("83aaa2"))
				draw_line(Vector2(x+17,y),Vector2(x+17,y+30),UI.PAPER,2)
		draw_style_box(UI.box(Color("82674c"),4,0),Rect2(141,164,78,111))
		draw_style_box(UI.box(Color("2d5a49"),2,0),Rect2(151,174,58,101))
		draw_circle(Vector2(198,230),3,UI.GOLD)
		draw_rect(Rect2(128,275,104,10),Color("baa581"))
		draw_rect(Rect2(116,285,128,10),Color("cbb894"))
		draw_string(UI.weight(UI.BODY,700),Vector2(136,144),"FACULTAD",HORIZONTAL_ALIGNMENT_LEFT,-1,15,UI.GREEN)
	draw_set_transform(Vector2.ZERO)
