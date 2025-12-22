extends SceneTree

func _init():
	var chess_logic = load("res://Systems/ChessLogic.gd").new()
	var passed = true
	
	print("--- TEST: En Passant ---")
	# Setup: White pawn on e5, Black pawn on d7. Black moves d7-d5. White captures e5xd6 ep.
	# "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3" -> After 1. e4 d5 2. e5
	# Actually let's use a simpler setup.
	# FEN: 8/8/8/3pP3/8/8/8/8 w - d6 0 1
	# White to move. En Passant target is d6. White pawn on e5.
	var ep_fen = "8/8/8/3pP3/8/8/8/8 w - d6 0 1"
	var ep_move = "e5d6"
	var expected_ep_fen_start = "8/8/3P4/8/8/8/8/8 b - -" 
	# Note: Black pawn at d5 should be gone. White pawn at d6.
	
	var res_ep = chess_logic.apply_move(ep_fen, ep_move)
	# Check board content manually to be safe about fullmove counters etc
	if res_ep.begins_with("8/8/3P4/8/8/8/8/8 b - -"):
		print("PASS: En Passant capture executed correctly.")
	else:
		print("FAIL: En Passant. Result: ", res_ep)
		passed = false

	print("\n--- TEST: Promotion ---")
	# White pawn on e7. Moves e7-e8Q.
	var promo_fen = "8/4P3/8/8/8/8/8/8 w - - 0 1"
	var promo_move = "e7e8q"
	var res_promo = chess_logic.apply_move(promo_fen, promo_move)
	# Should have Queen on e8
	if res_promo.begins_with("4Q3/8/8/8/8/8/8/8 b - -"):
		print("PASS: Promotion to Queen.")
	else:
		print("FAIL: Promotion. Result: ", res_promo)
		passed = false
		
	print("\n--- TEST: Castling (White Kingside) ---")
	# FEN: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1
	# Move: e1g1
	var cast_fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
	var cast_move = "e1g1"
	var res_cast = chess_logic.apply_move(cast_fen, cast_move)
	# Expect King on g1, Rook on f1.
	# "r3k2r/8/8/8/8/8/8/R4RK1 b kq - 1 1"
	if res_cast.contains("R4RK1"):
		print("PASS: White Kingside Castling.")
	else:
		print("FAIL: Castling. Result: ", res_cast)
		passed = false

	if passed:
		print("\nAll Tests Passed!")
		quit(0)
	else:
		print("\nTests Failed.")
		quit(1)
