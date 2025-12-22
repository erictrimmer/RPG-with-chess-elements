extends BotBase

func _init():
	bot_name = "Bobby"
	# Initialize Fischer-esque Opening Repertoire
	_load_repertoire()

func _load_repertoire():
	# Key: FEN (Position + Turn + Castling + EP)
	# Value: UCI Move
	
	# Load from JSON file
	var file_path = "res://Assets/Data/fischer_openings.json"
	if FileAccess.file_exists(file_path):
		var file = FileAccess.open(file_path, FileAccess.READ)
		var text = file.get_as_text()
		var json = JSON.new()
		var error = json.parse(text)
		if error == OK:
			var data = json.data
			if typeof(data) == TYPE_DICTIONARY:
				for fen_key in data:
					# Validate basic FEN structure to be safe, or just trust the file
					opening_book[fen_key] = data[fen_key]
				print("Bobby Loaded Repertoire: ", opening_book.size(), " lines.")
			else:
				printerr("Opening book JSON format error (not a dictionary).")
		else:
			printerr("JSON Parse Error: ", json.get_error_message())
	else:
		printerr("Opening book file not found: ", file_path)
		# Fallback to tiny baked-in set
		opening_book["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"] = "e2e4"
