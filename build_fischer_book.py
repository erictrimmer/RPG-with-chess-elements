"""
Parse Fischer.pgn and build an opening book JSON.
Outputs Data/OpeningBooks/fischer_openings.json in the format:
  { "board activeColor castling enPassant": "uci_move", ... }

Only Fischer's own moves are recorded (games where he is White or Black).
Up to MAX_PLIES half-moves per game are processed.
When a position appears in multiple games, the most frequent move wins.
"""

import chess
import chess.pgn
import json
from collections import defaultdict
from pathlib import Path

PGN_PATH = Path(__file__).parent / "Data" / "Fischer.pgn"
OUT_PATH = Path(__file__).parent / "Data" / "OpeningBooks" / "fischer_openings.json"
MAX_PLIES = 50  # 25 full moves

def fen_key(board: chess.Board) -> str:
    """4-part FEN key matching BotBase's lookup: board activeColor castling enPassant"""
    parts = board.fen().split(" ")
    return " ".join(parts[:4])

def main():
    position_moves: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    games_processed = 0
    games_skipped = 0

    with open(PGN_PATH, encoding="utf-8", errors="ignore") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            fischer_is_white = "Fischer" in white
            fischer_is_black = "Fischer" in black

            if not fischer_is_white and not fischer_is_black:
                games_skipped += 1
                continue

            board = game.board()
            ply = 0

            for move in game.mainline_moves():
                if ply >= MAX_PLIES:
                    break

                is_fischer_turn = (
                    (board.turn == chess.WHITE and fischer_is_white) or
                    (board.turn == chess.BLACK and fischer_is_black)
                )

                if is_fischer_turn:
                    key = fen_key(board)
                    uci = move.uci()
                    position_moves[key][uci] += 1

                board.push(move)
                ply += 1

            games_processed += 1

    # Pick the most frequent Fischer move for each position
    opening_book = {
        key: max(moves, key=moves.get)
        for key, moves in position_moves.items()
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(opening_book, f, indent=2, ensure_ascii=False)

    print(f"Games processed : {games_processed}")
    print(f"Games skipped   : {games_skipped} (non-Fischer)")
    print(f"Positions in book: {len(opening_book)}")
    print(f"Output written to: {OUT_PATH}")

if __name__ == "__main__":
    main()
