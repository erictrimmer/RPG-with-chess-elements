extends CanvasLayer

# ============================================================
# DialogManager — Upgraded Global Singleton
#
# Supports:
#   - Multi-page dialog sequences (press interact/Space to advance)
#   - Optional speaker name tag
#   - Optional speaker portrait (Texture2D)
#   - Choice buttons (same as before, signal-compatible)
#   - Typewriter text effect
#   - Backwards-compatible: show_dialog(text, choices) still works
#
# Usage examples:
#
#   # Simple one-liner (old style, still works):
#   DialogManager.show_dialog("Hello there!")
#
#   # Multi-page sequence:
#   DialogManager.show_sequence([
#       {"text": "Hey kid.", "speaker": "Tim"},
#       {"text": "I need a favour.", "speaker": "Tim"},
#       {"text": "Head to the landfill and grab me some scrap.", "speaker": "Tim"},
#   ], Callable(self, "_on_tim_sequence_done"))
#
#   # With portrait:
#   DialogManager.show_sequence([
#       {"text": "Nice to meet you!", "speaker": "Librarian",
#        "portrait": preload("res://Assets/Sprites/Characters/librarian_portrait.png")},
#   ])
#
#   # Final page with choices:
#   DialogManager.show_sequence([
#       {"text": "Want to play a game?", "speaker": "Alpert",
#        "choices": ["Sure", "Not now"]},
#   ], Callable(self, "_on_alpert_choice"))
# ============================================================

# --- Signals ---
signal dialog_choice_made(choice: String)   # Fired when a choice button is clicked
signal dialog_closed()                       # Fired when the last page is dismissed

# --- Layout constants (match 320x180 viewport) ---
const PANEL_X       = 2
const PANEL_Y       = 130
const PANEL_W       = 316
const PANEL_H       = 48

const PORTRAIT_SIZE = 40
const PORTRAIT_PAD  = 4

const NAME_H        = 10
const TEXT_PAD      = 4

const FONT_SIZE     = 8
const TYPEWRITER_SPEED = 0.03  # seconds per character

# --- UI Nodes (built in code, no scene needed) ---
var _panel: Panel
var _name_label: Label
var _portrait_rect: TextureRect
var _text_label: Label
var _continue_arrow: Label        # "▼" blinking hint
var _button_container: VBoxContainer

# --- State ---
var _pages: Array = []            # Array of page dicts
var _current_page: int = 0
var _on_done: Callable = Callable()  # optional callback when sequence ends
var _is_open: bool = false
var _is_typing: bool = false
var _full_text: String = ""
var _typewriter_timer: float = 0.0
var _chars_shown: int = 0


# ---------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------

func _ready() -> void:
	layer = 100
	_build_ui()


func _process(delta: float) -> void:
	if not _is_open:
		return
	if _is_typing:
		_typewriter_tick(delta)


func _unhandled_input(event: InputEvent) -> void:
	if not _is_open:
		return
	# Only handle advance on interact/space — choices use buttons
	if _button_container.visible:
		return
	if event.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		if _is_typing:
			_finish_typing()
		else:
			_advance()


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

## Simple one-liner (backwards-compatible with old callers).
func show_dialog(text: String, choices: Array = [], speaker: String = "",
		portrait: Texture2D = null) -> void:
	var page := {"text": text}
	if not speaker.is_empty():
		page["speaker"] = speaker
	if portrait != null:
		page["portrait"] = portrait
	if not choices.is_empty():
		page["choices"] = choices
	show_sequence([page])


## Show a multi-page dialog sequence.
## on_done: optional Callable called with no args when sequence ends,
##          or with the chosen string if the last page had choices.
func show_sequence(pages: Array, on_done: Callable = Callable()) -> void:
	_pages = pages
	_current_page = 0
	_on_done = on_done
	_is_open = true
	_panel.visible = true
	_show_page(_current_page)


## Close the dialog immediately (no signals).
func force_close() -> void:
	_is_open = false
	_is_typing = false
	_panel.visible = false


## Returns true if dialog is currently displayed.
func is_open() -> bool:
	return _is_open


# ---------------------------------------------------------------
# Internal — Page display
# ---------------------------------------------------------------

func _show_page(index: int) -> void:
	var page: Dictionary = _pages[index]

	# Speaker name
	var speaker: String = page.get("speaker", "")
	_name_label.text = speaker
	_name_label.visible = not speaker.is_empty()

	# Portrait
	var portrait = page.get("portrait", null)
	if portrait != null:
		_portrait_rect.texture = portrait
		_portrait_rect.visible = true
	else:
		_portrait_rect.texture = null
		_portrait_rect.visible = false

	# Reflow text area based on portrait presence
	_reflow_text_area(portrait != null)

	# Clear old choice buttons
	for child in _button_container.get_children():
		child.queue_free()

	var choices: Array = page.get("choices", [])

	if choices.is_empty():
		# Multi-page: show typewriter + advance arrow
		_button_container.visible = false
		_continue_arrow.visible = false
		_start_typing(page.get("text", ""))
	else:
		# Choice page: show full text immediately + buttons
		_continue_arrow.visible = false
		_is_typing = false
		_text_label.text = page.get("text", "")
		_button_container.visible = true
		for choice in choices:
			var btn := Button.new()
			btn.text = choice
			btn.add_theme_font_size_override("font_size", FONT_SIZE)
			btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			btn.pressed.connect(func(): _on_choice_selected(choice))
			_button_container.add_child(btn)


