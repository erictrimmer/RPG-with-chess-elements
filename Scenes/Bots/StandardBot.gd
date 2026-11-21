extends BotBase
class_name StandardBot

var profile: BotProfile

func _init(bot_profile: BotProfile):
	if bot_profile == null:
		printerr("StandardBot ERROR: Initialized with null profile!")
		bot_name = "Training Bot"
		return

	profile = bot_profile
	bot_name = profile.bot_name

	# Load opening book from JSON file if a path is provided
	if profile.opening_book_path != "":
		_load_opening_book_from_file(profile.opening_book_path)
	else:
		opening_book = profile.opening_book

func _load_opening_book_from_file(path: String):
	if not FileAccess.file_exists(path):
		printerr(bot_name + ": opening book file not found: " + path)
		opening_book = profile.opening_book
		return
	var file = FileAccess.open(path, FileAccess.READ)
	var json = JSON.new()
	if json.parse(file.get_as_text()) == OK and typeof(json.data) == TYPE_DICTIONARY:
		opening_book = json.data
		print(bot_name + ": loaded " + str(opening_book.size()) + " opening book positions from " + path)
	else:
		printerr(bot_name + ": failed to parse opening book JSON at " + path)
		opening_book = profile.opening_book

func request_move(fen: String, valid_moves: Array):
	var fen_parts = fen.split(" ")
	var fen_key = "%s %s %s %s" % [fen_parts[0], fen_parts[1], fen_parts[2], fen_parts[3]]

	if opening_book.has(fen_key):
		var book_move = opening_book[fen_key]
		print(bot_name + " found book move: " + book_move)
		await get_tree().create_timer(0.5 + (randf() * 0.5)).timeout
		emit_signal("move_chosen", book_move)
		return

	print(bot_name + " out of book, requesting engine (ELO " + str(profile.elo) + ")")
	emit_signal("move_chosen", "ENGINE_CALC")
