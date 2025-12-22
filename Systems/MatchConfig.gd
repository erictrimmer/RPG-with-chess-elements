extends Resource
class_name MatchConfig

enum Mode { CLASSIC, PUZZLE, TUTORIAL }

var mode: Mode = Mode.CLASSIC

# --- Classic / Bot Match Settings ---
var bot_profile: BotProfile = null
var player_color: String = "white" # "white" or "black"

# --- Puzzle Settings ---
var puzzle_fen: String = ""
var puzzle_objective: String = ""
var puzzle_success_text: String = ""
var puzzle_instruction: String = ""

# --- Metadata ---
var return_scene_path: String = "res://Scenes/world.tscn"
var reward_id: String = ""

# Factory methods for easy creation
static func create_bot_match(profile: BotProfile, player_side: String = "white") -> MatchConfig:
	var config = MatchConfig.new()
	config.mode = Mode.CLASSIC
	config.bot_profile = profile
	config.player_color = player_side
	return config

static func create_puzzle(fen: String, objective: String) -> MatchConfig:
	var config = MatchConfig.new()
	config.mode = Mode.PUZZLE
	config.puzzle_fen = fen
	config.puzzle_objective = objective
	return config
