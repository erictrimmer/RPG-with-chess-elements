using Godot;
using System;
using System.Threading.Tasks;
using PawnJourney; // ChessRules / MinimalChessBot / EngineStrength (built on ThirdParty/MinimalChess)

public partial class ChessEngine : Node
{
	[Signal]
	public delegate void LegalMovesReceivedEventHandler(Godot.Collections.Array<string> moves);

	[Signal]
	public delegate void AiMoveReceivedEventHandler(string bestMove);

	// Emitted after AnalyzeMove: lossCp is how much worse the played move was than the best one
	// (0 = best move), clamped to 0..2000. tag is whatever the caller passed in (e.g. "player", "bot").
	[Signal]
	public delegate void MoveAnalyzedEventHandler(string tag, string uciMove, int lossCp, int bestCp);

	private bool _isThinking = false;

	// Config
	private int _targetElo = -1; // -1 means no limit (full strength)

	// A move that arrives instantly feels wrong in a battle, so bots take at least this long.
	private const int MinThinkMs = 500;

	private readonly Random _random = new Random();

	public override void _Ready()
	{
		// The engine runs inside the game process now: no executable, no subprocess.
		GD.Print("Chess Engine Ready (embedded MinimalChess)");
	}

	public void SetEloStrength(int elo)
	{
		_targetElo = elo;
		GD.Print($"ELO Target set to: {_targetElo} -> {EngineStrength.ForElo(_targetElo)}");
	}

	// Public API called from GDScript
	public void RequestLegalMoves(string fen)
	{
		var moves = new Godot.Collections.Array<string>();

		try
		{
			foreach (var uci in ChessRules.LegalMoves(fen))
				moves.Add(uci);
		}
		catch (Exception e)
		{
			GD.PrintErr("Error generating moves: " + e.Message);
		}

		CallDeferred(MethodName.EmitSignal, SignalName.LegalMovesReceived, moves);
	}

	public void RequestAiMove(string fen, int difficultyMs = 800)
	{
		RequestAiMoveInternal(fen, _targetElo, difficultyMs);
	}

	// Kept for existing callers. Strength (including blunders) is now handled by the
	// engine for every move, so this just searches at the given ELO.
	public void RequestAiMoveWithBlunders(string fen, int targetElo)
	{
		RequestAiMoveInternal(fen, targetElo, 800);
	}

	private void RequestAiMoveInternal(string fen, int elo, int difficultyMs)
	{
		if (_isThinking) return;
		_isThinking = true;

		var settings = EngineStrength.ForElo(elo, difficultyMs);

		// Search on a worker thread so the game does not freeze while the bot thinks.
		Task.Run(async () =>
		{
			string move = "";
			try
			{
				var started = DateTime.UtcNow;
				move = MinimalChessBot.ChooseMove(fen, settings, _random);

				int remaining = MinThinkMs - (int)(DateTime.UtcNow - started).TotalMilliseconds;
				if (remaining > 0) await Task.Delay(remaining);
			}
			catch (Exception e)
			{
				GD.PrintErr($"Engine error: {e.Message}");
			}
			finally
			{
				_isThinking = false;
			}

			if (move == "") GD.PrintErr("Engine returned no move (game over or error).");
			if (IsInstanceValid(this))
				CallDeferred(MethodName.EmitAiMove, move);
		});
	}

	// Judge a move already played from fenBefore, on a worker thread. Result arrives via MoveAnalyzed.
	// Cheap (shallow) on purpose; it is used for reactions, not for grading.
	public void AnalyzeMove(string fenBefore, string uciMove, string tag = "")
	{
		Task.Run(() =>
		{
			int loss = 0, best = 0;
			bool ok = false;
			try
			{
				ok = MinimalChessBot.AnalyzeMove(fenBefore, uciMove, 3, 1500, out best, out int played);
				if (ok) loss = Math.Clamp(best - played, 0, 2000);
			}
			catch (Exception e)
			{
				GD.PrintErr($"Analysis error: {e.Message}");
			}
			if (ok && IsInstanceValid(this))
				CallDeferred(MethodName.EmitSignal, SignalName.MoveAnalyzed, tag, uciMove, loss, best);
		});
	}

	private void EmitAiMove(string move)
	{
		EmitSignal(SignalName.AiMoveReceived, move);
	}

	// Returns the new FEN, or the same FEN if the move is illegal.
	public string ApplyMove(string fen, string uciMove)
	{
		try
		{
			string result = ChessRules.ApplyMove(fen, uciMove);
			if (result == fen) GD.PrintErr($"Invalid move attempted: {uciMove}");
			return result;
		}
		catch (Exception e)
		{
			GD.PrintErr($"Move Error: {e.Message}");
			return fen;
		}
	}

	public bool IsMoveSafe(string fen, string uciMove)
	{
		try { return ChessRules.IsLegal(fen, uciMove); }
		catch (Exception e)
		{
			GD.PrintErr($"IsMoveSafe Exception: {e.Message}");
			return false;
		}
	}

	// Returns: "Checkmate", "Stalemate", "Draw" (50-move rule, insufficient material), or ""
	public string GetGameStatus(string fen)
	{
		try { return ChessRules.GetStatus(fen); }
		catch { return ""; }
	}

	// Standard algebraic notation (e.g. "Nf3", "exd5", "O-O", "Qh5+") for a move played from fenBefore.
	public string GetMoveSan(string fenBefore, string uciMove)
	{
		try { return ChessRules.ToSan(fenBefore, uciMove); }
		catch { return uciMove; }
	}
}
