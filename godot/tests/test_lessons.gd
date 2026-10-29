extends SceneTree
const Course = preload("res://scripts/course_data.gd")
var app
var failures = []
var speeches = 0
func _initialize(): call_deferred("run")
func run():
	app = load("res://scenes/main.tscn").instantiate()
	root.add_child(app)
	current_scene = app
	app.state.new_run({"player_name": "Clases"})
	app.enter_world()
	for year in range(5):
		for day in range(1,6):
			app.show_lecture(year,day)
			var view = app.lecture_view
			for index in range(view.boards.size()):
				view.index = index
				view.show_board()
				var parts = view.boards[index]["speech_parts"]
				for part in range(parts.size()):
					if not ResourceLoader.exists(parts[part]["audio"]): failures.append("Falta voz " + parts[part]["audio"])
					view.on_speech_changed(part)
					if view.speech.text != parts[part]["text"]: failures.append("Subtítulo fuera de sincronía")
					speeches += 1
				await process_frame
			view.transcript = true
			view.update_caption()
			if view.speech.text.is_empty(): failures.append("Transcripción vacía")
	app.free()
	await create_timer(0.15).timeout
	print(JSON.stringify({"module": "lessons", "classes":25,"speeches":speeches,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
