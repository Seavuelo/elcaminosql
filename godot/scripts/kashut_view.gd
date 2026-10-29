extends VBoxContainer

signal closed

const UI = preload("res://scripts/ui_kit.gd")
const Course = preload("res://scripts/course_data.gd")
const Figure = preload("res://scripts/learning_figure.gd")
const Table = preload("res://scripts/table_view.gd")
var store
var campaign
var audio
var day = 1
var answers: Array = []
var questions: Array = []
var remaining = 30.0
var duration = 30.0
var phase = "question"
var body: VBoxContainer
var timer: ProgressBar
var status: Label
var paused = false
var cooldown = 0.0

func _ready() -> void:
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	questions = Course.quiz(day)
	var record: Dictionary = campaign.progress()["quizzes"].get(str(day), {})
	answers = record.get("answers", []).duplicate()
	remaining = float(record.get("remaining", seconds(answers.size())))
	phase = "question" if answers.size() < questions.size() else "podium"
	body = VBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(body)
	show_phase()

func seconds(index: int) -> float:
	var item: Dictionary = questions[mini(index, questions.size() - 1)]
	var words = (item["question"] + " " + " ".join(item["options"])).split(" ").size()
	return minf(45, 25 + maxf(0, words - 25) * 0.5)

func clear_body() -> void:
	for child in body.get_children():
		body.remove_child(child)
		child.queue_free()

func show_phase() -> void:
	clear_body()
	if phase == "podium":
		show_podium()
	elif phase == "review":
		show_review()
	else:
		show_question()

func show_question() -> void:
	var index = answers.size()
	duration = seconds(index)
	remaining = minf(remaining, duration)
	var header = HBoxContainer.new()
	body.add_child(header)
	UI.text(header, "PREGUNTA %s DE %s" % [index + 1, questions.size()], 13, UI.COPPER)
	UI.fill(header)
	status = UI.text(header, "", 14, UI.MUTED)
	UI.action(header, "Reanudar reloj" if paused else "Pausar reloj", func(): paused = not paused; show_phase())
	timer = ProgressBar.new()
	timer.max_value = duration
	timer.value = remaining
	timer.custom_minimum_size.y = 7
	timer.show_percentage = false
	body.add_child(timer)
	var question = UI.text(body, questions[index]["question"], 29, UI.GREEN, true)
	question.add_theme_font_override("font", UI.weight(UI.TITLE, 600))
	UI.fill(body, true)
	var choices = GridContainer.new()
	choices.columns = 2
	choices.add_theme_constant_override("h_separation", 14)
	choices.add_theme_constant_override("v_separation", 14)
	body.add_child(choices)
	var colors = [Color("dce8d0"), Color("efdbbb"), Color("dce7e5"), Color("e9d6cd")]
	for i in range(questions[index]["options"].size()):
		var button = UI.action(choices, str(i + 1) + "  ·  " + questions[index]["options"][i], answer.bind(i))
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.custom_minimum_size = Vector2(0, 104)
		button.add_theme_font_size_override("font_size", 19)
		button.add_theme_stylebox_override("normal", UI.box(colors[i % colors.size()], 14, 20))
	UI.fill(body, true)
	UI.text(body, "El podio depende de tus aciertos, puedes leer con calma y pausar el reloj", 14, UI.MUTED, true)

func answer(value: int) -> void:
	if phase != "question" or cooldown > 0 or answers.size() >= questions.size():
		return
	answers.append(value)
	cooldown = 0.25
	if audio != null:
		audio.sfx("key")
	if answers.size() == questions.size():
		phase = "podium"
		campaign.record_quiz(answers)
	else:
		remaining = seconds(answers.size())
	persist()
	show_phase()

func score() -> int:
	var correct = 0
	for index in range(answers.size()):
		if int(answers[index]) == int(questions[index]["answer"]):
			correct += 1
	return correct

