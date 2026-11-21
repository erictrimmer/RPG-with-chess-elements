extends Control
class_name BattleBackdrop
## Flat full-screen backdrop for battles: two close tones in a soft checker plus a spotlight
## band behind the board. Pure drawing, no assets.

const CELL := 24

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func _draw() -> void:
	var s := get_viewport_rect().size
	draw_rect(Rect2(Vector2.ZERO, s), BattleTheme.BG)
	for y in range(0, int(s.y / CELL) + 1):
		for x in range(0, int(s.x / CELL) + 1):
			if (x + y) % 2 == 0:
				draw_rect(Rect2(x * CELL, y * CELL, CELL, CELL), BattleTheme.BG_ALT)
	# Spotlight band behind the board
	draw_rect(Rect2(0, 24, s.x, s.y - 48), Color(0, 0, 0, 0.18))
	draw_rect(Rect2(0, 22, s.x, 2), BattleTheme.PANEL_EDGE)
	draw_rect(Rect2(0, s.y - 24, s.x, 2), BattleTheme.PANEL_EDGE)
