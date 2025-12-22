extends CanvasLayer

signal draw_requested
signal resign_requested
signal promotion_selected(piece_type: String)

var pgn_label: RichTextLabel
var status_label: Label
var draw_btn: Button
var resign_btn: Button
var instruction_label: Label
var message_panel: Panel
var message_label: Label
var promotion_panel: Panel

# Config
const UI_LEFT_MARGIN = 180 # Start UI to the right of the board
const UI_WIDTH = 130
const SCREEN_HEIGHT = 180

func _ready():
	# Root Container (VBox for vertical list)
	var vbox = VBoxContainer.new()
	vbox.position = Vector2(UI_LEFT_MARGIN, 0)
	vbox.size = Vector2(UI_WIDTH, SCREEN_HEIGHT)
	vbox.add_theme_constant_override("separation", 5) # Spacing between elements
	add_child(vbox)
	
	# Spacer Top
	var spacer_top = Control.new()
	spacer_top.custom_minimum_size = Vector2(0, 2)
	vbox.add_child(spacer_top)
	
	# Common Settings
	var sm_label_settings = LabelSettings.new()
	sm_label_settings.font_size = 8
	
	# 1. PGN Title
	var title = Label.new()
	title.text = "History"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.label_settings = sm_label_settings
	vbox.add_child(title)
	
	# 2. PGN Window
	pgn_label = RichTextLabel.new()
	pgn_label.custom_minimum_size = Vector2(UI_WIDTH, 60) # Reduce slightly to give more room for text
	pgn_label.size_flags_vertical = Control.SIZE_EXPAND_FILL # Allow it to take available space if needed, or fixed
	pgn_label.scroll_active = true
	pgn_label.text = ""
	pgn_label.add_theme_font_size_override("normal_font_size", 8) 
	vbox.add_child(pgn_label)
	
	# 3. Instruction Label (For Puzzles)
	instruction_label = Label.new()
	instruction_label.text = ""
	instruction_label.custom_minimum_size = Vector2(UI_WIDTH, 10) # Minimum height, grows automatically
	instruction_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	instruction_label.label_settings = sm_label_settings
	vbox.add_child(instruction_label)
	
	# 4. Status
	status_label = Label.new()
	status_label.text = "White to Move"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.label_settings = sm_label_settings
	vbox.add_child(status_label)
	
	# 5. Buttons
	var button_container = HBoxContainer.new()
	button_container.alignment = BoxContainer.ALIGNMENT_CENTER
	button_container.add_theme_constant_override("separation", 10)
	vbox.add_child(button_container)
	
	draw_btn = Button.new()
	draw_btn.text = "Draw"
	draw_btn.add_theme_font_size_override("font_size", 8)
	draw_btn.pressed.connect(func(): emit_signal("draw_requested"))
	draw_btn.visible = false  # Hidden by default (for puzzles)
	button_container.add_child(draw_btn)
	
	resign_btn = Button.new()
	resign_btn.text = "Give Up"
	resign_btn.add_theme_font_size_override("font_size", 8)
	resign_btn.pressed.connect(func(): emit_signal("resign_requested"))
	button_container.add_child(resign_btn)

	_setup_message_overlay()
	_setup_promotion_dialog()

func _setup_message_overlay():
	message_panel = Panel.new()
	message_panel.visible = false
	message_panel.position = Vector2(40, 50) 
	message_panel.size = Vector2(240, 80)
	add_child(message_panel)
	message_panel.move_to_front() # Ensure it's on top
	
	var msg_settings = LabelSettings.new()
	msg_settings.font_size = 8
	
	message_label = Label.new()
	message_label.position = Vector2(10, 10)
	message_label.size = Vector2(220, 40)
	message_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message_label.label_settings = msg_settings
	message_panel.add_child(message_label)
	
	# Next button for puzzles
	var next_btn = Button.new()
	next_btn.text = "Next"
	next_btn.position = Vector2(85, 55)
	next_btn.size = Vector2(70, 20)
	next_btn.add_theme_font_size_override("font_size", 8)
	next_btn.visible = false
	next_btn.name = "NextButton"
	next_btn.pressed.connect(func(): 
		message_panel.visible = false
		if has_user_signal("next_puzzle_requested"): emit_signal("next_puzzle_requested")
	)
	message_panel.add_child(next_btn)

func _setup_promotion_dialog():
	promotion_panel = Panel.new()
	promotion_panel.visible = false
	promotion_panel.position = Vector2(60, 60)
	promotion_panel.size = Vector2(200, 60)
	add_child(promotion_panel)
	
	var title = Label.new()
	title.text = "Promote to:"
	title.position = Vector2(10, 5)
	title.size = Vector2(180, 15)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var title_settings = LabelSettings.new()
	title_settings.font_size = 8
	title.label_settings = title_settings
	promotion_panel.add_child(title)
	
	var hbox = HBoxContainer.new()
	hbox.position = Vector2(10, 25)
	hbox.size = Vector2(180, 30)
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox.add_theme_constant_override("separation", 5)
	promotion_panel.add_child(hbox)
	
	# Unicode chess pieces: ♕ ♖ ♗ ♘
	var pieces = [
		{"symbol": "♕", "code": "Q"},  # Queen
		{"symbol": "♖", "code": "R"},  # Rook
		{"symbol": "♗", "code": "B"},  # Bishop
		{"symbol": "♘", "code": "N"}   # Knight
	]
	
	for piece_data in pieces:
		var btn = Button.new()
		btn.text = piece_data["symbol"]
		btn.custom_minimum_size = Vector2(40, 25)
		btn.add_theme_font_size_override("font_size", 16)
		btn.pressed.connect(func(): _on_promotion_selected(piece_data["code"]))
		hbox.add_child(btn)

func _on_promotion_selected(piece: String):
	promotion_panel.visible = false
	emit_signal("promotion_selected", piece)

func show_promotion_dialog():
	promotion_panel.visible = true

func hide_promotion_dialog():
	promotion_panel.visible = false


func show_message(text: String, show_next_button: bool = false):
	message_label.text = text
	message_panel.visible = true
	
	var next_btn = message_panel.get_node_or_null("NextButton")
	if next_btn:
		next_btn.visible = show_next_button
	
	if not show_next_button:
		# Auto-hide after 4 seconds if no next button
		var t = get_tree().create_timer(4.0)
		t.timeout.connect(func(): if message_panel: message_panel.visible = false)

func hide_message():
	message_panel.visible = false


func set_instruction(text: String):
	instruction_label.text = text

func update_pgn(history_text: String):
	pgn_label.text = history_text
	pgn_label.scroll_to_line(pgn_label.get_line_count() - 1)

func update_status(text: String):
	status_label.text = text

func disable_buttons():
	draw_btn.disabled = true
	resign_btn.disabled = true

func enable_buttons():
	draw_btn.disabled = false
	resign_btn.disabled = false
