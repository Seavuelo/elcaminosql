extends Control

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
const Character = preload("res://scripts/character_art.gd")
var kind = "pipeline"
var variant = 0
var dark = false
var profile: Dictionary = {"skin": 0, "hair": 0, "shirt": 0}

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size.y = 146

func caption(rect: Rect2, text: String, color: Color, size_hint: int = 15) -> void:
	var font: Font = UI.BODY
	var point = size_hint
	for line in text.split("\n"):
		while point > 11 and font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, point).x > rect.size.x - 10:
			point -= 1
	var lines = text.split("\n")
	var height = font.get_height(point) * lines.size()
	var y = rect.position.y + (rect.size.y - height) / 2 + font.get_ascent(point)
	for line in lines:
		draw_string(font, Vector2(rect.position.x + 5, y), line, HORIZONTAL_ALIGNMENT_CENTER, rect.size.x - 10, point, color)
		y += font.get_height(point)

func tile(rect: Rect2, title: String, body: String, accent: Color = UI.GREEN) -> void:
	var style = UI.box(Color("2a5146") if dark else Color("e7ebdc"), 11, 0)
	style.border_color = accent.lightened(0.3)
	style.set_border_width_all(1)
	draw_style_box(style, rect)
	caption(Rect2(rect.position + Vector2(4, 8), Vector2(rect.size.x - 8, 28)), title, UI.GOLD if dark else accent, 14)
	caption(Rect2(rect.position + Vector2(4, 39), Vector2(rect.size.x - 8, rect.size.y - 44)), body, UI.PAPER if dark else UI.INK, 16)

func flow(titles: Array, bodies: Array) -> void:
	var count = titles.size()
	var gap = 28.0
	var width = (size.x - gap * (count - 1)) / count
	for i in range(count):
		var rect = Rect2(i * (width + gap), 8, width, size.y - 16)
		tile(rect, titles[i], bodies[i], UI.COPPER if i == variant % count else UI.GREEN)
		if i < count - 1:
			var p = Vector2(rect.end.x + 5, size.y * 0.5)
			var q = p + Vector2(gap - 10, 0)
			draw_line(p, q, UI.GOLD if dark else UI.COPPER, 2, true)
			draw_polyline(PackedVector2Array([q + Vector2(-5, -5), q, q + Vector2(-5, 5)]), UI.GOLD if dark else UI.COPPER, 2, true)

func number_tiles(values: Array, accepted: Array, legend: String) -> void:
	caption(Rect2(0, 0, size.x, 30), legend, UI.PAPER if dark else UI.INK, 17)
	var gap = 12.0
	var width = (size.x - gap * (values.size() - 1)) / values.size()
	for i in range(values.size()):
		var rect = Rect2(i * (width + gap), 43, width, size.y - 52)
		var color = Color("73a482") if accepted[i] else Color("b87f6b")
		draw_style_box(UI.box(color.darkened(0.3) if dark else color.lightened(0.5), 10, 0), rect)
		caption(rect, str(values[i]), UI.PAPER if dark else UI.INK, 25)

func miniature_table(rect: Rect2, title: String, columns: Array, rows: Array, accent: int = 0) -> void:
	draw_style_box(UI.box(Color("2b5345") if dark else Color("e3e9d9"), 10, 0), rect)
	caption(Rect2(rect.position, Vector2(rect.size.x, 32)), title, UI.GOLD if dark else UI.GREEN, 15)
	var row_height = (rect.size.y - 36) / (rows.size() + 1)
	var width = rect.size.x / columns.size()
	for column in range(columns.size()):
		var area = Rect2(rect.position + Vector2(column * width, 35), Vector2(width, row_height))
		draw_rect(area, Color("446a53") if dark else Color("ccdac2"))
		caption(area, columns[column], Color("f2d69e") if dark else UI.GREEN, 14)
	for row in range(rows.size()):
		var area = Rect2(rect.position + Vector2(0, 35 + (row + 1) * row_height), Vector2(rect.size.x, row_height))
		if row == variant % rows.size():
			draw_rect(area, Color(0.7, 0.8, 0.6, 0.13))
		for column in range(columns.size()):
			caption(Rect2(area.position + Vector2(column * width, 0), Vector2(width, row_height)), str(rows[row][column]), UI.GOLD if dark and column == accent else UI.PAPER if dark else UI.COPPER if column == accent else UI.INK, 15)

