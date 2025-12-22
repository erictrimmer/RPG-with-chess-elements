using Godot;
using System;
using System.Diagnostics;
using System.Collections.Generic;
using ChessDotNetCore; // Core Library

public partial class ChessEngine : Node
{
	[Signal]
	public delegate void LegalMovesReceivedEventHandler(Godot.Collections.Array<string> moves);

	[Signal]
	public delegate void AiMoveReceivedEventHandler(string bestMove);

	private Process _process;
	private bool _isReady = false;
	private bool _isThinking = false;
	private bool _uciOk = false;
	
	// Config
	private string _enginePath;
	private int _targetElo = -1; // -1 means no limit

	public override void _Ready()
	{
		// Path logic (matching GDScript logic)
		if (OS.HasFeature("windows"))
			_enginePath = ProjectSettings.GlobalizePath("res://Engine/chess_engine.exe");
		else
			_enginePath = ProjectSettings.GlobalizePath("res://Engine/chess_engine");

		StartEngine();
	}

	public void SetEloStrength(int elo)
	{
		_targetElo = elo;
		GD.Print($"ELO Target set to: {_targetElo}");
		
		// If engine is already initialized, apply settings
		if (_uciOk)
		{
			ApplyEloSettings();
		}
	}

	private void ApplyEloSettings()
	{
		if (_targetElo > 0)
		{
			// Map ELO to Skill Level (0-20, where 0 is weakest)
			// 200 ELO ≈ Skill 0, 1000 ELO ≈ Skill 5, 2000 ELO ≈ Skill 10
			int skillLevel = Math.Max(0, (_targetElo - 200) / 180);
			skillLevel = Math.Min(20, skillLevel);
			
			GD.Print($"Setting Skill Level to {skillLevel} (from ELO {_targetElo})");
			
			// Use Skill Level instead of UCI_Elo (more reliable)
			SendCommand($"setoption name Skill Level value {skillLevel}");
			
			// Also limit strength for very low ratings
			if (_targetElo < 1000)
			{
				SendCommand("setoption name UCI_LimitStrength value true");
				SendCommand($"setoption name UCI_Elo value {_targetElo}");
			}
		}
	}

	private void StartEngine()
	{
		try
		{
			var startInfo = new ProcessStartInfo
			{
				FileName = _enginePath,
				UseShellExecute = false,
				RedirectStandardInput = true,
				RedirectStandardOutput = true,
				CreateNoWindow = true
			};

			_process = new Process { StartInfo = startInfo };
			_process.EnableRaisingEvents = true; 
			_process.OutputDataReceived += OnOutputDataReceived;
			_process.Exited += OnEngineExited;
			_process.Start();
			_process.BeginOutputReadLine();

			SendCommand("uci");
			GD.Print("Chess Engine process started.");
		}
		catch (Exception e)
		{
			GD.PrintErr($"Failed to start chess engine: {e.Message}");
		}
	}

	private void OnEngineExited(object sender, EventArgs e)
	{
		GD.PrintErr("Chess Engine process exited unexpectedly!");
		_isReady = false;
		_isThinking = false;
		_process = null;
	}

	private void EnsureEngineRunning()
	{
		if (_process == null || _process.HasExited)
		{
			GD.Print("Attempting to restart Chess Engine...");
			StartEngine();
		}
	}

	private void SendCommand(string command)
	{
		try {
			if (_process != null && !_process.HasExited)
			{
				_process.StandardInput.WriteLine(command);
			}
		}
		catch (Exception e) { GD.PrintErr($"Send Command Error: {e.Message}"); }
	}

	private void OnOutputDataReceived(object sender, DataReceivedEventArgs e)
	{
		if (String.IsNullOrEmpty(e.Data)) return;

		string line = e.Data;
		
		if (line == "uciok")
		{
			_uciOk = true;
			GD.Print("UCI OK received");
			
			// Apply ELO settings BEFORE sending isready
			ApplyEloSettings();
			
			// Now send isready
			SendCommand("isready");
		}
		else if (line == "readyok")
		{
			_isReady = true;
			GD.Print("Chess Engine Ready (C#)");
		}
		else if (line.StartsWith("bestmove"))
		{
			_isThinking = false;
			var parts = line.Split(' ');
			if (parts.Length >= 2)
			{
				string bestMove = parts[1];
				CallDeferred(MethodName.EmitAiMove, bestMove);
			}
		}
	}

