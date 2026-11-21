# Interiors

## depot_interior.tscn

The inside of the railroad depot in `World/Downtown`. 14 × 12 tiles (224 × 192 px), built from LimeZu's
Modern Interiors (16 px): a checkerboard floor, red beadboard walls, two ticket desks, benches, crates,
plants, a rug and a few wall pictures.

**Doors.** Walk into a door while pushing toward it (up on the way in, down on the way out) and the
next scene loads. Brushing past does nothing.

| Outside (`downtown_test.tscn`) | Inside |
|---|---|
| `DepotDoorWest`: the double arched door, tiles 119-120 | exit doorway on columns 4-5, arrive at (80, 150) |
| `DepotDoorEast`: the single orange door, tile 125 | exit doorway on column 10, arrive at (168, 150) |

The inside doorways sit on the same columns as the doors on the outside, so each exit leads back out of
the door you came in by (to (1920, 1940) and (2008, 1940)).

The door markers in `downtown_level.tscn` (`door_42`, `door_43`) are one tile off the double door as
drawn, so the triggers were placed from the art, not the markers.

## How doors work

`Components/SceneDoor.gd` is an `Area2D`. Set `target_scene`, `target_spawn`, `target_facing` and
`push_action`. It stores the hand-off on the `GameState` autoload (a `next_spawn` meta value) and calls
`GameManager.go_to_scene`. Each level script calls `SceneDoor.apply_pending_spawn(get_tree(), player)` in
`_ready` (`World/Downtown/level_test.gd` and `World/Interior/interior_level.gd` both do). A level scene
needs the player to be in the `player` group, which `player_forge.gd` does.

Doors only work when the game runs with its autoloads (F6 on `downtown_test.tscn` is fine).

## Rebuilding

The scene and `depot_interior_tileset.tres` are generated; hand edits are overwritten on rebuild. Edit
the layout lists at the top of `Tools/world_builder/build_depot_interior.gd`, then:

```
python Tools/world_builder/prepare_depot_assets.py          # only if the cropped props are missing
Godot_console.exe --headless --path . --script res://Tools/world_builder/build_depot_interior.gd
```

Or stop regenerating and edit the scene in the editor. The Modern Interiors pack is licensed for use in
games but not for redistribution; it stays outside the repo (the cropped pieces in `Assets/Interiors/`
are what the game uses). Credit LimeZu (limezu.itch.io).
