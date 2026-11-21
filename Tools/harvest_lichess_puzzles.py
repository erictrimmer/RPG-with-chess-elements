#!/usr/bin/env python3
"""SUPERSEDED by Tools/PuzzleHarvester.html (drill batches). Kept as a command-line alternative for per-piece packs.

Harvests elementary checkmate puzzles from the Lichess puzzle database into small JSON "packs"
that PuzzleManager loads. The Lichess puzzle database is CC0 (public domain).

The CSV is read ONE ROW AT A TIME, so the 1+ GB file never has to fit in memory.

Usage (from the project folder):
    pip install chess
    python Tools/harvest_lichess_puzzles.py
Options:
    --input  Puzzles/lichess_db_puzzle.csv     the downloaded database
    --out    Data/PuzzlePacks                  where the packs are written
    --per-pack 150                             max puzzles per pack
    --max-rating 1200                          elementary = low rated
    --min-popularity 70                        Lichess community score (-100..100)
    --min-plays 200                            ignore barely-played puzzles
    --max-pieces 16                            prefer clean boards: skip crowded positions

What it does with each puzzle
  * The CSV FEN is the position BEFORE the opponent's last move; the real puzzle starts after it.
    We play that first move for you.
  * Mate-in-1 puzzles are kept only when exactly ONE move mates (a drill should have one answer).
  * Puzzles keep their own side to move: the game puts the player on whichever colour is to move
    and turns the board to match. (Pass --flip-black to mirror black-to-move puzzles into
    white-to-move ones instead; the "mirrored" field records when that happened.)
  * Mate-in-1 puzzles are filed by the piece that delivers mate (rook, queen, bishop, knight,
    pawn, promotion, discovered, double_check) and ALSO by Lichess's mate-pattern tags
    (back rank, smothered, Anastasia's, Arabian, ...).
  * Mate-in-2 puzzles go in one pack and carry the full "solution" line.
Output files: Data/PuzzlePacks/<pack>.json  =>  {"pack": ..., "puzzles": [ {...}, ... ]}
"""
import argparse, csv, heapq, json, os, sys
try:
    import chess
except ImportError:
    sys.exit("This script needs the python-chess library:  pip install chess")

PIECE_PACKS = {
    chess.ROOK: "rook", chess.QUEEN: "queen", chess.BISHOP: "bishop",
    chess.KNIGHT: "knight", chess.PAWN: "pawn", chess.KING: "king",
}
PIECE_NAMES = {"rook": "rook", "queen": "queen", "bishop": "bishop", "knight": "knight",
               "pawn": "pawn", "king": "king", "promotion": "promoted pawn",
               "discovered": "discovered check", "double_check": "double check"}
# Lichess theme -> (pack slug, nice name, hint)
PATTERNS = {
    "backRankMate":    ("back_rank", "back rank mate", "The king is trapped behind its own pawns. Attack the back rank."),
    "smotheredMate":   ("smothered", "smothered mate", "The king is surrounded by its own pieces. A knight can reach it."),
    "anastasiaMate":   ("anastasia", "Anastasia's mate", "A knight and a rook trap the king against the edge of the board."),
    "arabianMate":     ("arabian", "Arabian mate", "A rook and a knight mate a king stuck in the corner."),
    "bodenMate":       ("boden", "Boden's mate", "Two bishops attack along crossing diagonals."),
    "doubleBishopMate":("double_bishop", "double bishop mate", "Two bishops cover the king's escape squares."),
    "dovetailMate":    ("dovetail", "dovetail mate", "A queen next to the king, with the escape squares blocked by its own pieces."),
    "hookMate":        ("hook", "hook mate", "A rook, a knight and a pawn work together."),
    "killBoxMate":     ("kill_box", "kill box mate", "A rook protected by a queen boxes in the king."),
    "vukovicMate":     ("vukovic", "Vukovic mate", "A rook mates with help from a knight and another piece."),
    "balestraMate":    ("balestra", "Balestra mate", "A bishop and a queen deliver the mate."),
    "morphysMate":     ("morphy", "Morphy's mate", "A bishop and a rook mate the king."),
    "operaMate":       ("opera", "Opera mate", "A bishop and a rook mate on the back rank."),
    "pillsburysMate":  ("pillsbury", "Pillsbury's mate", "A rook and a bishop mate along the edge."),
    "triangleMate":    ("triangle", "triangle mate", "A queen and a rook, one square apart, trap the king."),
    "swallowstailMate":("swallowtail", "swallow's tail mate", "A queen right in front of the king; its own pieces block the escape."),
    "blindSwineMate":  ("blind_swine", "blind swine mate", "Two rooks on the seventh rank."),
    "cornerMate":      ("corner", "corner mate", "The king is stuck in the corner."),
}

