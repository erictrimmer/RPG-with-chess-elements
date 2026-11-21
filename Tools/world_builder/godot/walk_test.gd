extends SceneTree
## Drives the real player with simulated input inside the generated test scene and reports where it
## ends up, to prove collision works: walking into a building must stop, walking along a street must not.
## Run: Godot_console.exe --headless --path <project> --script res://Tools/world_builder/godot/walk_test.gd

var scene: Node
var player: CharacterBody2D
var tests := [
	# [name, start tile, action, frames, expectation]
	["north into depot (should stop at its wall)", Vector2(121, 122), "move_up", 120, "blocked"],
	["east along rail lane (should travel)", Vector2(121, 122), "move_right", 60, "moves"],
	["north up George St road (should travel)", Vector2(110, 100), "move_up", 90, "moves"],
	["east into the drugstore from George sidewalk (should stop)", Vector2(113, 100), "move_right", 90, "blocked"],
	["north into creek wall from inner walk (should stop)", Vector2(70, 47), "move_up", 90, "blocked"],
	["south across Market St bridge deck (should travel)", Vector2(47, 79), "move_down", 60, "moves"],
]
var t := 0
var frame := 0
var start_pos := Vector2.ZERO

func _init() -> void:
	scene = (load("res://World/Downtown/downtown_test.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	player = scene.get_node("Player")

func _physics_process(_d: float) -> bool:
	if t >= tests.size():
		return true
	var tc = tests[t]
	if frame == 0:
		player.global_position = tc[1] * 16.0 + Vector2(8, 12)
		player.velocity = Vector2.ZERO
		start_pos = player.global_position
		Input.action_press(tc[2])
	frame += 1
	if frame >= int(tc[3]):
		Input.action_release(tc[2])
		var moved := player.global_position.distance_to(start_pos)
		var expected_px := 100.0 * int(tc[3]) / 60.0
		var ok := (moved < expected_px * 0.6) if tc[4] == "blocked" else (moved > expected_px * 0.9)
		print("%s  %s: moved %.0f px of %.0f possible -> tile %s" % ["PASS" if ok else "FAIL", tc[0], moved, expected_px,
			str((player.global_position / 16.0).floor())])
		t += 1
		frame = 0
	return false
