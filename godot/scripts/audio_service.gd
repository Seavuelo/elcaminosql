extends Node

signal speech_changed(index: int)
signal narration_finished

var store
var music: AudioStreamPlayer
var voice: AudioStreamPlayer
var effects: AudioStreamPlayer
var context = ""
var parts: Array = []
var part_index = 0
var active = true

func _ready() -> void:
	add_to_group("game_audio")
	music = AudioStreamPlayer.new()
	voice = AudioStreamPlayer.new()
	effects = AudioStreamPlayer.new()
	add_child(music)
	add_child(voice)
	add_child(effects)
	voice.finished.connect(next_part)
	apply_settings()

func apply_settings() -> void:
	if music == null:
		return
	var settings: Dictionary = store.data["settings"]
	music.volume_db = linear_to_db(maxf(0.00001, float(settings["music_volume"]) * (0.3 if voice.playing else 1.0)))
	voice.volume_db = linear_to_db(maxf(0.00001, float(settings["narration_volume"])))
	effects.volume_db = linear_to_db(maxf(0.00001, float(settings["sfx_volume"])))
	if not settings["narration_enabled"]:
		voice.stop()

func set_context(value: String) -> void:
	if value == context:
		return
	context = value
	var tracks = {"menu": "bathroom_chill_loop.ogg", "study": "alex_morgan_jazz_loop.ogg", "exam": "a_kind_of_hope.mp3"}
	var stream = load("res://assets/music/" + tracks.get(value, tracks["study"]))
	if stream == null:
		return
	stream.loop = true
	music.stream = stream
	music.play()
	apply_settings()

func speak(items: Array, start: int = 0) -> void:
	stop_voice()
	parts = items.duplicate(true)
	part_index = clampi(start, 0, maxi(0, parts.size() - 1))
	play_part()

func play_part() -> void:
	if parts.is_empty() or not store.data["settings"]["narration_enabled"]:
		return
	if part_index >= parts.size():
		stop_voice()
		narration_finished.emit()
		return
	voice.stream = load(parts[part_index]["audio"])
	if voice.stream == null:
		next_part()
		return
	voice.play()
	voice.stream_paused = not active
	speech_changed.emit(part_index)
	apply_settings()

func next_part() -> void:
	part_index += 1
	play_part()

func stop_voice() -> void:
	if voice != null:
		voice.stop()
	parts.clear()
	apply_settings()

func pause(value: bool) -> void:
	active = not value
	if voice != null:
		voice.stream_paused = value

func sfx(name: String = "key") -> void:
	var stream = load("res://assets/sfx/" + name + ".wav")
	if stream != null:
		effects.stream = stream
		effects.play()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		pause(true)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		pause(false)

func _exit_tree() -> void:
	for player in [music, voice, effects]:
		if is_instance_valid(player):
			player.stop()
			player.stream = null
	parts.clear()