func welcome() -> void:
	var names = ["Marco", "Tú", "Moshi", "Carlos", "Sofía", "Matías"]
	var profiles = [{"skin": 0, "hair": 1, "shirt": 5, "hair_style": 0, "clothing_style": 4, "glasses": true}, profile,
		Course.peer_profile("moshi"), Course.peer_profile("carlos"), Course.peer_profile("sofia"), Course.peer_profile("matias")]
	var scale = clampf(minf(size.y / 120, size.x / 290), 1.0, 2.2)
	for i in range(names.size()):
		var x = (i + 0.5) * size.x / names.size()
		var y = size.y * 0.66
		Character.paint(self, Vector2(x, y), profiles[i], scale)
		draw_set_transform(Vector2.ZERO)
		caption(Rect2(x - size.x / 13, y + 10, size.x / 6.5, 28), names[i], UI.PAPER if dark else UI.INK, 16)

func relationship(junction: bool = false) -> void:
	var width = (size.x - (48 if not junction else 64)) / (2 if not junction else 3)
	var height = minf(size.y - 24, 210)
	var y = (size.y - height) / 2
	miniature_table(Rect2(0, y, width, height), "ESTUDIANTE", ["id", "nombre"], [[1, "Moshi"], [2, "Carlos"]])
	if junction:
		miniature_table(Rect2(width + 32, y, width, height), "INSCRIPCION", ["estudiante_id", "taller_id"], [[1, 7], [1, 8], [2, 7]])
		miniature_table(Rect2((width + 32) * 2, y, width, height), "TALLER", ["id", "nombre"], [[7, "Robótica"], [8, "Fotografía"]])
	else:
		miniature_table(Rect2(width + 48, y, width, height), "TUTORIA", ["estudiante_id", "tema"], [[1, "Claves"], [1, "Consultas"], [2, "Tipos"]])
	for i in range(2 if junction else 1):
		var start = Vector2((i + 1) * width + i * 32 + 3, size.y * 0.5)
		var end = start + Vector2(26 if junction else 42, 0)
		draw_line(start, end, UI.GOLD if dark else UI.COPPER, 2, true)
		for offset in [-7, 0, 7]:
			draw_line(end - Vector2(9, 0), end + Vector2(0, offset), UI.GOLD if dark else UI.COPPER, 2, true)