func _advance() -> void:
	_current_page += 1
	if _current_page < _pages.size():
		_show_page(_current_page)
	else:
		_close_sequence(null)


func _close_sequence(choice) -> void:
	_is_open = false
	_is_typing = false
	_panel.visible = false
	emit_signal("dialog_closed")
	if _on_done.is_valid():
		if choice != null:
			_on_done.call(choice)
		else:
			_on_done.call()


func _on_choice_selected(choice: String) -> void:
	emit_signal("dialog_choice_made", choice)
	_close_sequence(choice)


# ---------------------------------------------------------------
# Internal — Typewriter
# ---------------------------------------------------------------

func _start_typing(text: String) -> void:
	_full_text = text
	_chars_shown = 0
	_is_typing = true
	_text_label.text = ""
	_continue_arrow.visible = false


func _typewriter_tick(delta: float) -> void:
	_typewriter_timer += delta
	var chars_to_show := int(_typewriter_timer / TYPEWRITER_SPEED)
	if chars_to_show > _chars_shown:
		_chars_shown = min(chars_to_show, _full_text.length())
		_text_label.text = _full_text.substr(0, _chars_shown)
		if _chars_shown >= _full_text.length():
			_finish_typing()


func _finish_typing() -> void:
	_is_typing = false
	_text_label.text = _full_text
	_typewriter_timer = 0.0
	# Show the advance arrow only if this isn't the last page OR if there are more
	var page: Dictionary = _pages[_current_page]
	var choices: Array = page.get("choices", [])
	if choices.is_empty():
		_continue_arrow.visible = true


# ---------------------------------------------------------------
# Internal — UI Layout
# ---------------------------------------------------------------

func _build_ui() -> void:
	# Root panel
	_panel = Panel.new()
	_panel.visible = false
	_panel.position = Vector2(PANEL_X, PANEL_Y)
	_panel.size = Vector2(PANEL_W, PANEL_H)
	add_child(_panel)

	# Portrait (left side, hidden by default)
	_portrait_rect = TextureRect.new()
	_portrait_rect.position = Vector2(PORTRAIT_PAD, PORTRAIT_PAD)
	_portrait_rect.size = Vector2(PORTRAIT_SIZE, PORTRAIT_SIZE)
	_portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_portrait_rect.visible = false
	_panel.add_child(_portrait_rect)

	# Speaker name tag (above text)
	_name_label = Label.new()
	_name_label.position = Vector2(_text_x(false), TEXT_PAD)
	_name_label.size = Vector2(_text_w(false), NAME_H)
	_name_label.visible = false
	var name_settings := LabelSettings.new()
	name_settings.font_size = FONT_SIZE
	_name_label.label_settings = name_settings
	_panel.add_child(_name_label)

	# Main text label
	_text_label = Label.new()
	_text_label.position = Vector2(_text_x(false), TEXT_PAD + NAME_H)
	_text_label.size = Vector2(_text_w(false), PANEL_H - TEXT_PAD - NAME_H - 4)
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var text_settings := LabelSettings.new()
	text_settings.font_size = FONT_SIZE
	_text_label.label_settings = text_settings
	_panel.add_child(_text_label)

	# Continue arrow (▼ — press to advance)
	_continue_arrow = Label.new()
	_continue_arrow.text = "▼"
	_continue_arrow.position = Vector2(PANEL_W - 12, PANEL_H - 12)
	_continue_arrow.size = Vector2(10, 10)
	_continue_arrow.visible = false
	var arrow_settings := LabelSettings.new()
	arrow_settings.font_size = FONT_SIZE
	_continue_arrow.label_settings = arrow_settings
	_panel.add_child(_continue_arrow)

	# Choice button container (vertical stack)
	_button_container = VBoxContainer.new()
	_button_container.position = Vector2(_text_x(false), TEXT_PAD + NAME_H)
	_button_container.size = Vector2(_text_w(false), PANEL_H - TEXT_PAD - NAME_H - 4)
	_button_container.add_theme_constant_override("separation", 2)
	_button_container.visible = false
	_panel.add_child(_button_container)


func _reflow_text_area(has_portrait: bool) -> void:
	var tx := _text_x(has_portrait)
	var tw := _text_w(has_portrait)
	_name_label.position.x = tx
	_name_label.size.x = tw
	_text_label.position.x = tx
	_text_label.size.x = tw
	_button_container.position.x = tx
	_button_container.size.x = tw


func _text_x(has_portrait: bool) -> float:
	if has_portrait:
		return PORTRAIT_PAD + PORTRAIT_SIZE + PORTRAIT_PAD
	return TEXT_PAD


func _text_w(has_portrait: bool) -> float:
	if has_portrait:
		return PANEL_W - _text_x(true) - TEXT_PAD - 12
	return PANEL_W - TEXT_PAD * 2 - 12


## Legacy close method (for any existing callers).
func close_dialog() -> void:
	force_close()
