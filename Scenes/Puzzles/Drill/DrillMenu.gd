extends Control
## Lists every harvested drill batch (Data/PuzzlePacks) as a button; picking one plays it in BatchDrill.
## Run this scene with F6. Old-style packs without a batch id are listed under "Other packs".

const DRILL_SCENE := "res://Scenes/Puzzles/Drill/BatchDrill.tscn"

func _ready():
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Color("1c1e2e")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 8)
	add_child(margin)
	var column := VBoxContainer.new()
	margin.add_child(column)

	var title := Label.new()
	title.text = "Puzzle drills"
	title.add_theme_color_override("font_color", Color("f0c450"))
	column.add_child(title)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	var ids: Array = PuzzleManager.get_batches()
	for id in ids:
		_add_button(list, _label(String(id).to_upper() + "  " + PuzzleManager.get_batch_title(id), id, PuzzleManager.get_batch(id).size()), id)

	var others := []
	for theme in PuzzleManager.get_all_themes():
		var puzzles: Array = PuzzleManager.get_puzzles_by_theme(theme)
		if puzzles.size() > 0 and puzzles[0].get("batch", "") == "" and theme != "":
			others.append([theme, puzzles.size()])
	if others.size() > 0:
		var header := Label.new()
		header.text = "Other packs"
		header.add_theme_color_override("font_color", Color("9a9eb6"))
		list.add_child(header)
		for o in others:
			_add_button(list, _label(o[0], o[0], o[1]), o[0])

	if ids.is_empty() and others.is_empty():
		var none := Label.new()
		none.text = "No puzzles found. Put the harvested .json files in res://Data/PuzzlePacks."
		none.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		none.custom_minimum_size = Vector2(440, 0)
		list.add_child(none)

	var back := Button.new()
	back.text = "Back"
	back.pressed.connect(func(): GameManager.go_to_world())
	column.add_child(back)

# "Title  (12/50)" when the player has already made progress in this batch
func _label(title: String, id: String, total: int) -> String:
	var done := int(GameState.drill_progress.get(id, 0))
	if done > 0 and done < total:
		return "%s  (%d/%d)" % [title, done, total]
	return "%s  (%d)" % [title, total]

func _add_button(parent: Node, text: String, batch_id: String):
	var b := Button.new()
	b.text = text
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.pressed.connect(func():
		GameState.set_meta("drill_batch", batch_id)
		GameManager.go_to_scene(DRILL_SCENE))
	parent.add_child(b)
