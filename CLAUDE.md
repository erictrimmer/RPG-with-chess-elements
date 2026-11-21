# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pawn's Journey is a chess-based RPG built with Godot 4 (.NET). Players explore overworld maps, interact with NPCs, complete quests, and engage in chess matches against AI bots powered by Stockfish.

## Running the Project

- Open in **Godot 4.3+** (with .NET/C# support enabled)
- Main scene: `res://Scenes/MainMenu.tscn`
- Dependencies: .NET 8.0 SDK, NuGet package `ChessDotNetCore` v1.6.0 (managed via `PawnJourney.csproj`)
- Stockfish executable lives at `Engine/chess_engine.exe` and is launched as a subprocess by `ChessEngine.cs`

To run the logic test script:
```
godot --script check_logic.gd
```

Python scripts in `Tools/legacy/` (`center_sprites.py`, `fix_sprite_centering.py`) are utility tools for processing sprite assets — not part of the game build.

## Architecture

### Autoload Singletons (globally accessible)

| Singleton | File | Purpose |
|---|---|---|
| `GameManager` | `Systems/GameManager.gd` | Scene transitions, scene registry |
| `GameState` | `Systems/GameState.gd` | Persistent player data (rating, tutorials, position) |
| `DialogManager` | `Systems/DialogManager.gd` | Global dialog UI (typewriter, sequences, choices) |
| `InventoryManager` | `Systems/InventoryManager.gd` | Quest item tracking |
| `QuestManager` | `Systems/QuestManager.gd` | Multi-stage quest progression with signals |
| `PuzzleManager` | `Systems/PuzzleManager.gd` | JSON puzzle loading with ELO/tag filtering |
| `OpeningBookManager` | `Systems/OpeningBookManager.gd` | FEN→UCI opening book lookup for bots |

### Chess Engine Layer (`Systems/ChessEngine.cs`)

The only C# file. Wraps Stockfish via UCI protocol as an external process. Key methods:
- `RequestLegalMoves(fen)` — offline via ChessDotNetCore
- `RequestAiMove(fen, difficultyMs)` — Stockfish with time limit
- `RequestAiMoveWithBlunders(fen, targetElo)` — weakened play for low-ELO bots
- `ApplyMove(fen, uciMove)` / `GetGameStatus(fen)` / `GetMoveSan(...)` — move application and notation

### Battle Flow

`BattleController.gd` orchestrates all chess match logic: piece selection, legal move highlighting, player/bot turns, puzzle verification, PGN recording, and promotion dialogs. It connects to `board.gd` (rendering) and `GameUI.gd` (UI layer).

Bot turn order: opening book lookup via `OpeningBookManager` → fallback to Stockfish. Bot behavior is defined in `Resources/BotProfile.gd` resource files and per-bot scripts under `Scenes/Bots/`.

### Scene Structure

- **Overworld**: `Scenes/Downtown.tscn` — large (1504×1504px) exploration map with NPCs, camera boundaries, and interaction areas. (`Yorktown.tscn` and `MainWorld.tscn` were archived to `_archive/`: their tileset art no longer exists.)
- **Battle**: `Scenes/StandardMatch.tscn` — entry point; uses `BattleController.gd` + `GameUI.gd`
- **Puzzles**: `Scenes/Puzzles/<PieceType>/<PieceType>Tutorial.tscn` — one per piece type (Pawns, Knights, Queens, etc.)
- **Bots**: `Scenes/Bots/` — `BotBase.gd` (abstract, emits `move_chosen`), `StandardBot.gd`, plus named bots

### Dialog System

Two APIs in `DialogManager.gd`:
- Legacy: `show_dialog(text, choices)`
- Modern: `show_sequence(pages, on_done_callable)` — preferred for multi-page sequences

See `.agent/guides/npc_dialog_system.md` for the full NPC interaction implementation guide (node structure, signal wiring, scene transition with position persistence).

### Quest System

5-act story tracked in `QuestManager.gd`. Quests have stages: `"not_started"`, `"active"`, `"complete"`, plus custom intermediate strings. Quest progression emits signals consumed by NPCs and scene scripts.

### Data Files

All under `Data/`:
- `BotConfigs/*.json` — ELO, opening moves, behavior
- `OpeningBooks/*.json` — FEN → UCI move mappings
- `Puzzles/*.json` — FEN, target move, tags, ELO range
- `PuzzlePacks/<batch>.json` — drill batches (see below), loaded by `PuzzleManager`
- `Fischer.pgn` — master games (535KB, for reference)

### Viewport

Internal: 320×180px (retro pixel art). Display: 1280×720 via 4× integer scaling. Renderer: GL Compatibility.

## Known Problems

### Broken Bot Scripts
`Scenes/Bots/Bot200.gd`, `ItalianPunisher.gd`, and `ScholarsMate.gd` are all broken and will crash if instantiated. They call `start_bot_game()`, `load_bot_config()`, and `get_player_color()` — none of which exist anywhere in the codebase. `Bot200.gd` also incorrectly `extends GameManager` instead of `BotBase`. These appear to be a half-finished second approach to the bot system; the working approach is `StandardBot.gd` + `BobbyBot.gd`. Do not instantiate or build on these three scripts without fixing them first.

### BobbyBot.gd is unused
`Scenes/Bots/BobbyBot.gd` is dead code. Bobby is implemented via `Resources/Bots/Bobby.tres` (a `BotProfile`) used with `StandardBot`. The `.gd` file also has a wrong asset path and should not be built upon.

### Orphaned Puzzle Tutorials
King, Bishop, and Rook tutorial scenes and scripts exist (`Scenes/Puzzles/Kings/`, `Bishops/`, `Rooks/`) but are never registered in `GameManager.gd` and are unreachable in-game. Only Pawn and Knight tutorials are wired up.

### Dead Data Files
`Data/BotConfigs/italian_punisher.json`, `Data/BotConfigs/scholars_mate.json`, and `Data/OpeningBooks/italian_game.json` are only referenced by the broken bot scripts above.

## Puzzle Drill Batches

Beginner drills are short, specific sets, easiest first (in the spirit of Russian-style drilling). They are harvested from the Lichess puzzle database (CC0) with `Tools/PuzzleHarvester.html` (open it in Chrome or Edge, pick `Puzzles/lichess_db_puzzle.csv`, scan, then write into `Data/PuzzlePacks`). It runs locally and streams the 1+ GB file.

Batches (50 puzzles each by default; mate in 1 is rated 600 or under, everything else 1400 or under): 1a-1d mate in 1 by rook/bishop/knight/pawn, 1e mixed mate in 1; 2a-2d win a rook/knight/bishop/queen, 2e save the draw; 3a double check, 3b-3f mate in 2 by queen/rook/knight/bishop/pawn; 4a-4d sacrifice queen/rook/bishop/knight; 5a-5d win a pinned (to the king) rook/knight/bishop/queen by attacking it with another piece.

Every puzzle is a JSON object with `fen` (side to move may be either colour), `solution` (UCI moves: yours, the reply, yours...), `objective_move` (= `solution[0]`), `batch`, `batch_title` and `order`. Mate-in-1 and mate-in-2 puzzles have exactly one answer (checked by the harvester). `PuzzleManager.get_batches()`, `get_batch(id)` and `get_batch_title(id)` read them. The harvester source is `Tools/harvester_src/` (`shell.html` + `app.js`; `build.py` inlines chess.js, BSD-2, into one file). `Tools/harvest_lichess_puzzles.py` is the older command-line harvester and is superseded by it.

Playing a batch: open `Scenes/Puzzles/Drill/BatchDrill.tscn`, set **Batch Id** in the Inspector (`1a`, `3b`, `5c`... or an old pack name like `rook_mate_in_1`) and run the scene with F6. It plays the batch easiest first and makes the opponent's replies for multi-move solutions (`BatchDrill.gd`). To launch it from code: `GameState.set_meta("drill_batch", "1a")` then `GameManager.go_to_scene("res://Scenes/Puzzles/Drill/BatchDrill.tscn")`.

All battle/puzzle dialog is spoken in the right-hand bubble (never over the board); buttons (Next, the Menu options) appear in the left panel via `GameUI.show_choices()`. The **Menu** button in a drill offers Continue (next puzzle of this type; resumes the unsolved one if you leave mid-puzzle), Different puzzles (DrillMenu) and Exit (back to the world). Progress per batch is kept in `GameState.drill_progress` while the game runs. To open the drills from the world, call `GameManager.start_drills(player_node.global_position)`; Exit then returns the player to that spot.

Not built yet: a world entry point (NPC/door) that calls `start_drills`, and saving drill progress to disk.
