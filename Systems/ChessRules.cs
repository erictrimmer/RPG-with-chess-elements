using System;
using System.Collections.Generic;
using System.Text;
using MinimalChess; // vendored in ThirdParty/MinimalChess (MIT, Thomas Jahn)
using Color = MinimalChess.Color; // stays unambiguous even if Godot is ever imported project-wide

namespace PawnJourney
{
	/// <summary>
	/// Chess rules on FEN strings, built on the embedded MinimalChess board:
	/// legal moves, applying a move, game status and SAN notation.
	/// Like MinimalChessBot this file imports neither Godot nor anything else with a Move/Piece/Color type.
	/// Moves are UCI strings in lowercase ("e2e4", "e7e8q"). Everything here is thread-safe
	/// (it only touches boards it creates itself).
	/// </summary>
	public static class ChessRules
	{
		/// <summary>All legal moves for the side to move.</summary>
		public static List<string> LegalMoves(string fen)
		{
			var result = new List<string>();
			foreach (var m in Legal(new Board(fen)))
				result.Add(Uci(m));
			return result;
		}

		public static bool IsLegal(string fen, string uciMove)
		{
			return Find(Legal(new Board(fen)), uciMove, out _);
		}

		/// <summary>
		/// Plays a move and returns the new FEN. Returns the original FEN if the move is illegal.
		/// The en passant field is only filled in when an en passant capture is actually possible
		/// (this is what the opening book keys were built with).
		/// </summary>
		public static string ApplyMove(string fen, string uciMove)
		{
			var board = new Board(fen);
			if (!Find(Legal(board), uciMove, out Move move))
				return fen;

			var (castling, halfmove, fullmove) = ParseFields(fen);
			bool whiteMoved = board.SideToMove == Color.White;
			bool isPawn = IsPawn(board[move.FromSquare]);
			bool isCapture = board[move.ToSquare] != Piece.None ||
				(isPawn && File(move.FromSquare) != File(move.ToSquare)); // diagonal pawn move to an empty square = en passant

			var after = new Board(board, move);

			// Castling rights: lost when a king or rook leaves, or a rook is captured on its home square.
			string rights = castling == "-" ? "" : castling;
			foreach (int sq in new[] { move.FromSquare, move.ToSquare })
			{
				switch (sq)
				{
					case 4:  rights = Remove(rights, "KQ"); break; // e1
					case 60: rights = Remove(rights, "kq"); break; // e8
					case 0:  rights = Remove(rights, "Q"); break;  // a1
					case 7:  rights = Remove(rights, "K"); break;  // h1
					case 56: rights = Remove(rights, "q"); break;  // a8
					case 63: rights = Remove(rights, "k"); break;  // h8
				}
			}
			if (rights == "") rights = "-";

			// En passant target square, only if a legal en passant capture exists.
			string ep = "-";
			if (isPawn && Math.Abs(Rank(move.ToSquare) - Rank(move.FromSquare)) == 2)
			{
				int epSquare = (move.FromSquare + move.ToSquare) / 2;
				foreach (var reply in Legal(after))
				{
					if (reply.ToSquare == epSquare && IsPawn(after[reply.FromSquare]) && File(reply.FromSquare) != File(reply.ToSquare))
					{
						ep = Notation.ToSquareName((byte)epSquare);
						break;
					}
				}
			}

			int newHalfmove = (isPawn || isCapture) ? 0 : halfmove + 1;
			int newFullmove = whiteMoved ? fullmove : fullmove + 1;

			var sb = new StringBuilder();
			for (int r = 7; r >= 0; r--)
			{
				int empty = 0;
				for (int f = 0; f < 8; f++)
				{
					var p = after[r, f];
					if (p == Piece.None) { empty++; continue; }
					if (empty > 0) { sb.Append(empty); empty = 0; }
					sb.Append(Notation.ToChar(p));
				}
				if (empty > 0) sb.Append(empty);
				if (r > 0) sb.Append('/');
			}
			sb.Append(after.SideToMove == Color.White ? " w " : " b ");
			sb.Append(rights).Append(' ').Append(ep).Append(' ').Append(newHalfmove).Append(' ').Append(newFullmove);
			return sb.ToString();
		}

		/// <summary>"Checkmate", "Stalemate", "Draw" (50-move rule or insufficient material) or "".</summary>
		/// <remarks>Threefold repetition cannot be detected from a single FEN, so it is not reported.</remarks>
		public static string GetStatus(string fen)
		{
			// Tutorial positions such as a lone pawn have no kings: that is a lesson, not a game,
			// so no mate/stalemate/draw is ever declared there.
			string placement = fen.Split(' ')[0];
			if (placement.IndexOf('K') < 0 || placement.IndexOf('k') < 0)
				return "";
			var board = new Board(fen);
			if (Legal(board).Count == 0)
				return board.IsChecked(board.SideToMove) ? "Checkmate" : "Stalemate";

			var (_, halfmove, _) = ParseFields(fen);
			if (halfmove >= 100 || InsufficientMaterial(board))
				return "Draw";
			return "";
		}

