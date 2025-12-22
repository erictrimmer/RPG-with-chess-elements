extends CharacterBody2D

func _ready():
	add_to_group("player")

const SPEED = 100.0
# Time (in seconds) before the player switches to the special "Idle" animation
const TIMED_IDLE_TIMEOUT: float = 5.0 

@onready var sprite = $Sprite2D
@onready var anim = $AnimationPlayer

# Track the last direction the player was facing
var last_direction = "down"

# Variable: Counter for the idle timer
var timed_idle_timer: float = 0.0

# --- CONSTANTS for Animation Names (Case-sensitive names from your AnimationPlayer) ---
const ANIM_WALKSIDE = &"WalkSide"
const ANIM_WALKDOWN = &"WalkDown"
const ANIM_WALKUP = &"WalkUp"
const ANIM_IDLESIDE = &"IdleSide"
const ANIM_IDLEDOWN = &"IdleDown"
const ANIM_IDLEUP = &"IdleUp"
const ANIM_TIMED_IDLE = &"Idle"  # Your 5-second timed idle animation (Loop DISABLED)
# NOTE: ANIM_ACTION and is_doing_action removed.

# Helper function to get the current animation
func get_current_animation_name() -> StringName:
	return anim.get_current_animation()


func _physics_process(delta):
	# Get input direction
	var input_vector = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	
	# --- 1. Handle Action Button (Only detects input; no animation logic) ---
	if Input.is_action_just_pressed("ui_accept"):
		# When space is pressed, the interaction (e.g., with PawnTutorial) should
		# be handled by another node, such as an Area2D signal, NOT here.
		pass 
	
	# --- 2. Handle Movement and Velocity ---
	if input_vector:
		velocity = input_vector * SPEED
	else:
		velocity = Vector2.ZERO
		
	move_and_slide()
	
	position = position.round()
	
	# --- 3. Update Idle Timer ---
	var is_moving = input_vector.length_squared() > 0.0
	
	if is_moving:
		timed_idle_timer = 0.0
	else:
		timed_idle_timer += delta
	
	# --- 4. Update Animation ---
	update_animation(input_vector)


func update_animation(input_vector: Vector2):
	# Action logic is removed, so we only check movement status
		
	var is_moving = input_vector.length_squared() > 0.0
	var current_anim = get_current_animation_name()

	if is_moving:
		# Player is MOVING: Reset timer and play walk animation
		timed_idle_timer = 0.0 
		
		# Moving - play walk animation and update last direction
		if abs(input_vector.x) >= abs(input_vector.y):
			# Horizontal Movement
			var new_anim = ANIM_WALKSIDE
			if current_anim != new_anim:
				anim.play(new_anim)
				
			if input_vector.x > 0:
				sprite.flip_h = false # Right
				last_direction = "right"
			else:
				sprite.flip_h = true # Left
				last_direction = "left"
		else:
			# Vertical Movement
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
		# Player is NOT MOVING: Handle Idle States
		
		# A. Determine the standard directional idle animation
		var standard_idle_anim = ""
		match last_direction:
			"up":
				standard_idle_anim = ANIM_IDLEUP
			"down":
				standard_idle_anim = ANIM_IDLEDOWN
			"left":
				sprite.flip_h = true
				standard_idle_anim = ANIM_IDLESIDE
			"right":
				sprite.flip_h = false
				standard_idle_anim = ANIM_IDLESIDE
			_:
				standard_idle_anim = ANIM_IDLEDOWN
				
		# B. Check if the TIMED IDLE ANIMATION ("Idle") should play
		var should_start_timed_idle = (timed_idle_timer >= TIMED_IDLE_TIMEOUT)
		
		if should_start_timed_idle:
			
			var new_anim = ANIM_TIMED_IDLE
			
			# If we are NOT already playing the special timed idle, start it.
			if current_anim != new_anim:
				anim.play(new_anim)
				
				# Connect signal to know when the one-shot animation finishes
				if not anim.is_connected("animation_finished", Callable(self, "_on_timed_idle_finished")):
					anim.animation_finished.connect(_on_timed_idle_finished)

				# Reset the timer immediately after starting the animation
				timed_idle_timer = 0.0 
				
		# C. If special timed idle is NOT scheduled to play, stick to the standard directional idle.
		elif current_anim != ANIM_TIMED_IDLE: 
			if current_anim != standard_idle_anim:
				anim.play(standard_idle_anim)


# --- TIMED IDLE FINISHED HANDLER (Loop Disabled) ---

func _on_timed_idle_finished(anim_name: StringName):
	if anim_name == ANIM_TIMED_IDLE: 
		
		anim.animation_finished.disconnect(Callable(self, "_on_timed_idle_finished"))
		
		# Force the animation system to re-evaluate its state
		update_animation(Vector2.ZERO)
