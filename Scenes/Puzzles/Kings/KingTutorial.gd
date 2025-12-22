extends "res://Systems/GameManager.gd"

var current_puzzle_index = 0

var puzzles = [
	{
		"fen": "8/8/8/8/4K3/8/8/8 w - - 0 1",
		"objective": "e4e5",
		"instruction": "The King is important but slow. He moves one square in any direction. Move forward.",
		"success": "Correct! One step at a time."
	},
	{
		"fen": "8/8/8/3p4/3K4/8/8/8 w - - 0 1",
		"objective": "d4d5",
		"instruction": "Capture the pawn next to you (d5).",
		"success": "Captured!"
	},
	{
		"fen": "8/8/8/8/8/8/4P3/4K3 w - - 0 1",
		"objective": "e1f2",
		"instruction": "The King likes to stay safe. Move to f2 behind your pawn.",
		"success": "Safe and sound."
	},
	{
		"fen": "8/8/8/8/8/8/8/4K2r w - - 0 1", # Check by rook on h1
		"objective": "e1f2",
		"instruction": "You are in Check! The enemy Rook attacks your King. You MUST move to safety (f2).",
		"success": "Phew! Avoided the check."
	},
	{
		"fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
		"objective": "e1g1",
		"instruction": "Special Move: Castling! Move the King TWO squares towards the Rook to castle kingside (g1).",
		"success": "Excellent! You've mastered the King and Castling."
	}
]

func _ready():
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.PUZZLE
	config.player_color = "white"
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

func _on_next_puzzle_requested():
	current_puzzle_index += 1
	load_current_puzzle()

func _end_game(reason: String):
	super._end_game(reason)

func _on_resign_requested():
	return_to_world("failed")

func return_to_world(result: String):
	GameState.set_tutorial_state("king_tutorial", result)
	get_tree().change_scene_to_file("res://Scenes/world.tscn")

func handle_player_move(uci_move: String):
	if not is_battle_active or not is_players_turn or not chess_engine: return
	
	var current_puzzle = puzzles[current_puzzle_index]
	var objective = current_puzzle["objective"]
	
	if uci_move == objective:
		var new_fen = chess_engine.call("ApplyMove", current_fen, uci_move)
		if new_fen != current_fen:
			current_fen = new_fen
			is_players_turn = false
			_record_move_pgn(uci_move, is_player_white)
			redraw_board_from_fen(current_fen)
			if game_ui_node: 
				game_ui_node.show_message(puzzle_success_text, true)
				game_ui_node.update_status("Success!")
			is_battle_active = false
			_end_game("Success!")
	else:
		var is_safe = false
		if chess_engine.has_method("IsMoveSafe"):
			is_safe = chess_engine.call("IsMoveSafe", current_fen, uci_move)
		if is_safe:
			if game_ui_node: game_ui_node.show_message("Legal, but not the right move.", false) 
			if board_node:
				board_node.highlight_square(selected_square, false)
				selected_square = ""
		else:
			if board_node:
				board_node.highlight_square(selected_square, false)
				selected_square = ""
