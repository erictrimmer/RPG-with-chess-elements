extends Node
class_name BotBase

# Signal emitted when the bot has chosen a move
signal move_chosen(uci_move: String)

var bot_name: String = "Generic Bot"
var playing_color: bool = false # false = black, true = white

# Opening book: Dictionary mapping FEN keys (partial) to move strings
# Example: {"rnbqk...": "e2e4"}
var opening_book: Dictionary = {}

func initialize(is_white: bool):
	playing_color = is_white
	print(bot_name + " initialized. Playing White? " + str(playing_color))

# Main entry point for requesting a move
func request_move(fen: String, valid_moves: Array):
	# 1. Check opening book
	# We need a simplified FEN usually (position only), but full FEN is fine if keys match exactly
	# Or, more robustly, match the board state part of FEN
	
	# Simplify FEN for lookup (remove clock/move counts if needed) or just use full string
	# Ideally, we key by "rnbqk..." part + active color + castling + ep
	var fen_parts = fen.split(" ")
	var fen_key = "%s %s %s %s" % [fen_parts[0], fen_parts[1], fen_parts[2], fen_parts[3]]
	
	if opening_book.has(fen_key):
		var book_move = opening_book[fen_key]
		print(bot_name + " found book move: " + book_move)
		
		# Validate book move is actually valid? (Ideally yes)
		# For now, trust the book.
		
		# Simulate "thinking" delay for realism
		await get_tree().create_timer(0.5).timeout
		emit_signal("move_chosen", book_move)
		return

	# 2. If no book move, fallback to Engine calculation
	# This function should be overridden by specific bots or utilize the globally available ChessEngine
	_calculate_engine_move(fen)

func _calculate_engine_move(fen: String):
	# Default implementation calls the GameManager's engine request indirectly
	# BUT, since Bot is a script, it might easier to signal "use_engine"
	# Or the GameManager calls this, and if it returns nothing, GameManager uses Engine.
	
	# Current Architecture: GameManager handles Engine.
	# So if this function emits "move_chosen" with "", GameManager knows to ask Engine?
	# Better: This bot should interact with the ChessEngine directly or mimic it.
	
	# For simplicity: Emitting an explicit signal "use_engine" logic
	# Actually, simpler: The Bot returns null or emits special signal if it wants the engine to take over.
	print(bot_name + " out of book. Requesting engine calculation.")
	emit_signal("move_chosen", "ENGINE_CALC")