func show_podium() -> void:
	var total = score()
	var rank = 1 if total == 10 else 2 if total >= 8 else 3 if total >= 7 else 0
	UI.heading(body, "Fin del Kashut", "¡Primer lugar!" if rank == 1 else "¡Estás en el podio!" if rank > 0 else "Una oportunidad para entender más", "%s respuestas correctas de %s" % [total, questions.size()])
	var podium = HBoxContainer.new()
	podium.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(podium)
	var names = ["Moshi", "Sofía", "Carlos", "Matías"]
	var scores = [9, 8, 6, 5] if total == 10 else [10, 7, 6, 5] if total >= 8 else [10, 9, 6, 5] if total == 7 else [10, 9, 7, 6]
	var ranking = []
	for i in range(names.size()):
		ranking.append({"name": names[i], "score": scores[i], "player": false})
	ranking.append({"name": store.data["player_name"], "score": total, "player": true})
	ranking.sort_custom(func(a, b): return a["score"] > b["score"] if a["score"] != b["score"] else not a["player"])
	for place in [1, 0, 2]:
		var wrapper = VBoxContainer.new()
		wrapper.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		podium.add_child(wrapper)
		UI.fill(wrapper, true)
		var card = UI.card(wrapper, Color("ead5a3") if place == 0 else Color("e1e5d7"))
		card.get_parent().custom_minimum_size.y = 230 if place == 0 else 185 if place == 1 else 155
		UI.text(card, str(place + 1), 35, UI.GREEN).horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		UI.text(card, ranking[place]["name"], 23, UI.INK, true).horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		UI.text(card, "%s aciertos" % ranking[place]["score"], 15, UI.MUTED).horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.text(body, "XP total de este día: %s" % int(Course.all()["kashut_rewards"][int(campaign.quiz_record().get("best", total))]), 15, UI.GREEN)
	UI.action(body, "Salir del Kashut" if total == 10 else "Revisar mis respuestas", func():
		if total == 10:
			campaign.review_quiz()
			closed.emit()
		else:
			phase = "review"
			show_phase(), true)
	UI.action(body, "Volver a practicar", restart)
	UI.text(body, "Mejorar tu mejor puntaje entrega la diferencia de XP, repetir el mismo resultado no suma más", 13, UI.MUTED, true)
	if audio != null and rank > 0:
		audio.sfx("success")
		celebrate(rank == 1)

func celebrate(first: bool) -> void:
	var particles = CPUParticles2D.new()
	particles.position = Vector2(size.x * 0.5, 80)
	particles.amount = 70 if first else 35
	particles.one_shot = true
	particles.explosiveness = 1
	particles.lifetime = 2.0
	particles.direction = Vector2.UP
	particles.spread = 110
	particles.gravity = Vector2(0, 240)
	particles.initial_velocity_min = 110
	particles.initial_velocity_max = 220
	particles.scale_amount_min = 2
	particles.scale_amount_max = 5
	particles.color = UI.GOLD
	body.add_child(particles)
	particles.emitting = true

func show_review() -> void:
	UI.heading(body, "Lo que nos llevamos", "Entender vale más que adivinar")
	var list = UI.scroll(body)
	for index in range(questions.size()):
		if int(answers[index]) == int(questions[index]["answer"]):
			continue
		var question: Dictionary = questions[index]
		var card = UI.card(list, Color("ede7d6"))
		UI.text(card, "%s  ·  %s" % [index + 1, question["question"]], 20, UI.GREEN, true)
		UI.text(card, "Tu respuesta: " + (question["options"][int(answers[index])] if int(answers[index]) >= 0 else "Sin respuesta"), 15, UI.RED, true)
		UI.text(card, "Respuesta: " + question["options"][int(question["answer"])], 17, UI.GREEN, true)
		UI.text(card, question["feedback"], 17, UI.INK, true)
		var figure = Figure.new()
		figure.kind = question["diagram"]
		card.add_child(figure)
	UI.action(body, "Ya lo revisé", func(): campaign.review_quiz(); closed.emit(), true)

func restart() -> void:
	answers = []
	phase = "question"
	remaining = seconds(0)
	show_phase()
	persist()

func persist() -> void:
	var record: Dictionary = campaign.progress()["quizzes"].get(str(day), {"best": 0, "xp_granted": 0, "reviewed": false})
	record["answers"] = answers.duplicate()
	record["remaining"] = remaining
	if answers.size() < questions.size():
		record["reviewed"] = false
	campaign.progress()["quizzes"][str(day)] = record
	store.save()

func _process(delta: float) -> void:
	cooldown = maxf(0, cooldown - delta)
	if phase == "question" and not paused:
		remaining = maxf(0, remaining - delta)
		if is_instance_valid(timer):
			timer.value = remaining
			status.text = "%s s" % ceili(remaining)
		if remaining <= 0:
			answer(-1)

func _unhandled_key_input(event: InputEvent) -> void:
	if phase == "question" and event is InputEventKey and event.pressed and not event.echo:
		if event.keycode >= KEY_1 and event.keycode <= KEY_4:
			answer(event.keycode - KEY_1)
			get_viewport().set_input_as_handled()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		paused = true

func _exit_tree() -> void:
	persist()
