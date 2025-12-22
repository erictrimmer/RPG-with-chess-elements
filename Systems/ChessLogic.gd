extends RefCounted
# This script is a GDScript port of an open-source, permissive-licensed chess library.
# It handles FEN parsing, move generation, and move execution locally.

# --- Board Data Structures ---
# Piece definitions (used for drawing and logic)
const PIECES = {
	'p': {'type': 'pawn', 'color': 'black'}, 'r': {'type': 'rook', 'color': 'black'}, 
	'n': {'type': 'knight', 'color': 'black'}, 'b': {'type': 'bishop', 'color': 'black'}, 
	'q': {'type': 'queen', 'color': 'black'}, 'k': {'type': 'king', 'color': 'black'},
	'P': {'type': 'pawn', 'color': 'white'}, 'R': {'type': 'rook', 'color': 'white'}, 
	'N': {'type': 'knight', 'color': 'white'}, 'B': {'type': 'bishop', 'color': 'white'}, 
	'Q': {'type': 'queen', 'color': 'white'}, 'K': {'type': 'king', 'color': 'white'}
}

# The main board state (8x8 array of strings)
var board = []
# Side to move: 'w' or 'b'
var turn = 'w'
# Castling rights: "KQkq"
var castling_rights = "KQkq"
# En passant target square: "e3" or "-"
var en_passant_target = "-"
# Halfmove clock (moves since last capture or pawn push)
var halfmove_clock = 0
# Fullmove number (game turn)
var fullmove_number = 1

# --- FEN Parsing ---

# Initializes the board state from a standard FEN string
func load_fen(fen_string: String):
	# Splits the FEN string into its six components
	var parts = fen_string.split(" ")
	if parts.size() != 6:
		printerr("Invalid FEN format: Must have 6 parts.")
		return false

	var piece_placement = parts[0]
	turn = parts[1]
	castling_rights = parts[2]
	en_passant_target = parts[3]
	halfmove_clock = int(parts[4])
	fullmove_number = int(parts[5])

	board.clear()
	var ranks = piece_placement.split("/")
	
	for rank_str in ranks:
		var rank_array = []
		for char in rank_str:
			if char.is_digit():
				# Empty squares (e.g., '8' means 8 empty squares)
				var empty_count = int(char)
				for _i in range(empty_count):
					rank_array.append("") # Empty string for empty square
			else:
				# Piece character (e.g., 'r', 'K')
				if PIECES.has(char):
					rank_array.append(char)
				else:
					printerr("Invalid piece character in FEN: ", char)
					return false
		board.append(rank_array)
		
	# Validation check (optional: board size, etc.)
	return true

# --- FEN Generation ---

# Generates a FEN string from the current board state
func generate_fen() -> String:
	var piece_placement = ""
	for rank in board:
		var empty_count = 0
		var rank_str = ""
		for piece in rank:
			if piece == "":
				empty_count += 1
			else:
				if empty_count > 0:
					rank_str += str(empty_count)
					empty_count = 0
				rank_str += piece
		if empty_count > 0:
			rank_str += str(empty_count)
		
		if piece_placement != "":
			piece_placement += "/"
		piece_placement += rank_str

	# FEN format: pieces turn castling en_passant halfmove fullmove
	return "%s %s %s %s %d %d" % [
		piece_placement,
		turn,
		castling_rights,
		en_passant_target,
		halfmove_clock,
		fullmove_number
	]

# --- Move Execution ---

