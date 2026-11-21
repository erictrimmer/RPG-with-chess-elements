extends CharacterBody2D
## Player driven by a Pixel Character Forge sheet (Character Generator 2.0 layout):
## 56 columns x 20 rows of 16x32 frames. Each animation row holds its directions
## back to back in the order right, up, left, down (6 frames per direction for Idle and Walk).
## Swap `sheet` in the Inspector to make any other forged character playable.

const SPEED := 100.0
const FRAMES := 6
const COLUMNS := 56
const ROW_IDLE := 1
const ROW_WALK := 2
const DIR_INDEX := {&"right": 0, &"up": 1, &"left": 2, &"down": 3}
const WALK_FPS := 10.0
const IDLE_FPS := 3.0

@export var sheet: Texture2D:
	set(value):
		sheet = value
		if is_node_ready():
			$Sprite2D.texture = value

@onready var sprite: Sprite2D = $Sprite2D

var last_direction: StringName = &"down"
var acc := Vector2.ZERO
var _anim_time := 0.0
var _moving := false

func _ready() -> void:
	add_to_group("player")
	if sheet:
		sprite.texture = sheet
	sprite.hframes = COLUMNS
	sprite.vframes = 20
	_update_frame()

func _physics_process(delta: float) -> void:
	var direction := Vector2(
		Input.get_axis("move_left", "move_right"),
		Input.get_axis("move_up", "move_down"))

	if direction.length() > 0.0:
		direction = direction.normalized()
		velocity = direction * SPEED
	else:
		velocity = Vector2.ZERO

	# Same sub-pixel handling as the original player: keep the node on whole pixels.
	var precise_pos := global_position + acc
	move_and_slide()
	precise_pos += velocity * delta
	global_position = precise_pos.floor()
	acc = precise_pos - global_position

	_pick_direction(direction)
	var was_moving := _moving
	_moving = direction.length_squared() > 0.0
	if _moving != was_moving:
		_anim_time = 0.0
	_anim_time += delta
	_update_frame()

func _pick_direction(input_vector: Vector2) -> void:
	if input_vector.length_squared() == 0.0:
		return
	# Prefer the current axis a little so diagonals don't flicker between sprites.
	var h_pref := 0.1 if (last_direction == &"left" or last_direction == &"right") else 0.0
	var v_pref := 0.1 if (last_direction == &"up" or last_direction == &"down") else 0.0
	if absf(input_vector.x) + h_pref >= absf(input_vector.y) + v_pref:
		last_direction = &"right" if input_vector.x > 0.0 else &"left"
	else:
		last_direction = &"down" if input_vector.y > 0.0 else &"up"

func _update_frame() -> void:
	var row := ROW_WALK if _moving else ROW_IDLE
	var fps := WALK_FPS if _moving else IDLE_FPS
	var step := int(_anim_time * fps) % FRAMES
	var col: int = DIR_INDEX[last_direction] * FRAMES + step
	sprite.frame = row * COLUMNS + col
