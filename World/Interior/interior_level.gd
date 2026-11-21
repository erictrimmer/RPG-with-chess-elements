extends Node2D
## Test harness for a small interior: puts the player where the door they used leads, pins the
## camera so the room sits centred in the view, and paints the area outside the room black.
## Rooms are smaller than the 480x270 viewport, so the camera limits are exactly viewport-sized.

const SceneDoor := preload("res://Components/SceneDoor.gd")
const VIEW := Vector2i(480, 270)

@export var player_path: NodePath = ^"Entities/Player"
## Room size in pixels (set by the builder script).
@export var room_size := Vector2i(224, 192)

func _ready() -> void:
	RenderingServer.set_default_clear_color(Color.BLACK)
	var player := get_node_or_null(player_path)
	if player == null:
		return
	SceneDoor.apply_pending_spawn(get_tree(), player)
	var cam: Camera2D = player.get_node_or_null("Camera2D")
	if cam:
		var c := Vector2i(room_size / 2)
		var tl := c - VIEW / 2
		cam.limit_left = tl.x
		cam.limit_top = tl.y
		cam.limit_right = tl.x + VIEW.x
		cam.limit_bottom = tl.y + VIEW.y
		cam.reset_smoothing()

func _exit_tree() -> void:
	# Back to Godot's default grey for the overworld scenes.
	RenderingServer.set_default_clear_color(Color(0.3, 0.3, 0.3))
