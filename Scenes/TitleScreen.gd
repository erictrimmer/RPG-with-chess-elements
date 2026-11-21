extends Control
## York Chess Quest: title screen. Continue, New Game, Load Game, Quit.
## The UI is built in code so a restyle (font, colors) happens in MenuStyle.gd, not in a scene file.

const MenuStyle := preload("res://Scenes/UI/MenuStyle.gd")
const SlotPickerScript := preload("res://Scenes/UI/SlotPicker.gd")

const TITLE := "YORK CHESS QUEST"
const SUBTITLE := "An RPG Chess Adventure!"
const VIEW := Vector2(480, 270)

var _menu: VBoxContainer
var _continue_btn: Button
var _picker: VBoxContainer
var _picker_box: PanelContainer
var _status: Label
var _scroll := 0.0

func _ready() -> void:
	RenderingServer.set_default_clear_color(MenuStyle.BG)
	theme = MenuStyle.make_theme()
	_build()
	_show_menu()

func _exit_tree() -> void:
	RenderingServer.set_default_clear_color(Color(0.3, 0.3, 0.3))  # Godot's default, for the levels

func _process(delta: float) -> void:
	_scroll = fmod(_scroll + delta * 10.0, 32.0)
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, VIEW), MenuStyle.BG)
	# A slowly sliding chessboard band along the bottom edge.
	var tile := 16.0
	for row in 3:
		for col in range(-2, int(VIEW.x / tile) + 3):
			var dark := (row + col) % 2 == 0
			var x := col * tile - _scroll * (1.0 if row % 2 == 0 else -1.0)
			var shade := MenuStyle.PANEL if dark else MenuStyle.PANEL2
			draw_rect(Rect2(x, VIEW.y - (3 - row) * tile, tile, tile), shade)
	draw_rect(Rect2(0, VIEW.y - 3 * tile - 2, VIEW.x, 2), MenuStyle.ACCENT.darkened(0.4))

func _build() -> void:
	var title := Label.new()
	title.text = TITLE
	title.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	title.offset_top = 22
	title.offset_bottom = 60
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", MenuStyle.ACCENT)
	title.add_theme_color_override("font_outline_color", Color("2a1d05"))
	title.add_theme_constant_override("outline_size", 4)
	add_child(title)

	var subtitle := Label.new()
	subtitle.text = SUBTITLE
	subtitle.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	subtitle.offset_top = 62
	subtitle.offset_bottom = 82
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", MenuStyle.FG)
	add_child(subtitle)

	_menu = VBoxContainer.new()
	_menu.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_menu.offset_left = -70
	_menu.offset_right = 70
	_menu.offset_top = 98
	_menu.add_theme_constant_override("separation", 5)
	add_child(_menu)
	_continue_btn = _add_button("Continue", _on_continue)
	_add_button("New Game", _on_new_game)
	_add_button("Load Game", _on_load_game)
	_add_button("Quit", func(): get_tree().quit())

	_picker_box = PanelContainer.new()
	_picker_box.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_picker_box.offset_left = -165
	_picker_box.offset_right = 165
	_picker_box.offset_top = 92
	add_child(_picker_box)
	_picker = SlotPickerScript.new()
	_picker.slot_chosen.connect(_on_slot_chosen)
	_picker.cancelled.connect(_show_menu)
	_picker_box.add_child(_picker)

	_status = Label.new()
	_status.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_status.offset_top = -78
	_status.offset_bottom = -58
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status.add_theme_color_override("font_color", Color("ff6b73"))
	add_child(_status)

func _add_button(text: String, handler: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, 24)
	b.pressed.connect(handler)
	_menu.add_child(b)
	return b

func _show_menu() -> void:
	_picker_box.hide()
	_menu.show()
	_status.text = ""
	_continue_btn.disabled = SaveManager.most_recent_slot() < 0
	(_continue_btn if not _continue_btn.disabled else _menu.get_child(1)).grab_focus()

var _picker_action := ""

func _open_picker(action: String, mode: int, note := "") -> void:
	_picker_action = action
	_menu.hide()
	_status.text = ""
	_picker_box.show()
	_picker.setup(mode, note)

func _on_continue() -> void:
	var slot := SaveManager.most_recent_slot()
	if slot >= 0 and not SaveManager.load_slot(slot):
		_status.text = SaveManager.last_error

func _on_new_game() -> void:
	_open_picker("new", SlotPickerScript.Mode.NEW)

func _on_load_game() -> void:
	_open_picker("load", SlotPickerScript.Mode.LOAD)

func _on_slot_chosen(slot: int) -> void:
	var ok := SaveManager.start_new_game(slot) if _picker_action == "new" else SaveManager.load_slot(slot)
	if not ok:
		_show_menu()
		_status.text = SaveManager.last_error
