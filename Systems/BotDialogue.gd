extends RefCounted
class_name BotDialogue
## Picks what an opponent says in its text bubble, by event.
##
## Lines live in JSON so they are easy to rewrite:  { "event_name": ["line", "line", ...], ... }
## A bot file (BotProfile.dialogue_path) overrides the shared defaults per event; any event it does
## not define falls back to Data/Dialogue/default.json. Lines may use {player} and {bot}.
##
## Events: intro, player_capture, bot_capture, player_check, bot_check, player_promote, bot_promote,
##         player_blunder, player_inaccuracy, player_good, bot_blunder,
##         outro_bot_wins, outro_player_wins, outro_draw, outro_resign
##
## "Forced" events always speak. Everything else obeys a quiet gap (in plies) so the bot does not
## chatter on every move.

const DEFAULT_PATH := "res://Data/Dialogue/default.json"
const FORCED := ["intro", "outro_bot_wins", "outro_player_wins", "outro_draw", "outro_resign",
		"player_blunder", "bot_blunder"]

var bot_name: String = "Opponent"
var player_name: String = "Player"
var min_gap_plies: int = 3

var _pools: Dictionary = {}
var _last_line: Dictionary = {}
var _plies_since_line: int = 99
var _rng := RandomNumberGenerator.new()

func _init(path: String = "", bot: String = "Opponent", player: String = "Player") -> void:
	bot_name = bot
	player_name = player
	_rng.randomize()
	_merge(_load_json(DEFAULT_PATH))
	if path != "":
		_merge(_load_json(path))

func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		if path != "":
			push_warning("BotDialogue: file not found: " + path)
		return {}
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is Dictionary:
		return parsed
	push_warning("BotDialogue: could not parse " + path)
	return {}

func _merge(pools: Dictionary) -> void:
	for event in pools.keys():
		var lines = pools[event]
		if lines is Array and lines.size() > 0:
			_pools[event] = lines   # a bot file replaces the default pool for that event

## Call once per ply (every move made by either side).
func tick() -> void:
	_plies_since_line += 1

func has_event(event: String) -> bool:
	return _pools.has(event)

## Returns a line, or "" if the bot should stay quiet right now.
func pick(event: String) -> String:
	if not _pools.has(event):
		return ""
	if not (event in FORCED) and _plies_since_line < min_gap_plies:
		return ""
	var lines: Array = _pools[event]
	var line := ""
	for attempt in 4:   # avoid repeating the previous line of the same event
		line = str(lines[_rng.randi() % lines.size()])
		if lines.size() < 2 or line != _last_line.get(event, ""):
			break
	_last_line[event] = line
	_plies_since_line = 0
	return line.replace("{player}", player_name).replace("{bot}", bot_name)
