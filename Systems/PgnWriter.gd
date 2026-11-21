extends RefCounted
class_name PgnWriter
## Builds standard PGN text for a finished (or unfinished) game and writes it to the user's
## data folder so it can be loaded into any analysis tool (lichess, chess.com, Stockfish GUIs...).

const SAVE_DIR := "user://games"
const START_FEN := "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

## meta keys: white, black, white_elo, black_elo (ints, optional), result, termination, start_unix,
## start_fen (optional), event (optional)
static func build(meta: Dictionary, sans: Array) -> String:
	var t: Dictionary = Time.get_datetime_dict_from_unix_time(int(meta.get("start_unix", Time.get_unix_time_from_system())))
	var local: Dictionary = Time.get_datetime_dict_from_system()
	var result: String = meta.get("result", "*")
	var tags: Array = [
		["Event", meta.get("event", "Pawn's Journey Casual Game")],
		["Site", "Pawn's Journey"],
		["Date", "%04d.%02d.%02d" % [local.year, local.month, local.day]],
		["Round", "-"],
		["White", meta.get("white", "?")],
		["Black", meta.get("black", "?")],
		["Result", result],
		["UTCDate", "%04d.%02d.%02d" % [t.year, t.month, t.day]],
		["UTCTime", "%02d:%02d:%02d" % [t.hour, t.minute, t.second]],
		["WhiteElo", str(meta.get("white_elo", "?"))],
		["BlackElo", str(meta.get("black_elo", "?"))],
		["TimeControl", "-"],
		["Variant", "Standard"],
		["Termination", meta.get("termination", "Unterminated")],
	]
	var fen: String = meta.get("start_fen", START_FEN)
	if fen != START_FEN:
		tags.append(["SetUp", "1"])
		tags.append(["FEN", fen])

	var out := ""
	for tag in tags:
		out += '[%s "%s"]\n' % [tag[0], _escape(str(tag[1]))]
	out += "\n" + _movetext(sans, result, fen) + "\n"
	return out

static func _escape(s: String) -> String:
	return s.replace("\\", "\\\\").replace('"', '\\"')

static func _movetext(sans: Array, result: String, fen: String) -> String:
	var tokens: Array = []
	var black_first := fen.split(" ").size() > 1 and fen.split(" ")[1] == "b"
	var ply := 1 if black_first else 0
	var number := 1
	if fen.split(" ").size() > 5:
		number = int(fen.split(" ")[5])
	for san in sans:
		if ply % 2 == 0:
			tokens.append("%d." % number)
		elif tokens.is_empty():
			tokens.append("%d..." % number)
		tokens.append(str(san))
		if ply % 2 == 1:
			number += 1
		ply += 1
	tokens.append(result)
	# Wrap at 80 columns as the PGN spec recommends
	var lines: Array = []
	var line := ""
	for tok in tokens:
		if line.length() + tok.length() + 1 > 80 and line != "":
			lines.append(line)
			line = tok
		else:
			line = tok if line == "" else line + " " + tok
	lines.append(line)
	return "\n".join(lines)

static func games_dir_global() -> String:
	return ProjectSettings.globalize_path(SAVE_DIR)

## Returns {ok: bool, path: String (absolute), error: String}
static func save(pgn_text: String, white: String, black: String) -> Dictionary:
	var err := DirAccess.make_dir_recursive_absolute(games_dir_global())
	if err != OK and err != ERR_ALREADY_EXISTS:
		return {"ok": false, "path": "", "error": "Could not create the games folder (error %d)." % err}
	var d: Dictionary = Time.get_datetime_dict_from_system()
	var base := "%04d-%02d-%02d_%02d%02d_%s-vs-%s" % [d.year, d.month, d.day, d.hour, d.minute, _slug(white), _slug(black)]
	var path := "%s/%s.pgn" % [SAVE_DIR, base]
	var n := 2
	while FileAccess.file_exists(path):
		path = "%s/%s_%d.pgn" % [SAVE_DIR, base, n]
		n += 1
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return {"ok": false, "path": "", "error": "Could not write the file (error %d)." % FileAccess.get_open_error()}
	f.store_string(pgn_text)
	f.close()
	return {"ok": true, "path": ProjectSettings.globalize_path(path), "error": ""}

static func _slug(s: String) -> String:
	var out := ""
	for c in s:
		if c.is_valid_identifier() or c == "-" or c.is_valid_int():
			out += c
		elif c == " ":
			out += "-"
	return out if out != "" else "Player"