	// Public API called from GDScript
	public void RequestLegalMoves(string fen)
	{
		EnsureEngineRunning();
		
		var moves = new Godot.Collections.Array<string>();
		
		try 
		{
			var game = new ChessGame(fen);
			// Manually determine player from FEN to avoid API ambiguity
			var parts = fen.Split(' ');
			var player = (parts[1] == "w") ? Player.White : Player.Black;

			var validMoves = game.GetValidMoves(player);
			
			foreach (var m in validMoves)
			{
				// Convert Move object to UCI string (e.g. "e2e4")
				string uci = m.OriginalPosition.ToString().ToLower() + m.NewPosition.ToString().ToLower();
				if (m.Promotion.HasValue) 
				{
					uci += Char.ToLower(m.Promotion.Value);
				}
				moves.Add(uci);
			}
		}
		catch (Exception e) 
		{
			GD.PrintErr("Error generating moves: " + e.Message);
		}

		CallDeferred(MethodName.EmitSignal, SignalName.LegalMovesReceived, moves);
	}

	public void RequestAiMove(string fen, int difficultyMs = 800)
	{
		EnsureEngineRunning();
		
		if (_isThinking) return;
		_isThinking = true;

		SendCommand($"position fen {fen}");
		SendCommand($"go movetime {difficultyMs}");
	}

	// For weak bots: pick random legal moves instead of using engine
	public void RequestAiMoveWithBlunders(string fen, int targetElo)
	{
		try
		{
			var game = new ChessGame(fen);
			var parts = fen.Split(' ');
			var player = (parts[1] == "w") ? Player.White : Player.Black;
			var validMoves = game.GetValidMoves(player);
			
			if (validMoves.Count == 0)
			{
				GD.PrintErr("No legal moves available!");
				CallDeferred(MethodName.EmitAiMove, "");
				return;
			}

			string chosenMove;
			
			// Calculate blunder rate: 200 ELO = 70% random, 800 ELO = 10% random
			float blunderChance = Math.Max(0, Math.Min(1, (800 - targetElo) / 600.0f * 0.7f));
			var random = new Random();
			
			if (random.NextDouble() < blunderChance)
			{
				// Pick completely random move
				var randomMove = validMoves[random.Next(validMoves.Count)];
				chosenMove = randomMove.OriginalPosition.ToString().ToLower() + 
							randomMove.NewPosition.ToString().ToLower();
				if (randomMove.Promotion.HasValue)
					chosenMove += Char.ToLower(randomMove.Promotion.Value);
					
				GD.Print($"Bot blundered! Random move: {chosenMove}");
			}
			else
			{
				// Use Stockfish for this move
				RequestAiMove(fen, 100);
				return;
			}
			
			CallDeferred(MethodName.EmitAiMove, chosenMove);
		}
		catch (Exception e)
		{
			GD.PrintErr($"Error in RequestAiMoveWithBlunders: {e.Message}");
			CallDeferred(MethodName.EmitAiMove, "");
		}
	}

	private void EmitAiMove(string move)
	{
		EmitSignal(SignalName.AiMoveReceived, move);
	}
	
	// Uses ChessDotNet for robust State Update
	public string ApplyMove(string fen, string uciMove)
	{
		 try 
		 {
			var game = new ChessGame(fen);
			var srcStr = uciMove.Substring(0, 2);
			var dstStr = uciMove.Substring(2, 2);
			char? promo = null;
			
			if (uciMove.Length == 5)
			{
				 string pChar = uciMove.Substring(4, 1).ToUpper(); 
				 promo = pChar[0];
			}

			// Manually determine player from FEN
			var parts = fen.Split(' ');
			var player = (parts[1] == "w") ? Player.White : Player.Black;

			// Construct Move using correct API (Position objects)
			var startPos = new Position(srcStr);
			var endPos = new Position(dstStr);
			var move = new Move(startPos, endPos, player, promo);

			var status = game.MakeMove(move, true); // true = validate
			
			if (status == MoveType.Invalid)
			{
				GD.PrintErr($"Invalid move attempted: {uciMove}");
				return fen;
			}

			return game.GetFen();
		 }
		 catch (Exception e)
		 {
			 GD.PrintErr($"Move Error: {e.Message}");
			 return fen;
		 }
	}
	
