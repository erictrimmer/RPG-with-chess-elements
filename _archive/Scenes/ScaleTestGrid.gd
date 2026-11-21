extends Node2D
# Draws a faint 16px grid over the scale test. Press G to toggle.
@export var size_tiles := Vector2i(60, 50)

func _draw():
	var c := Color(1, 1, 1, 0.12)
	for x in range(size_tiles.x + 1):
		draw_line(Vector2(x * 16, 0), Vector2(x * 16, size_tiles.y * 16), c)
	for y in range(size_tiles.y + 1):
		draw_line(Vector2(0, y * 16), Vector2(size_tiles.x * 16, y * 16), c)

func _unhandled_input(event):
	if event is InputEventKey and event.pressed and event.keycode == KEY_G:
		visible = not visible
