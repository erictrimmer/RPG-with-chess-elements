extends VBoxContainer
## The save-slot list shared by the title screen (new game, load) and the pause menu (save, load).
## Call setup(mode), then listen for slot_chosen(slot) and cancelled.
##
## Overwriting a used slot and deleting a save both need a second press to confirm.

enum Mode { NEW, SAVE, LOAD }

signal slot_chosen(slot: int)
signal cancelled

var mode: Mode = Mode.LOAD
var _pending := ""   # the action waiting for a second press: "use_1", "del_2"
var _note := ""

func setup(new_mode: Mode, note := "") -> void:
	mode = new_mode
	_note = note
	_pending = ""
	_rebuild("")

func _unhandled_input(event: InputEvent) -> void:
	if is_visible_in_tree() and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		cancelled.emit()

func _heading() -> String:
	match mode:
		Mode.NEW: return "New game: pick a slot"
		Mode.SAVE: return "Save game: pick a slot"
	return "Load game: pick a slot"

func _rebuild(focus_name: String) -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()
	add_theme_constant_override("separation", 4)

	var heading := Label.new()
	heading.text = _heading()
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	heading.add_theme_font_size_override("font_size", 13)
	heading.add_theme_color_override("font_color", preload("res://Scenes/UI/MenuStyle.gd").ACCENT)
	add_child(heading)
	if _note != "":
		var note := Label.new()
		note.text = _note
		note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		note.add_theme_color_override("font_color", preload("res://Scenes/UI/MenuStyle.gd").MUTED)
		add_child(note)

	var first_enabled: Button = null
	for slot in SaveManager.SLOT_COUNT:
		var info := SaveManager.get_slot_info(slot)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		add_child(row)

		var pick := Button.new()
		pick.name = "slot_%d" % slot
		pick.alignment = HORIZONTAL_ALIGNMENT_LEFT
		pick.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		pick.custom_minimum_size = Vector2(0, 44)
		pick.text = _slot_text(info)
		pick.disabled = mode == Mode.LOAD and (not info["exists"] or info["corrupt"])
		pick.pressed.connect(_on_slot_pressed.bind(slot, info))
		row.add_child(pick)
		if first_enabled == null and not pick.disabled:
			first_enabled = pick

		if info["exists"]:
			var del := Button.new()
			del.name = "del_%d" % slot
			del.text = "Sure?" if _pending == "del_%d" % slot else "Delete"
			del.custom_minimum_size = Vector2(56, 44)
			del.pressed.connect(_on_delete_pressed.bind(slot))
			row.add_child(del)

	var back := Button.new()
	back.name = "back"
	back.text = "Back"
	back.pressed.connect(func(): cancelled.emit())
	add_child(back)

	var target: Control = null
	if focus_name != "":
		target = find_child(focus_name, true, false) as Control
	if target == null:
		target = first_enabled if first_enabled != null else back
	target.call_deferred("grab_focus")

func _slot_text(info: Dictionary) -> String:
	var n := int(info["slot"]) + 1
	if _pending == "use_%d" % int(info["slot"]):
		return "Slot %d\nThis slot is in use. Press again to overwrite it." % n
	if not info["exists"]:
		return "Slot %d\nEmpty" % n
	if info["corrupt"]:
		return "Slot %d\nDamaged save file (you can delete it)" % n
	return "Slot %d  -  %s\n%s\n%s  |  %s" % [
		n, info["location"], info["progress"],
		SaveManager.format_playtime(info["playtime"]), SaveManager.format_saved_at(info["saved_at"])]

func _on_slot_pressed(slot: int, info: Dictionary) -> void:
	var needs_confirm: bool = info["exists"] and mode != Mode.LOAD
	if needs_confirm and _pending != "use_%d" % slot:
		_pending = "use_%d" % slot
		_rebuild("slot_%d" % slot)
		return
	_pending = ""
	slot_chosen.emit(slot)

func _on_delete_pressed(slot: int) -> void:
	if _pending != "del_%d" % slot:
		_pending = "del_%d" % slot
		_rebuild("del_%d" % slot)
		return
	SaveManager.delete_slot(slot)
	_pending = ""
	_rebuild("slot_%d" % slot)
