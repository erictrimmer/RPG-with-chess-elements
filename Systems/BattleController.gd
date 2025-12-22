extends Node2D

class_name BattleController

# --- VISUALIZATION REFERENCES ---
var board_node: Node2D

# --- EXTERNAL REFERENCES ---
var chess_engine: Node
var active_bot: Node = null
var game_ui_node: Node 

# --- GAME STATE ---
var current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
var is_players_turn = true
var is_battle_active = false
var selected_square: String = ""
var legal_moves = []
var pending_promotion_move: String = ""

# PGN State
var fullmove_number = 1
var pgn_history = ""

# Puzzle State
var is_puzzle_mode = false
var puzzle_objective_move = "" 
var puzzle_success_text = ""

# Bot Config
var is_bot_game = false
var bot_difficulty_ms = 800
var _targetElo = -1

@export var is_player_white = true

func _ready():
	# 1. References
	board_node = get_node_or_null("Board")
	
	# 2. Immediate Initialization
	setup_battle_scene()

func setup_battle_scene():
	is_battle_active = true
	var config = GameState.current_match_config
	if not config: config = MatchConfig.new()
	
	# 1. Initialize State
	if config.mode == MatchConfig.Mode.PUZZLE:
		current_fen = config.puzzle_fen if config.puzzle_fen != "" else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
		is_player_white = true
		is_puzzle_mode = true
	else:
		current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
		is_player_white = (config.player_color != "black")
		is_puzzle_mode = false
		
	# 2. Board Prep & INITIAL DRAW
	if board_node:
		# VISUAL SAFEGUARD: Create a camera to force focus on the board
		var cam = Camera2D.new()
		# Use Top-Left anchor for easier pixel coordinate reasoning
		cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
		cam.position = Vector2(0, 0)
		cam.enabled = true
		cam.make_current()
		add_child(cam)
		print("BattleController: Created Safe Camera at ", cam.position)

		if board_node.has_method("set_flipped"):
			board_node.set_flipped(not is_player_white)
		# Connection safety
		if not board_node.is_connected("square_clicked", handle_square_click):
			board_node.connect("square_clicked", handle_square_click)
		
		# Draw immediately so there's something to see
		print("BattleController: Initial Immediate Draw. FEN: ", current_fen)
		board_node.place_pieces_from_fen(current_fen)

	# 3. UI Setup
	var ui_script = load("res://Scenes/GameUI.gd")
	if ui_script:
		game_ui_node = ui_script.new()
		add_child(game_ui_node)
		game_ui_node.connect("draw_requested", _on_draw_requested)
		game_ui_node.connect("resign_requested", _on_resign_requested)
		
	# 4. Engine Link
	chess_engine = GameManager.chess_engine
	if not chess_engine:
		var engine_script = load("res://Systems/ChessEngine.cs")
		chess_engine = engine_script.new()
		add_child(chess_engine)
	
	if not chess_engine.is_connected("LegalMovesReceived", on_legal_moves_updated):
		chess_engine.connect("LegalMovesReceived", on_legal_moves_updated)
	if not chess_engine.is_connected("AiMoveReceived", process_ai_move):
		chess_engine.connect("AiMoveReceived", process_ai_move)
	
	# 5. Bot Setup (Wrapped to prevent crashes hiding the board)
	if config.bot_profile:
		var bot_script = load("res://Scenes/Bots/StandardBot.gd")
		if bot_script:
			var bot = bot_script.new(config.bot_profile)
			if bot:
				bot.initialize(not is_player_white)
				set_bot(bot)
				_targetElo = config.bot_profile.elo
				bot_difficulty_ms = 800
	
	# 6. Final UI Updates
	if game_ui_node:
		game_ui_node.update_pgn("")
		game_ui_node.update_status("White to Move" if is_player_white else "Computer Thinking...")
		game_ui_node.set_instruction(config.puzzle_instruction if is_puzzle_mode else "") 
		game_ui_node.enable_buttons()

	# 7. SAFETY REDRAW (Just in case anything cleared it or flipped it)
	if board_node:
		print("BattleController: Executing Safety Redraw with FEN: ", current_fen)
		board_node.place_pieces_from_fen(current_fen)

	# 8. Start Turn
	is_players_turn = is_player_white
	if is_players_turn:
		# Small delay for engine safety
		if chess_engine.has_method("RequestLegalMoves"):
			print("BattleController: Requesting Legal Moves (Deferred)")
			chess_engine.call_deferred("RequestLegalMoves", current_fen)
	else:
		print("BattleController: Requesting AI Move (Internal)")
		request_ai_move_internal(current_fen)

