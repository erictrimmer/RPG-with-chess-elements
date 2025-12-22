extends CharacterBody2D

signal interaction_requested(npc_name: String)

@export var npc_name = "Pawn Tutor"
@export var interaction_range = 30.0

@onready var interaction_area = $InteractionArea
@onready var sprite = $Sprite2D
var is_player_in_range = false

# Dialog states
enum DialogState { INITIAL, COMPLETED, FAILED }
var dialog_state = DialogState.INITIAL

func _ready():
	add_to_group("npcs")
	print("PawnTutor: _ready() called, position: ", global_position)
	print("PawnTutor: InteractionArea exists: ", has_node("InteractionArea"))
	if has_node("InteractionArea"):
		var area = get_node("InteractionArea")
		print("PawnTutor: InteractionArea collision_mask: ", area.collision_mask)
		print("PawnTutor: InteractionArea monitoring: ", area.monitoring)

func _process(_delta):
	if is_player_in_range and Input.is_action_just_pressed("ui_accept"):
		print("PawnTutor: Interact key pressed")
		show_dialog()

func _on_area_entered(body):
	print("PawnTutor: Body entered - ", body.name, " in group player: ", body.is_in_group("player"))
	if body.is_in_group("player"):
		is_player_in_range = true
		modulate = Color(1.3, 1.3, 1.3)
		print("PawnTutor: Player in range, lighting up!")

func _on_area_exited(body):
	if body.is_in_group("player"):
		is_player_in_range = false
		modulate = Color(1.0, 1.0, 1.0)
		emit_signal("interaction_requested", "close_dialog")

func show_dialog():
	print("PawnTutor: Attempting to show dialog. State: ", dialog_state)
	match dialog_state:
		DialogState.INITIAL:
			print("PawnTutor: Emitting 'show_initial' signal")
			emit_signal("interaction_requested", "show_initial")
		DialogState.COMPLETED:
			print("PawnTutor: Emitting 'show_completed' signal")
			emit_signal("interaction_requested", "show_completed")
		DialogState.FAILED:
			print("PawnTutor: Emitting 'show_failed' signal")
			emit_signal("interaction_requested", "show_failed")

func set_dialog_state(state: DialogState):
	dialog_state = state
