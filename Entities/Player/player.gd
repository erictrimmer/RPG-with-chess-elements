extends CharacterBody2D

func _ready():
	add_to_group("player")

const SPEED = 100.0
const TIMED_IDLE_TIMEOUT: float = 5.0 

@onready var sprite = $Sprite2D
@onready var anim = $AnimationPlayer

var last_direction = "down"
var timed_idle_timer: float = 0.0

const ANIM_WALKSIDE = &"WalkSide"
const ANIM_WALKLEFT = &"WalkLeft"
const ANIM_WALKDOWN = &"WalkDown"
const ANIM_WALKUP = &"WalkUp"
const ANIM_IDLESIDE = &"IdleSide"
const ANIM_IDLELEFT = &"IdleLeft"
const ANIM_IDLEDOWN = &"IdleDown"
const ANIM_IDLEUP = &"IdleUp"
const ANIM_TIMED_IDLE = &"Idle"

func get_current_animation_name() -> StringName:
	return anim.get_current_animation()

var acc := Vector2.ZERO

func _physics_process(delta):
	var direction := Vector2.ZERO
	direction.x = Input.get_axis("move_left", "move_right")
	direction.y = Input.get_axis("move_up", "move_down")
	
	if direction.length() > 0:
		direction = direction.normalized()
		velocity = direction * SPEED
		timed_idle_timer = 0.0
	else:
		velocity = Vector2.ZERO
		timed_idle_timer += delta
		
	# Store precise position before physics
	var precise_pos = global_position + acc
	
	move_and_slide()
	
	# Calculate how much we were SUPPOSED to move including the remainder
	precise_pos += velocity * delta
	
	# Snap the actual node to the whole pixel
	global_position = precise_pos.floor()
	
	# Save the remainder for the next frame
	acc = precise_pos - global_position
	
	update_animation(direction)

func update_animation(input_vector: Vector2):
	var is_moving = input_vector.length_squared() > 0.0
	var current_anim = get_current_animation_name()

	if is_moving:
		var abs_x = abs(input_vector.x)
		var abs_y = abs(input_vector.y)
		
		var h_pref = 0.1 if (last_direction == "left" or last_direction == "right") else 0.0
		var v_pref = 0.1 if (last_direction == "up" or last_direction == "down") else 0.0
		
		if (abs_x + h_pref) >= (abs_y + v_pref):
			if input_vector.x > 0:
				var new_anim = ANIM_WALKSIDE
				if current_anim != new_anim:
					anim.play(new_anim)
				sprite.flip_h = false
				last_direction = "right"
			else:
				var new_anim = ANIM_WALKLEFT
				if current_anim != new_anim:
					anim.play(new_anim)
				sprite.flip_h = false
				last_direction = "left"
		else:
			if input_vector.y > 0:
				var new_anim = ANIM_WALKDOWN
				if current_anim != new_anim:
					anim.play(new_anim)
				last_direction = "down"
			else:
				var new_anim = ANIM_WALKUP
				if current_anim != new_anim:
					anim.play(new_anim)
				last_direction = "up"
	else:
		var standard_idle_anim = ""
		match last_direction:
			"up": standard_idle_anim = ANIM_IDLEUP
			"down": standard_idle_anim = ANIM_IDLEDOWN
			"left": 
				sprite.flip_h = false
				standard_idle_anim = ANIM_IDLELEFT
			"right":
				sprite.flip_h = false
				standard_idle_anim = ANIM_IDLESIDE
			_: standard_idle_anim = ANIM_IDLEDOWN
				
		var should_start_timed_idle = (timed_idle_timer >= TIMED_IDLE_TIMEOUT)
		
		if should_start_timed_idle:
			var new_anim = ANIM_TIMED_IDLE
			if current_anim != new_anim:
				anim.play(new_anim)
				if not anim.is_connected("animation_finished", Callable(self, "_on_timed_idle_finished")):
					anim.animation_finished.connect(_on_timed_idle_finished)
				timed_idle_timer = 0.0 
		elif current_anim != ANIM_TIMED_IDLE: 
			if current_anim != standard_idle_anim:
				anim.play(standard_idle_anim)

func _on_timed_idle_finished(anim_name: StringName):
	if anim_name == ANIM_TIMED_IDLE: 
		if anim.is_connected("animation_finished", Callable(self, "_on_timed_idle_finished")):
			anim.animation_finished.disconnect(Callable(self, "_on_timed_idle_finished"))
		update_animation(Vector2.ZERO)
