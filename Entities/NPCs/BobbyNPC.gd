extends CharacterBody2D

signal interaction_requested(interaction_id: String)

@onready var interaction_area = $InteractionArea
@onready var sprite = $Sprite2D
@onready var animation_player = $AnimationPlayer
var is_player_in_range = false

func _ready():
	add_to_group("npcs")
	# Start with idle (frame 0)
	sprite.frame = 0

func _process(_delta):
	if is_player_in_range and Input.is_action_just_pressed("ui_accept"):
		print("BobbyNPC interaction triggered.")
		play_talking()  # Start talking animation
		emit_signal("interaction_requested", "show_bobby_challenge")
	
	# Monitor frame if animation is playing
	if animation_player and animation_player.is_playing():
		if animation_player.current_animation == "taunt":
			print("Bobby Frame: ", sprite.frame, " Time: ", animation_player.current_animation_position)

func _on_area_entered(body):
	print("BobbyNPC: Body entered - ", body.name, " in group player: ", body.is_in_group("player"))
	if body.is_in_group("player"):
		is_player_in_range = true
		modulate = Color(1.3, 1.3, 1.3)
		print("BobbyNPC: Player in range, lighting up!")
		
func _on_area_exited(body):
	if body.is_in_group("player"):
		is_player_in_range = false
		modulate = Color(1.0, 1.0, 1.0)
		emit_signal("interaction_requested", "close_dialog")
		# Stop any animations when player leaves
		animation_player.stop()
		sprite.frame = 0

# Call this when Bobby is talking (during dialog)
func play_talking():
	print("BobbyNPC: play_talking() called")
	if animation_player:
		animation_player.play("talking")
		print("BobbyNPC: Playing 'talking' animation")

# Call this when player loses or gives up
func play_taunt():
	print("BobbyNPC: play_taunt() called")
	if animation_player:
		animation_player.play("taunt")
		print("BobbyNPC: Playing 'taunt' animation")
	else:
		print("BobbyNPC: ERROR - animation_player is null!")

# Call this to return to idle
func stop_animations():
	print("BobbyNPC: stop_animations() called")
	if animation_player:
		animation_player.stop()
		sprite.frame = 0
