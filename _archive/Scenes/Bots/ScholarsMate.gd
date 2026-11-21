extends "res://Scenes/Bots/BotBase.gd"

func _ready():
	load_bot_config("res://Data/BotConfigs/scholars_mate.json")
	super._ready()
	
	var player_is_white = get_player_color()
	var elo = bot_config.get("elo", 400)
	var difficulty = 100
	
	await get_tree().create_timer(0.1).timeout
	start_bot_game(player_is_white, difficulty, elo)
