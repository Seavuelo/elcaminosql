extends PanelContainer
const UI = preload("res://scripts/ui_kit.gd")
const Arena = preload("res://scripts/league_arena.gd")
const INK = Color("392b3b")
const NIGHT = Color("332636")
const GOLD = Color("e4bd78")
const PALE = Color("f3e6c9")
const ROSE = Color("d7a9b6")
var league
var audio
var phase = "prepare"
var body: VBoxContainer
var balance: Label
var status: Label
var nav: HBoxContainer
var arena
var score: Label
var clock: Label
var live_log: VBoxContainer
var cue_label: Label
var event_count = -1
var last_second = -1
func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_theme_stylebox_override("panel", UI.box(NIGHT, 18, 20))
	var column = VBoxContainer.new()
	add_child(column)
	var header = HBoxContainer.new()
	column.add_child(header)
	var title = UI.text(header, "Liga de Dioses", 34, PALE)
	title.add_theme_font_override("font", UI.weight(UI.TITLE, 650))
	UI.fill(header)
	balance = UI.text(header, "", 20, GOLD)
	nav = HBoxContainer.new()
	column.add_child(nav)
	for page in [["prepare", "Preparar partida"], ["gods", "Dioses"], ["upgrades", "Aumentos"], ["history", "Mi última partida"]]:
		var button = action(nav, page[1], show_page.bind(page[0]))
		button.set_meta("page", page[0])
	body = VBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(body)
	status = UI.text(column, "La XP se consigue estudiando, jugar partidas conserva tu experiencia y mejora tu rango", 13, ROSE, true)
	show_page("battle" if league.state()["battle"] != null else "prepare")
func action(parent: Node, title: String, callback: Callable, selected: bool = false) -> Button:
	var button = UI.action(parent, title, callback)
	button.add_theme_stylebox_override("normal", UI.box(GOLD if selected else Color("51404e"), 9, 11))
	button.add_theme_stylebox_override("hover", UI.box(Color("edcd96") if selected else Color("69505f"), 9, 11))
	for state in ["font_color", "font_hover_color", "font_focus_color"]:
		button.add_theme_color_override(state, INK if selected else PALE)
	return button
func portrait(parent: Node, god: String, width: int = 112) -> TextureRect:
	var texture = TextureRect.new()
	texture.texture = load("res://assets/league/" + god + ".png")
	texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	texture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	texture.custom_minimum_size = Vector2(width, width * 70.0 / 64)
	parent.add_child(texture)
	return texture
func clear_body() -> void:
	for child in body.get_children():
		body.remove_child(child)
		child.queue_free()
	arena = null
func show_page(page: String) -> void:
	phase = page
	clear_body()
	balance.text = "%s XP" % int(league.state()["xp"])
	for button in nav.get_children():
		var selected = button.get_meta("page") == page
		button.add_theme_stylebox_override("normal", UI.box(GOLD if selected else Color("51404e"), 9, 11))
		for key in ["font_color", "font_hover_color", "font_focus_color"]:
			button.add_theme_color_override(key, INK if selected else PALE)
	if league.state()["battle"] != null and page != "battle":
		action(body, "Tu partida sigue en curso, volver a la arena", show_page.bind("battle"), true)
	match page:
		"prepare": preparation()
		"gods": gods()
		"upgrades": upgrades()
		"battle": battle_view()
		"history": history()
func choose(key: String, value: String) -> void:
	if league.choose(key, value): show_page(phase)
