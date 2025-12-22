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
	
	_puzzles_loaded = true
	print("Loaded ", _all_puzzles.size(), " puzzles")

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
	return filtered

func get_puzzles_by_tag(tag: String) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		var tags = puzzle.get("tags", [])
		if tag in tags:
			filtered.append(puzzle)
	return filtered

func get_puzzles_by_difficulty(difficulty: String) -> Array:
	var filtered = []
	for puzzle in _all_puzzles:
		if puzzle.get("difficulty", "") == difficulty:
			filtered.append(puzzle)
	return filtered

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
