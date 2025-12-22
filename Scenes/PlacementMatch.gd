extends BattleController

func _ready():
	# Configure the match for calibration
	var config = MatchConfig.new()
	config.mode = MatchConfig.Mode.STANDARD
	config.player_color = "white"
	GameState.current_match_config = config
	
	super._ready() # Standard setup
	
	is_bot_game = true 
	bot_difficulty_ms = 800
	_targetElo = 800 
	
	# Updating UI specifically for Placement
	if game_ui_node:
		game_ui_node.update_status("Placement Match: Play your best!")

# Intercept Game Over to calculate ELO
func _end_game(reason: String):
	# Don't call super._end_game because we want custom behavior here
	is_battle_active = false
	if game_ui_node: 
		game_ui_node.update_status(reason)
		game_ui_node.disable_buttons()
	
	var result_score = 0.5 # Draw
	if "White Wins" in reason:
		result_score = 1.0
	elif "Black Wins" in reason:
		result_score = 0.0
	
	_calculate_initial_rating(result_score)

func _calculate_initial_rating(score: float):
	var estimated_rating = 400.0
	
	if score == 1.0:
		estimated_rating = 800.0
		DialogManager.show_dialog("Victory! Your estimated rating is 800.", ["Return to World"])
	elif score == 0.5:
		estimated_rating = 400.0
		DialogManager.show_dialog("Draw. Your estimated rating is 400.", ["Return to World"])
	else:
		estimated_rating = 100.0
		DialogManager.show_dialog("Defeat. Your estimated rating is 100. Keep practicing!", ["Return to World"])
		
	# Save to GameState
	GameState.player_rating = estimated_rating
	GameState.games_played += 1
	GameState.is_rating_established = true
	
	# Wait for dialog choice
	if not DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
		DialogManager.dialog_choice_made.connect(_on_dialog_choice)

func _on_dialog_choice(choice: String):
	if choice == "Return to World":
		if DialogManager.dialog_choice_made.is_connected(_on_dialog_choice):
			DialogManager.dialog_choice_made.disconnect(_on_dialog_choice)
		GameManager.go_to_world()