func preparation() -> void:
	var scroll = UI.scroll(body)
	var row = HBoxContainer.new()
	scroll.add_child(row)
	var selected = UI.card(row, PALE)
	selected.add_theme_constant_override("separation", 6)
	selected.get_parent().add_theme_stylebox_override("panel", UI.box(PALE, 16, 14))
	selected.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var summary = HBoxContainer.new()
	selected.add_child(summary)
	var god = league.state()["god"]
	var profile = league.content["profiles"][god]
	portrait(summary, god, 104)
	var info = VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	summary.add_child(info)
	info.add_theme_constant_override("separation", 5)
	UI.text(info, "TU DIOS", 11, UI.COPPER)
	UI.text(info, league.content["gods"][god][0], 28, INK).add_theme_font_override("font", UI.weight(UI.TITLE, 650))
	UI.text(info, league.content["gods"][god][1], 14, UI.MUTED, true)
	UI.text(info, profile["skill"] + "  ·  " + profile["detail"], 15, INK, true)
	UI.compact(UI.action(selected, "Elegir otro dios", show_page.bind("gods")))
	var report = UI.card(row, Color("e5d7c5"))
	report.add_theme_constant_override("separation", 6)
	report.get_parent().add_theme_stylebox_override("panel", UI.box(Color("e5d7c5"), 16, 14))
	report.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var prep = league.preparation()
	var enemy = prep["enemy"]
	UI.text(report, "INFORME DEL RIVAL", 11, UI.COPPER)
	UI.text(report, enemy["name"], 23, INK, true)
	UI.text(report, enemy["style"], 15, UI.MUTED, true)
	UI.text(report, enemy["hint"], 17, INK, true)
	UI.text(report, "Preparación estimada  ·  %s%%" % roundi(float(prep["chance"]) * 100), 15, UI.GREEN)
	var odds = ProgressBar.new()
	odds.value = prep["chance"] * 100
	odds.show_percentage = false
	odds.add_theme_stylebox_override("fill", UI.box(UI.GREEN, 6, 0))
	odds.add_theme_stylebox_override("background", UI.box(Color("c8bca5"), 6, 0))
	odds.custom_minimum_size.y = 10
	report.add_child(odds)
	var build = UI.card(scroll, Color("eee1ca"))
	build.add_theme_constant_override("separation", 6)
	build.get_parent().add_theme_stylebox_override("panel", UI.box(Color("eee1ca"), 16, 14))
	var options = HBoxContainer.new()
	build.add_child(options)
	for spec in [["strategy", "Estrategia", "strategies"], ["relic", "Reliquia", "relics"]]:
		var column = VBoxContainer.new()
		column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		column.add_theme_constant_override("separation", 5)
		options.add_child(column)
		UI.text(column, spec[1], 13, UI.COPPER)
		var selector = OptionButton.new()
		var keys = league.content[spec[2]].keys()
		for index in range(keys.size()):
			var item = league.content[spec[2]][keys[index]]
			selector.add_item(item if item is String else item[0])
			if keys[index] == league.state()[spec[0]]: selector.select(index)
		selector.disabled = league.state()["battle"] != null
		column.add_child(selector)
		selector.item_selected.connect(func(index): choose(spec[0], keys[index]))
		var description = league.content["strategy_info"][league.state()["strategy"]][0] if spec[0] == "strategy" else league.content["relics"][league.state()["relic"]][1]
		UI.text(column, description, 14, INK, true)
	var links = PackedStringArray()
	if prep["synergy"]: links.append("Dios y estrategia se complementan")
	if prep["relic_match"]: links.append("La reliquia potencia su habilidad")
	if prep["counter"]: links.append("Tu estrategia responde al rival")
	UI.text(build, "  /  ".join(links) if not links.is_empty() else "Prueba otra combinación o invierte en el punto que revela el informe del rival", 14, UI.GREEN, true)
	var bottom = HBoxContainer.new()
	body.add_child(bottom)
	var state = league.state()
	UI.text(bottom, league.rank_name() + "  ·  %s LP  ·  %s victorias / %s partidas" % [int(state["rating"]), int(state["wins"]), int(state["matches"])], 15, PALE, true)
	var start = action(bottom, "Volver a la partida" if state["battle"] != null else "Buscar partida", start_match, true)
	start.custom_minimum_size.x = 230
func start_match() -> void:
	if league.state()["battle"] != null or league.start_battle():
		show_page("battle")
		if audio != null: audio.sfx("bell")
	else: status.text = league.notice
