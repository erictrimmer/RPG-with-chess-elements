extends CanvasLayer
## Battle screen UI for the 480x270 viewport.
##
##   left   : players, move list in algebraic notation, Save Game (PGN) / Open Folder
##   centre : the board (drawn by board.gd)
##   right  : opponent portrait, name plate and a text bubble (Punch-Out style between-round chatter)
##
## Public API used by BattleController and the puzzle tutorials is unchanged:
## show_message, hide_message, set_instruction, update_pgn, update_status, enable/disable_buttons,
## show/hide_promotion_dialog, and the signals draw_requested, resign_requested, promotion_selected.
## New: save_requested, set_opponent, set_players, say, show_save_result, set_save_enabled,
## set_player_is_white.

signal draw_requested
signal resign_requested
signal save_requested
signal promotion_selected(piece_type: String)
signal choice_selected(id: String)   # a button from show_choices() was pressed

const PORTRAIT_FALLBACK := "res://Assets/UI/portrait_placeholder.png"
const PIECE_DIR := "res://Assets/Sprites/pieces_staunton/"
const GUIDE_NAME := "Guide"

# Layout (viewport 480x270)
const LEFT_X := 6
const PANEL_W := 132
const RIGHT_X := 342
const PANEL_Y := 30
const PANEL_H := 210
const BUBBLE_H := 84        # opponent text bubble height
const PORTRAIT_REST_Y := 3.0

var pgn_label: RichTextLabel
var status_label: Label
var draw_btn: Button
var resign_btn: Button
var save_btn: Button
var open_folder_btn: Button
var save_status_label: Label
var white_label: Label
var black_label: Label
var instruction_label: Label   # kept for compatibility; puzzle instructions are shown in the bubble
var message_panel: Panel
var message_label: Label
var choice_panel: Panel
var choice_box: VBoxContainer
var _choices_are_next := false
var promotion_panel: Panel
var promotion_buttons: Array[Button] = []
var portrait_rect: TextureRect
var name_label: Label
var bubble_panel: Panel
var bubble_label: Label

var _speak_tween: Tween
var _bounce_tween: Tween
var _saved_dir: String = ""
var _player_is_white: bool = true
var _opponent_set: bool = false

func _ready() -> void:
	_build_backdrop()
	_build_left_panel()
	_build_right_panel()
	_build_top_and_bottom_bars()
	_setup_message_overlay()
	_setup_promotion_dialog()
	# Without a configured opponent (puzzles) the right column shows the guide.
	if not _opponent_set:
		set_opponent(GUIDE_NAME, null)

# ---------------------------------------------------------------- building

func _build_backdrop() -> void:
	var bg_layer := CanvasLayer.new()
	bg_layer.layer = -10
	add_child(bg_layer)
	bg_layer.add_child(BattleBackdrop.new())

func _panel(pos: Vector2, size: Vector2) -> Panel:
	var p := Panel.new()
	p.position = pos
	p.size = size
	p.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.PANEL, BattleTheme.PANEL_EDGE, 2, 4))
	add_child(p)
	return p

func _small_label(text: String, pos: Vector2, size: Vector2, color: Color = BattleTheme.TEXT, parent: Node = null) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = size
	l.label_settings = BattleTheme.label_settings(BattleTheme.FONT_SMALL, color)
	(parent if parent else self).add_child(l)
	return l

func _build_left_panel() -> void:
	var panel := _panel(Vector2(LEFT_X, PANEL_Y), Vector2(PANEL_W, PANEL_H))

	white_label = _small_label("White: -", Vector2(6, 4), Vector2(PANEL_W - 12, 12), BattleTheme.TEXT, panel)
	black_label = _small_label("Black: -", Vector2(6, 16), Vector2(PANEL_W - 12, 12), BattleTheme.TEXT_DIM, panel)
	white_label.clip_text = true
	white_label.visible = false   # shown by set_players (bot games only)
	black_label.visible = false
	black_label.clip_text = true

	var notation_bg := Panel.new()
	notation_bg.position = Vector2(4, 32)
	notation_bg.size = Vector2(PANEL_W - 8, 80)
	notation_bg.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.BG, BattleTheme.FRAME, 1, 2))
	panel.add_child(notation_bg)

	pgn_label = RichTextLabel.new()
	pgn_label.position = Vector2(2, 2)
	pgn_label.size = Vector2(PANEL_W - 12, 76)
	pgn_label.bbcode_enabled = true
	pgn_label.scroll_active = true
	pgn_label.fit_content = false
	pgn_label.add_theme_font_size_override("normal_font_size", BattleTheme.FONT_BODY)
	pgn_label.add_theme_font_size_override("bold_font_size", BattleTheme.FONT_BODY)
	pgn_label.add_theme_color_override("default_color", BattleTheme.TEXT)
	notation_bg.add_child(pgn_label)

	save_btn = Button.new()
	save_btn.text = "Save game (PGN)"
	save_btn.position = Vector2(4, 118)
	BattleTheme.style_button(save_btn)
	save_btn.set_deferred("size", Vector2(PANEL_W - 8, 20))   # after the theme overrides are in effect
	save_btn.pressed.connect(func(): save_requested.emit())
	panel.add_child(save_btn)

	open_folder_btn = Button.new()
	open_folder_btn.text = "Open folder"
	open_folder_btn.position = Vector2(4, 140)
	open_folder_btn.visible = false
	BattleTheme.style_button(open_folder_btn)
	open_folder_btn.set_deferred("size", Vector2(PANEL_W - 8, 20))   # after the theme overrides are in effect
	open_folder_btn.pressed.connect(_on_open_folder_pressed)
	panel.add_child(open_folder_btn)

	save_status_label = _small_label("", Vector2(4, 164), Vector2(PANEL_W - 8, 42), BattleTheme.TEXT_DIM, panel)
	save_status_label.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY

