extends RefCounted
class_name BattleTheme
## Shared look for the battle screen: one flat palette plus small style helpers.
## Everything is designed for the 480x270 viewport (24px board squares).

const BG := Color8(28, 30, 46)
const BG_ALT := Color8(33, 36, 54)
const PANEL := Color8(42, 45, 68)
const PANEL_EDGE := Color8(96, 102, 146)
const TEXT := Color8(234, 232, 242)
const TEXT_DIM := Color8(150, 154, 182)
const ACCENT := Color8(240, 196, 80)
const BUBBLE_FILL := Color8(250, 246, 232)
const BUBBLE_EDGE := Color8(30, 30, 44)
const BUBBLE_TEXT := Color8(30, 30, 44)
const BUTTON := Color8(58, 62, 92)
const BUTTON_HOVER := Color8(78, 84, 124)
const BUTTON_DOWN := Color8(36, 38, 60)
const BUTTON_DISABLED := Color8(44, 46, 62)

const LIGHT_SQUARE := Color8(226, 212, 178)
const DARK_SQUARE := Color8(112, 140, 128)
const LAST_MOVE := Color(0.95, 0.85, 0.3, 0.45)
const SELECT := Color(1.0, 1.0, 0.2, 0.5)
const FRAME := Color8(20, 21, 34)
const FRAME_LIGHT := Color8(96, 102, 146)

const FONT_SMALL := 8
const FONT_BODY := 10

static func box(fill: Color, edge: Color, border: int = 2, margin: int = 4) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.border_color = edge
	sb.set_border_width_all(border)
	sb.set_corner_radius_all(0)
	sb.content_margin_left = margin
	sb.content_margin_right = margin
	sb.content_margin_top = margin
	sb.content_margin_bottom = margin
	sb.anti_aliasing = false
	return sb

static func style_button(btn: Button) -> void:
	btn.add_theme_stylebox_override("normal", box(BUTTON, PANEL_EDGE, 1, 3))
	btn.add_theme_stylebox_override("hover", box(BUTTON_HOVER, ACCENT, 1, 3))
	btn.add_theme_stylebox_override("pressed", box(BUTTON_DOWN, ACCENT, 1, 3))
	btn.add_theme_stylebox_override("disabled", box(BUTTON_DISABLED, BUTTON_DOWN, 1, 3))
	btn.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	btn.add_theme_color_override("font_color", TEXT)
	btn.add_theme_color_override("font_hover_color", TEXT)
	btn.add_theme_color_override("font_pressed_color", TEXT)
	btn.add_theme_color_override("font_disabled_color", TEXT_DIM)
	btn.add_theme_font_size_override("font_size", FONT_SMALL)

static func label_settings(size: int = FONT_SMALL, color: Color = TEXT) -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font_size = size
	ls.font_color = color
	return ls
