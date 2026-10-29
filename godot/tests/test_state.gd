extends SceneTree
const State = preload("res://scripts/study_state.gd")
var failures = []
func _initialize():
	var folder = ProjectSettings.globalize_path("res://../.preview/test-state").path_join(str(Time.get_ticks_usec()))
	var store = State.new(folder)
	store.new_run({"player_name":"Guardado"})
	var valid = store.data.duplicate(true)
	for pair in [["activities", {"completed": "filtro"}], ["activities", {"investigations": []}], ["activities", {"investigations": {"reservas": {"read": [], "diagnosed": 1}}}], ["activities", {"investigations": {"reservas": {"read": [7], "diagnosed": true}}}], ["career", {"defended": "sí"}], ["career", {"project": []}], ["career", {"choice": 1}], ["furniture_level", {"bed": 7}], ["relationships", {"moshi": -1}], ["nexo", {"onboarded": 1}]]:
		var damaged = valid.duplicate(true)
		damaged[pair[0]] = pair[1]
		if store.valid(damaged): failures.append(pair[0])
	if not store.valid(valid): failures.append("La partida válida fue rechazada")
	print(JSON.stringify({"module":"state","checks":11,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