func _build_right_panel() -> void:
	# Portrait frame
	var frame := _panel(Vector2(RIGHT_X, PANEL_Y), Vector2(PANEL_W, 102))
	portrait_rect = TextureRect.new()
	portrait_rect.position = Vector2((PANEL_W - 96) / 2.0, PORTRAIT_REST_Y)
	portrait_rect.size = Vector2(96, 96)
	portrait_rect.custom_minimum_size = Vector2(96, 96)
	portrait_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	frame.add_child(portrait_rect)

	# Name plate
	var plate := _panel(Vector2(RIGHT_X, PANEL_Y + 104), Vector2(PANEL_W, 18))
	plate.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.FRAME, BattleTheme.PANEL_EDGE, 1, 2))
	name_label = _small_label("", Vector2(0, 2), Vector2(PANEL_W, 14), BattleTheme.ACCENT, plate)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	# Bubble
	bubble_panel = Panel.new()
	bubble_panel.position = Vector2(RIGHT_X, PANEL_Y + 130)
	bubble_panel.size = Vector2(PANEL_W, BUBBLE_H)
	bubble_panel.clip_contents = false
	bubble_panel.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.BUBBLE_FILL, BattleTheme.BUBBLE_EDGE, 2, 5))
	add_child(bubble_panel)

	var tail_fill := Polygon2D.new()
	tail_fill.polygon = PackedVector2Array([Vector2(22, 2), Vector2(30, -6), Vector2(38, 2)])
	tail_fill.color = BattleTheme.BUBBLE_FILL
	bubble_panel.add_child(tail_fill)
	var tail_edge := Line2D.new()
	tail_edge.points = PackedVector2Array([Vector2(22, 1), Vector2(30, -7), Vector2(38, 1)])
	tail_edge.width = 2.0
	tail_edge.default_color = BattleTheme.BUBBLE_EDGE
	tail_edge.antialiased = false
	bubble_panel.add_child(tail_edge)

	bubble_label = Label.new()
	bubble_label.position = Vector2(6, 6)
	bubble_label.size = Vector2(PANEL_W - 12, BUBBLE_H - 12)
	bubble_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	bubble_label.clip_text = true
	bubble_label.label_settings = BattleTheme.label_settings(BattleTheme.FONT_BODY, BattleTheme.BUBBLE_TEXT)
	bubble_label.label_settings.line_spacing = -3.0
	bubble_panel.add_child(bubble_label)
	bubble_panel.visible = false

func _build_top_and_bottom_bars() -> void:
	# Status line above the board
	status_label = Label.new()
	status_label.text = "White to Move"
	status_label.position = Vector2(144, 5)
	status_label.size = Vector2(192, 14)
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.clip_text = true
	status_label.label_settings = BattleTheme.label_settings(BattleTheme.FONT_BODY, BattleTheme.TEXT)
	add_child(status_label)

	# Compatibility: some scripts read/write instruction_label directly. It is not displayed.
	instruction_label = Label.new()
	instruction_label.visible = false
	add_child(instruction_label)

	draw_btn = Button.new()
	draw_btn.text = "Draw"
	draw_btn.position = Vector2(RIGHT_X, 247)
	BattleTheme.style_button(draw_btn)
	draw_btn.set_deferred("size", Vector2(60, 18))   # after the theme overrides are in effect
	draw_btn.visible = false   # hidden by default (puzzles)
	draw_btn.pressed.connect(func(): draw_requested.emit())
	add_child(draw_btn)

	resign_btn = Button.new()
	resign_btn.text = "Give up"
	resign_btn.position = Vector2(RIGHT_X + 66, 247)
	BattleTheme.style_button(resign_btn)
	resign_btn.set_deferred("size", Vector2(66, 18))   # after the theme overrides are in effect
	resign_btn.pressed.connect(func(): resign_requested.emit())
	add_child(resign_btn)