func _draw() -> void:
	if size.x < 80 or size.y < 50:
		return
	match kind:
		"welcome":
			welcome()
		"pipeline", "scattered":
			flow(["TUS DATOS", "SQL", "SQLITE", "RESULTADO"], ["Información\norganizada", "Lo que\nsolicitas", "El motor\nlo ejecuta", "Filas y\ncolumnas"])
		"table", "entities", "attributes":
			miniature_table(Rect2(20, 8, size.x - 40, size.y - 16), "ESTUDIANTE", ["id", "nombre", "promedio"], [[1, "Moshi", "6,8"], [2, "Carlos", "5,0"], [3, "Sofía", "6,5"]])
		"types", "type_mapping":
			miniature_table(Rect2(8, 8, size.x - 16, size.y - 16), "DEL DISEÑO A SQLITE", ["Qué guardas", "Tipo lógico", "SQLite"], [["Un nombre", "VARCHAR", "TEXT"], ["Una cantidad", "NUMERIC, escala 0", "INTEGER"], ["Una nota", "NUMERIC", "REAL"]], 1)
		"precision":
			flow(["NUMERIC(4,2)", "12.50", "125.50"], ["Hasta 4 dígitos\nHasta 2 decimales", "4 dígitos\nSí cabe", "5 dígitos\nNo cabe"])
		"capacity":
			caption(Rect2(0, 0, size.x, 32), "NUMERIC(10,0) admite hasta diez dígitos, no exige usarlos todos", UI.PAPER if dark else UI.INK, 16)
			var width = (size.x - 36) / 10
			for i in range(10):
				var rect = Rect2(18 + i * width, 52, width - 5, 50)
				draw_style_box(UI.box(Color("7ea391") if i >= 8 else Color("d7d6c4"), 5, 0), rect)
				caption(rect, str(i - 7) if i >= 8 else "", UI.INK, 23)
		"key":
			flow(["ID 7", "ID 8", "ID 7 REPETIDO"], ["Ana\nPrimer registro", "Ana\nNombre permitido", "El identificador\ndebe ser único"])
		"null":
			flow(["NULL", "0", "TEXTO VACÍO"], ["Valor\ndesconocido", "Un número\nconocido", "Texto\nconocido"])
		"codes":
			flow(["CÓDIGO", "TELÉFONO", "CANTIDAD"], ["0012\nTexto", "+56 9 1234 5678\nTexto", "12 productos\nNúmero"])
		"names":
			flow(["ENTIDAD", "ATRIBUTO", "CONVENCIÓN"], ["ESTUDIANTE\nSingular", "fecha_nacimiento\nPalabras con _", "anio_ingreso\nSin espacios ni tildes"])
		"binary":
			flow(["ARCHIVO", "BLOB", "CONTENIDO"], ["Una foto\nun documento", "Datos\nbinarios", "Bytes\n01001010"])
		"affinity":
			flow(["COLUMNA NUMERIC", "TEXTO '12'", "TEXTO 'DOCE'"], ["Afinidad\nde SQLite", "Puede convertirse\na número", "Puede seguir\ncomo texto"])
		"checks", "range":
			flow(["TIPO REAL", "REGLA", "NOTA 8"], ["Permite decimales\ntambién 8", "Entre 1 y 7\nCHECK", "Fuera del rango\nSe rechaza"])
		"relation", "reparent", "identifying":
			relationship()
		"junction":
			relationship(true)
		"conversion":
			flow(["MODELO LÓGICO", "RELACIONAL", "SQL"], ["Entidades\ny relaciones", "Tablas\nPK y FK", "CREATE TABLE\nRestricciones"])
		"filter":
			number_tiles(["3,2", "3,9", "4,0", "6,0"], [true, true, false, false], "Ejemplo: nota < 4 conserva solo las dos primeras")
		"sort", "paging":
			flow(["SIN ORDEN", "ORDER BY", "LIMIT Y OFFSET"], ["6 · 3 · 5 · 4", "3 · 4 · 5 · 6", "Elegir una página\ndel resultado ordenado"])
		"update", "delete":
			flow(["ANTES", "WHERE id = 2", "DESPUÉS"], ["1 · Ana\n2 · Carlos\n3 · Moshi", "Una fila\nseleccionada", "Cambiar esa fila" if kind == "update" else "Borrar esa fila\nConservar las demás"])
		"aggregate":
			flow(["NOTAS", "CONTAR", "PROMEDIAR"], ["4 · NULL · 6", "COUNT(*) = 3\nCOUNT(nota) = 2", "AVG(nota) = 5\nNULL no es cero"])
		"grouping", "having":
			flow(["FILAS", "GROUP BY", "HAVING"], ["A · A · A · B", "A: 3 filas\nB: 1 fila", "COUNT(*) >= 2\nConservar grupo A"])
		"join", "leftjoin":
			flow(["ESTUDIANTE", "COINCIDIR ID", "TUTORIA"], ["Una persona\npor identificador", "Relacionar claves\nLEFT conserva sin pareja" if kind == "leftjoin" else "Relacionar las claves\nCada pareja produce una fila", "Sus tutorías\no NULL sin pareja"])
		"subquery":
			flow(["CONSULTA INTERIOR", "RESULTADO", "CONSULTA EXTERIOR"], ["Calcula un valor\no una lista", "Un promedio\nidentificadores", "Usa ese resultado\npara decidir qué mostrar"])
		"view":
			flow(["TABLAS", "CONSULTA GUARDADA", "VISTA"], ["Datos actuales", "Un nombre\npara un SELECT", "Consultar\nsu resultado"])
		"index":
			flow(["BÚSQUEDA", "ÍNDICE", "TABLA"], ["Un valor\nque encontrar", "Referencias\norganizadas", "Las filas\ncorrespondientes"])
		_:
			flow(["OBSERVA", "PRUEBA", "COMPARA"], ["Qué pide\nel problema", "Una consulta\ncon tus datos", "Qué cambió\ny por qué"])