		/// <summary>Standard algebraic notation for a move, e.g. "Nf3", "exd5", "O-O", "Qh5+". Returns the UCI string if the move is illegal.</summary>
		public static string ToSan(string fen, string uciMove)
		{
			var board = new Board(fen);
			var legal = Legal(board);
			if (!Find(legal, uciMove, out Move move))
				return uciMove;

			var piece = board[move.FromSquare];
			char letter = char.ToUpperInvariant(Notation.ToChar(piece));
			bool isPawn = letter == 'P';
			bool isCapture = board[move.ToSquare] != Piece.None || (isPawn && File(move.FromSquare) != File(move.ToSquare));

			string san;
			if (letter == 'K' && Math.Abs(File(move.ToSquare) - File(move.FromSquare)) == 2)
			{
				san = File(move.ToSquare) > File(move.FromSquare) ? "O-O" : "O-O-O";
			}
			else
			{
				var sb = new StringBuilder();
				string from = Notation.ToSquareName(move.FromSquare);
				if (isPawn)
				{
					if (isCapture) sb.Append(from[0]);
				}
				else
				{
					sb.Append(letter);
					// Disambiguate when another piece of the same kind can also reach the square.
					bool clash = false, sameFile = false, sameRank = false;
					foreach (var other in legal)
					{
						if (other.ToSquare != move.ToSquare || other.FromSquare == move.FromSquare) continue;
						if (board[other.FromSquare] != piece) continue;
						clash = true;
						if (File(other.FromSquare) == File(move.FromSquare)) sameFile = true;
						if (Rank(other.FromSquare) == Rank(move.FromSquare)) sameRank = true;
					}
					if (clash)
					{
						if (!sameFile) sb.Append(from[0]);
						else if (!sameRank) sb.Append(from[1]);
						else sb.Append(from);
					}
				}
				if (isCapture) sb.Append('x');
				sb.Append(Notation.ToSquareName(move.ToSquare));
				if (move.Promotion != Piece.None)
					sb.Append('=').Append(char.ToUpperInvariant(Notation.ToChar(move.Promotion)));
				san = sb.ToString();
			}

			var after = new Board(board, move);
			if (after.IsChecked(after.SideToMove))
				san += Legal(after).Count == 0 ? "#" : "+";
			return san;
		}

		// ---------------------------------------------------------------- helpers

		private static List<Move> Legal(Board board)
		{
			var moves = new List<Move>(40);
			var scratch = new Board();
			var side = board.SideToMove;
			board.CollectMoves(m =>
			{
				scratch.Copy(board);
				scratch.Play(m);
				if (!scratch.IsChecked(side)) moves.Add(m);
			});
			return moves;
		}

		// MinimalChess writes white promotions as "a7a8Q"; UCI (and the game) use lowercase.
		private static string Uci(Move m) => m.ToString().ToLowerInvariant();

		private static bool Find(List<Move> legal, string uciMove, out Move found)
		{
			string wanted = (uciMove ?? "").ToLowerInvariant();
			foreach (var m in legal)
			{
				if (Uci(m) == wanted) { found = m; return true; }
			}
			found = default;
			return false;
		}

		private static (string Castling, int Halfmove, int Fullmove) ParseFields(string fen)
		{
			var f = fen.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
			string castling = f.Length > 2 ? f[2] : "-";
			int halfmove = (f.Length > 4 && int.TryParse(f[4], out int h)) ? h : 0;
			int fullmove = (f.Length > 5 && int.TryParse(f[5], out int n) && n > 0) ? n : 1;
			return (castling, halfmove, fullmove);
		}

		private static string Remove(string rights, string chars)
		{
			foreach (char c in chars) rights = rights.Replace(c.ToString(), "");
			return rights;
		}

		private static int File(int square) => square % 8;
		private static int Rank(int square) => square / 8;
		private static bool IsPawn(Piece p) => char.ToUpperInvariant(Notation.ToChar(p)) == 'P';

		private static bool InsufficientMaterial(Board board)
		{
			int knights = 0, whiteBishops = 0, blackBishops = 0;
			int whiteBishopColor = -1, blackBishopColor = -1;
			for (int sq = 0; sq < 64; sq++)
			{
				char c = Notation.ToChar(board[sq]);
				switch (c)
				{
					case 'P': case 'p': case 'R': case 'r': case 'Q': case 'q':
						return false;
					case 'N': case 'n':
						knights++; break;
					case 'B': whiteBishops++; whiteBishopColor = (File(sq) + Rank(sq)) % 2; break;
					case 'b': blackBishops++; blackBishopColor = (File(sq) + Rank(sq)) % 2; break;
				}
			}
			int minors = knights + whiteBishops + blackBishops;
			if (minors <= 1) return true;                      // K v K, K+minor v K
			if (knights == 0 && whiteBishops == 1 && blackBishops == 1)
				return whiteBishopColor == blackBishopColor;   // K+B v K+B on the same colour
			return false;
		}
	}
}