func _setup_message_overlay() -> void:
	# Messages are spoken in the side bubble, never drawn over the board. message_panel/message_label are
	# kept (hidden) so scripts that read message_label.text keep working.
	message_panel = Panel.new()
	message_panel.visible = false
	add_child(message_panel)
	message_label = Label.new()
	message_panel.add_child(message_label)

	# Choice buttons (Next puzzle, menu options) sit in the left column below the notation.
	choice_panel = Panel.new()
	choice_panel.visible = false
	choice_panel.position = Vector2(LEFT_X + 4, PANEL_Y + 116)
	choice_panel.size = Vector2(PANEL_W - 8, 90)
	choice_panel.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.PANEL, BattleTheme.ACCENT, 2, 4))
	add_child(choice_panel)
	choice_box = VBoxContainer.new()
	choice_box.position = Vector2(4, 4)
	choice_box.size = Vector2(PANEL_W - 16, 82)
	choice_box.add_theme_constant_override("separation", 3)
	choice_panel.add_child(choice_box)

func _setup_promotion_dialog() -> void:
	promotion_panel = Panel.new()
	promotion_panel.visible = false
	promotion_panel.position = Vector2(134, 100)
	promotion_panel.size = Vector2(212, 70)
	promotion_panel.add_theme_stylebox_override("panel", BattleTheme.box(BattleTheme.PANEL, BattleTheme.ACCENT, 2, 6))
	add_child(promotion_panel)

	var title := _small_label("Promote to:", Vector2(0, 4), Vector2(212, 12), BattleTheme.TEXT, promotion_panel)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	var hbox := HBoxContainer.new()
	hbox.position = Vector2(8, 22)
	hbox.size = Vector2(196, 40)
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox.add_theme_constant_override("separation", 6)
	promotion_panel.add_child(hbox)

	for code in ["Q", "R", "B", "N"]:
		var btn := Button.new()
		btn.custom_minimum_size = Vector2(40, 38)
		btn.expand_icon = false
		btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		btn.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		BattleTheme.style_button(btn)
		btn.pressed.connect(func(): _on_promotion_selected(code))
		hbox.add_child(btn)
		promotion_buttons.append(btn)
	_refresh_promotion_icons()

# ---------------------------------------------------------------- players, opponent, bubble

## Which side the human plays (affects the colour of the promotion pieces).
func set_player_is_white(is_white: bool) -> void:
	_player_is_white = is_white
	_refresh_promotion_icons()

func _refresh_promotion_icons() -> void:
	var prefix := "w" if _player_is_white else "b"
	var kinds := ["q", "r", "b", "n"]
	for i in promotion_buttons.size():
		var path: String = PIECE_DIR + prefix + kinds[i] + ".png"
		if ResourceLoader.exists(path):
			promotion_buttons[i].icon = load(path)
		else:
			promotion_buttons[i].text = kinds[i].to_upper()

func set_players(white_name: String, black_name: String) -> void:
	white_label.visible = true
	black_label.visible = true
	white_label.text = "White: " + white_name
	black_label.text = "Black: " + black_name

func set_opponent(display_name: String, avatar: Texture2D) -> void:
	_opponent_set = true
	name_label.text = display_name
	if avatar:
		portrait_rect.texture = avatar
	elif ResourceLoader.exists(PORTRAIT_FALLBACK):
		portrait_rect.texture = load(PORTRAIT_FALLBACK)

## Shows a line in the opponent's text bubble with a typewriter effect. "" hides the bubble.
func say(text: String) -> void:
	if _speak_tween and _speak_tween.is_valid():
		_speak_tween.kill()
	if text == "":
		bubble_panel.visible = false
		return
	bubble_panel.visible = true
	bubble_label.text = text
	# Long lines (tutorial instructions) get a smaller font so they always fit
	bubble_label.label_settings.font_size = 10 if text.length() <= 90 else (9 if text.length() <= 120 else 8)
	bubble_label.visible_ratio = 0.0
	var duration: float = clampf(text.length() * 0.022, 0.3, 3.0)
	_speak_tween = create_tween()
	_speak_tween.tween_property(bubble_label, "visible_ratio", 1.0, duration)
	_bounce_portrait(duration)

func _bounce_portrait(duration: float) -> void:
	if _bounce_tween and _bounce_tween.is_valid():
		_bounce_tween.kill()
	var rest_y := PORTRAIT_REST_Y
	portrait_rect.position.y = rest_y
	_bounce_tween = create_tween()
	var beats := int(duration / 0.16)
	for i in beats:
		_bounce_tween.tween_property(portrait_rect, "position:y", rest_y - 2.0, 0.08)
		_bounce_tween.tween_property(portrait_rect, "position:y", rest_y, 0.08)
	_bounce_tween.tween_property(portrait_rect, "position:y", rest_y, 0.01)

