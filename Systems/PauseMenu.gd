extends CanvasLayer
## Pause menu (Esc) for any scene that has a player: Resume, Save Game, Load Game, Quit to Title.
## It stays out of battles and menus: with no player in the scene, Esc does nothing here.

const MenuStyle := preload("res://Scenes/UI/MenuStyle.gd")
const SlotPickerScript := preload("res://Scenes/UI/SlotPicker.gd")

var _root: Control
var _menu_panel: PanelContainer
var _info: Label
var _status: Label
var _picker_panel: PanelContainer
var _picker: VBoxContainer
var _resume_btn: Button

func _ready() -> void:
	layer = 90
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build()

func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("ui_cancel"):
		return
	if visible:
		get_viewport().set_input_as_handled()
		if _picker_panel.visible:
			_show_menu()
		else:
			close()
	elif _can_open():
		get_viewport().set_input_as_handled()
		open()

func _can_open() -> bool:
	var scene := get_tree().current_scene
	if scene == null or scene.scene_file_path == SaveManager.TITLE_SCENE:
		return false
	return SaveManager.can_save() and not DialogManager.is_open()

func open() -> void:
	get_tree().paused = true
	visible = true
	_show_menu()

func close() -> void:
	visible = false
	get_tree().paused = false

func _build() -> void:
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.theme = MenuStyle.make_theme()
	add_child(_root)

	var dim := ColorRect.new()
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.65)
	_root.add_child(dim)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.add_child(center)

	_menu_panel = PanelContainer.new()
	center.add_child(_menu_panel)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(150, 0)
	box.add_theme_constant_override("separation", 5)
	_menu_panel.add_child(box)

	var title := Label.new()
	title.text = "Paused"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 15)
	title.add_theme_color_override("font_color", MenuStyle.ACCENT)
	box.add_child(title)

	_info = Label.new()
	_info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_info.add_theme_color_override("font_color", MenuStyle.MUTED)
	box.add_child(_info)

	_resume_btn = _button(box, "Resume", close)
	_button(box, "Save Game", func(): _open_picker(SlotPickerScript.Mode.SAVE))
	_button(box, "Load Game", func(): _open_picker(SlotPickerScript.Mode.LOAD))
	_button(box, "Quit to Title", _quit_to_title)

	_status = Label.new()
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(_status)

	_picker_panel = PanelContainer.new()
	center.add_child(_picker_panel)
	_picker = SlotPickerScript.new()
	_picker.custom_minimum_size = Vector2(320, 0)
	_picker.slot_chosen.connect(_on_slot_chosen)
	_picker.cancelled.connect(_show_menu)
	_picker_panel.add_child(_picker)
	_picker_panel.hide()

func _button(parent: Control, text: String, handler: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, 24)
	b.pressed.connect(handler)
	parent.add_child(b)
	return b

func _show_menu(message := "") -> void:
	_picker_panel.hide()
	_menu_panel.show()
	_status.text = message
	var scene := get_tree().current_scene
	var where := str(SaveManager.LOCATION_NAMES.get(scene.scene_file_path, "")) if scene else ""
	_info.text = "%s  |  %s" % [where, SaveManager.format_playtime(GameState.playtime)] if where != "" else SaveManager.format_playtime(GameState.playtime)
	_resume_btn.grab_focus()

var _picker_mode := 0

func _open_picker(mode: int) -> void:
	_picker_mode = mode
	_menu_panel.hide()
	_picker_panel.show()
	_picker.setup(mode)

func _on_slot_chosen(slot: int) -> void:
	if _picker_mode == SlotPickerScript.Mode.SAVE:
		if SaveManager.save_to_slot(slot):
			_show_menu("Saved to slot %d." % (slot + 1))
		else:
			_show_menu(SaveManager.last_error)
	else:
		if SaveManager.load_slot(slot):
			close()
		else:
			_show_menu(SaveManager.last_error)

func _quit_to_title() -> void:
	visible = false
	SaveManager.return_to_title()
