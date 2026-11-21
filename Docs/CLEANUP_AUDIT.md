# Cleanup audit

Read-only scan of the project on 2026-11-21. Nothing was deleted or moved.
Safety net: commit `e3d047e` on branch `checkpoint/pre-cleanup` has everything except the two things
listed under "Not in the checkpoint".

**How "unreferenced" was decided.** I built a reference graph from every `res://` path and `uid://` in
scenes, resources and scripts, then walked it from: `project.godot` (main scene and autoloads),
`GameManager.gd`'s scene list, the drill and tutorial scenes, `downtown_test.tscn`, and
`depot_interior.tscn`. A file counts as **unreachable** if the walk never touches it. That does not
prove it is dead: something that is only opened from the editor, or a tool you run by hand, shows up as
unreachable. I found no dynamic scene loading (no `load("res://..." + name)` patterns), so the scan
should not be missing hidden references. Of 2,122 files scanned, 152 were reachable.

## Not in the checkpoint (on purpose)

| Item | Size | Why |
|---|---|---|
| `Assets/Modern Exteriors/` | 18 MB | Licensed pack, not for redistribution. Back it up where you bought it. |
| `Puzzles/lichess_db_puzzle.csv` | 1.1 GB | Source data for the puzzle harvester. Too big for GitHub. Re-downloadable. |

Both should go into `.gitignore` (proposed below). Neither is touched by cleanup.

## Tier A: safe to delete (junk, duplicates, regenerable)

| Files | Notes |
|---|---|
| `Entities/Player/*.tmp` (4), `Scenes/BattleScene.tscn*.tmp` (3) | Godot editor temp files from crashed saves. |
| `PawnJourney.csproj.old`, `files.zip` | Old project file; stray zip (already git-ignored). |
| `Entities/3D Objects/desktop.ini` | Windows folder metadata. |
| `Assets/Sprites/Grok _ X.html` and `Grok _ X_files/` (20 files, 6.6 MB) | A saved web page. |
| `Data/Puzzles/Puzzle packs/` (5 files) | Byte-for-byte duplicate of `Data/PuzzlePacks/`. |
| `Assets/Interiors/depot/chair_a.png`, `window_pane.png` | Cropped props I made and ended up not using. |

## Tier B: archive (dead today, might be wanted later)