def mirror_move(m):
    return chess.Move(chess.square_mirror(m.from_square), chess.square_mirror(m.to_square),
                      m.promotion)

def piece_count(board):
    return len(board.piece_map())

def mating_moves(board):
    out = []
    for mv in board.legal_moves:
        board.push(mv)
        if board.is_checkmate():
            out.append(mv)
        board.pop()
    return out

def classify_mate_in_1(board_before, mate_move):
    """Which piece delivered mate? (board_before = position where the mating move is played)"""
    if mate_move.promotion:
        return "promotion"
    mover_type = board_before.piece_type_at(mate_move.from_square)
    board_after = board_before.copy()
    board_after.push(mate_move)
    checkers = list(board_after.checkers())
    if len(checkers) >= 2:
        return "double_check"
    if checkers and checkers[0] != mate_move.to_square:
        return "discovered"
    return PIECE_PACKS.get(mover_type, "other")

def article(word):
    return "an" if word[0].lower() in "aeiou" else "a"

def build_puzzle(row, board, moves, kind, mirrored, pack_key, pattern=None, bucket_piece=None):
    rating = int(row["Rating"])
    side = "White" if board.turn == chess.WHITE else "Black"
    lines = [m.uci() for m in moves]
    themes = row["Themes"].split()
    tags = ["mate_in_1" if kind == 1 else "mate_in_2"]
    if bucket_piece: tags.append(bucket_piece + "_mate")
    if pattern: tags.append(PATTERNS[pattern][0])
    tags.append("elementary" if rating < 1000 else "beginner")
    if kind == 1:
        if pattern:
            success = f"Checkmate! That's {article(PATTERNS[pattern][1])} {PATTERNS[pattern][1]}."
            hint = PATTERNS[pattern][2]
        elif bucket_piece:
            who = PIECE_NAMES.get(bucket_piece, bucket_piece)
            success = f"Checkmate! The {who} delivers mate." if bucket_piece not in ("discovered", "double_check", "promotion") else f"Checkmate by {who}!"
            hint = "Find the check where the king has no escape and nothing can block or capture."
        instruction = f"{side} to move. Deliver checkmate in one move!"
    else:
        success = "Checkmate in two! Well done."
        hint = "Look for a forcing first move: the king must have no good reply."
        instruction = f"{side} to move. Checkmate in two moves!"
    if pattern:
        name = f"{PATTERNS[pattern][1].capitalize()} #{row['PuzzleId']}"
    elif kind == 1:
        name = f"{PIECE_NAMES.get(bucket_piece, bucket_piece).capitalize()} mate in 1 #{row['PuzzleId']}"
    else:
        name = f"Mate in 2 #{row['PuzzleId']}"
    return {
        "id": row["PuzzleId"],
        "name": name,
        "elo_min": max(100, rating - 150),
        "elo_max": rating + 250,
        "theme": pack_key,
        "difficulty": "easy" if rating < 800 else ("medium" if rating < 1200 else "hard"),
        "fen": board.fen(),
        "objective_move": lines[0],
        "solution": lines,
        "instruction": instruction,
        "success_text": success,
        "hint": hint,
        "tags": tags,
        "mirrored": mirrored,
        "rating": rating,
        "source": "lichess puzzle database (CC0)",
    }

def prepare(row, kind, flip_black=False):
    """Returns (board at puzzle start, player moves list, mirrored) or None."""
    try:
        board = chess.Board(row["FEN"])
        seq = [chess.Move.from_uci(u) for u in row["Moves"].split()]
    except ValueError:
        return None
    if len(seq) < 2:
        return None
    # first move belongs to the opponent
    if seq[0] not in board.legal_moves:
        return None
    board.push(seq[0])
    seq = seq[1:]
    mirrored = False
    if board.turn == chess.BLACK and flip_black:
        board = board.mirror()          # flips the board and swaps colours; White is now to move
        seq = [mirror_move(m) for m in seq]
        mirrored = True
    # replay and validate
    test = board.copy()
    for m in seq:
        if m not in test.legal_moves:
            return None
        test.push(m)
    if not test.is_checkmate():
        return None
    return board, seq, mirrored

