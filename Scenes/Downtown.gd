extends Node2D

@onready var player_node = $Entities/Player
@onready var entities_node = $Entities

func _ready():
	# Initial setup for Downtown
	print("Downtown: Scene loaded.")
	
	# Connect to Global signals if needed
	if DialogManager and DialogManager.dialog_choice_made:
		if not DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
			DialogManager.dialog_choice_made.connect(_on_dialog_choice)
		
	# Setup Camera limits for Downtown based on the tilemap size
	if player_node:
		var camera = player_node.get_node_or_null("Camera2D")
		if camera:
			camera.limit_left = 0
			camera.limit_top = 0
			# world size: 1504px
			camera.limit_right = 1504
			camera.limit_bottom = 1504
			camera.zoom = Vector2(1.0, 1.0)
			print("Downtown: Camera zoom set to 1.0 and limits to 1504x1504.")

func _on_dialog_choice(choice: String):
	# Handle generic dialog choices for Downtown quests
	pass

func _on_npc_interaction(interaction_type: String, npc_id: String):
	# To be implemented when NPCs are added
	pass
