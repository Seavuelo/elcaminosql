extends VBoxContainer
const UI = preload("res://scripts/ui_kit.gd")
const MODES = ["windowed", "borderless", "fullscreen"]
const RESOLUTIONS = [[1024, 720], [1280, 800], [1366, 768], [1600, 900], [1920, 1080], [2560, 1440]]
var store
var audio
var message: Label
var preview: PanelContainer
var countdown: Label
var seconds_left = 0.0
var previous: Dictionary = {}
var proposed: Dictionary = {}
var mode: OptionButton
var resolution: OptionButton
var monitor: OptionButton

static func apply_window(settings: Dictionary) -> void:
	var screen = clampi(int(settings.get("monitor", DisplayServer.window_get_current_screen())), 0, maxi(0, DisplayServer.get_screen_count() - 1))
	if not settings.has("monitor") and DisplayServer.screen_get_size(screen).x < 1000:
		for candidate in range(DisplayServer.get_screen_count()):
			var dimensions = DisplayServer.screen_get_size(candidate)
			if dimensions.x >= 1000 and dimensions.x > dimensions.y:
				screen = candidate
				break
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
	DisplayServer.window_set_current_screen(screen)
	var kind = settings.get("screen_mode", "windowed")
	if kind == "borderless":
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	elif kind == "fullscreen":
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	else:
		var available = DisplayServer.screen_get_usable_rect(screen)
		var selected = settings.get("resolution", [1280, 800])
		var dimensions = Vector2i(int(selected[0]), int(selected[1]))
		var maximum = available.size - Vector2i(16, 48)
		var minimum = Vector2i(mini(1000, maximum.x), mini(680, maximum.y))
		DisplayServer.window_set_min_size(minimum)
		dimensions = dimensions.clamp(minimum, maximum)
		DisplayServer.window_set_size(dimensions)
		DisplayServer.window_set_position(available.position + (available.size - dimensions) / 2)

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	var content = UI.scroll(self)
	var row = HBoxContainer.new()
	content.add_child(row)
	var display = UI.card(row, Color("e7eadb"))
	display.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.heading(display, "A tu medida", "Pantalla")
	UI.text(display, "Modo de pantalla", 14, UI.MUTED)
	mode = OptionButton.new()
	for title in ["Ventana", "Ventana sin bordes", "Pantalla completa"]: mode.add_item(title)
	mode.select(maxi(0, MODES.find(store.data["settings"]["screen_mode"])))
	display.add_child(mode)
	UI.text(display, "Resolución de la ventana", 14, UI.MUTED)
	resolution = OptionButton.new()
	for index in range(RESOLUTIONS.size()):
		resolution.add_item("%s × %s" % RESOLUTIONS[index])
		if RESOLUTIONS[index] == store.data["settings"]["resolution"]: resolution.select(index)
	display.add_child(resolution)
	resolution.disabled = mode.selected != 0
	mode.item_selected.connect(func(index): resolution.disabled = index != 0)
	UI.text(display, "Monitor", 14, UI.MUTED)
	monitor = OptionButton.new()
	for index in range(DisplayServer.get_screen_count()):
		var dimensions = DisplayServer.screen_get_size(index)
		monitor.add_item("Pantalla %s  ·  %s × %s" % [index + 1, dimensions.x, dimensions.y])
	if monitor.item_count > 0:
		monitor.select(clampi(int(store.data["settings"].get("monitor", DisplayServer.window_get_current_screen())), 0, monitor.item_count - 1))
	else:
		monitor.add_item("Sin pantalla disponible")
		monitor.disabled = true
	display.add_child(monitor)
	UI.text(display, "Sin bordes ocupa todo el monitor, la resolución elegida se usa al jugar en ventana", 14, UI.GREEN, true)
	UI.action(display, "Probar estos ajustes", preview_display, true)
	var sound = UI.card(row, Color("eee5d0"))
	sound.get_parent().size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UI.heading(sound, "Con calma", "Audio")
	for spec in [["music_volume", "Música"], ["sfx_volume", "Sonidos"], ["narration_volume", "Voz de Marco"]]:
		var label = UI.text(sound, spec[1] + "  ·  %s%%" % roundi(float(store.data["settings"][spec[0]]) * 100), 15)
		var slider = HSlider.new()
		slider.min_value = 0
		slider.max_value = 1
		slider.step = 0.01
		slider.value = store.data["settings"][spec[0]]
		sound.add_child(slider)
		slider.value_changed.connect(func(value):
			var old = store.data["settings"][spec[0]]
			store.data["settings"][spec[0]] = value
			if not store.save():
				store.data["settings"][spec[0]] = old
				slider.set_value_no_signal(old)
				message.text = store.notice
			label.text = spec[1] + "  ·  %s%%" % roundi(float(store.data["settings"][spec[0]]) * 100)
			if audio != null: audio.apply_settings()
		)
	var voice = CheckBox.new()
	voice.text = "Escuchar las clases de Marco"
	voice.button_pressed = store.data["settings"]["narration_enabled"]
	sound.add_child(voice)
	voice.toggled.connect(func(value):
		var old = store.data["settings"]["narration_enabled"]
		store.data["settings"]["narration_enabled"] = value
		if not store.save():
			store.data["settings"]["narration_enabled"] = old
			voice.set_pressed_no_signal(old)
			message.text = store.notice
		if audio != null: audio.apply_settings()
	)
	UI.text(sound, "La voz se usa en las clases del profesor, puedes silenciarla y seguir leyendo a tu ritmo", 14, UI.MUTED, true)
	message = UI.text(self, "Los cambios de pantalla se revierten si no los confirmas", 14, UI.MUTED, true)

func preview_display() -> void:
	if seconds_left > 0: return
	previous = store.data["settings"].duplicate(true)
	proposed = previous.duplicate(true)
	proposed.merge({"screen_mode": MODES[mode.selected], "resolution": RESOLUTIONS[resolution.selected].duplicate(), "monitor": monitor.selected}, true)
	apply_window(proposed)
	seconds_left = 12
	preview = PanelContainer.new()
	preview.add_theme_stylebox_override("panel", UI.box(Color("e3d0a7"), 14, 18))
	add_child(preview)
	var column = VBoxContainer.new()
	preview.add_child(column)
	countdown = UI.text(column, "", 19, UI.INK, true)
	var actions = HBoxContainer.new()
	column.add_child(actions)
	UI.action(actions, "Conservar estos ajustes", confirm_display, true).grab_focus()
	UI.action(actions, "Volver a como estaba", revert_display)

func confirm_display() -> void:
	if seconds_left <= 0: return
	var old = store.data["settings"].duplicate(true)
	for key in ["screen_mode", "resolution", "monitor"]: store.data["settings"][key] = proposed[key]
	if not store.save():
		store.data["settings"] = old
		revert_display()
		message.text = store.notice
		return
	seconds_left = 0
	preview.queue_free()
	preview = null
	message.text = "Ajustes guardados"

func revert_display() -> void:
	if seconds_left <= 0: return
	apply_window(previous)
	seconds_left = 0
	if is_instance_valid(preview): preview.queue_free()
	preview = null
	message.text = "Volvimos a los ajustes anteriores"

func _process(delta: float) -> void:
	if seconds_left > 0:
		seconds_left = maxf(0, seconds_left - delta)
		countdown.text = "¿Se ve bien? Conserva estos ajustes o volveremos a los anteriores en %s segundos" % ceili(seconds_left)
		if seconds_left == 0:
			seconds_left = 0.01
			revert_display()
func _exit_tree() -> void:
	if seconds_left > 0: apply_window(previous)
