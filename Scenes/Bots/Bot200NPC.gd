extends Area2D

signal interaction_requested(type)

enum DialogState { INITIAL, WIN, LOSE, IDLE }
var current_state = DialogState.INITIAL

func _ready():
	# Visual setup - ensure sprite is visible
	var sprite = $Sprite2D
	if sprite:
		sprite.modulate = Color(1, 1, 1, 1) # Ensure full visibility
		sprite.scale = Vector2(0.05, 0.05) # Scale down the giant pawn texture

func _input(event):
	if event.is_action_pressed("interact") and len(get_overlapping_bodies()) > 0:
		for body in get_overlapping_bodies():
			if body.name == "Player":
				print("Bot200 Interaction Request Sent")
				emit_signal("interaction_requested", "show_bot_200_challenge")
				get_viewport().set_input_as_handled()

func _on_body_entered(body):
	if body.name == "Player":
		$Sprite2D.modulate = Color(1.2, 1.2, 1.2) # Highlight

func _on_body_exited(body):
	if body.name == "Player":
		$Sprite2D.modulate = Color(1, 1, 1) # Normal