func set_bot(bot_instance: Node):
	if active_bot:
		active_bot.queue_free()
	active_bot = bot_instance
	if active_bot:
		add_child(active_bot)
		if not active_bot.is_connected("move_chosen", _on_bot_move_chosen):
			active_bot.connect("move_chosen", _on_bot_move_chosen)

func _on_bot_move_chosen(uci_move: String):
	if uci_move == "ENGINE_CALC":
		_request_engine_move_only(current_fen)
	else:
		process_ai_move(uci_move)

func request_ai_move_internal(fen: String):
	if active_bot:
		active_bot.request_move(fen, legal_moves)
	else:
		_request_engine_move_only(fen)

func _request_engine_move_only(fen: String):
	if chess_engine and chess_engine.has_method("RequestAiMove"):
		chess_engine.call("RequestAiMove", fen, bot_difficulty_ms)

func redraw_board_from_fen(fen: String):
	if board_node:
		board_node.place_pieces_from_fen(fen)
	else:
		printerr("BattleController ERROR: board_node is null during redraw_board_from_fen")

func on_legal_moves_updated(moves: Array):
	legal_moves = moves

func handle_square_click(square_name: String):
	if not is_battle_active or not is_players_turn: 
		return
	
	var piece_at_square = board_node.get_piece_at_square(square_name)
	
	if selected_square.is_empty():
		var owned = false
		if piece_at_square:
			owned = _is_piece_owned_by_player(piece_at_square)
			
		if piece_at_square and owned:
			selected_square = square_name
			board_node.highlight_square(square_name, true)
	else:
		if square_name == selected_square:
			board_node.highlight_square(selected_square, false)
			selected_square = ""
		elif piece_at_square and _is_piece_owned_by_player(piece_at_square):
			board_node.highlight_square(selected_square, false)
			selected_square = square_name
			board_node.highlight_square(square_name, true)
		else:
			var uci_move = selected_square + square_name
			
			# Promotion Check
			var is_promo_rank = (selected_square[1] == "7" and square_name[1] == "8" and is_player_white) or \
								(selected_square[1] == "2" and square_name[1] == "1" and not is_player_white)
			
			if is_promo_rank:
				var source_piece = board_node.get_piece_at_square(selected_square)
				if source_piece and source_piece.piece_type == source_piece.Type.PAWN:
					var src_file = ord(selected_square[0])
					var dst_file = ord(square_name[0])
					if abs(src_file - dst_file) <= 1:
						var test_promo_move = uci_move + "q"
						if chess_engine.call("IsMoveSafe", current_fen, test_promo_move):
							pending_promotion_move = uci_move
							if game_ui_node:
								game_ui_node.show_promotion_dialog()
								if not game_ui_node.promotion_selected.is_connected(_on_promotion_chosen):
									game_ui_node.promotion_selected.connect(_on_promotion_chosen)
							return
				
			handle_player_move(uci_move)
			board_node.highlight_square(selected_square, false)
			selected_square = ""

func _on_promotion_chosen(piece: String):
	if pending_promotion_move != "":
		var uci_move = pending_promotion_move + piece.to_lower()
		pending_promotion_move = ""
		handle_player_move(uci_move)
		board_node.highlight_square(selected_square, false)
		selected_square = ""

func _is_piece_owned_by_player(piece_node) -> bool:
	if is_player_white: return piece_node.is_white()
	else: return not piece_node.is_white()

