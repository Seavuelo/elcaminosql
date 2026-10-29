extends Node

signal finished(result: Dictionary)
var pid = -1
var request_path = ""
var elapsed = 0.0
var directory = "user://"
var timeout_seconds = 5.0

func start(query: String) -> bool:
	return start_job({"query": query})

func start_job(payload: Dictionary) -> bool:
	if pid > 0:
		return false
	var folder = ProjectSettings.globalize_path(directory)
	if DirAccess.make_dir_recursive_absolute(folder) != OK:
		finished.emit({"ok": false, "error": "No se pudo preparar la consulta temporal"})
		return false
	request_path = folder.path_join("sql-%s-%s.json" % [OS.get_process_id(), Time.get_ticks_usec()])
	var request = FileAccess.open(request_path, FileAccess.WRITE)
	if request == null:
		finished.emit({"ok": false, "error": "No se pudo escribir la consulta temporal"})
		return false
	request.store_string(JSON.stringify(payload))
	request.close()
	var args = PackedStringArray(["--headless", "--audio-driver", "Dummy"])
	if OS.has_feature("editor"):
		args.append_array(["--path", ProjectSettings.globalize_path("res://")])
	args.append_array(["--", "--sql-worker", request_path])
	pid = OS.create_process(OS.get_executable_path(), args, false)
	elapsed = 0
	if pid <= 0:
		cleanup()
		finished.emit({"ok": false, "error": "No se pudo iniciar SQLite"})
		return false
	return true

func _process(delta: float) -> void:
	if pid <= 0:
		return
	elapsed += delta
	if not OS.is_process_running(pid):
		var result = JSON.parse_string(FileAccess.get_file_as_string(request_path + ".result")) if FileAccess.file_exists(request_path + ".result") else null
		cleanup()
		finished.emit(result if result is Dictionary else {"ok": false, "error": "SQLite no pudo terminar la consulta"})
	elif elapsed >= timeout_seconds:
		cleanup()
		finished.emit({"ok": false, "error": "La consulta superó los cinco segundos, simplifica los cálculos o los JOIN"})

func cleanup() -> void:
	if pid > 0 and OS.is_process_running(pid):
		OS.kill(pid)
	pid = -1
	for suffix in ["", ".result", ".baseline.db", ".baseline.db-journal"]:
		if not request_path.is_empty() and FileAccess.file_exists(request_path + suffix):
			DirAccess.remove_absolute(request_path + suffix)

func _exit_tree() -> void:
	cleanup()
