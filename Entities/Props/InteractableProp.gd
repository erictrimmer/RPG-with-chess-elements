extends StaticBody2D
class_name InteractableProp

## Base scene for solid, explicitly-interactive environment objects
## (chessboards, signs, locked doors, shop counters — see Style Bible §8).
## Instance or inherit this scene rather than hand-wiring Area2D/signals per object.

signal interaction_requested(interaction_id: String)
signal player_entered_range
signal player_exited_range

@export var interaction_id: String = ""
@export var prompt_text: String = "Press Space"

@onready var interaction_area: Area2D = $InteractionArea

var is_player_in_range := false

func _ready() -> void:
	add_to_group("interactable_props")

func _process(_delta: float) -> void:
	if is_player_in_range and Input.is_action_just_pressed("ui_accept"):
		emit_signal("interaction_requested", interaction_id)

func _on_interaction_area_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		is_player_in_range = true
		emit_signal("player_entered_range")

func _on_interaction_area_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		is_player_in_range = false
		emit_signal("player_exited_range")
