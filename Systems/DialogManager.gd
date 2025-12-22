extends CanvasLayer

signal dialog_choice_made(choice: String)

var dialog_panel: Panel
var dialog_label: Label
var button_container: HBoxContainer

func _ready():
	setup_dialog_ui()

func setup_dialog_ui():
	layer = 100 # Ensure it draws on top of everything
	
	# Dialog panel
	dialog_panel = Panel.new()
	dialog_panel.visible = false
	dialog_panel.position = Vector2(40, 120)
	dialog_panel.size = Vector2(240, 50)
	add_child(dialog_panel)
	
	# Dialog text
	dialog_label = Label.new()
	dialog_label.position = Vector2(10, 5)
	dialog_label.size = Vector2(220, 20)
	dialog_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var label_settings = LabelSettings.new()
	label_settings.font_size = 8
	dialog_label.label_settings = label_settings
	dialog_panel.add_child(dialog_label)
	
	# Button container
	button_container = HBoxContainer.new()
	button_container.position = Vector2(10, 28)
	button_container.size = Vector2(220, 18)
	button_container.alignment = BoxContainer.ALIGNMENT_CENTER
	button_container.add_theme_constant_override("separation", 10)
	dialog_panel.add_child(button_container)

func show_dialog(text: String, choices: Array = []):
	print("DialogManager: show_dialog called with text: ", text)
	dialog_label.text = text
	
	# Clear existing buttons
	for child in button_container.get_children():
		child.queue_free()
	
	# Add choice buttons
	for choice in choices:
		var btn = Button.new()
		btn.text = choice
		btn.add_theme_font_size_override("font_size", 8)
		btn.pressed.connect(func(): _on_choice_selected(choice))
		button_container.add_child(btn)
	
	dialog_panel.visible = true

func close_dialog():
	dialog_panel.visible = false

func _on_choice_selected(choice: String):
	emit_signal("dialog_choice_made", choice)
	close_dialog()
