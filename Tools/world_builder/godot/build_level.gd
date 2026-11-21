extends SceneTree
## Builds TileSet + chunk scenes + level scene from a world_builder JSON spec.
## Run:  Godot_console.exe --headless --path <project> --script res://Tools/world_builder/godot/build_level.gd -- <res://path/to/spec.json> <res://output/dir>
##
## Output:
##   <out>/<name>_tileset.tres          TileSet: 2 atlas sources (terrain, objects), physics layer 0 = world solids (layer 3)
##   <out>/chunks/<name>_c<cx>_<cy>.tscn  one scene per 32x32 chunk: Ground / Decals / Objects / Overhead TileMapLayers
##   <out>/<name>_level.tscn              all chunks instanced + an Entities y-sort node + Markers
##   <out>/<name>_test.tscn               level + player, for walking around

const WORLD_LAYER_BIT := 4   # physics layer 3 = "World solids" (style bible §8)

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("usage: -- <spec.json> <out_dir>")
		quit(1)
		return
	var spec_path: String = args[0]
	var out_dir: String = args[1]
	var spec = JSON.parse_string(FileAccess.get_file_as_string(spec_path))
	if spec == null:
		push_error("could not parse " + spec_path)
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir + "/chunks"))
	var name: String = spec["name"]
	var ts := _build_tileset(spec)
	var ts_path := "%s/%s_tileset.tres" % [out_dir, name]
	var err := ResourceSaver.save(ts, ts_path)
	print("tileset saved: ", ts_path, " err=", err)
	ts = load(ts_path)

	var chunk: int = int(spec["chunk"])
	var W: int = int(spec["width"])
	var H: int = int(spec["height"])
	var cols := int(ceil(float(W) / chunk))
	var rows := int(ceil(float(H) / chunk))
	var T: int = int(spec["tile_size"])

	# bucket cells per chunk per layer
	var buckets := {}
	for layer in spec["layers"]:
		for c in layer["cells"]:
			var x: int = int(c[0]); var y: int = int(c[1])
			var key := Vector2i(x / chunk, y / chunk)
			if not buckets.has(key):
				buckets[key] = {}
			if not buckets[key].has(layer["name"]):
				buckets[key][layer["name"]] = []
			buckets[key][layer["name"]].append(c)

	var chunk_paths := {}
	for cy in rows:
		for cx in cols:
			var root := Node2D.new()
			root.name = "Chunk_%d_%d" % [cx, cy]
			for layer in spec["layers"]:
				var tml := TileMapLayer.new()
				tml.name = layer["name"]
				tml.tile_set = ts
				tml.z_index = int(layer["z"])
				tml.collision_enabled = layer["name"] in ["Ground", "Objects"]
				root.add_child(tml)
				tml.owner = root
				var cells = buckets.get(Vector2i(cx, cy), {}).get(layer["name"], [])
				for c in cells:
					tml.set_cell(Vector2i(int(c[0]) - cx * chunk, int(c[1]) - cy * chunk), int(c[2]), Vector2i(int(c[3]), int(c[4])))
			var ps := PackedScene.new()
			ps.pack(root)
			var p := "%s/chunks/%s_c%d_%d.tscn" % [out_dir, name, cx, cy]
			ResourceSaver.save(ps, p)
			chunk_paths[Vector2i(cx, cy)] = p
			root.free()
	print("chunks saved: ", chunk_paths.size())

	# ---- level scene
	var level := Node2D.new()
	level.name = name.capitalize().replace(" ", "")
	var chunks_node := Node2D.new()
	chunks_node.name = "Chunks"
	level.add_child(chunks_node)
	chunks_node.owner = level
	for cy in rows:
		for cx in cols:
			var inst: Node2D = (load(chunk_paths[Vector2i(cx, cy)]) as PackedScene).instantiate()
			inst.position = Vector2(cx * chunk * T, cy * chunk * T)
			chunks_node.add_child(inst)
			inst.owner = level
	var ents := Node2D.new()
	ents.name = "Entities"
	ents.y_sort_enabled = true
	level.add_child(ents)
	ents.owner = level
	var markers := Node2D.new()
	markers.name = "Markers"
	level.add_child(markers)
	markers.owner = level
	var i := 0
	for m in spec["markers"]:
		var mk := Marker2D.new()
		mk.name = "%s_%d" % [m["name"], i]
		i += 1
		mk.position = Vector2(int(m["x"]) * T + T / 2, int(m["y"]) * T + T / 2)
		mk.set_meta("kind", m["name"])
		for k in m["data"]:
			mk.set_meta(k, m["data"][k])
		markers.add_child(mk)
		mk.owner = level
	level.set_meta("size_px", Vector2i(W * T, H * T))
	var lps := PackedScene.new()
	lps.pack(level)
	var level_path := "%s/%s_level.tscn" % [out_dir, name]
	ResourceSaver.save(lps, level_path)
	print("level saved: ", level_path)
	level.free()
	_build_test_scene(spec, out_dir, name, level_path, T)
	quit(0)


## A playable test scene: the level, the project's player at the spawn marker, camera clamped.
func _build_test_scene(spec, out_dir: String, name: String, level_path: String, T: int) -> void:
	var player_scene_path := "res://Entities/Player/player.tscn"
	if not ResourceLoader.exists(player_scene_path):
		print("no player scene; skipping test scene")
		return
	var root := Node2D.new()
	root.name = name.capitalize().replace(" ", "") + "Test"
	var scr := load("res://World/Downtown/level_test.gd")
	if scr:
		root.set_script(scr)
	var lvl: Node2D = (load(level_path) as PackedScene).instantiate()
	lvl.name = "Level"
	root.add_child(lvl)
	lvl.owner = root
	var spawn := Vector2(spec["width"] * T / 2, spec["height"] * T / 2)
	for m in spec["markers"]:
		if m["name"] == "spawn":
			spawn = Vector2(int(m["x"]) * T + T / 2, int(m["y"]) * T + T)
	var player: CharacterBody2D = (load(player_scene_path) as PackedScene).instantiate()
	player.name = "Player"
	player.position = spawn
	player.collision_mask = 2 | WORLD_LAYER_BIT   # collide with NPC bodies (layer 2) + world solids (layer 3)
	root.add_child(player)
	player.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	var p := "%s/%s_test.tscn" % [out_dir, name]
	ResourceSaver.save(ps, p)
	print("test scene saved: ", p)
	root.free()


func _build_tileset(spec) -> TileSet:
	var ts := TileSet.new()
	var T: int = int(spec["tile_size"])
	ts.tile_size = Vector2i(T, T)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(0, WORLD_LAYER_BIT)
	ts.set_physics_layer_collision_mask(0, 0)
	for src in spec["sources"]:
		var atlas := TileSetAtlasSource.new()
		atlas.resource_name = src["name"]
		atlas.texture = load(src["png"])
		atlas.texture_region_size = Vector2i(T, T)
		ts.add_source(atlas, int(src["id"]))
		var h := T / 2.0
		for t in src["tiles"]:
			var coords := Vector2i(int(t["a"][0]), int(t["a"][1]))
			if not atlas.has_tile(coords):
				atlas.create_tile(coords)
			var col = t["col"]
			if col != null:
				var td := atlas.get_tile_data(coords, 0)
				var x := float(col[0]) - h
				var y := float(col[1]) - h
				var w := float(col[2])
				var hh := float(col[3])
				td.add_collision_polygon(0)
				td.set_collision_polygon_points(0, 0, PackedVector2Array([
					Vector2(x, y), Vector2(x + w, y), Vector2(x + w, y + hh), Vector2(x, y + hh)]))
	return ts
