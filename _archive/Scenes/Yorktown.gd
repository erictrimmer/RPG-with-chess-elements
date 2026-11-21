extends Node2D

@onready var player_node = $Entities/Player
@onready var entities_node = $Entities

func _ready():
	# Initial setup for Yorktown
	print("Yorktown: Scene loaded.")
	
	# Connect to Global signals if needed
	if not DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
		DialogManager.dialog_choice_made.connect(_on_dialog_choice)
		
	# Setup Camera limits for Yorktown (approx 2000x2000)
	if player_node:
		var camera = player_node.get_node_or_null("Camera2D")
		if camera:
			camera.limit_left = 0
			camera.limit_top = 0
			camera.limit_right = 2000
			camera.limit_bottom = 2000
			print("Yorktown: Camera limits set to 2000x2000.")

func _on_dialog_choice(choice: String):
	# Handle generic dialog choices for Yorktown quests
	pass

func _on_npc_interaction(interaction_type: String, npc_id: String):
	# To be implemented when NPCs are added
	pass
