extends BattleController

var current_puzzle_index = 0

var puzzles = [
	{
		"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
		"objective": "e2e3",
		"instruction": "Pawns usually move forward one square. Move the pawn on e2 to e3.",
		"success": "Correct! Pawns move forward one square at a time."
	},
	{
		"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
		"objective": "e2e4",
		"instruction": "However, on their very first move, pawns can move TWO squares! Move e2 to e4.",
		"success": "Great! Moving two squares is only allowed on the first move."
	},
	{
		"fen": "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1", # d4 vs e5
		"objective": "d4e5",
		"instruction": "Pawns capture diagonally one square forward. Capture the black pawn with your d4 pawn.",
		"success": "Nice! Pawns move straight but capture diagonally."
	},
	{
		"fen": "8/4P3/8/8/8/8/8/8 w - - 0 1", # Promotion setup
		"objective": "e7e8q", # Explicit queen promotion for validation
		"instruction": "When a pawn reaches the other side, it promotes! Move the pawn to the last rank.",
		"success": "Promotion! You can choose to become a Queen, Rook, Bishop, or Knight."
	},
	{
		"fen": "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3", # d7-d5 just happened. En passant target at d6.
		"objective": "e5d6",
		"instruction": "En Passant! The black pawn just moved d7-d5, landing next to your pawn on e5. Capture it by moving your pawn to d6!",
		"success": "Excellent! That is 'En Passant' (In Passing)."
	}
]

func _ready():
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.PUZZLE
	config.player_color = "white"
	if puzzles.size() > 0:
		config.puzzle_fen = puzzles[0]["fen"]
		config.puzzle_instruction = puzzles[0]["instruction"]
	GameState.current_match_config = config
	
	super._ready()
	
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
	GameState.set_tutorial_state("pawn_tutorial", result)
	GameManager.go_to_world()

func handle_player_move(uci_move: String):
	if not is_battle_active or not is_players_turn or not chess_engine: return
	
	var current_puzzle = puzzles[current_puzzle_index]
	var objective = current_puzzle["objective"]
	
	var matches = (uci_move == objective)
	if not matches and uci_move.length() == 5 and objective.length() == 5:
		if uci_move.substr(0,4) == objective.substr(0,4):
			matches = true
	
	if matches:
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
