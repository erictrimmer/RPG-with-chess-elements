using System;
using System.Collections.Generic;
using System.Diagnostics;
using MinimalChess; // vendored in ThirdParty/MinimalChess (MIT, Thomas Jahn)

namespace PawnJourney
{
	/// <summary>
	/// Thin adapter around the embedded MinimalChess engine.
	///
	/// This file deliberately does NOT import Godot: Godot.Color collides with MinimalChess.Color.
	/// It speaks only FEN and UCI strings.
	///
	/// MinimalChess keeps static state (transposition table, a scratch board), so every
	/// call is serialized with a lock. Callers may run it on a background thread.
	/// </summary>
	public static class MinimalChessBot
	{
		private const int HashSizeMb = 16;
		private const int MateThreshold = 9000; // Evaluation.IsCheckmate uses |score| > 9000

		private static readonly object Gate = new object();
		private static bool _initialized;

		private static void EnsureInit()
		{
			if (_initialized) return;
			Transpositions.Resize(HashSizeMb);
			_initialized = true;
		}

		/// <summary>
		/// Chooses a move for the side to move. Returns "" if the game is over (no legal moves).
		/// </summary>
		public static string ChooseMove(string fen, StrengthSettings s, Random rng)
		{
			return ChooseMove(new Board(fen), s, rng);
		}

		public static string ChooseMove(Board board, StrengthSettings s, Random rng)
		{
			lock (Gate)
			{
				EnsureInit();
				// Cleared every move so stale deep entries cannot make a weak bot play stronger.
				Transpositions.Clear();

				var legal = new LegalMoves(board);
				if (legal.Count == 0) return "";
				if (legal.Count == 1) return ToUci(legal[0]);

				var clock = Stopwatch.StartNew();

				// Full strength: a plain iterative-deepening search, same as the UCI engine does.
				if (s.IsFullStrength || (s.MarginCp == 0 && s.BlunderChance <= 0 && s.Depth > 0))
					return ToUci(SearchBest(board, s.Depth, s.MaxTimeMs, clock));

				// Weakened play: score every root move, then choose among them.
				var scored = ScoreRootMoves(board, legal, s.Depth, s.MaxTimeMs, clock);
				return ToUci(PickMove(scored, legal, s, rng));
			}
		}


		/// <summary>
		/// Judges a move that was just played: scores every legal move from <paramref name="fen"/> at a
		/// shallow depth and reports the best score and the played move's score, both in centipawns
		/// from the mover's point of view. Returns false if the move is not legal there.
		/// Used for reactions ("nice move", "you blundered"), so it is deliberately cheap.
		/// </summary>
		public static bool AnalyzeMove(string fen, string uci, int depth, int maxTimeMs, out int bestCp, out int playedCp)
		{
			bestCp = 0; playedCp = 0;
			lock (Gate)
			{
				EnsureInit();
				Transpositions.Clear();
				var board = new Board(fen);
				var legal = new LegalMoves(board);
				if (legal.Count == 0) return false;

				var scores = ScoreRootMoves(board, legal, depth, maxTimeMs, Stopwatch.StartNew());
				int played = -1;
				bestCp = int.MinValue;
				for (int i = 0; i < scores.Length; i++)
				{
					if (scores[i] > bestCp) bestCp = scores[i];
					if (ToUci(legal[i]) == uci.ToLowerInvariant()) played = i;
				}
				if (played < 0) return false;
				playedCp = scores[played];
				return true;
			}
		}

		// MinimalChess writes white promotions as "a7a8Q"; the game (and UCI) use lowercase "a7a8q".
		private static string ToUci(Move m) => m.ToString().ToLowerInvariant();

		// Best move by iterative deepening, limited by depth and time.
		private static Move SearchBest(Board board, int maxDepth, int maxTimeMs, Stopwatch clock)
		{
			var search = new IterativeSearch(board);
			search.SearchDeeper(); // first iteration: cheap, no time check, always completes
			Move best = search.PrincipalVariation[0];

			while (search.Depth < maxDepth && clock.ElapsedMilliseconds < maxTimeMs / 4)
			{
				// Aborted iterations return garbage scores, so only keep completed ones.
				search.SearchDeeper(() => clock.ElapsedMilliseconds >= maxTimeMs);
				if (search.Aborted) break;
				if (search.PrincipalVariation.Length > 0)
					best = search.PrincipalVariation[0];
				if (search.GameOver) break;
			}
			return best;
		}

		// Score (from the mover's point of view, in centipawns) of each legal root move.
		private static int[] ScoreRootMoves(Board board, LegalMoves legal, int depth, int maxTimeMs, Stopwatch clock)
		{
			int side = (int)board.SideToMove;
			var scores = new int[legal.Count];

			for (int i = 0; i < legal.Count; i++)
			{
				var child = new Board(board, legal[i]);

				// Depth 0, or out of time: judge the position after the move by static evaluation only.
				if (depth <= 0 || clock.ElapsedMilliseconds >= maxTimeMs)
				{
					scores[i] = side * child.Score;
					continue;
				}

				// The move itself counts as one ply, so search the reply to (depth - 1).
				// IterativeSearch scores are always from White's point of view.
				var search = new IterativeSearch(child);
				while (search.Depth < Math.Max(1, depth - 1))
					search.SearchDeeper();
				scores[i] = side * search.Score;
			}
			return scores;
		}

		private static Move PickMove(int[] scores, LegalMoves legal, StrengthSettings s, Random rng)
		{
			int bestIdx = 0;
			for (int i = 1; i < scores.Length; i++)
				if (scores[i] > scores[bestIdx]) bestIdx = i;
			int best = scores[bestIdx];

			// A forced win is always played; weak bots still finish the game.
			if (best > MateThreshold) return legal[bestIdx];

			// Blunder: a random legal move that does not walk into mate in the horizon.
			if (s.BlunderChance > 0 && rng.NextDouble() < s.BlunderChance)
			{
				var safe = new List<int>();
				for (int i = 0; i < scores.Length; i++)
					if (scores[i] > -MateThreshold) safe.Add(i);
				if (safe.Count > 0)
					return legal[safe[rng.Next(safe.Count)]];
			}

			if (s.MarginCp <= 0) return legal[bestIdx];

			// Weighted pick among moves within the margin; closer to the best = more likely.
			double temperature = Math.Max(1.0, s.MarginCp / 2.0);
			var candidates = new List<(int Index, double Weight)>();
			double total = 0;
			for (int i = 0; i < scores.Length; i++)
			{
				int loss = best - scores[i];
				if (loss > s.MarginCp) continue;
				double w = Math.Exp(-loss / temperature);
				candidates.Add((i, w));
				total += w;
			}

			double roll = rng.NextDouble() * total;
			foreach (var (index, weight) in candidates)
			{
				roll -= weight;
				if (roll <= 0) return legal[index];
			}
			return legal[bestIdx];
		}
	}
}