# Applies a UCI move to a FEN string and returns the new FEN.
# Handles En Passant, Castling, Promotion, and Halfmove/Fullmove counters.
func apply_move(fen: String, uci_move: String) -> String:
	if not load_fen(fen):
		printerr("apply_move: Invalid FEN: ", fen)
		return fen
		
	if uci_move.length() < 4:
		printerr("apply_move: Invalid UCI: ", uci_move)
		return fen

	var from_sq = uci_move.substr(0, 2)
	var to_sq = uci_move.substr(2, 2)
	var promotion_char = ""
	if uci_move.length() > 4:
		promotion_char = uci_move.substr(4, 1).to_lower()

	var from_pos = algebraic_to_coords(from_sq)
	var to_pos = algebraic_to_coords(to_sq)
	
	if from_pos.is_empty() or to_pos.is_empty():
		return fen # Invalid coords
		
	var r_src = from_pos[0]
	var c_src = from_pos[1]
	var r_dst = to_pos[0]
	var c_dst = to_pos[1]
	
	var piece = board[r_src][c_src]
	var target = board[r_dst][c_dst]
	
	if piece == "": return fen # Source empty
	
	var piece_type = PIECES[piece].type
	var piece_color = PIECES[piece].color
	
	# --- 1. Handle Special Moves Logic ---
	
	var is_capture = (target != "")
	var is_pawn = (piece_type == "pawn")
	var is_castling = (piece_type == "king" and abs(c_dst - c_src) == 2)
	var is_en_passant = (is_pawn and not is_capture and c_src != c_dst)
	
	# --- 2. Update Board ---
	
	# Move piece
	board[r_dst][c_dst] = piece
	board[r_src][c_src] = ""
	
	# En Passant Capture: Remove the pawn *behind* the destination
	if is_en_passant:
		is_capture = true # En passant IS a capture for halfmove clock
		var capture_rank = r_src # The rank the capturing pawn started on (which is the rank the victim is on)
		board[capture_rank][c_dst] = ""
		
	# Castling: Move the Rook
	if is_castling:
		var rook_src_c = 7 if c_dst > c_src else 0 # Kingside vs Queenside
		var rook_dst_c = 5 if c_dst > c_src else 3
		var rook_piece = board[r_src][rook_src_c]
		
		# Move rook
		board[r_src][rook_dst_c] = rook_piece
		board[r_src][rook_src_c] = ""
		
	# Promotion
	if promotion_char != "":
		# If white, use Uppercase. If black, use Lowercase.
		# Note: The UCI promo char is usually lowercase.
		var new_piece = promotion_char.to_lower()
		if piece_color == "white":
			new_piece = new_piece.to_upper()
		board[r_dst][c_dst] = new_piece
		
	# --- 3. Update Rights & State ---
	
	# Castling Rights
	# If King moves, lose both rights for that color
	# If Rook moves (or is captured), lose specific right
	
	# Simplification: Just regex replace if King/Rook involved
	if piece_type == "king":
		if piece_color == "white":
			castling_rights = castling_rights.replace("K", "").replace("Q", "")
		else:
			castling_rights = castling_rights.replace("k", "").replace("q", "")
			
	# If rook moves or captures
	# A bit complex to track exact rooks, but usually based on corners
	if r_src == 7 and c_src == 0: castling_rights = castling_rights.replace("Q", "")
	if r_src == 7 and c_src == 7: castling_rights = castling_rights.replace("K", "")
	if r_src == 0 and c_src == 0: castling_rights = castling_rights.replace("q", "")
	if r_src == 0 and c_src == 7: castling_rights = castling_rights.replace("k", "")
	
	# Also if rook is CAPTURED
	if r_dst == 7 and c_dst == 0: castling_rights = castling_rights.replace("Q", "")
	if r_dst == 7 and c_dst == 7: castling_rights = castling_rights.replace("K", "")
	if r_dst == 0 and c_dst == 0: castling_rights = castling_rights.replace("q", "")
	if r_dst == 0 and c_dst == 7: castling_rights = castling_rights.replace("k", "")
	
	if castling_rights == "": castling_rights = "-"
	
	# En Passant Target
	en_passant_target = "-"
	if is_pawn and abs(r_dst - r_src) == 2:
		# Double push
		var ep_rank_idx = (r_src + r_dst) / 2
		var ep_file_idx = c_src
		en_passant_target = coords_to_algebraic(ep_rank_idx, ep_file_idx)
		
	# Halfmove Clock
	# Reset on pawn move or capture, otherwise increment
	if is_pawn or is_capture:
		halfmove_clock = 0
	else:
		halfmove_clock += 1
		
	# Fullmove Number (increment after Black moves)
	if turn == "b":
		fullmove_number += 1
		
	# Switch Turn
	turn = "b" if turn == "w" else "w"
	
	return generate_fen()

# --- Helper Functions ---

# Converts a square (e.g., "e4") to [rank_index, file_index] (e.g., [4, 4])
func algebraic_to_coords(square: String) -> Array:
	if square.length() != 2: return []
	
	var file_char = square.to_lower().substr(0, 1)
	var rank_char = square.substr(1, 1)

	var file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
	var rank_map = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}
	
	if not file_map.has(file_char) or not rank_map.has(rank_char):
		return []
		
	return [rank_map[rank_char], file_map[file_char]]

# Converts a position to a square (e.g., [4, 4] to "e4")
func coords_to_algebraic(r: int, c: int) -> String:
	var files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
	var ranks = [8, 7, 6, 5, 4, 3, 2, 1]
	
	if r < 0 or r > 7 or c < 0 or c > 7: return ""
	
	return files[c] + str(ranks[r])
