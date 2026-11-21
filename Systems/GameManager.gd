extends Node

# --- SCENE REGISTRY ---
const WORLD_SCENE = "res://Scenes/demo.tscn"
const BATTLE_SCENE = "res://Scenes/StandardMatch.tscn"
const PAWN_TUTORIAL = "res://Scenes/Puzzles/Pawns/PawnTutorial.tscn"
const KNIGHT_TUTORIAL = "res://Scenes/Puzzles/Knights/KnightTutorial.tscn"
const QUEEN_TUTORIAL = "res://Scenes/Puzzles/Queens/QueenTutorial.tscn"
const DRILL_MENU = "res://Scenes/Puzzles/Drill/DrillMenu.tscn"

# --- SYSTEM REFERENCES ---
var chess_engine: Node = null

func _ready():
	# Initialize persistent systems
	_setup_chess_engine()

func _setup_chess_engine():
	var engine_script = load("res://Systems/ChessEngine.cs")
	if engine_script:
		# For C# nodes in Godot 4, .new() on the script is often more reliable
		chess_engine = engine_script.new()
		chess_engine.name = "ChessEngine"
		add_child(chess_engine)
		print("Global ChessEngine initialized (C#).")
	else:
		printerr("Failed to load ChessEngine.cs")

# --- SCENE MANAGEMENT ---

func go_to_world():
	_cleanup_current_scene()
	get_tree().change_scene_to_file(WORLD_SCENE)

func go_to_battle(config: MatchConfig):
	GameState.current_match_config = config
	_cleanup_current_scene()
	get_tree().change_scene_to_file(BATTLE_SCENE)

# Open the puzzle drills from the world. Remembers where the player stands, so exiting the drills
# puts them back there (the world restores GameState's saved position).
func start_drills(player_position: Vector2):
	GameState.save_player_position(player_position)
	go_to_scene(DRILL_MENU)

func go_to_scene(path: String):
	_cleanup_current_scene()
	get_tree().change_scene_to_file(path)

func _cleanup_current_scene():
	# Disconnect any global signals that might have been leftover
	if DialogManager.dialog_choice_made.is_connected(_on_generic_dialog_callback):
		DialogManager.dialog_choice_made.disconnect(_on_generic_dialog_callback)
	
	# Any other cleanup logic here
	pass

# Placeholder for generic signal safety if needed
func _on_generic_dialog_callback(_choice): pass

# --- ERROR HANDLING UTILS ---

func safe_disconnect(sig: Signal, callable: Callable):
	if sig.is_connected(callable):
		sig.disconnect(callable)

func safe_connect(sig: Signal, callable: Callable):
	if not sig.is_connected(callable):
		sig.connect(callable)
