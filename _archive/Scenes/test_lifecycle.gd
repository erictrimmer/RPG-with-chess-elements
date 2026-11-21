extends Node2D

func _ready():
	print("LIFECYCLE: World scene ready!")
	var label = Label.new()
	label.text = "IF YOU SEE THIS, THE ENGINE IS WORKING"
	label.position = Vector2(50, 80)
	add_child(label)
