extends Sprite2D

# --- Properties for Board Script to Assign ---
# CRITICAL FIX: Explicitly declaring 'fen_char' allows board.gd to assign to it.
var fen_char: String = ""

# Internal properties derived from fen_char
var is_white: bool = true
var piece_type: String = "P" # K, Q, R, B, N, P

# --- Texture Constants ---
# IMPORTANT: These paths are now configured to: res://Assets/Sprites/pieces/
# Ensure your image files use the standard naming convention (e.g., 'wp.png' for White Pawn)

const WHITE_PAWN_TEX = preload("res://Assets/Sprites/pieces/wp.png")
const BLACK_PAWN_TEX = preload("res://Assets/Sprites/pieces/bp.png")
const WHITE_ROOK_TEX = preload("res://Assets/Sprites/pieces/wr.png")
const BLACK_ROOK_TEX = preload("res://Assets/Sprites/pieces/br.png")
const WHITE_KNIGHT_TEX = preload("res://Assets/Sprites/pieces/wn.png")
const BLACK_KNIGHT_TEX = preload("res://Assets/Sprites/pieces/bn.png")
const WHITE_BISHOP_TEX = preload("res://Assets/Sprites/pieces/wb.png")
const BLACK_BISHOP_TEX = preload("res://Assets/Sprites/pieces/bb.png")
const WHITE_QUEEN_TEX = preload("res://Assets/Sprites/pieces/wq.png")
const BLACK_QUEEN_TEX = preload("res://Assets/Sprites/pieces/bq.png")
const WHITE_KING_TEX = preload("res://Assets/Sprites/pieces/wk.png")
const BLACK_KING_TEX = preload("res://Assets/Sprites/pieces/bk.png")

# Map FEN character type and color (True=White) to the Texture
var piece_texture_map = {
	"P": { true: WHITE_PAWN_TEX, false: BLACK_PAWN_TEX },
	"R": { true: WHITE_ROOK_TEX, false: BLACK_ROOK_TEX },
	"N": { true: WHITE_KNIGHT_TEX, false: BLACK_KNIGHT_TEX },
	"B": { true: WHITE_BISHOP_TEX, false: BLACK_BISHOP_TEX },
	"Q": { true: WHITE_QUEEN_TEX, false: BLACK_QUEEN_TEX },
	"K": { true: WHITE_KING_TEX, false: BLACK_KING_TEX },
}

# --- Initialization Method (Called by board.gd) ---
func set_fen_char(char: String):
	fen_char = char
	
	# 1. Determine Color: Uppercase is White
	is_white = (char.to_upper() == char)
	
	# 2. Determine Type: The piece type is the uppercase character
	piece_type = char.to_upper()
	
	# 3. Apply the texture
	set_piece_texture()


func _ready():
	# Ensures the piece is centered on the square's position
	centered = true
	
	# Fallback texture setting if piece is placed manually in editor
	if piece_type in piece_texture_map:
		set_piece_texture()


func set_piece_texture():
	if piece_type in piece_texture_map:
		var color_map = piece_texture_map[piece_type]
		if is_white in color_map:
			self.texture = color_map[is_white]
		else:
			print("Error: Texture color configuration missing for type:", piece_type)
	else:
		print("Error: Invalid piece type provided:", piece_type)
