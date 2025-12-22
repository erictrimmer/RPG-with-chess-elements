import re
import json
import sys
import os

# --- Minimal Chess Engine for SAN Parsing ---

class Board:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # 8x8 board, 0 is a8, 63 is h1? No, let's use Rank/File
        # board[row][col], row 0 is Rank 8, row 7 is Rank 1
        self.board = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['.','.','.','.','.','.','.','.'],
            ['.','.','.','.','.','.','.','.'],
            ['.','.','.','.','.','.','.','.'],
            ['.','.','.','.','.','.','.','.'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']
        ]
        self.turn = 'w'
        self.castling = "KQkq"
        self.ep_target = None # (row, col)
        
    def get_fen(self):
        rows = []
        for r in range(8):
            empty = 0
            row_str = ""
            for c in range(8):
                p = self.board[r][c]
                if p == '.':
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += p
            if empty > 0:
                row_str += str(empty)
            rows.append(row_str)
        
        ep_str = "-"
        if self.ep_target:
            r, c = self.ep_target
            # coords to algebraic
            f_char = chr(ord('a') + c)
            r_char = str(8 - r)
            ep_str = f_char + r_char
            
        return "/".join(rows) + f" {self.turn} {self.castling} {ep_str}"
        
    def parse_san(self, san):
        # Strips check/mate symbols
        clean = san.replace('+', '').replace('#', '')
        
        # Castling
        if clean == 'O-O':
            return self.get_castling_move(king_side=True)
        if clean == 'O-O-O':
            return self.get_castling_move(king_side=False)
            
        # Pawn Moves (e4, exd5, a4)
        # Identify target square
        target_alg = clean[-2:]
        target_r, target_c = self.alg_to_coords(target_alg)
        
        # Identify piece type
        piece_char = 'P' if clean[0].islower() else clean[0]
        
        # Identification cues
        # Examples: Nf3, Ndf3, R1e2, Qh4e1
        discriminator = clean[:-2].replace(piece_char, '', 1) 
        if piece_char == 'P': discriminator = clean[:-2] # for cxd5 -> 'c' x 'd5' -> 'cx'
        discriminator = discriminator.replace('x', '')
        
        candidates = self.find_candidates(piece_char, target_r, target_c)
        
        matched_move = None
        
        for cand in candidates:
            # cand is ((r, c), uci_str)
            src_r, src_c = cand[0]
            
            # Check discriminator
            if discriminator:
                # File char match?
                src_f_char = chr(ord('a') + src_c)
                src_r_char = str(8 - src_r)
                
                match_file = (discriminator in src_f_char)
                match_rank = (discriminator in src_r_char)
                
                # If discriminator is full coord 'e2', we need both?
                # Usually it's just one char unless extreme ambiguity.
                
                # Simplified: if discriminator contains characters, they must ALL match properties of src
                matches_d = True
                for d in discriminator:
                    if d not in (src_f_char + src_r_char):
                        matches_d = False
                        break
                if not matches_d:
                    continue
            
            # Verify legality (pinned?)
            # We are skipping full pin checks for simplicity, assuming valid PGN.
            # But we must check pseudo-legality (knight jump pattern etc)
            matched_move = cand
            break
            
        if matched_move:
            return matched_move[1]
        
        return None

    def find_candidates(self, piece_type, tr, tc):
        # Returns list of ((sr, sc), uci)
        cands = []
        piece_map = {'N':'n', 'B':'b', 'R':'r', 'Q':'q', 'K':'k', 'P':'p'}
        target_char = piece_map[piece_type] if self.turn == 'b' else piece_type
        
        # Scan board for pieces of this type/color
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == target_char:
                    # Can this piece move to (tr, tc)?
                    move_uci = self.can_move_to(r, c, tr, tc, piece_type)
                    if move_uci:
                        cands.append(((r,c), move_uci))
        return cands

    def can_move_to(self, r, c, tr, tc, p_type):
        # Pseudos checks
        dr = tr - r
        dc = tc - c
        
        # Color multiplier for pawn direciton
        direction = -1 if self.turn == 'w' else 1
        
        if p_type == 'P':
            # Push
            if dc == 0:
                if dr == direction and self.board[tr][tc] == '.':
                    return self.to_uci(r,c,tr,tc)
                # Double push
                if (r == 6 and self.turn == 'w') or (r == 1 and self.turn == 'b'):
                    if dr == 2*direction and self.board[tr][tc] == '.' and self.board[r+direction][c] == '.':
                        return self.to_uci(r,c,tr,tc)
            # Capture
            if abs(dc) == 1 and dr == direction:
                if self.board[tr][tc] != '.':
                    return self.to_uci(r,c,tr,tc)
                # En Passant
                if self.ep_target == (tr, tc):
                    return self.to_uci(r,c,tr,tc)

        if p_type == 'N':
            if abs(dr)*abs(dc) == 2:
                return self.to_uci(r,c,tr,tc)
                
        if p_type == 'B' or p_type == 'Q':
            if abs(dr) == abs(dc):
                if self.is_clear_path(r,c,tr,tc): return self.to_uci(r,c,tr,tc)
        
        if p_type == 'R' or p_type == 'Q':
            if dr==0 or dc==0:
                if self.is_clear_path(r,c,tr,tc): return self.to_uci(r,c,tr,tc)
                
        if p_type == 'K':
            if max(abs(dr), abs(dc)) == 1:
                return self.to_uci(r,c,tr,tc)
                
        return None

    def is_clear_path(self, r1, c1, r2, c2):
        dr = 0 if r1==r2 else (1 if r2>r1 else -1)
        dc = 0 if c1==c2 else (1 if c2>c1 else -1)
        curr_r, curr_c = r1 + dr, c1 + dc
        while (curr_r, curr_c) != (r2, c2):
            if self.board[curr_r][curr_c] != '.': return False
            curr_r += dr
            curr_c += dc
        return True

    def get_castling_move(self, king_side):
        # Returns uci string e1g1 etc
        r = 7 if self.turn == 'w' else 0
        king_c = 4
        target_c = 6 if king_side else 2
        return self.to_uci(r, king_c, r, target_c)
        
    def to_uci(self, r1, c1, r2, c2):
        files = "abcdefgh"
        return f"{files[c1]}{8-r1}{files[c2]}{8-r2}"

    def alg_to_coords(self, alg):
        c = ord(alg[0]) - ord('a')
        r = 8 - int(alg[1])
        return r, c

    def apply_uci(self, uci):
        r1, c1 = self.alg_to_coords(uci[:2])
        r2, c2 = self.alg_to_coords(uci[2:4])
        
        piece = self.board[r1][c1]
        captured = self.board[r2][c2]
        
        # Move on board
        self.board[r1][c1] = '.'
        self.board[r2][c2] = piece
        
        # Handle Castling Rook Move (Physical)
        if piece.lower() == 'k':
            if abs(c2-c1) > 1:
                if c2 > c1: # Kingside
                    self.board[r1][7] = '.'
                    self.board[r1][5] = 'R' if self.turn == 'w' else 'r'
                else: # Queenside
                    self.board[r1][0] = '.'
                    self.board[r1][3] = 'R' if self.turn == 'w' else 'r'

        # Update Castling Rights (Logic)
        # 1. Moving King
        if piece == 'K': self.castling = self.castling.replace('K', '').replace('Q', '')
        if piece == 'k': self.castling = self.castling.replace('k', '').replace('q', '')
        
        # 2. Moving Rook
        if piece == 'R':
            if r1 == 7 and c1 == 0: self.castling = self.castling.replace('Q', '')
            if r1 == 7 and c1 == 7: self.castling = self.castling.replace('K', '')
        if piece == 'r':
            if r1 == 0 and c1 == 0: self.castling = self.castling.replace('q', '')
            if r1 == 0 and c1 == 7: self.castling = self.castling.replace('k', '')

        # 3. Capturing Rook
        if captured == 'R':
            if r2 == 7 and c2 == 0: self.castling = self.castling.replace('Q', '')
            if r2 == 7 and c2 == 7: self.castling = self.castling.replace('K', '')
        if captured == 'r':
            if r2 == 0 and c2 == 0: self.castling = self.castling.replace('q', '')
            if r2 == 0 and c2 == 7: self.castling = self.castling.replace('k', '')
            
        if self.castling == "": self.castling = "-"
                    
        # Update Turn
        self.turn = 'b' if self.turn == 'w' else 'w'
        
        self.ep_target = None
        
        # Set EP target if double pawn push
        if piece.lower() == 'p' and abs(r2 - r1) == 2:
            mid_r = (r1 + r2) // 2
            self.ep_target = (mid_r, c1)


