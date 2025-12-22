extends "res://Scenes/Bots/BotBase.gd"

func _ready():
	# Load config BEFORE calling super._ready()
	load_bot_config("res://Data/BotConfigs/italian_punisher.json")
	
	# Call parent initialization
	super._ready()
	
	# Get color from config (white/black/random)
	var player_is_white = get_player_color()
	
	# Use config values
	var elo = bot_config.get("elo", 600)
	var difficulty = 200
	
	await get_tree().create_timer(0.1).timeout
	start_bot_game(player_is_white, difficulty, elo)

