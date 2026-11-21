extends BattleController
## Plays a harvested drill batch (Data/PuzzlePacks) from the first puzzle (easiest) to the last.
## Pick a batch in DrillMenu, or set "Batch Id" here ("1a", "3b", "rook_mate_in_1"...) and run with F6.
## Solutions with several moves are played out: the opponent's reply is made for you.
## "Menu" opens: Continue (next puzzle of this type), Different puzzles (DrillMenu), Exit (back to the world).
## Progress per batch is kept in GameState.drill_progress.

const DRILL_MENU_SCENE := "res://Scenes/Puzzles/Drill/DrillMenu.tscn"

@export var batch_id: String = "1a"

var batch: Array = []
var index := 0
var solution: Array = []
var step := 0
var solved := 0
var missed := 0
var _missed_this_puzzle := false
var _puzzle_done := false
var _menu_open := false

func _ready():
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.PUZZLE
	config.player_color = "white"
	GameState.current_match_config = config

	super._ready()

	if GameState.has_meta("drill_batch"):
		batch_id = GameState.get_meta("drill_batch")
		GameState.remove_meta("drill_batch")

	batch = PuzzleManager.get_batch(batch_id)
	if batch.is_empty():
		batch = PuzzleManager.get_puzzles_by_theme(batch_id)     # also accept an old-style pack name
		batch.sort_custom(func(a, b): return a.get("rating", 0) < b.get("rating", 0))

	if game_ui_node:
		if not game_ui_node.has_signal("next_puzzle_requested"):
			game_ui_node.add_user_signal("next_puzzle_requested")
		if not game_ui_node.is_connected("next_puzzle_requested", _on_next_puzzle_requested):
			game_ui_node.connect("next_puzzle_requested", _on_next_puzzle_requested)
		game_ui_node.choice_selected.connect(_on_choice_selected)
		game_ui_node.resign_btn.text = "Menu"

	if batch.is_empty():
		is_battle_active = false
		if game_ui_node:
			game_ui_node.say("No puzzles for '%s'. Opening the drill menu..." % batch_id)
		await get_tree().create_timer(1.5).timeout
		if is_inside_tree():
			GameManager.go_to_scene(DRILL_MENU_SCENE)
		return

	index = int(GameState.drill_progress.get(batch_id, 0))
	if index >= batch.size():
		index = 0
	load_current_puzzle()

func load_current_puzzle():
	if index >= batch.size():
		_finish()
		return
	var p: Dictionary = batch[index]
	solution = p.get("solution", [p.get("objective_move", "")])
	step = 0
	_missed_this_puzzle = false
	_puzzle_done = false
	_menu_open = false

	is_battle_active = true
	is_puzzle_mode = true
	current_fen = p["fen"]
	set_player_side_from_fen(current_fen)
	puzzle_objective_move = solution[0]
	puzzle_success_text = p.get("success_text", "Correct!")
	pgn_history = ""
	fullmove_number = 1
	is_players_turn = true

	redraw_board_from_fen(current_fen)
	if game_ui_node:
		game_ui_node.hide_choices()
		game_ui_node.update_pgn("")
		game_ui_node.update_status("%s  %d / %d" % [p.get("batch_title", batch_id), index + 1, batch.size()])
		game_ui_node.set_instruction(p.get("instruction", ""))
		game_ui_node.enable_buttons()
	if chess_engine:
		chess_engine.call("RequestLegalMoves", current_fen)

func _moves_match(a: String, b: String) -> bool:
	if a == b:
		return true
	return a.length() == 5 and b.length() == 5 and a.substr(0, 4) == b.substr(0, 4)   # same move, other promotion piece

func handle_player_move(uci_move: String):
	if not is_battle_active or not is_players_turn or _menu_open or chess_engine == null:
		return
	if not _moves_match(uci_move, solution[step]):
		if chess_engine.call("IsMoveSafe", current_fen, uci_move):
			if not _missed_this_puzzle:
				_missed_this_puzzle = true
				missed += 1
			if game_ui_node:
				game_ui_node.say("Legal, but not the right move. Try again!")
				_repeat_instruction_later()
		return
	_play(uci_move, is_player_white)
	step += 1
	if step >= solution.size():
		solved += 1
		_puzzle_done = true
		is_battle_active = false
		is_players_turn = false
		GameState.drill_progress[batch_id] = index + 1
		if game_ui_node:
			game_ui_node.show_message(puzzle_success_text, true)
			game_ui_node.update_status("Solved!  %d / %d" % [index + 1, batch.size()])
		return
	# the opponent's reply from the stored solution, then it is the player's turn again
	is_players_turn = false
	await get_tree().create_timer(0.6).timeout
	if not is_inside_tree() or _menu_open:
		return
	_play(solution[step], not is_player_white)
	step += 1
	is_players_turn = true
	chess_engine.call("RequestLegalMoves", current_fen)

func _repeat_instruction_later():
	var at := index
	await get_tree().create_timer(2.5).timeout
	if is_inside_tree() and index == at and is_battle_active and not _menu_open and game_ui_node:
		game_ui_node.say(batch[index].get("instruction", ""))

func _play(uci_move: String, white_moved: bool):
	var san = chess_engine.call("GetMoveSan", current_fen, uci_move)
	current_fen = chess_engine.call("ApplyMove", current_fen, uci_move)
	_record_move_pgn(san, white_moved)
	redraw_board_from_fen(current_fen)
	_mark_last_move(uci_move)

func _on_next_puzzle_requested():
	index += 1
	load_current_puzzle()

# "Menu" button: Continue / Different puzzles / Exit
func _on_resign_requested():
	_open_menu()

func _open_menu():
	if _menu_open or not game_ui_node:
		return
	_menu_open = true
	var finished := index >= batch.size() or (_puzzle_done and index + 1 >= batch.size())
	game_ui_node.show_choices([
		["continue", "Play again" if finished else "Continue"],
		["types", "Different puzzles"],
		["exit", "Exit"]])
	game_ui_node.say("What next?")

func _on_choice_selected(id: String):
	match id:
		"continue":
			if index >= batch.size() or (_puzzle_done and index + 1 >= batch.size()):
				GameState.drill_progress[batch_id] = 0      # finished: start the batch again
				index = 0
				load_current_puzzle()
			elif _puzzle_done:
				index += 1                                   # solved: on to the next puzzle
				load_current_puzzle()
			else:
				_menu_open = false                           # unsolved: back to the same puzzle
				is_players_turn = true
				game_ui_node.say(batch[index].get("instruction", ""))
		"types":
			GameManager.go_to_scene(DRILL_MENU_SCENE)
		"exit":
			GameManager.go_to_world()

func _finish():
	is_battle_active = false
	GameState.drill_progress[batch_id] = 0
	if game_ui_node:
		game_ui_node.say("Drill finished: %d solved, %d with a miss, out of %d." % [solved, missed, batch.size()])
	_open_menu()
