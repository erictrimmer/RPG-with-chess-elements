extends Node

# Persistent state for the game
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

