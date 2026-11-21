extends Node

# Singleton for managing chess puzzles

var _all_puzzles = []
var _puzzles_loaded = false

func _ready():
	load_all_puzzles()

func load_all_puzzles():
	if _puzzles_loaded:
		return
	
	_all_puzzles.clear()
	
	# Scan Data/Puzzles directory for JSON files
	var dir = DirAccess.open("res://Data/Puzzles/")
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if file_name.ends_with(".json"):
				var puzzle = load_puzzle("res://Data/Puzzles/" + file_name)
				if puzzle:
					_all_puzzles.append(puzzle)
			file_name = dir.get_next()
		
		dir.list_dir_end()
	
	# Packs: one JSON file per category holding many puzzles (made by Tools/harvest_lichess_puzzles.py)
	_load_pack_directory("res://Data/PuzzlePacks/")
	
	_puzzles_loaded = true
	print("Loaded ", _all_puzzles.size(), " puzzles")

# A puzzle can appear in several packs (a rook back-rank mate is in the rook pack and the back-rank
# pack), so every pack keeps its own complete list for get_puzzles_by_theme(), while the tag, ELO and
# difficulty queries remove repeats by the puzzle's "id".
func _load_pack_directory(dir_path: String):
	var dir = DirAccess.open(dir_path)
	if not dir:
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json"):
			var pack = load_puzzle(dir_path + file_name)
			for puzzle in pack.get("puzzles", []):
				_all_puzzles.append(puzzle)
		file_name = dir.get_next()
	dir.list_dir_end()

func _unique(puzzles: Array) -> Array:
	var seen = {}
	var result = []
	for puzzle in puzzles:
		var id = puzzle.get("id", "")
		if id != "":
			if seen.has(id):
				continue
			seen[id] = true
		result.append(puzzle)
	return result

func load_puzzle(path: String) -> Dictionary:
	var file = FileAccess.open(path, FileAccess.READ)
	if not file:
		printerr("Failed to load puzzle: ", path)
		return {}
	
	var json_string = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var error = json.parse(json_string)
	
	if error != OK:
		printerr("Failed to parse puzzle JSON: ", path)
		return {}
	
	return json.data

# Get puzzles filtered by criteria
func get_puzzles_by_theme(theme: String) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		if puzzle.get("theme", "") == theme:
			filtered.append(puzzle)
	return filtered

func get_puzzles_by_elo(player_elo: int) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		var min_elo = puzzle.get("elo_min", 0)
		var max_elo = puzzle.get("elo_max", 3000)
		if player_elo >= min_elo and player_elo <= max_elo:
			filtered.append(puzzle)
	return _unique(filtered)

func get_puzzles_by_tag(tag: String) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		var tags = puzzle.get("tags", [])
		if tag in tags:
			filtered.append(puzzle)
	return _unique(filtered)

func get_puzzles_by_difficulty(difficulty: String) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		if puzzle.get("difficulty", "") == difficulty:
			filtered.append(puzzle)
	return _unique(filtered)

# Get random puzzle matching criteria
func get_random_puzzle_by_theme(theme: String) -> Dictionary:
	var puzzles = get_puzzles_by_theme(theme)
	if puzzles.size() == 0:
		return {}
	return puzzles[randi() % puzzles.size()]

func get_random_puzzle_by_elo(player_elo: int) -> Dictionary:
	var puzzles = get_puzzles_by_elo(player_elo)
	if puzzles.size() == 0:
		return {}
	return puzzles[randi() % puzzles.size()]

func get_all_themes() -> Array:
	var themes = []
	for puzzle in _all_puzzles:
		var theme = puzzle.get("theme", "")
		if theme != "" and theme not in themes:
			themes.append(theme)
	return themes

func get_all_tags() -> Array:
	var all_tags = []
	for puzzle in _all_puzzles:
		var tags = puzzle.get("tags", [])
		for tag in tags:
			if tag not in all_tags:
				all_tags.append(tag)
	return all_tags

# ---- Drill batches (made by Tools/PuzzleHarvester.html) ----
# Every puzzle in Data/PuzzlePacks/<batch>.json carries "batch" ("1a", "3b", ...), "batch_title" and "order".
# A batch runs easiest to hardest, so get_batch() returns its puzzles sorted by rating.
func get_batch(batch_id: String) -> Array:
	var result = []
	for puzzle in _all_puzzles:
		if puzzle.get("batch", "") == batch_id:
			result.append(puzzle)
	result.sort_custom(func(a, b): return a.get("rating", 0) < b.get("rating", 0))
	return result

# Batch ids in drill order, e.g. ["1a", "1b", ..., "5d"]; only batches that were actually harvested.
func get_batches() -> Array:
	var order = {}
	for puzzle in _all_puzzles:
		var id = puzzle.get("batch", "")
		if id != "":
			order[id] = puzzle.get("order", 0)
	var ids = order.keys()
	ids.sort_custom(func(a, b): return order[a] < order[b])
	return ids

func get_batch_title(batch_id: String) -> String:
	for puzzle in _all_puzzles:
		if puzzle.get("batch", "") == batch_id:
			return puzzle.get("batch_title", batch_id)
	return batch_id
