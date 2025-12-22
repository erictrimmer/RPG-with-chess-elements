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

func request_move(fen: String, valid_moves: Array):
	# 1. Opening Book Check
	# We try to match FEN substrings ideally (e.g. just position)
	# For now, simplistic FEN matching or exact match
	var fen_parts = fen.split(" ")
	var fen_key = "%s %s %s %s" % [fen_parts[0], fen_parts[1], fen_parts[2], fen_parts[3]]
	
	# Check our profile's book
	if profile.opening_book.has(fen_key):
		var book_move = profile.opening_book[fen_key]
		print(bot_name + " (StandardBot) found book move: " + book_move)
		
		# Fake thinking delay
		await get_tree().create_timer(0.5 + (randf() * 0.5)).timeout
		emit_signal("move_chosen", book_move)
		return
	
	# 2. Engine Fallback
	# We rely on the Engine to calculate if out of book.
	# We pass "ENGINE_CALC" but we might need to set the ELO somewhere?
	# Does the engine support per-request ELO? Not currently via simple signal.
	# But GameManager knows 'bot_difficulty_ms' or '_targetElo'.
	# We should ideally communicate the profile's ELO to the GameManager.
	
	print(bot_name + " out of book. Using ELO: " + str(profile.elo))
	emit_signal("move_chosen", "ENGINE_CALC")
