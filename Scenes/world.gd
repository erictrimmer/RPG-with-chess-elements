extends Node2D

var player_node
var pawn_tutor_npc
var bobby_npc
var player_saved_position = Vector2.ZERO
var current_npc_interaction = null

func _ready():
	# Find player and NPC nodes
	player_node = get_node_or_null("Player")
	pawn_tutor_npc = get_node_or_null("PawnTutor")
	bobby_npc = get_node_or_null("BobbyNPC")
	var bot_200_npc = get_node_or_null("Bot200NPC")
	
	if not player_node:
		printerr("Player node not found! Make sure there's a node named 'Player' in the scene.")
		# Don't return, allow other logic (might be running test scene)
	
	if pawn_tutor_npc:
		print("Found PawnTutor: ", pawn_tutor_npc.get_script())
		if pawn_tutor_npc.has_signal("interaction_requested"):
			pawn_tutor_npc.interaction_requested.connect(func(type): _on_npc_interaction(type, "pawn_tutor"))
		else:
			printerr("PawnTutor doesn't have interaction_requested signal!")
		
	if bobby_npc:
		print("Found BobbyNPC: ", bobby_npc.get_script())
		if bobby_npc.has_signal("interaction_requested"):
			bobby_npc.interaction_requested.connect(func(type): _on_npc_interaction(type, "bobby"))
		else:
			printerr("BobbyNPC doesn't have interaction_requested signal!")
			
	if bot_200_npc:
		if bot_200_npc.has_signal("interaction_requested"):
			bot_200_npc.interaction_requested.connect(func(type): _on_npc_interaction(type, "bot_200"))
	
	# Connect dialog signals
	if not DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
		DialogManager.dialog_choice_made.connect(_on_dialog_choice)
	
	# Check if returning from tutorial
	# Check if returning from tutorial or battle
	check_world_return_state()
	
	# Expand World
	expand_world_map()

	# Configure Player Camera Limits for single screen
	if player_node:
		var camera = player_node.get_node_or_null("Camera2D")
		if camera:
			camera.limit_left = 0
			camera.limit_top = 0
			camera.limit_right = 320
			camera.limit_bottom = 180

func expand_world_map():
	var tilemap = get_node_or_null("TileMapLayer")
	if tilemap:
		var source_id = 0 # Assuming Floors_Tiles is source 0
		var atlas_coords = Vector2i(1, 4) # A safe existing floor tile coordinate
		
		# Fill a large area
		for x in range(-200, 200):
			for y in range(-200, 200):
				var coords = Vector2i(x, y)
				if tilemap.get_cell_source_id(coords) == -1:
					tilemap.set_cell(coords, source_id, atlas_coords)

func _on_npc_interaction(interaction_type: String, npc_id: String):
	print("World received interaction: ", interaction_type, " from ", npc_id)
	current_npc_interaction = npc_id
	
	match interaction_type:
		"show_initial":
			DialogManager.show_dialog(
				"Want to learn how pawns move?",
				["Yes", "Not now"]
			)
		"show_completed":
			DialogManager.show_dialog("Good job!", [])
		"show_failed":
			DialogManager.show_dialog(
				"Try again?",
				["Yes", "No"]
			)
		"show_bobby_challenge":
			DialogManager.show_dialog(
				"Care for a game? I only play the best moves.",
				["Challenge Bobby", "No thanks"]
			)
		"show_bot_200_challenge":
			DialogManager.show_dialog(
				"Hi! I'm new. Want to play a practice game?",
				["Play Bot 200", "No thanks"]
			)
		"close_dialog":
			DialogManager.close_dialog()
			current_npc_interaction = null

func _on_dialog_choice(choice: String):
	if current_npc_interaction == "pawn_tutor":
		match choice:
			"Yes":
				start_pawn_tutorial()
			"Not now", "No":
				DialogManager.close_dialog()
	
	elif current_npc_interaction == "bobby":
		match choice:
			"Challenge Bobby":
				handle_bobby_challenge_flow()
			"No thanks":
				DialogManager.close_dialog()
				
	elif current_npc_interaction == "bot_200":
		match choice:
			"Play Bot 200":
				start_bot_200_match()
			"No thanks":
				DialogManager.close_dialog()
	
	elif current_npc_interaction == "bobby_color_select":
		match choice:
			"White":
				GameState.player_color_override = "white"
				GameState.bobby_last_color = "black" # Bobby plays Black
				start_bobby_match()
			"Black":
				GameState.player_color_override = "black"
				GameState.bobby_last_color = "white" # Bobby plays White
				start_bobby_match()
	
	elif current_npc_interaction == "bobby_swap_confirm":
		match choice:
			"Let's Play":
				start_bobby_match()

