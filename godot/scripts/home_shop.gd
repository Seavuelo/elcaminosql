extends RefCounted
const Layout = preload("res://scripts/room_layout.gd")
const GOODS = {
	"bed": {"name": "Una cama de verdad", "price": 28, "description": "Una base de madera, colchón y ropa de cama para descansar después de clases", "level": 1},
	"desk": {"name": "Estación de trabajo", "price": 45, "description": "Un monitor amplio, teclado y equipo de escritorio, tus proyectos siguen disponibles con el notebook", "level": 1},
	"shelf": {"name": "Librero de madera", "price": 14, "description": "Un lugar para tus apuntes y esas lecturas que ahora sí vas a terminar"},
	"lamp": {"name": "Lámpara cálida", "price": 10, "description": "Luz suave para las noches de estudio"},
	"rug": {"name": "Alfombra tejida", "price": 12, "description": "Terracota y crema para darle calidez a tu pieza"},
	"plant": {"name": "Planta de interior", "price": 6, "description": "Un poco de verde entre consulta y consulta"},
	"sofa": {"name": "Sofá de lino", "price": 24, "description": "Cojines verde salvia y un rincón donde bajar las revoluciones"},
	"coffee_table": {"name": "Mesa de centro", "price": 12, "description": "Madera clara, una taza y algo para leer"},
	"chest": {"name": "Baúl de madera", "price": 10, "description": "Guarda lo que antes quedaba tirado junto al colchón"},
	"aquarium": {"name": "Acuario", "price": 30, "description": "Agua, plantas y peces que hacen su vida mientras tú estudias"},
	"bonsai": {"name": "Bonsái", "price": 18, "description": "Un árbol pequeño con más paciencia que todos nosotros"},
}
var store
var notice = ""
func _init(save_system): store = save_system
func owned(id: String) -> bool:
	return int(store.data["furniture_level"].get(id, 0)) >= GOODS[id]["level"] if GOODS[id].has("level") else store.data["items"].has(id)
func buy(id: String, player: Vector2 = Vector2(5, 6)) -> bool:
	if not GOODS.has(id): notice = "Ese artículo no está en el catálogo"; return false
	if owned(id): notice = "Ya tienes este artículo"; return false
	if store.data["money"] < GOODS[id]["price"]: notice = "Todavía falta dinero, los encargos de Nexo ayudan a reunirlo"; return false
	var before = store.data.duplicate(true)
	if GOODS[id].has("level"):
		store.data["furniture_level"][id] = GOODS[id]["level"]
	else:
		var placed = false
		for cell in positions(id):
			var candidate = {"cell": [cell.x, cell.y], "rotated": false}
			if not Layout.can_place(store.data["items"], id, candidate) or Layout.footprint(id, candidate).has_point(Vector2i((player + Vector2(0.5, 0.5)).floor())): continue
			var arrangement = store.data["items"].duplicate(true)
			arrangement[id] = candidate
			if not Layout.accessible(arrangement): continue
			store.data["items"] = arrangement
			placed = true
			break
		if not placed: notice = "No cabe con la distribución actual, mueve algunos muebles y vuelve a intentarlo"; return false
	store.data["money"] -= GOODS[id]["price"]
	if not store.save():
		store.data = before
		notice = store.notice
		return false
	notice = "Compra guardada, puedes mover el mueble desde Decorar"
	return true

func positions(id: String) -> Array:
	var preferred = {"shelf": Vector2i(0, 0), "lamp": Vector2i(8, 1), "rug": Vector2i(4, 4), "plant": Vector2i(8, 5), "sofa": Vector2i(7, 6), "coffee_table": Vector2i(4, 4), "chest": Vector2i(2, 0), "aquarium": Vector2i(3, 1), "bonsai": Vector2i(1, 1)}
	var result = [preferred.get(id, Vector2i(3, 3))]
	for y in range(8):
		for x in range(10):
			var cell = Vector2i(x, y)
			if cell not in result: result.append(cell)
	return result
