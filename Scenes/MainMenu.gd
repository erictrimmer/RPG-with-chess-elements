extends Control

# Scene paths
const SCENE_MAIN     = "res://Scenes/Main.tscn"
const SCENE_DOWNTOWN = "res://Scenes/Downtown.tscn"
const SCENE_PAWN_TUT = "res://Scenes/Puzzles/PawnTutorial.tscn"

# How many seconds to wait before auto-showing the menu
const TITLE_DISPLAY_TIME := 10.0

@onready var title_label    : Label      = $TitleContainer/Title
@onready var subtitle_label : Label      = $TitleContainer/Subtitle
@onready var menu_container : VBoxContainer = $MenuContainer
@onready var title_timer    : Timer      = $TitleTimer
@onready var bg_panel       : ColorRect  = $Background

var menu_revealed := false

func _ready() -> void:
	# Hide menu until prompt is done
	menu_container.modulate.a = 0.0
	menu_container.visible = false

	# Fade in the title labels
	title_label.modulate.a    = 0.0
	subtitle_label.modulate.a = 0.0
	_fade_in_titles()

	# Start the timer
	title_timer.wait_time = TITLE_DISPLAY_TIME
	title_timer.one_shot  = true
	title_timer.timeout.connect(_reveal_menu)
	title_timer.start()

func _fade_in_titles() -> void:
	var tween := create_tween()
	tween.tween_property(title_label, "modulate:a", 1.0, 1.5)
	tween.tween_interval(0.3)
	tween.tween_property(subtitle_label, "modulate:a", 1.0, 1.2)

func _reveal_menu() -> void:
	if menu_revealed:
		return
	menu_revealed = true
	menu_container.visible = true
	var tween := create_tween()
	tween.tween_property(menu_container, "modulate:a", 1.0, 0.6)

func _unhandled_input(event: InputEvent) -> void:
	if menu_revealed:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		_skip_to_menu()
	elif event is InputEventMouseButton and event.pressed:
		_skip_to_menu()

func _skip_to_menu() -> void:
	title_timer.stop()
	# Make sure titles are fully visible before menu pops
	title_label.modulate.a    = 1.0
	subtitle_label.modulate.a = 1.0
	_reveal_menu()

# ──────────────────────────────────────────────
#  Button callbacks
# ──────────────────────────────────────────────

func _on_new_game_pressed() -> void:
	get_tree().change_scene_to_file(SCENE_MAIN)

func _on_downtown_pressed() -> void:
	get_tree().change_scene_to_file(SCENE_DOWNTOWN)

func _on_pawn_tutorial_pressed() -> void:
	get_tree().change_scene_to_file(SCENE_PAWN_TUT)