func gods() -> void:
	var scroll = UI.scroll(body)
	var grid = GridContainer.new()
	grid.columns = 3
	scroll.add_child(grid)
	for god in league.content["gods"]:
		var chosen = god == league.state()["god"]
		var card = UI.card(grid, Color("e7d2ad") if chosen else PALE)
		card.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var row = HBoxContainer.new()
		card.add_child(row)
		portrait(row, god, 82)
		var info = VBoxContainer.new()
		info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(info)
		var item = league.content["gods"][god]
		UI.text(info, item[0], 22, INK)
		UI.text(info, item[1], 13, UI.MUTED, true)
		UI.text(info, "Maestría %s/10" % int(league.state()["mastery"][god]), 12, UI.COPPER)
		var profile = league.content["profiles"][god]
		UI.text(card, profile["detail"], 14, INK, true)
		UI.text(card, "Daño %s  /  Resistencia %s  /  Utilidad %s" % [int(profile["stats"][0]), int(profile["stats"][1]), int(profile["stats"][2])], 11, UI.MUTED, true)
		var select = UI.action(card, "Seleccionado" if chosen else "Elegir " + item[0], choose.bind("god", god), chosen)
		select.disabled = league.state()["battle"] != null or chosen
func upgrades() -> void:
	var scroll = UI.scroll(body)
	UI.text(scroll, "La maestría pertenece al dios elegido, los otros cuatro aumentos sirven para todos", 15, PALE, true)
	var grid = GridContainer.new()
	grid.columns = 3
	scroll.add_child(grid)
	for key in league.KEYS:
		var card = UI.card(grid, PALE)
		card.add_theme_constant_override("separation", 6)
		card.get_parent().add_theme_stylebox_override("panel", UI.box(PALE, 14, 12))
		card.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var level = league.level(key)
		UI.text(card, league.content["upgrades"][key][0], 22, INK, true)
		UI.text(card, league.content["upgrades"][key][1], 14, UI.MUTED, true)
		UI.text(card, "NIVEL %s / 10" % level, 12, UI.COPPER)
		var bar = ProgressBar.new()
		bar.max_value = 10
		bar.value = level
		bar.show_percentage = false
		bar.custom_minimum_size.y = 10
		bar.add_theme_stylebox_override("fill", UI.box(Color("896264"), 5, 0))
		bar.add_theme_stylebox_override("background", UI.box(Color("d2c5aa"), 5, 0))
		card.add_child(bar)
		UI.text(card, "Precisión  ·  %.1f s" % (0.3 + level * 0.1), 13, INK)
		var buy = UI.action(card, "Nivel máximo" if level >= 10 else "Mejorar  ·  %s XP" % league.cost(key), func():
			if league.buy(key) and audio != null: audio.sfx("success")
			show_page("upgrades")
			status.text = league.notice
		, true)
		UI.compact(buy)
		buy.disabled = level >= 10 or league.state()["xp"] < league.cost(key) or league.state()["battle"] != null
	var guide = UI.card(grid, Color("ddc397"))
	guide.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.text(guide, "Una buena combinación", 22, INK, true)
	UI.text(guide, "Mira el punto débil del rival y el estilo de tu dios, una reliquia puede darte una ventaja mientras entrenas el aumento que te falta", 16, INK, true)
func battle_view() -> void:
	if league.state()["battle"] == null:
		show_page("history")
		return
	var top = HBoxContainer.new()
	body.add_child(top)
	clock = UI.text(top, "", 15, GOLD)
	UI.fill(top)
	score = UI.text(top, "", 20, PALE)
	var row = HBoxContainer.new()
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(row)
	var left = VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(left)
	arena = Arena.new()
	arena.league = league
	arena.attempted.connect(func(result):
		if audio != null: audio.sfx("success" if result.get("success", false) else "error")
	)
	left.add_child(arena)
	cue_label = UI.text(left, "Solo algunas jugadas necesitan tu precisión, haz clic en el círculo o pulsa Espacio cuando el anillo llegue a la banda verde", 14, PALE, true)
	var report = UI.card(row, Color("493746"))
	report.get_parent().custom_minimum_size.x = 260
	report.get_parent().size_flags_horizontal = Control.SIZE_FILL
	UI.text(report, "RELATO DE LA PARTIDA", 12, GOLD)
	UI.text(report, league.state()["battle"]["result"]["enemy"]["name"], 15, ROSE, true)
	live_log = UI.scroll(report)
	event_count = -1
	last_second = -1
	arena.grab_focus()
	refresh_battle()
