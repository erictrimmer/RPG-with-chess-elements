extends Area2D
## A doorway between two scenes. The player triggers it by walking into it, i.e. by overlapping
## this area while holding the `push_action` direction (so brushing past a door does nothing).
##
## Place it so it overlaps the player's feet when they stand pressed against the door.
## Both scenes consume the hand-off through `SceneDoor.apply_pending_spawn(player)`.

const META_KEY := &"next_spawn"

@export_file("*.tscn") var target_scene: String
## Where the player appears in the target scene (that scene's pixel coordinates).
@export var target_spawn := Vector2.ZERO
## Direction the player faces on arrival: "up", "down", "left" or "right".
@export var target_facing: StringName = &"up"
## Input action that must be held while overlapping for the door to open.
@export var push_action: StringName = &"move_up"
## Seconds after the scene loads before the door can fire (stops instant bounce-back).
@export var arm_delay := 0.5

var _age := 0.0
var _used := false

func _ready() -> void:
	collision_layer = 0
	collision_mask = 1 # the player lives on layer 1
	monitoring = true

func _physics_process(delta: float) -> void:
	_age += delta
	if _used or _age < arm_delay or target_scene == "":
		return
	if not Input.is_action_pressed(push_action):
		return
	for body in get_overlapping_bodies():
		if body.is_in_group("player"):
			_use()
			return

func _use() -> void:
	_used = true
	var state := get_node_or_null("/root/GameState")
	var manager := get_node_or_null("/root/GameManager")
	if state == null or manager == null:
		push_warning("SceneDoor needs the GameState and GameManager autoloads (run the game, not a bare scene).")
		_used = false
		return
	state.set_meta(META_KEY, {"pos": target_spawn, "facing": target_facing})
	manager.go_to_scene(target_scene)

## Called by a level's script in _ready: moves the player to the spawn point a door asked for.
static func apply_pending_spawn(tree: SceneTree, player: Node2D) -> bool:
	var state := tree.root.get_node_or_null("GameState")
	if state == null or player == null or not state.has_meta(META_KEY):
		return false
	var data: Dictionary = state.get_meta(META_KEY)
	state.remove_meta(META_KEY)
	player.global_position = data["pos"]
	if "last_direction" in player:
		player.last_direction = data["facing"]
	if "acc" in player:
		player.acc = Vector2.ZERO
	return true
