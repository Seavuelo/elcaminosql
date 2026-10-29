extends SceneTree
const SQL = preload("res://scripts/school_sql.gd")
const Course = preload("res://scripts/course_data.gd")
func _initialize() -> void:
	var folder = ProjectSettings.globalize_path("res://../.preview/test-school-sql")
	DirAccess.make_dir_recursive_absolute(folder)
	var history = []
	var count = 0
	var failures = []
	for year in range(1, 5):
		for day in range(1, 5):
			var list = Course.tasks(year, day)
			for index in range(list.size()):
				var id = "%s_%s_%s" % [year, day, index]
				var result = SQL.evaluate({"query": list[index]["sql"], "task_id": id, "history": history}, folder.path_join(id))
				if not result.get("ok", false) or not result.get("correct", false):
					failures.append({"id": id, "result": result})
				if list[index]["is_write"]:
					history.append(id)
				count += 1
	for year in range(1, 5):
		var list = Course.exams(year)
		for index in range(list.size()):
			var id = "exam_%s_1_%s" % [year, index]
			var result = SQL.evaluate({"query": list[index]["sql"], "task_id": id, "history": history}, folder.path_join(id))
			if not result.get("ok", false) or not result.get("correct", false):
				failures.append({"id": id, "result": result})
			if list[index]["is_write"]:
				history.append(id)
			count += 1
	for query in ["UPDATE estudiante SET nombre='x'", "DELETE FROM estudiante", "PRAGMA database_list", "ATTACH DATABASE 'x' AS x", "SELECT 1; DELETE FROM estudiante", "SELECT load_extension('x')"]:
		var result = SQL.evaluate({"query": query, "task_id": "1_1_0", "history": []}, folder.path_join("protected"))
		if result.get("ok", false): failures.append({"unsafe": query})
		count += 1
	print(JSON.stringify({"module": "school_sql", "checks": count, "failures": failures}))
	quit(0 if failures.is_empty() else 1)
