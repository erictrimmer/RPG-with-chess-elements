extends "res://Systems/GameManager.gd"

func _ready():
	# Allow base initialization
	super._ready()
	
	randomize()
	# 50/50 Chance to be White or Black
	var player_is_white = randi() % 2 == 0
	
	# Difficulty: 200ms (gives some variety in moves)
	var difficulty = 200 
	
	# ELO Rating: 200 (Beginner)
	var elo = 200
	
	# Delay slightly for UI init
	await get_tree().create_timer(0.1).timeout
	
	start_bot_game(player_is_white, difficulty, elo)
