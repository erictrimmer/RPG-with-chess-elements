extends CharacterBody2D

@onready var animation_player = $AnimationPlayer
@onready var sprite = $Sprite2D

@export var character_name: String = "Visitor"
@export var initial_direction: String = "down"

func _ready():
	play_idle(initial_direction)

func play_idle(direction: String):
	match direction.lower():
		"right":
			animation_player.play("IdleRight")
		"up":
			animation_player.play("IdleUp")
		"left":
			animation_player.play("IdleLeft")
		"down", _:
			animation_player.play("IdleDown")

func _on_area_entered(body):
	if body.name == "Player":
		if DialogManager:
			DialogManager.show_dialog("Hi")

func _on_area_exited(body):
	if body.name == "Player":
		if DialogManager:
			DialogManager.close_dialog()