func handle_bobby_challenge_flow():
	# Wait a frame to let the previous dialog close event finish, 
	# otherwise the new dialog gets hidden immediately.
	await get_tree().process_frame
	
	if GameState.bobby_last_color == "none":
		# First time: Ask
		current_npc_interaction = "bobby_color_select"
		DialogManager.show_dialog("Which color do you prefer for our first game?", ["White", "Black"])
	else:
		# Swap colors
		current_npc_interaction = "bobby_swap_confirm"
		var next_bobby_color = "white" if GameState.bobby_last_color == "black" else "black"
		var text = "This time I'll play " + next_bobby_color + "."
		
		# Set states for launch
		GameState.bobby_last_color = next_bobby_color
		GameState.player_color_override = "black" if next_bobby_color == "white" else "white"
		
		DialogManager.show_dialog(text, ["Let's Play"])

func start_bobby_match():
	# Save state
	if player_node:
		GameState.save_player_position(player_node.global_position)
	
	# Set Match Config
	var bobby_res = load("res://Resources/Bots/Bobby.tres")
	if not bobby_res:
		printerr("World ERROR: Failed to load Bobby.tres!")
		return
		
	if GameState.player_color_override == "":
		GameState.player_color_override = "white" # meaningful default
		
	var config = MatchConfig.create_bot_match(bobby_res, GameState.player_color_override)
	GameState.set_match_config(config)
	
	print("World: Starting match vs ", bobby_res.bot_name, " as ", GameState.player_color_override)
	GameManager.go_to_battle(config)

func start_bot_200_match():
	# Save state
	if player_node:
		GameState.save_player_position(player_node.global_position)
	
	# Set Match Config
	var bot_res = load("res://Resources/Bots/Bot200.tres")
	if not bot_res:
		printerr("World ERROR: Failed to load Bot200.tres!")
		return
		
	# Bot 200 is always white for simplicity in this test
	var config = MatchConfig.create_bot_match(bot_res, "black")
	GameState.set_match_config(config)
	
	print("World: Starting match vs ", bot_res.bot_name)
	GameManager.go_to_battle(config)

func start_pawn_tutorial():
	# Save player position
	if player_node:
		player_saved_position = player_node.global_position
		GameState.save_player_position(player_saved_position)
		print("Saved player position: ", player_saved_position)
	
	# Store that we're entering tutorial
	GameState.set_tutorial_state("pawn_tutorial", "in_progress")
	
	# Load tutorial scene
	GameManager.go_to_scene(GameManager.PAWN_TUTORIAL)

func check_world_return_state():
	# 1. Pawn Tutorial Check
	var tutorial_state = GameState.get_tutorial_state("pawn_tutorial")
	
	match tutorial_state:
		"completed":
			if pawn_tutor_npc:
				pawn_tutor_npc.set_dialog_state(pawn_tutor_npc.DialogState.COMPLETED)
			# Reset state
			GameState.set_tutorial_state("pawn_tutorial", "not_started")
		"failed":
			if pawn_tutor_npc:
				pawn_tutor_npc.set_dialog_state(pawn_tutor_npc.DialogState.FAILED)
			# Reset state
			GameState.set_tutorial_state("pawn_tutorial", "not_started")
	
	# 2. General Dialog Check (Bobby GG)
	if GameState.pending_world_dialog == "bobby_gg":
		DialogManager.show_dialog("GG! You played well.", [])
		GameState.pending_world_dialog = ""
		
		# Play Bobby's taunt animation AFTER dialog is shown
		print("Checking Bobby taunt flag: ", GameState.bobby_should_taunt)
		if GameState.bobby_should_taunt and bobby_npc:
			# Wait a frame to ensure everything is loaded
			await get_tree().process_frame
			print("Bobby should taunt! Playing animation...")
			if bobby_npc.has_method("play_taunt"):
				bobby_npc.play_taunt()
				print("Bobby taunt animation started!")
			else:
				print("ERROR: Bobby doesn't have play_taunt method!")
			GameState.bobby_should_taunt = false  # Reset flag
	
	# Restore player position from GameState
	var saved_pos = GameState.get_saved_player_position()
	if saved_pos != Vector2.ZERO and player_node:
		player_node.global_position = saved_pos
		print("Restored player position: ", saved_pos)
