extends RefCounted

const SIZE = Vector2i(10, 8)
const CATALOG = {
	"bed": {"name": "Cama", "size": Vector2i(2, 3)},
	"desk": {"name": "Escritorio", "size": Vector2i(3, 1)},
	"chair": {"name": "Silla", "size": Vector2i(1, 1)},
	"shelf": {"name": "Librero", "size": Vector2i(2, 1)},
	"lamp": {"name": "Lámpara", "size": Vector2i(1, 1)},
	"rug": {"name": "Alfombra", "size": Vector2i(3, 2)},
	"plant": {"name": "Planta de interior", "size": Vector2i(1, 1)},
	"sofa": {"name": "Sofá de lino", "size": Vector2i(2, 1)},
	"coffee_table": {"name": "Mesa de centro", "size": Vector2i(2, 1)},
	"chest": {"name": "Baúl de madera", "size": Vector2i(2, 1)},
	"aquarium": {"name": "Acuario", "size": Vector2i(2, 1)},
	"bonsai": {"name": "Bonsái", "size": Vector2i(1, 1)},
}

static func initial() -> Dictionary:
	return {
		"bed": {"cell": [0, 3], "rotated": false},
		"desk": {"cell": [5, 0], "rotated": false},
		"chair": {"cell": [6, 2], "rotated": false},
		"shelf": {"cell": [0, 0], "rotated": false},
		"lamp": {"cell": [8, 1], "rotated": false},
		"rug": {"cell": [4, 4], "rotated": false},
	}

static func footprint(id: String, item: Dictionary) -> Rect2i:
	var dimensions: Vector2i = CATALOG[id]["size"]
	if item["rotated"]:
		dimensions = Vector2i(dimensions.y, dimensions.x)
	return Rect2i(Vector2i(int(item["cell"][0]), int(item["cell"][1])), dimensions)

static func can_place(items: Dictionary, id: String, item: Dictionary) -> bool:
	if not CATALOG.has(id):
		return false
	var area = footprint(id, item)
	if not Rect2i(Vector2i.ZERO, SIZE).encloses(area) or area.has_point(Vector2i(9, 7)):
		return false
	if id == "rug":
		return true
	for other in items:
		if other != id and other != "rug" and area.intersects(footprint(other, items[other])):
			return false
	return true

static func valid(items: Variant) -> bool:
	if not items is Dictionary:
		return false
	for required in ["bed", "desk", "chair"]:
		if not items.has(required):
			return false
	for id in items:
		if not CATALOG.has(id) or not items[id] is Dictionary:
			return false
		var item: Dictionary = items[id]
		var cell = item.get("cell")
		if not cell is Array or cell.size() != 2 or not item.get("rotated") is bool:
			return false
		for coordinate in cell:
			if not (coordinate is int or coordinate is float) or not is_finite(float(coordinate)) or coordinate < 0 or coordinate > 9 or float(coordinate) != int(coordinate):
				return false
		if not can_place(items, id, item):
			return false
	return true

static func starter() -> Dictionary:
	var items = initial()
	for id in ["shelf", "lamp", "rug"]: items.erase(id)
	return items

static func accessible(items: Dictionary) -> bool:
	var blocked = {}
	for id in items:
		if id == "rug": continue
		var rect = footprint(id, items[id])
		for y in range(rect.position.y, rect.end.y):
			for x in range(rect.position.x, rect.end.x): blocked[Vector2i(x, y)] = true
	var start = Vector2i(0, 7)
	if blocked.has(start): return false
	var pending = [start]
	var visited = {start: true}
	while not pending.is_empty():
		var cell = pending.pop_front()
		for delta in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var next = cell + delta
			if Rect2i(Vector2i.ZERO, SIZE).has_point(next) and not blocked.has(next) and not visited.has(next):
				visited[next] = true
				pending.append(next)
	for id in ["bed", "desk"]:
		var rect = footprint(id, items[id])
		var reachable = false
		for cell in visited:
			for delta in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
				if rect.has_point(cell + delta): reachable = true
		if not reachable: return false
	return true
