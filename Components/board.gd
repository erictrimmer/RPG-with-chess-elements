extends Node2D

# --- CONFIG ---
const SQUARE_SIZE: int = 16
const BOARD_SIZE_PIXELS = SQUARE_SIZE * 8 # 128
const VIEWPORT_WIDTH = 320
const VIEWPORT_HEIGHT = 180

const LIGHT_SQUARE_COLOR = Color(0.9, 0.9, 0.8, 1.0)
const DARK_SQUARE_COLOR = Color(0.4, 0.6, 0.8, 1.0)
const HIGHLIGHT_COLOR = Color(1.0, 1.0, 0.0, 0.5) # Semi-transparent Yellow

signal square_clicked(square_name: String)

# --- REFERENCES ---
var piece_scene = preload("res://Components/Piece.tscn") 
var pieces = {} # Dictionary to store Piece nodes: {square_name: Piece_node}

# --- INPUT STATE ---
var selected_square: String = ""
var valid_moves = []
var is_flipped: bool = false # If true, board is viewed from Black's perspective (h1 top-left)

# --- SETUP ---

func _ready():
	# Position the board to the left to make room for UI
	position.x = 24  # Left margin
	position.y = (VIEWPORT_HEIGHT - BOARD_SIZE_PIXELS) / 2.0 # Vertically centered
	
	# Enables the _draw() function to be called
	queue_redraw()
	
	setup_coordinates()

func set_flipped(flipped: bool):
	is_flipped = flipped
	queue_redraw()
	setup_coordinates()
	# Game Manager calls place_pieces_from_fen which handles re-layout


func _draw():
	# Draw the checkered board pattern
	for rank in range(8):
		for file in range(8):
			var is_light = (rank + file) % 2 == 0
			var color = LIGHT_SQUARE_COLOR if is_light else DARK_SQUARE_COLOR
			var rect = Rect2(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
			draw_rect(rect, color)
	
	# Draw square highlight if a piece is selected
	if selected_square != "":
		# Convert square name (e.g. "e2") to visual grid coordinates
		var file_idx = ord(selected_square[0]) - ord('a')
		var rank_idx = 8 - int(selected_square[1]) # 0-7, 0 is Rank 8
		
		# If flipped, invert coordinates
		if is_flipped:
			file_idx = 7 - file_idx
			rank_idx = 7 - rank_idx
			
		var rect = Rect2(file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
		draw_rect(rect, HIGHLIGHT_COLOR)

func setup_coordinates():
	# Clear existing labels first (simple way: remove all Label children)
	for child in get_children():
		if child is Label:
			child.queue_free()
			
	var label_settings = LabelSettings.new()
	label_settings.font_size = 8
	label_settings.font_color = Color(1, 1, 1, 0.7) 

	# Files (a-h): Top and Bottom
	for i in range(8):
		# If flipped, File 0 is 'h', File 7 is 'a'
		var char_code = ord('h') - i if is_flipped else ord('a') + i
		var char_str = char(char_code)
		
		var lbl_b = _create_label(char_str, label_settings)
		lbl_b.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl_b.position = Vector2(i * SQUARE_SIZE, BOARD_SIZE_PIXELS)
		lbl_b.size = Vector2(SQUARE_SIZE, 12)
		add_child(lbl_b)
		
		var lbl_t = _create_label(char_str, label_settings)
		lbl_t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl_t.position = Vector2(i * SQUARE_SIZE, -12)
		lbl_t.size = Vector2(SQUARE_SIZE, 12)
		add_child(lbl_t)

	# Ranks (1-8): Left and Right
	for i in range(8):
		# If flipped, Rank 0 (top) is '1', Rank 7 (bottom) is '8'
		# Normal: Rank 0 (top) is '8', Rank 7 (bottom) is '1'
		var rank_val = i + 1 if is_flipped else 8 - i
		var num_str = str(rank_val)
		
		var lbl_l = _create_label(num_str, label_settings)
		lbl_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		lbl_l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		lbl_l.position = Vector2(-12, i * SQUARE_SIZE)
		lbl_l.size = Vector2(10, SQUARE_SIZE)
		add_child(lbl_l)
		
		var lbl_r = _create_label(num_str, label_settings)
		lbl_r.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		lbl_r.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		lbl_r.position = Vector2(BOARD_SIZE_PIXELS + 2, i * SQUARE_SIZE)
		lbl_r.size = Vector2(10, SQUARE_SIZE)
		add_child(lbl_r)

func _create_label(text_val: String, settings: LabelSettings) -> Label:
	var lbl = Label.new()
	lbl.text = text_val
	lbl.label_settings = settings
	return lbl

func place_pieces_from_fen(fen: String):
	print("Board: Placing pieces from FEN: ", fen)
	for piece in pieces.values():
		piece.queue_free()
	pieces.clear()
	for piece in pieces.values():
		piece.queue_free()
	pieces.clear()

	var parts = fen.split(" ")
	if parts.size() < 1 or (parts.size() == 1 and parts[0] == ""):
		printerr("Board ERROR: Invalid or empty FEN passed: '", fen, "'")
		return
		
	var piece_placement = parts[0]
	var ranks = piece_placement.split("/")

	var rank_idx = 0
	for rank_str in ranks:
		var file_idx = 0
		for char in rank_str:
			if char.is_valid_int():
				file_idx += int(char)
			else:
				var square_name = index_to_square(file_idx, rank_idx)
				var new_piece = piece_scene.instantiate()
				new_piece.initialize_piece(char, SQUARE_SIZE)
				
				# Position logic
				var vis_file = 7 - file_idx if is_flipped else file_idx
				var vis_rank = 7 - rank_idx if is_flipped else rank_idx
				
				new_piece.position.x = vis_file * SQUARE_SIZE + SQUARE_SIZE / 2.0
				new_piece.position.y = vis_rank * SQUARE_SIZE + SQUARE_SIZE / 2.0
				
				add_child(new_piece)
				print("  Board: Created piece ", char, " at ", square_name, " (", new_piece.position, ")")
				pieces[square_name] = new_piece
				file_idx += 1
		rank_idx += 1

	selected_square = ""
	valid_moves.clear()
	queue_redraw()

# Helper to get piece for selection logic in GameManager
func get_piece_at_square(square_name: String):
	return pieces.get(square_name)

# Helper for GameManager to highlight squares
func highlight_square(square_name: String, enable: bool):
	if enable:
		selected_square = square_name
	elif selected_square == square_name:
		selected_square = ""
	queue_redraw()

func _input(event):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		# Convert click position to local position of the Board node
		var pos = get_local_mouse_position()
		# print("Board Click Local: ", pos)
		
		# Check if click is within board bounds
		if pos.x >= 0 and pos.x < BOARD_SIZE_PIXELS and pos.y >= 0 and pos.y < BOARD_SIZE_PIXELS:
			handle_click(pos)

func handle_click(click_pos: Vector2):
	var vis_file_idx = floor(click_pos.x / SQUARE_SIZE)
	var vis_rank_idx = floor(click_pos.y / SQUARE_SIZE)
	
	# Determine logical file/rank
	var file_idx = 7 - vis_file_idx if is_flipped else vis_file_idx
	var rank_idx = 7 - vis_rank_idx if is_flipped else vis_rank_idx
	
	var clicked_square = index_to_square(file_idx, rank_idx)
	square_clicked.emit(clicked_square)

func index_to_square(file_idx: int, rank_idx: int) -> String:
	# Logical conversion never changes (Rank 0 in FEN is Row 8)
	var file_char = char(file_idx + ord('a'))
	var rank_num = 8 - rank_idx
	return "%s%d" % [file_char, rank_num]
