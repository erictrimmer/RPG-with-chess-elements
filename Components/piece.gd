extends Sprite2D

# Piece properties
# RENAMED from 'Color' to 'PieceColor' to avoid conflict with Godot's built-in Color type.
enum PieceColor { WHITE, BLACK }
enum Type { PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING }

var piece_color: int
var piece_type: int

# Dictionary to map FEN characters to resource paths
const PIECE_TEXTURE_MAP = {
	"P": "res://Assets/Sprites/pieces/wp.png", # White Pawn
	"N": "res://Assets/Sprites/pieces/wn.png", # White Knight
	"B": "res://Assets/Sprites/pieces/wb.png", # White Bishop
	"R": "res://Assets/Sprites/pieces/wr.png", # White Rook
	"Q": "res://Assets/Sprites/pieces/wq.png", # White Queen
	"K": "res://Assets/Sprites/pieces/wk.png", # White King
	
	"p": "res://Assets/Sprites/pieces/bp.png", # Black Pawn
	"n": "res://Assets/Sprites/pieces/bn.png", # Black Knight
	"b": "res://Assets/Sprites/pieces/bb.png", # Black Bishop
	"r": "res://Assets/Sprites/pieces/br.png", # Black Rook
	"q": "res://Assets/Sprites/pieces/bq.png", # Black Queen
	"k": "res://Assets/Sprites/pieces/bk.png", # Black King
}

# New initialization function called by Board.gd
func initialize_piece(fen_char: String, target_size: int):
	# 1. Load texture and set properties
	var texture_path = set_piece_from_fen(fen_char)
	
	if texture_path:
		var tex = load(texture_path)
		if tex:
			self.texture = tex
			# 2. Scale piece to fit target square size
			var tex_size = texture.get_size()
			var scale_factor = float(target_size) / float(max(tex_size.x, tex_size.y))
			
			# Fix: Use Linear filtering for these high-res pieces scaled down to 16px
			texture_filter = TextureFilter.TEXTURE_FILTER_LINEAR
			
			scale = Vector2(scale_factor, scale_factor)
		else:
			print("Piece ERROR: Could not load texture: ", texture_path)
			# Fallback: Magenta Block
			texture = PlaceholderTexture2D.new()
			modulate = Color(1, 0, 1, 1) # MAGENTA
			queue_free()
	else:
		# If set_piece_from_fen returned null (invalid FEN char), it already called queue_free()
		pass

func _enter_tree():
	# print("  Piece: Entered Tree! Name: ", name)
	pass

func _ready():
	z_index = 10 # Force on top of board
	# print("  Piece: _ready() called. Visible? ", visible, " Pos: ", position, " Z: ", z_index)

func _exit_tree():
	# print("  Piece: Exited Tree! Name: ", name)
	pass

# Sets the piece's appearance based on the FEN character
# Returns texture path if valid, null otherwise
func set_piece_from_fen(fen_char: String):
	if fen_char in PIECE_TEXTURE_MAP:
		# Set piece type and color based on the character
		piece_color = PieceColor.WHITE if fen_char.to_upper() == fen_char else PieceColor.BLACK
		
		match fen_char.to_lower():
			"p": piece_type = Type.PAWN
			"n": piece_type = Type.KNIGHT
			"b": piece_type = Type.BISHOP
			"r": piece_type = Type.ROOK
			"q": piece_type = Type.QUEEN
			"k": piece_type = Type.KING
			
		return PIECE_TEXTURE_MAP[fen_char]
		
	else:
		# Should not happen if FEN is valid, but good for error handling
		print("ERROR: Invalid FEN character: ", fen_char)
		queue_free() # Remove invalid piece
		return null

func is_white() -> bool:
	return piece_color == PieceColor.WHITE
