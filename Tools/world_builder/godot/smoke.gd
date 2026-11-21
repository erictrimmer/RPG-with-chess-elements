extends SceneTree
func _init():
	print("GODOT_OK ", Engine.get_version_info().string)
	var ts := TileSet.new()
	ts.tile_size = Vector2i(16,16)
	print("tileset ok")
	quit()