def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join(root, "Puzzles", "lichess_db_puzzle.csv"))
    ap.add_argument("--out", default=os.path.join(root, "Data", "PuzzlePacks"))
    ap.add_argument("--per-pack", type=int, default=150)
    ap.add_argument("--max-rating", type=int, default=1200)
    ap.add_argument("--min-popularity", type=int, default=70)
    ap.add_argument("--min-plays", type=int, default=200)
    ap.add_argument("--max-pieces", type=int, default=16)
    ap.add_argument("--no-mate-in-2", action="store_true")
    ap.add_argument("--flip-black", action="store_true",
                    help="mirror black-to-move puzzles so White always moves (not needed by the game)")
    args = ap.parse_args()

    heaps = {}      # pack -> heap of (score, counter, puzzle)
    seen = {}       # pack -> set of piece placements already taken
    counter = 0
    rows = kept = 0

    def offer(pack, score, puzzle, placement):
        nonlocal counter
        h = heaps.setdefault(pack, [])
        s = seen.setdefault(pack, set())
        if placement in s:
            return
        counter += 1
        if len(h) < args.per_pack:
            heapq.heappush(h, (score, counter, puzzle)); s.add(placement)
        elif score > h[0][0]:
            old = heapq.heapreplace(h, (score, counter, puzzle))
            s.discard(old[2]["fen"].split()[0]); s.add(placement)

    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows += 1
            if rows % 500000 == 0:
                print(f"  ...{rows:,} rows read, {kept:,} candidates", file=sys.stderr)
            themes = row["Themes"].split()
            kind = 1 if "mateIn1" in themes else (2 if "mateIn2" in themes and not args.no_mate_in_2 else 0)
            if not kind:
                continue
            try:
                rating = int(row["Rating"]); pop = int(row["Popularity"]); plays = int(row["NbPlays"])
            except ValueError:
                continue
            if rating > args.max_rating or pop < args.min_popularity or plays < args.min_plays:
                continue
            prep = prepare(row, kind, args.flip_black)
            if prep is None:
                continue
            board, seq, mirrored = prep
            pieces = piece_count(board)
            if pieces > args.max_pieces:
                continue
            score = pop - 3 * pieces - rating / 100.0     # popular, uncluttered, easy
            placement = board.fen().split()[0]

            if kind == 1:
                mates = mating_moves(board)
                if len(mates) != 1:            # a drill needs exactly one answer
                    continue
                piece = classify_mate_in_1(board, seq[0])
                kept += 1
                offer(f"{piece}_mate_in_1", score,
                      build_puzzle(row, board, seq, 1, mirrored, f"{piece}_mate_in_1", None, piece), placement)
                for t in themes:
                    if t in PATTERNS:
                        slug = PATTERNS[t][0]
                        offer(f"{slug}_mate_in_1", score,
                              build_puzzle(row, board, seq, 1, mirrored, f"{slug}_mate_in_1", t, piece), placement)
            else:
                kept += 1
                offer("mate_in_2", score, build_puzzle(row, board, seq, 2, mirrored, "mate_in_2"), placement)

    os.makedirs(args.out, exist_ok=True)
    for old in os.listdir(args.out):
        if old.endswith(".json"):
            os.remove(os.path.join(args.out, old))   # regenerate cleanly
    summary = []
    for pack, h in sorted(heaps.items()):
        puzzles = [p for _, _, p in sorted(h, key=lambda t: -t[0])]
        with open(os.path.join(args.out, pack + ".json"), "w", encoding="utf-8") as out:
            json.dump({"pack": pack, "source": "Lichess puzzle database (CC0)", "puzzles": puzzles}, out, indent=1)
        summary.append((pack, len(puzzles)))
    print(f"\nRead {rows:,} rows; {kept:,} usable puzzles; wrote {len(summary)} packs to {args.out}")
    for pack, n in summary:
        print(f"  {pack:28s} {n:4d}")

if __name__ == "__main__":
    main()
