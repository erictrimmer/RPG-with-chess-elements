extends SceneTree
## Runs downtown_test.tscn exactly as F6 would (as the current scene, autoloads active),
## waits, then reports the player/camera state and saves a screenshot.
var f := 0
func _init() -> void:
	change_scene_to_file("res://World/Downtown/downtown_test.tscn")
func _process(_d: float) -> bool:
	f += 1
	if f == 40:
		var s := current_scene
		print("scene: ", s, " children: ", s.get_children() if s else [])
		var p := s.get_node_or_null("Player") if s else null
		print("player: ", p, " class ", p.get_class() if p else "", " script ", p.get_script() if p else null)
		if p:
			print(" pos ", p.global_position, " visible ", p.visible, " z ", p.z_index, " children ", p.get_children())
			var cam := p.get_node_or_null("Camera2D") as Camera2D
			if cam: print(" cam current ", cam.is_current(), " enabled ", cam.enabled, " screen center ", cam.get_screen_center_position())
		print("viewport cam: ", root.get_viewport().get_camera_2d())
		root.get_viewport().get_texture().get_image().save_png("res://World/Downtown/previews/_f6_check.png")
		return true
	return false
