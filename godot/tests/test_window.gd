extends SceneTree
const Settings = preload("res://scripts/settings_view.gd")
var failures = []
func _initialize(): call_deferred("run")
func run():
	var screen = DisplayServer.window_get_current_screen()
	var actual = DisplayServer.screen_get_size(screen)
	Settings.apply_window({"screen_mode": "borderless", "monitor": screen, "resolution": [1280, 800]})
	await process_frame
	await process_frame
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_FULLSCREEN: failures.append("Sin bordes debe usar fullscreen del escritorio")
	if DisplayServer.window_get_size() != actual: failures.append("Sin bordes debe ocupar todo el monitor")
	Settings.apply_window({"screen_mode": "windowed", "monitor": screen, "resolution": [1280, 800]})
	await process_frame
	await process_frame
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED: failures.append("Volver a ventana")
	if DisplayServer.window_get_flag(DisplayServer.WINDOW_FLAG_BORDERLESS): failures.append("Recuperar los bordes")
	var store = preload("res://scripts/study_state.gd").new(ProjectSettings.globalize_path("res://../.preview/test-window").path_join(str(Time.get_ticks_usec())))
	store.new_run({"player_name": "Pantalla"})
	store.data["settings"]["monitor"] = screen
	var view = Settings.new()
	view.store = store
	root.add_child(view)
	view.mode.select(1)
	view.preview_display()
	if store.data["settings"]["screen_mode"] != "windowed": failures.append("La vista previa no debe guardar todavía")
	view.seconds_left = 0.1
	view._process(0.2)
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED or view.seconds_left > 0: failures.append("La cuenta atrás revierte automáticamente")
	view.mode.select(1)
	view.preview_display()
	view.confirm_display()
	var restored = preload("res://scripts/study_state.gd").new(store.directory)
	if restored.data["settings"]["screen_mode"] != "borderless": failures.append("Confirmar conserva el cambio al recargar")
	view.free()
	Settings.apply_window({"screen_mode": "windowed", "monitor": screen, "resolution": [1280, 800]})
	print(JSON.stringify({"module": "window", "monitor": [actual.x, actual.y], "window": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y], "failures": failures}))
	quit(0 if failures.is_empty() else 1)