def parse_pgn_file(pgn_path):
    book = {} # FEN -> {move: count}
    
    with open(pgn_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split games
    games = content.split('[Event')
    print(f"Found {len(games)-1} games.") # First split is usually empty
    
    for g_text in games:
        if not g_text.strip(): continue
        
        # Extract Moves
        # Find the blank line separating headers from moves
        parts = g_text.split('\n\n')
        if len(parts) < 2: continue
        
        moves_block = parts[1].replace('\n', ' ')
        # Remove comments, results, move numbers
        moves_clean = re.sub(r'\{[^}]*\}', '', moves_block) # comments
        moves_clean = re.sub(r'\d+\.', '', moves_clean) # numbers
        moves_clean = moves_clean.replace('1-0', '').replace('0-1', '').replace('1/2-1/2', '').replace('*', '')
        
        tokens = moves_clean.split()
        
        board = Board()
        
        # Limit to first 12 plies (6 moves) for opening book
        limit = 12
        for i, san in enumerate(tokens):
            if i >= limit: break
            
            # Correctly handle EP target so it matches BotBase logic
            full_fen = board.get_fen()
            parts = full_fen.split(' ')
            current_fen = f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}"
            
            # Skip if we already failed to track this game
            uci = board.parse_san(san)
            if not uci:
                # print(f"Failed to parse SAN: {san} at {current_fen}")
                break
                
            # Add to book
            if current_fen not in book: book[current_fen] = {}
            if uci not in book[current_fen]: book[current_fen][uci] = 0
            book[current_fen][uci] += 1
            
            board.apply_uci(uci)
            
    return book

def condense_book(raw_book):
    final_book = {}
    for fen, moves in raw_book.items():
        # Pick best move
        best_move = max(moves, key=moves.get)
        final_book[fen] = best_move
    return final_book

if __name__ == "__main__":
    pgn_path = "f:/pawn's-journey/Data/Fischer.pgn"
    out_path = "f:/pawn's-journey/Assets/Data/fischer_openings.json"
    
    if os.path.exists(pgn_path):
        raw = parse_pgn_file(pgn_path)
        final = condense_book(raw)
        
        with open(out_path, 'w') as f:
            json.dump(final, f, indent=4)
        print(f"Generated opening book with {len(final)} positions.")
    else:
        print("PGN file not found.")