func handle_player_move(uci_move: String):
	if chess_engine == null:
		return
		
	var is_safe = false
	if chess_engine.has_method("IsMoveSafe"):
		is_safe = chess_engine.call("IsMoveSafe", current_fen, uci_move)
	
	if not is_safe:
		return
	
	var san = chess_engine.call("GetMoveSan", current_fen, uci_move)
	var new_fen = chess_engine.call("ApplyMove", current_fen, uci_move)
	
	if new_fen != current_fen:
		current_fen = new_fen
		is_players_turn = false
		_record_move_pgn(san, is_player_white)
		redraw_board_from_fen(current_fen)
		
		if is_puzzle_mode:
			if _check_puzzle_success(uci_move):
				return
		
		_check_game_status()
		if is_battle_active:
			request_ai_move_internal(current_fen)
			if game_ui_node: game_ui_node.update_status("Thinking...")

func _check_puzzle_success(uci_move: String) -> bool:
	var move_matches = (uci_move == puzzle_objective_move)
	if not move_matches and uci_move.length() == 5 and puzzle_objective_move.length() == 5:
		if uci_move.substr(0, 4) == puzzle_objective_move.substr(0, 4):
			move_matches = true
			
	if move_matches:
		if game_ui_node: 
			game_ui_node.show_message(puzzle_success_text, true)
			game_ui_node.update_status("Success!")
		is_battle_active = false
		_end_game("Success!")
		return true
	return false

func process_ai_move(uci_move: String):
	if uci_move == "" or not is_battle_active or is_players_turn: return
	
	var san = chess_engine.call("GetMoveSan", current_fen, uci_move)
	var new_fen = chess_engine.call("ApplyMove", current_fen, uci_move)
	
	if new_fen != current_fen:
		current_fen = new_fen
		is_players_turn = true
		_record_move_pgn(san, not is_player_white)
		redraw_board_from_fen(current_fen)
		_check_game_status()
		if is_battle_active:
			chess_engine.call("RequestLegalMoves", current_fen)
			if game_ui_node: 
				var turn_text = "White's Turn" if is_player_white else "Black's Turn"
				game_ui_node.update_status(turn_text)

func _record_move_pgn(san_move: String, is_white: bool):
	if is_white:
		pgn_history += "%d. %s " % [fullmove_number, san_move]
	else:
		pgn_history += "%s\n" % san_move
		fullmove_number += 1
	if game_ui_node:
		game_ui_node.update_pgn(pgn_history)

func _check_game_status():
	if chess_engine == null or not chess_engine.has_method("GetGameStatus"):
		return
		
	var status = chess_engine.call("GetGameStatus", current_fen)
	if status == "Checkmate":
		var content = "Checkmate! " + ("White Wins" if not is_players_turn else "Black Wins")
		_end_game(content)
	elif status == "Stalemate":
		_end_game("Stalemate! Draw.")
	elif status == "Draw":
		_end_game("Draw!")

func _end_game(reason: String):
	is_battle_active = false
	if game_ui_node: 
		game_ui_node.update_status(reason)
		game_ui_node.disable_buttons()
		
	var config = GameState.current_match_config
	if config and config.bot_profile:
		var player_lost = ("Black Wins" in reason and is_player_white) or ("White Wins" in reason and not is_player_white)
		if player_lost:
			GameState.bobby_should_taunt = true
		
		await get_tree().create_timer(1.5).timeout
		
		# SAFE SIGNAL HANDLING
		if not DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
			DialogManager.dialog_choice_made.connect(_on_dialog_choice)
		DialogManager.show_dialog("Good game. Rematch?", ["Yes", "No"])

func _on_dialog_choice(choice: String):
	if choice == "Yes":
		var config = GameState.current_match_config
		if config:
			config.player_color = "black" if config.player_color == "white" else "white"
		get_tree().reload_current_scene()
	else:
		var config = GameState.current_match_config
		if config and config.bot_profile:
			GameState.bobby_should_taunt = true
		GameState.pending_world_dialog = "bobby_gg"
		
		# SAFE SIGNAL HANDLING
		if DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
			DialogManager.dialog_choice_made.disconnect(_on_dialog_choice)
			
		GameManager.go_to_world()

func _on_draw_requested():
	_end_game("Draw Agreed.")

func _on_resign_requested():
	_end_game("Resigned.")

func _close_dialog_after_delay(delay: float):
	await get_tree().create_timer(delay).timeout
	DialogManager.close_dialog()