	// Uses ChessDotNet for robust Validation
	public bool IsMoveSafe(string fen, string uciMove)
	{
		try 
		{
			var game = new ChessGame(fen);
			var srcStr = uciMove.Substring(0, 2);
			var dstStr = uciMove.Substring(2, 2);
			char? promo = null;
			if (uciMove.Length == 5) promo = uciMove.Substring(4, 1).ToUpper()[0];

			// Manually determine player from FEN
			var parts = fen.Split(' ');
			var player = (parts[1] == "w") ? Player.White : Player.Black;

			var startPos = new Position(srcStr);
			var endPos = new Position(dstStr);

			// Safer Validation: Get ALL valid moves and check if ours is in there.
			var validMoves = game.GetValidMoves(player);
			
			// Debug: Print all valid moves to console to handle tricky cases like En Passant
			string allMovesStr = "";
			foreach (var m in validMoves) 
			{
				string s = m.OriginalPosition.ToString() + m.NewPosition.ToString();
				allMovesStr += s + ", ";
				
				if (m.OriginalPosition.Equals(startPos) && m.NewPosition.Equals(endPos))
				{
					if (promo.HasValue)
					{
						if (m.Promotion.HasValue && m.Promotion.Value == promo.Value) return true;
					}
					else
					{
						if (!m.Promotion.HasValue) return true;
					}
				}
			}
			
			GD.Print($"IsMoveSafe Check: {uciMove}. Valid Moves Found: [{allMovesStr}]");
			
			return false;
		}
		catch (Exception ex)
		{
			GD.PrintErr($"IsMoveSafe Exception: {ex.Message}");
			return false; 
		}
	}

	// New API for PGN / Game Over logic
	// Returns: "Checkmate", "Stalemate", "Draw", or ""
	public string GetGameStatus(string fen)
	{
		try
		{
			var game = new ChessGame(fen);
			var parts = fen.Split(' ');
			var player = (parts[1] == "w") ? Player.White : Player.Black;

			if (game.IsCheckmated(player)) return "Checkmate";
			if (game.IsStalemated(player)) return "Stalemate";
			if (game.IsDraw()) return "Draw"; // 50-move rule, insufficiency, etc.
			
			return "";
		}
		catch { return ""; }
	}

	// Convert Last Move to SAN (e.g., "Nf3") roughly
	// Since we don't have full history here easily without passing it,
	// we make a best effort based on the move + board state before move.
	public string GetMoveSan(string fenBefore, string uciMove)
	{
		try
		{
			 // To get accurate SAN, we need the board state BEFORE the move
			 var game = new ChessGame(fenBefore);
			 var parts = fenBefore.Split(' ');
			 var player = (parts[1] == "w") ? Player.White : Player.Black;
			 
			 var srcStr = uciMove.Substring(0, 2);
			 var dstStr = uciMove.Substring(2, 2);
			 char? promo = null; 
			 if (uciMove.Length == 5) promo = uciMove.Substring(4, 1).ToUpper()[0];
			 
			 var move = new Move(new Position(srcStr), new Position(dstStr), player, promo);
			 
			 // ChessDotNet doesn't have a public "MoveToSan" method easily exposed on Move object?
			 // Actually, usually `move.ToString()` might be Coordinate notation.
			 // We can check if `game.MakeMove` return provides info, but let's try to query library.
			 // Workaround: We will use a simplified SAN generator or rely on client side logic if library fails.
			 // CHECK: CheckDotNetCore Move class doesn't store SAN. 
			 // We'd have to implement algebraic notation manually if not present.
			 // For now, let's return UCI as fallback if we can't find it, but I'll try to be clever.
			 
			 // Simple SAN Implementation:
			 var piece = game.GetPieceAt(new Position(srcStr));
			 char fenChar = piece.GetFenCharacter();
			 bool isPawn = (Char.ToUpper(fenChar) == 'P');
			 
			 string pieceChar = isPawn ? "" : Char.ToUpper(fenChar).ToString();
			 
			 // Capture?
			 bool isCapture = game.GetPieceAt(new Position(dstStr)) != null;
			 
			 string san = pieceChar;
			 
			 if (isCapture) 
			 {
				 if (isPawn) san = srcStr.Substring(0,1);
				 san += "x";
			 }
			 
			 san += dstStr;
			 
			 if (promo.HasValue) san += "=" + promo.Value;
			 
			 // Check/Checkmate suffix
			 // Apply move to see legal status
			 game.MakeMove(move, true);
			 var opponent = (player == Player.White) ? Player.Black : Player.White;
			 if (game.IsCheckmated(opponent)) san += "#";
			 else if (game.IsInCheck(opponent)) san += "+";
			 
			 return san;
		}
		catch { return uciMove; }
	}

	public override void _ExitTree()
	{
		if (_process != null && !_process.HasExited)
		{
			_process.Kill();
		}
	}
}
