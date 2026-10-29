extends VBoxContainer
const UI = preload("res://scripts/ui_kit.gd")
const Shop = preload("res://scripts/home_shop.gd")
const Room = preload("res://scripts/room_view.gd")
var store
var player = Vector2(5, 6)
var shop
var balance: Label
var list: VBoxContainer
var notice: Label
var preview
signal purchased
func _ready():
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	shop = Shop.new(store)
	var row = HBoxContainer.new()
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(row)
	var left = VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(left)
	UI.heading(left, "Tu lugar", "De a poco, más tuyo", "El dinero de tus proyectos se convierte en un espacio donde dan ganas de volver")
	preview = Room.new()
	preview.state = store
	preview.enabled = false
	preview.custom_minimum_size = Vector2(460, 340)
	preview.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(preview)
	balance = UI.text(left, "", 24, UI.GREEN)
	UI.text(left, "Las mejoras del equipo son opcionales, todas las clases y proyectos funcionan con tu notebook inicial", 14, UI.MUTED, true)
	var side = PanelContainer.new()
	side.custom_minimum_size.x = 430
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(side)
	list = UI.scroll(side)
	notice = UI.text(self, "Compra un artículo y después ubícalo a tu gusto desde Decorar", 14, UI.GREEN, true)
	refresh()
func refresh():
	balance.text = "$%s disponibles" % int(store.data["money"])
	for child in list.get_children():
		list.remove_child(child)
		child.queue_free()
	for id in Shop.GOODS:
		var item = Shop.GOODS[id]
		var card = UI.card(list, Color("eee6d2"))
		card.add_theme_constant_override("separation", 7)
		UI.text(card, item["name"], 22, UI.GREEN, true)
		UI.text(card, item["description"], 15, UI.MUTED, true)
		var owned = shop.owned(id)
		var buy = UI.action(card, "Ya es tuyo" if owned else "Comprar  ·  $%s" % item["price"], func():
			if shop.buy(id, player):
				purchased.emit()
				preview.queue_redraw()
			refresh()
			notice.text = shop.notice
		, not owned)
		buy.disabled = owned or store.data["money"] < item["price"]