Move to `_archive/` (git-ignored for Godot's import step) rather than delete.

- **Broken bot scripts and their data** (listed in CLAUDE.md as crashing): `Scenes/Bots/Bot200*`,
  `ItalianPunisher*`, `ScholarsMate*`, `BobbyBot.gd`, plus `Data/BotConfigs/italian_punisher.json`,
  `scholars_mate.json` and `Data/OpeningBooks/italian_game.json`, `scholars_mate.json`.
- **Stub scenes** (under 1 KB, unused): `Components/Knight.tscn`, `Components/Pieces/*.tscn` (6),
  `Entities/Buildings/Market.tscn`, `Entities/Enemies/KnightNPC.*`, `Entities/Player/character_body_2d.tscn`,
  `Scenes/World.gd.tscn`, `Scenes/board.tscn`, `Scenes/Main.tscn`, `Scenes/test_lifecycle.*`,
  `Scenes/Puzzles/PawnTutorial.tscn` (stale duplicate), `Scenes/Puzzles/BackRankMateTest.*`.
- **Superseded tile art:** `Assets/Tiles/` (486 single tiles, 88 KB), `Assets/Game_Maker_Studio_Autotiles_*`,
  `Scenes/Godot_Autotiles_16x16.png` (differs from the copy in `Assets/Tilemap/`),
  `Assets/Tilemap/Modern_Exteriors_Complete_Tileset.png` (6.9 MB), `Assets/Tilemap/DowntownTileSet.tres`.
- **Unused art packs:** `Assets/Sprites/Pixel Crawler - Free Pack/` (338 files, 2.5 MB),
  `Assets/Sprites/chess images/` (24 files), `Assets/Sprites/pieces/` (11 of 12 unused; only `wp.png` is referenced, and the Staunton set is
  the one in use), `Assets/Sprites/Backgrounds`, `Buildings`, `red_square_bot.png`, `red_circle.png`.
- **Old character sheets:** `Max.png`, `max_spritesheet*.png`, `New_max_spritesheet.png`,
  `Entities/Player/bobby.svg`. Keep `Bobby_idle_spritemap.png` (still referenced) and
  `NewCharacterSheet.png` (the old player, used by `player.tscn`). `Chess_RPG_cyhippy.png` is the
  current player's sheet.
- **Root-level one-off scripts:** `center_sprites.py`, `fix_sprite_centering.py`, `create_perfect_spritesheet.py`,
  `check_img.py`, `check_new_sprite.py`, `check_logic.gd`, `check_size.gd`. Move to `Tools/legacy/`.
- **Scale-test scaffolding:** `Assets/ScaleTest/`, `Scenes/ScaleTest.tscn`, `Scenes/ScaleTestGrid.gd`,
  `Claude outputs/scaletest_preview.png`.
- **`Engine/chess_engine.exe`** (590 KB): CLAUDE.md says Stockfish runs from here, but nothing in the code
  references it, and the engine log says the embedded MinimalChess is in use. Confirm, then archive.

## Tier C: your decision

- **Old overworld:** `Scenes/Downtown.tscn` (85 KB), `Scenes/Yorktown.tscn`, `MainWorld.tscn`,
  `Scenes/demo.tscn` (the current main scene). They look superseded by the generated `World/Downtown/`, but
  `demo.tscn` and `GameManager` still use them, and `Yorktown.tscn` and `MainWorld.tscn` have broken tile
  references (below).
- **Generated town tooling:** `Tools/world_builder/` (39 files) and `World/Downtown/`. You said the level isn't
  good enough yet; keep until the handcrafted replacement exists.
- **Forge character sheets:** the 25 `Chess_RPG_*.png` sheets are unreferenced only because they aren't placed
  in the world yet. These are your new NPC art. Keep.
- **Unreachable but alive-looking:** `Scenes/MainMenu.*`, `PlacementMatch.*`, King, Bishop and Rook tutorials,
  `Entities/NPCs/Visitor.*`, `Scenes/Wireframe.gd`, `Systems/BattleTheme.gd`, `BotDialogue.gd`, `PgnWriter.gd`,
  `Data/Dialogue/default.json`. They are likely story material or in-progress; keep until the plan says otherwise.
- **Puzzle and book data:** `Data/PuzzlePacks/`, `Data/Fischer.pgn` (used by `build_fischer_book.py`),
  `Tools/harvester_src/`, `Tools/PuzzleHarvester.html`.

## Broken references (real bugs, not clutter)

| File | Points at (missing) |
|---|---|
| `Systems/DialogManager.gd` | `Assets/Sprites/Characters/librarian_portrait.png` (a live autoload) |
| `Systems/MatchConfig.gd` | `Scenes/world.tscn` |
| `Entities/Enemies/KnightNPC.tscn` | `Scenes/world.tscn` |
| `Scenes/Yorktown.tscn` | `Assets/Tilesets/Pack/Grass.png`, `Street.png`, `Dirt` |
| `MainWorld.tscn` | `Assets/Tilesets/CP_V1.0.4.png` |
| `Scenes/Bots/BobbyBot.gd` | `Assets/Data/fischer_openings.json` (dead file anyway) |

`GameManager.WORLD_SCENE` also points at `demo.tscn` while `CLAUDE.md` and `MainMenu` describe other entry
points, so the docs and the code disagree about what the first scene is.

## Repository health

- `.git` is 501 MB on disk (loose objects; `git gc` would shrink it). The history contains a 7 MB tileset
  PNG and other large binaries.
- Proposed `.gitignore` additions: `Puzzles/lichess_db_puzzle.csv`, `Assets/Modern Exteriors/`,
  `_archive/`, `*.tmp`, `desktop.ini`.
- `CLAUDE.md` is out of date: it names `MainMenu.tscn` as the main scene (it is `demo.tscn`), says Stockfish is
  launched from `Engine/chess_engine.exe` (the code uses MinimalChess), and doesn't mention the forge player,
  `SceneDoor`, the interior or `World/`.

## Suggested order

1. Delete Tier A (small, no risk), then run Godot's headless import to confirm nothing breaks.
2. Move Tier B to `_archive/` in one commit, then import again.
3. Fix the broken references (a short pass: stop pointing at files that don't exist).
4. Update `.gitignore` and `CLAUDE.md`, then `git gc`.
5. Decide Tier C with the master plan in hand.

## Tier A: done

Deleted on branch `checkpoint/pre-cleanup`: 7 `.tmp` files, `PawnJourney.csproj.old`, `files.zip` (every file in
it matched a copy already in the project), `desktop.ini`, the saved `Grok _ X` page, the duplicate
`Data/Puzzles/Puzzle packs/`, and two unused depot props (also removed from `prepare_depot_assets.py`).
After the deletions, Godot re-imports the project with no new errors, and the depot door playthrough
passes (enter and leave through both doors, side and back walls hold).

## Scripts that do not parse (found during the post-cleanup import)

Godot reports parse errors in more scripts than CLAUDE.md lists. None of them are Tier A files, and none of
them are loaded by the scenes the game currently runs:

`Scenes/Bots/Bot200.gd`, `ScholarsMate.gd` (known), plus `Scenes/PlacementMatch.gd`,
`Scenes/Puzzles/BackRankMateTest.gd`, `Scenes/Puzzles/Bishops/BishopTutorial.gd`,
`Scenes/Puzzles/Kings/KingTutorial.gd`. They call functions or use variables (`start_bot_game`,
`start_puzzle`, `game_ui_node`, `_end_game`) that no longer exist on `GameManager`. Add these to Tier C when
you decide what happens to the tutorials.

## Tier B: done

930 files moved (git records them as renames, so history follows) to `_archive/`, keeping their original
folder paths so anything can be moved back. `_archive/.gdignore` makes Godot skip the folder (no import, no
parse errors). Six one-off Python and GDScript tools went to `Tools/legacy/` instead.

Moved: the broken bot scripts and their data, stub scenes, the 486 loose tiles and old autotile sheets, the
unused Pixel Crawler pack, "chess images", old backgrounds and building art, the old Max sprite sheets,
scale-test scaffolding, and `Engine/chess_engine.exe`.

**Kept after a second check** (still referenced by files that remain, so moving them would break something):

| Kept | Because |
|---|---|
| `Assets/Sprites/pieces/` (all 12) | `Systems/BasePiece.gd` loads the 11 other pieces, and `PawnLessonProp.tscn` the pawn. My Tier B list said 11 were unused; the first scan missed `BasePiece.gd` because it is only reached through a class name. |
| `Assets/Tilemap/DowntownTileSet.tres` and `Modern_Exteriors_Complete_Tileset.png` | `Scenes/Downtown.tscn` uses them (Tier C). |
| `Assets/Sprites/Backgrounds/Downtown_Wireframe.png` | `Scenes/Downtown.tscn` uses it (Tier C). |
| `Scenes/Main.tscn` | `Scenes/MainMenu.gd` loads it. |
| `Scenes/Puzzles/PawnTutorial.tscn` | `MainMenu.gd` still points at this "stale duplicate" instead of the one in `Pawns/`. Repoint, then archive. |
| `check_logic.gd` | Documented in CLAUDE.md as the logic test. |

The scan now also counts class-name references (a script that only says `extends BotBase` or `BasePiece`
used to look unreferenced).

Checks after the move: Godot import shows no new errors (only the parse errors already listed for
`PlacementMatch.gd` and the Bishop and King tutorials). All 13 live scenes load and instantiate. The depot
door playthrough passes.

## Broken references: done

| Was | Now |
|---|---|
| `DialogManager.gd` → `librarian_portrait.png` | It was only in a usage example in a comment; the example now uses a placeholder path. |
| `MatchConfig.return_scene_path` → `Scenes/world.tscn` | Points at `Scenes/demo.tscn` (same as `GameManager.WORLD_SCENE`). Nothing reads this field yet. |
| `KingTutorial.gd` → `Scenes/world.tscn` | Calls `GameManager.go_to_world()`. (The script still has its other parse errors.) |
| `MainMenu.gd` → stale `Scenes/Puzzles/PawnTutorial.tscn` | Points at `Scenes/Puzzles/Pawns/PawnTutorial.tscn`; the stale duplicate is now in `_archive/`. |
| `Scenes/Yorktown.tscn`, `MainWorld.tscn` → missing tilesets | Their art (`Assets/Tilesets/`) was deleted in your last commit and `Pack/` is not in history, so these can't be repaired. Moved to `_archive/` with `Yorktown.gd`; the unused `GameManager.YORKTOWN_SCENE` constant is gone. |
| `KnightNPC.tscn`, `BobbyBot.gd` | Already archived in Tier B. |

A scan of every live scene, script and resource now finds no `res://` path that points at a missing file. All
13 live scenes still load; the import errors are unchanged (the PlacementMatch, Bishop and King scripts).
