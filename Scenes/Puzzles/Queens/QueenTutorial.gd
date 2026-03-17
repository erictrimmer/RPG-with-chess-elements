extends BattleController

var current_puzzle_index = 0

var puzzles = [
	{
		"fen": "8/8/8/8/8/8/8/3Q4 w - - 0 1",
		"objective": "d1d8",
		"instruction": "The Queen is the most powerful piece! She moves like a Rook and a Bishop combined. Move to d8.",
		"success": "Correct! That was a vertical move like a Rook."
	},
	{
		"fen": "3Q4/8/8/8/8/8/8/8 w - - 0 1",
		"objective": "d8h4",
		"instruction": "Now move diagonally from d8 to h4.",
		"success": "Great! That was a diagonal move like a Bishop."
	},
	{
		"fen": "8/7p/8/5Q2/8/8/8/8 w - - 0 1",
		"objective": "f5h7",
		"instruction": "Capture the black pawn on h7!",
		"success": "Captured! The Queen can dominate the whole board."
	}
]

func _ready():
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.PUZZLE
	config.player_color = "white"
	# Pre-load data so BattleController can draw it instantly
	if puzzles.size() > 0:
		config.puzzle_fen = puzzles[0]["fen"]
		config.puzzle_instruction = puzzles[0]["instruction"]
	GameState.current_match_config = config
	
	super._ready() # This draws the first puzzle via BattleController's new logic
	
	if game_ui_node:
		if not game_ui_node.has_signal("next_puzzle_requested"):
			game_ui_node.add_user_signal("next_puzzle_requested")
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
	print("QueenTutorial: Returning to world with result: ", result)
	GameState.set_tutorial_state("queen_tutorial", result)
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
			# Trigger end game logic but don't call return_to_world immediately
	else:
		if chess_engine.call("IsMoveSafe", current_fen, uci_move):
			if game_ui_node: game_ui_node.show_message("Legal, but not the right move. Try again!", false)
