extends Node

# Persistent state for the game
var player_name: String = "Player" # shown on the battle screen and written into saved PGN files
var player_rating: float = 400.0
var games_played: int = 0
var is_rating_established: bool = false


# Tutorial completion flags
var tutorial_states = {
	"pawn_tutorial": "not_started"
}

# Current opponent ID for BattleScene to consume
var current_opponent: String = "" # e.g. "bobby", "engine", "puzzler"

func set_tutorial_state(tutorial_name: String, state: String):
	tutorial_states[tutorial_name] = state

func get_tutorial_state(tutorial_name: String) -> String:
	return tutorial_states.get(tutorial_name, "not_started")

# Current Match Configuration
var current_match_config: MatchConfig = null

func set_match_config(config: MatchConfig):
	current_match_config = config

var bobby_last_color: String = "none" # "white", "black", or "none"
var player_color_override: String = "white" # "white" or "black"

var saved_player_position: Vector2 = Vector2.ZERO

func save_player_position(pos: Vector2):
	saved_player_position = pos

func get_saved_player_position() -> Vector2:
	return saved_player_position

var pending_world_dialog: String = "" # e.g. "bobby_gg"
var bobby_should_taunt: bool = false # Set to true when player loses/gives up to Bobby

# Drill batches: batch id -> index of the puzzle to resume at (kept while the game runs)
var drill_progress: Dictionary = {}

# Story flags: anything the world or a cutscene wants to remember ("met_death": true, "crew_crash_seen": true).
var flags: Dictionary = {}

# Seconds of play on this save (SaveManager advances it while a game is running).
var playtime: float = 0.0

func set_flag(flag_id: String, value: Variant = true) -> void:
	flags[flag_id] = value

func get_flag(flag_id: String, default_value: Variant = false) -> Variant:
	return flags.get(flag_id, default_value)

# --- Save / load -------------------------------------------------------------
# Only plain data (strings, numbers, bools, dictionaries) so it round-trips through JSON.

func get_save_data() -> Dictionary:
	return {
		"player_name": player_name,
		"player_rating": player_rating,
		"games_played": games_played,
		"is_rating_established": is_rating_established,
		"tutorial_states": tutorial_states.duplicate(),
		"bobby_last_color": bobby_last_color,
		"player_color_override": player_color_override,
		"drill_progress": drill_progress.duplicate(),
		"flags": flags.duplicate(true),
		"playtime": playtime,
	}

func load_save_data(data: Dictionary) -> void:
	reset_for_new_game()
	player_name = str(data.get("player_name", player_name))
	player_rating = float(data.get("player_rating", player_rating))
	games_played = int(data.get("games_played", games_played))
	is_rating_established = bool(data.get("is_rating_established", is_rating_established))
	for key in data.get("tutorial_states", {}):
		tutorial_states[str(key)] = str(data["tutorial_states"][key])
	bobby_last_color = str(data.get("bobby_last_color", bobby_last_color))
	player_color_override = str(data.get("player_color_override", player_color_override))
	for key in data.get("drill_progress", {}):
		drill_progress[str(key)] = int(data["drill_progress"][key])  # JSON turns ints into floats
	flags = data.get("flags", {}).duplicate(true)
	playtime = float(data.get("playtime", 0.0))

## Back to a fresh game. Quests and inventory have their own clear() (SaveManager calls all three).
func reset_for_new_game() -> void:
	player_name = "Player"
	player_rating = 400.0
	games_played = 0
	is_rating_established = false
	tutorial_states = {"pawn_tutorial": "not_started"}
	current_opponent = ""
	current_match_config = null
	bobby_last_color = "none"
	player_color_override = "white"
	saved_player_position = Vector2.ZERO
	pending_world_dialog = ""
	bobby_should_taunt = false
	drill_progress = {}
	flags = {}
	playtime = 0.0
