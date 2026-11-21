extends RefCounted
## One look for the title screen and the pause menu: dark panels, a gold accent, small clear text.
## Swap the font here once a pixel font is chosen (Theme.default_font); every menu follows.

const ACCENT := Color("f5b83d")
const BG := Color("15121c")
const PANEL := Color("1d1928")
const PANEL2 := Color("262134")
const PANEL3 := Color("30293f")
const LINE := Color("3a3350")
const FG := Color("ece7f6")
const MUTED := Color("a39cb8")

static func _box(bg: Color, border: Color, border_width := 1) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(border_width)
	s.set_corner_radius_all(2)
	s.content_margin_left = 8
	s.content_margin_right = 8
	s.content_margin_top = 4
	s.content_margin_bottom = 4
	return s

static func make_theme() -> Theme:
	var t := Theme.new()
	t.default_font_size = 11
	t.set_stylebox("normal", "Button", _box(PANEL2, LINE))
	t.set_stylebox("hover", "Button", _box(PANEL3, MUTED))
	t.set_stylebox("pressed", "Button", _box(ACCENT.darkened(0.55), ACCENT))
	t.set_stylebox("focus", "Button", _box(PANEL3, ACCENT, 2))
	t.set_stylebox("disabled", "Button", _box(PANEL, LINE))
	for color_name in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		t.set_color(color_name, "Button", FG)
	t.set_color("font_disabled_color", "Button", MUTED.darkened(0.4))
	t.set_color("font_color", "Label", FG)
	t.set_stylebox("panel", "PanelContainer", _box(PANEL, LINE))
	return t