func refresh_battle() -> void:
	if league.state()["battle"] == null: return
	var match_state = league.state()["battle"]
	var elapsed = float(match_state["elapsed"])
	var second = int(elapsed)
	if second != last_second:
		clock.text = "EN VIVO  ·  %02d:%02d  /  %.0f s de simulación" % [int(elapsed * 0.72), int(fmod(elapsed * 43.2, 60)), match_state["duration"]]
		last_second = second
	score.text = "%s / %s / %s" % league.live_score()
	var events = match_state["result"]["events"].filter(func(item): return float(item["time"]) <= elapsed)
	if events.size() != event_count:
		for child in live_log.get_children():
			live_log.remove_child(child)
			child.queue_free()
		for index in range(maxi(0, events.size() - 5), events.size()):
			var event = events[index]
			UI.text(live_log, event["text"], 15, Color("efc4b6") if event["type"] == "death" else PALE, true)
			event_count = events.size()
	var cue = league.current_cue()
	if not cue.is_empty():
		cue_label.text = league.content["cue_text"][cue["kind"]][0] + "  ·  " + league.content["cue_text"][cue["kind"]][1]
	else:
		cue_label.text = "Las oportunidades son opcionales, tu preparación también decide el resultado, puedes cerrar el teléfono mientras sigue la partida"
func history() -> void:
	var result = league.state()["last_match"]
	if result == null:
		UI.text(body, "UNRANKED", 13, GOLD)
		UI.text(body, "Tu primera partida está por comenzar", 30, PALE, true)
		UI.text(body, "Elige un dios, piensa en una estrategia y mira qué necesita tu equipo", 18, ROSE, true)
		action(body, "Preparar mi primera partida", show_page.bind("prepare"), true)
		return
	var scroll = UI.scroll(body)
	var card = UI.card(scroll, Color("e8d4ac") if result["win"] else Color("ddc9c3"))
	var row = HBoxContainer.new()
	card.add_child(row)
	portrait(row, result["god"], 130)
	var details = VBoxContainer.new()
	details.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(details)
	UI.text(details, "VICTORIA" if result["win"] else "DERROTA", 34, INK).add_theme_font_override("font", UI.weight(UI.TITLE, 700))
	UI.text(details, "%s / %s / %s" % [int(result["kills"]), int(result["deaths"]), int(result["assists"])], 28, INK)
	UI.text(details, "%s  ·  %s%s LP" % [league.rank_name(), "+" if result["rating_delta"] > 0 else "", int(result["rating_delta"])], 17, UI.GREEN if result["win"] else UI.RED)
	if result.get("mvp", false): UI.text(details, "MVP  ·  Tu equipo sintió la diferencia", 15, UI.COPPER)
	if result.get("rank_before", "") != result.get("rank_after", ""):
		UI.text(card, "Nuevo rango  ·  " + result["rank_after"], 22, UI.GREEN)
	var weak = "vision" if result["deaths"] > 7 and league.level("vision") < 4 else "positioning" if result["deaths"] > 5 else league.content["profiles"][result["god"]]["focus"]
	UI.text(card, "Para tu próxima partida  ·  " + league.content["upgrades"][weak][1].to_lower(), 16, INK, true)
	for item in result.get("precision", []):
		UI.text(scroll, item["text"], 15, GOLD if item["status"] in ["hit", "perfect"] else ROSE, true)
	UI.text(scroll, "ASÍ OCURRIÓ", 12, GOLD)
	for event in result.get("events", []):
		UI.text(scroll, "%02d s  ·  %s" % [int(event["time"]), event["text"]], 15, PALE, true)
	var actions = HBoxContainer.new()
	body.add_child(actions)
	action(actions, "Buscar otra partida", start_match, true)
	action(actions, "Revisar mi combinación", show_page.bind("prepare"))
	action(actions, "Entrenar aumentos", show_page.bind("upgrades"))
func _process(_delta: float) -> void:
	if not is_instance_valid(body): return
	balance.text = "%s XP" % int(league.state()["xp"])
	if phase == "battle":
		if league.state()["battle"] == null:
			show_page("history")
			if audio != null: audio.sfx("success")
		else: refresh_battle()
func _exit_tree() -> void:
	if league != null: league.store.save()
