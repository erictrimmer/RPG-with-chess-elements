extends "res://Systems/GameManager.gd"

var back_rank_puzzles = []
var current_puzzle_index = 0

func _ready():
	super._ready()
	
	# Load all back rank mate puzzles
	back_rank_puzzles = PuzzleManager.get_puzzles_by_tag("back_rank")
	
	if back_rank_puzzles.is_empty():
		printerr("No back rank puzzles found!")
		return
	
	print("Loaded ", back_rank_puzzles.size(), " back rank mate puzzles")
	
	await get_tree().create_timer(0.1).timeout
	load_next_puzzle()

func load_next_puzzle():
	if current_puzzle_index >= back_rank_puzzles.size():
		print("All puzzles completed!")
		if game_ui_node:
			game_ui_node.show_message("All back rank mate puzzles completed! Great job!")
		return
	
	var puzzle = back_rank_puzzles[current_puzzle_index]
	
	print("Loading puzzle ", current_puzzle_index + 1, "/", back_rank_puzzles.size(), ": ", puzzle.get("name", "Unknown"))
	
	# Start the puzzle
	start_puzzle(
		puzzle.get("fen", ""),
		puzzle.get("objective_move", ""),
		puzzle.get("instruction", ""),
		puzzle.get("success_text", "")
	)

# Override to show next button after success
func _end_game(reason: String):
	super._end_game(reason)
	
	if reason.contains("Success"):
		# Show next button
		if game_ui_node:
			var next_btn = game_ui_node.message_panel.get_node_or_null("NextButton")
			if next_btn:
				# Disconnect any previous connections
				if next_btn.pressed.is_connected(_on_next_puzzle):
					next_btn.pressed.disconnect(_on_next_puzzle)
				next_btn.pressed.connect(_on_next_puzzle)

func _on_next_puzzle():
	current_puzzle_index += 1
	
	if game_ui_node:
		game_ui_node.hide_message()
	
	load_next_puzzle()

# Override resign to skip puzzle
func _on_resign_requested():
	print("Puzzle skipped")
	if game_ui_node:
		game_ui_node.show_message("Puzzle skipped. Moving to next...", false)
	
	await get_tree().create_timer(1.0).timeout
	_on_next_puzzle()
