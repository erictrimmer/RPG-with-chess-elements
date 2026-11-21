extends Resource
class_name BotProfile

@export_group("Identity")
@export var bot_name: String = "Generic Bot"
@export var avatar: Texture2D
@export_multiline var description: String = ""

@export_group("Chess Settings")
@export_range(100, 3500) var elo: int = 800
@export var opening_book: Dictionary = {}
# Dictionary format: { "fen_substring": "uci_move" }
# Example: { "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": "e2e4" }
@export var opening_book_path: String = ""
# If set, StandardBot loads the opening book from this JSON file at runtime
# instead of using the inline opening_book dictionary above.

@export_group("Behavior")
@export var color_preference: String = "any" # "white", "black", "any"
@export var start_dialog: String = "Good luck!"
@export var win_dialog: String = "Checkmate."
@export var lose_dialog: String = "You played well."

@export_group("Dialogue")
@export_file("*.json") var dialogue_path: String = ""
# Per-bot text-bubble lines (see Data/Dialogue/bobby.json). Events the file does not define fall
# back to Data/Dialogue/default.json.
