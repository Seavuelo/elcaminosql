extends SceneTree
const State = preload("res://scripts/study_state.gd")
const Shop = preload("res://scripts/home_shop.gd")
const Layout = preload("res://scripts/room_layout.gd")
var checks = 0
var failures = []
func check(value, message):
	checks += 1
	if not value: failures.append(message)
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-home").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name": "Mi casa"})
	var shop = Shop.new(store)
	check(store.data["items"].size() == 3 and store.data["furniture_level"]["bed"] == 0, "La partida comienza con colchón, escritorio y silla")
	check(Layout.valid(store.data["items"]) and Layout.accessible(store.data["items"]), "La habitación inicial es válida y transitable")
	check(not shop.buy("sofa"), "No comprar sin dinero")
	store.reward_money(500, "fixture")
	for id in Shop.GOODS:
		var previous = store.data["money"]
		check(shop.buy(id), "Comprar " + id)
		check(store.data["money"] == previous - Shop.GOODS[id]["price"], "Descuento exacto " + id)
		check(Layout.valid(store.data["items"]) and Layout.accessible(store.data["items"]), "La compra conserva acceso " + id)
		previous = store.data["money"]
		check(not shop.buy(id) and store.data["money"] == previous, "Sin compras duplicadas " + id)
	var restored = State.new(folder)
	check(restored.data["items"] == store.data["items"] and restored.data["money"] == store.data["money"], "Compras recuperadas desde disco")
	store.new_run({"player_name": "Revertir"})
	store.reward_money(100, "fixture")
	store.recovery_blocked = true
	var before = store.data.duplicate(true)
	check(not shop.buy("bed") and before == store.data, "Un fallo de guardado revierte la mejora y el dinero")
	var blocked = Layout.starter()
	blocked["sofa"] = {"cell": [0, 6], "rotated": false}
	blocked["lamp"] = {"cell": [1, 7], "rotated": false}
	check(not Layout.accessible(blocked), "Rechazar una puerta encerrada entre muebles")
	check(Layout.valid(Layout.initial()), "Las habitaciones anteriores siguen siendo compatibles")
	print(JSON.stringify({"module": "home", "checks": checks, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
