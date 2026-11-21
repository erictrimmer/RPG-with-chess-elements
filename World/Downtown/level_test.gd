extends Node2D
## Test harness for a generated world level: clamps the player's camera to the level bounds.
## The level scene stores its pixel size in the "size_px" metadata.
## If the player came through a SceneDoor (e.g. out of a building), they are moved to its spawn point.

const SceneDoor := preload("res://Components/SceneDoor.gd")

@export var level_path: NodePath = ^"Level"
@export var player_path: NodePath = ^"Player"

func _ready() -> void:
	var level := get_node_or_null(level_path)
	var player := get_node_or_null(player_path)
	if level == null or player == null:
		return
	SceneDoor.apply_pending_spawn(get_tree(), player)
	var size: Vector2i = level.get_meta("size_px", Vector2i(2560, 2048))
	var cam: Camera2D = player.get_node_or_null("Camera2D")
	if cam:
		cam.limit_left = 0
		cam.limit_top = 0
		cam.limit_right = size.x
		cam.limit_bottom = size.y
