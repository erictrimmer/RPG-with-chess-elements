@tool
extends EditorScript

func _run():
	var texture = load("res://Assets/Sprites/Characters/max_spritesheet.png")
	if texture:
		print("Image Size: ", texture.get_width(), "x", texture.get_height())
	else:
		print("Could not load texture")
