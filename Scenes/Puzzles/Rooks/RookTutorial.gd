extends BattleController

var current_puzzle_index = 0

var puzzles = [
	{
		"fen": "8/8/8/8/8/8/8/3R4 w - - 0 1",
		"objective": "d1d8",
		"instruction": "Rooks move in straight lines - horizontally or vertically. Move to d8.",
		"success": "Correct! Rooks can move any distance in a straight line."
	},
	{
		"fen": "3R4/8/8/8/8/8/8/8 w - - 0 1",
		"objective": "d8h8",
		"instruction": "Now move the Rook from d8 to h8.",
		"success": "Great! That was a horizontal move."
	},
	{
		"fen": "8/7p/8/8/8/8/8/7R w - - 0 1",
		"objective": "h1h7",
		"instruction": "Capture the black pawn on h7!",
		"success": "Captured! Rooks are simple but very strong."
	}
]

func _ready():
	# Ensure player is always White for this tutorial
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.PUZZLE
	config.player_color = "white"
	GameState.current_match_config = config
	
	super._ready()
	
	if game_ui_node:
		if not game_ui_node.has_signal("next_puzzle_requested"):
			game_ui_node.add_user_signal("next_puzzle_requested")
		
		# Connect to the signal
		if not game_ui_node.is_connected("next_puzzle_requested", _on_next_puzzle_requested):
			game_ui_node.connect("next_puzzle_requested", _on_next_puzzle_requested)

	load_current_puzzle()

func load_current_puzzle():
	if current_puzzle_index < puzzles.size():
		var data = puzzles[current_puzzle_index]
		start_puzzle(
			data["fen"],
			data["objective"],
			data["instruction"],
			data["success"]
		)
	else:
		return_to_world("completed")

func start_puzzle(fen: String, objective: String, instruction: String, success: String):
	is_battle_active = true
	is_puzzle_mode = true
	current_fen = fen
	puzzle_objective_move = objective
	puzzle_success_text = success
	
	pgn_history = ""
	fullmove_number = 1
	is_players_turn = true
	
	redraw_board_from_fen(current_fen)
	
	if game_ui_node:
		game_ui_node.update_pgn("")
		game_ui_node.update_status("Puzzle: White to Move")
		game_ui_node.set_instruction(instruction)
		game_ui_node.enable_buttons()
		
	if chess_engine:
		chess_engine.call("RequestLegalMoves", current_fen)

func _on_next_puzzle_requested():
	current_puzzle_index += 1
	load_current_puzzle()

func _on_resign_requested():
	return_to_world("failed")

func return_to_world(result: String):
	GameState.set_tutorial_state("rook_tutorial", result)
	GameManager.go_to_world()

func handle_player_move(uci_move: String):
	if not is_battle_active or not is_players_turn or not chess_engine: return
	
	var current_puzzle = puzzles[current_puzzle_index]
	var objective = current_puzzle["objective"]
	
	if uci_move == objective:
		var san = chess_engine.call("GetMoveSan", current_fen, uci_move)
		var new_fen = chess_engine.call("ApplyMove", current_fen, uci_move)
		if new_fen != current_fen:
			current_fen = new_fen
			is_players_turn = false
			_record_move_pgn(san, is_player_white)
			redraw_board_from_fen(current_fen)
			if game_ui_node: 
				game_ui_node.show_message(puzzle_success_text, true)
				game_ui_node.update_status("Success!")
			is_battle_active = false
	else:
		if chess_engine.call("IsMoveSafe", current_fen, uci_move):
			if game_ui_node: game_ui_node.show_message("Legal, but not the right move. Try again!", false)