# ---------------------------------------------------------------- notation and saving

# Accepts the BattleController history text: "1. e4 e5\n2. Nf3 Nc6\n3. Bb5 " and draws it as a table.
func update_pgn(history_text: String) -> void:
	var rows: Array = []
	for line in history_text.split("\n", false):
		var tokens: PackedStringArray = line.strip_edges().split(" ", false)
		if tokens.size() < 2:
			continue
		rows.append(tokens)
	var bb := ""
	if rows.size() > 0:
		bb = "[table=3]"
		for i in rows.size():
			var t: PackedStringArray = rows[i]
			var is_last: bool = (i == rows.size() - 1)
			bb += "[cell][color=#%s]%s[/color]  [/cell]" % [BattleTheme.TEXT_DIM.to_html(false), t[0].trim_suffix("...") + "."]
			var cells: Array = []
			if t[0].ends_with("..."):
				cells = ["...", t[1] if t.size() > 1 else ""]   # Black moved first: "1... e5"
			else:
				cells = [t[1] if t.size() > 1 else "", t[2] if t.size() > 2 else ""]
			for j in 2:
				var mv: String = cells[j]
				var is_latest: bool = is_last and mv != "" and mv != "..." and (j == 1 or cells[1] == "")
				var col := BattleTheme.ACCENT if is_latest else BattleTheme.TEXT
				bb += "[cell][color=#%s]%s[/color]  [/cell]" % [col.to_html(false), mv]
		bb += "[/table]"
	pgn_label.text = bb
	call_deferred("_scroll_notation_to_end")

func _scroll_notation_to_end() -> void:
	var bar := pgn_label.get_v_scroll_bar()
	if bar:
		bar.value = bar.max_value

func set_save_enabled(enabled: bool) -> void:
	save_btn.visible = enabled
	if not enabled:
		open_folder_btn.visible = false
		save_status_label.text = ""

## Called by BattleController after trying to write the PGN. On success `info` is the absolute
## file path; on failure it is an error message.
func show_save_result(ok: bool, info: String) -> void:
	if ok:
		_saved_dir = info.get_base_dir()
		save_status_label.text = "Saved:\n" + info.get_file()
		save_status_label.add_theme_color_override("font_color", BattleTheme.ACCENT)
		open_folder_btn.visible = true
	else:
		save_status_label.text = info
		save_status_label.add_theme_color_override("font_color", Color8(240, 120, 120))

func _on_open_folder_pressed() -> void:
	if _saved_dir != "":
		OS.shell_open(_saved_dir)

# ---------------------------------------------------------------- promotion, messages, status

func _on_promotion_selected(piece: String) -> void:
	promotion_panel.visible = false
	promotion_selected.emit(piece)

func show_promotion_dialog() -> void:
	promotion_panel.visible = true
	promotion_panel.move_to_front()

func hide_promotion_dialog() -> void:
	promotion_panel.visible = false

func show_message(text: String, show_next_button: bool = false) -> void:
	message_label.text = text
	say(text)
	if show_next_button:
		show_choices([["next", "Next"]])
		_choices_are_next = true

func hide_message() -> void:
	if _choices_are_next:
		hide_choices()

## Shows a column of buttons in the left panel. options = [[id, label], ...]. Pressing one hides the
## column and emits choice_selected(id). The id "next" also emits the old next_puzzle_requested signal.
func show_choices(options: Array) -> void:
	for child in choice_box.get_children():
		child.queue_free()
	_choices_are_next = false
	for o in options:
		var btn := Button.new()
		btn.text = o[1]
		btn.custom_minimum_size = Vector2(PANEL_W - 16, 22)
		BattleTheme.style_button(btn)
		var id: String = o[0]
		btn.pressed.connect(func(): _on_choice_pressed(id))
		choice_box.add_child(btn)
	choice_panel.visible = true
	choice_panel.move_to_front()

func hide_choices() -> void:
	choice_panel.visible = false
	_choices_are_next = false

func _on_choice_pressed(id: String) -> void:
	hide_choices()
	choice_selected.emit(id)
	if id == "next" and has_user_signal("next_puzzle_requested"):
		emit_signal("next_puzzle_requested")

## Puzzle/tutorial instructions appear in the bubble, spoken by the guide.
func set_instruction(text: String) -> void:
	instruction_label.text = text
	if text != "":
		say(text)

func update_status(text: String) -> void:
	status_label.text = text

func disable_buttons() -> void:
	draw_btn.disabled = true
	resign_btn.disabled = true

func enable_buttons() -> void:
	draw_btn.disabled = false
	resign_btn.disabled = false
