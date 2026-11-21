extends SceneTree
## Builds res://World/Interior/depot_interior.tscn (and its TileSet) from the Modern Interiors pieces
## that prepare_depot_assets.py copied into Assets/Interiors. Run headless from the project root:
##
##   Godot_console.exe --headless --path . --script res://Tools/world_builder/build_depot_interior.gd
##
## The room is 14 tiles wide, like the depot's outside, and its two exit doors sit at the same tile
## columns as the two doors drawn on the outside (the double arched door on columns 4-5 and the
## single orange door on column 10), so "leave by the door you came in" holds.

const T := 16
const COLS := 14
const ROWS := 12                      # rows 0-1 wall, 2-10 floor, 11 front wall with the two exit doors
const ROOM := Vector2i(COLS * T, ROWS * T)
const DOORS := [[4, 2], [10, 1]]      # [first tile column, width in tiles]
const DOOR_COLS := [4, 5, 10]
const FLOOR_SHEET := "res://Assets/Interiors/Room_Builder_Floors_16x16.png"
const WALL_SHEET := "res://Assets/Interiors/Room_Builder_Walls_16x16.png"
const PROP_DIR := "res://Assets/Interiors/depot/"
const TILESET_PATH := "res://World/Interior/depot_interior_tileset.tres"
const SCENE_PATH := "res://World/Interior/depot_interior.tscn"
const FLOOR_BASE := Vector2i(5, 20)   # checkerboard: rows 20 and 21 alternate
const WALL_TOP := 24                  # red beadboard wall: rows 24 (upper) and 25 (lower), columns 11..13
const FRONT_WALL_COLOR := Color("2b2540")

# Where each exit door leads on the outside (downtown_test.tscn coordinates): just south of the matching door.
const OUTSIDE_SCENE := "res://World/Downtown/downtown_test.tscn"
const OUTSIDE_SPAWN := [Vector2(1920, 1940), Vector2(2008, 1940)]

# Props: [texture, x of left edge, y of the bottom edge, solid collision height in px (0 = walk-through)]
const PROPS := [
	["desk", 44, 64, 14], ["desk", 126, 64, 14],
	["chair_b", 62, 52, 0], ["chair_b", 144, 52, 0],
	["palm", 8, 62, 8], ["palm", 192, 62, 8],
	["bin", 108, 52, 8],
	["bench_light", 34, 122, 10], ["bench_light", 34, 146, 10],
	["bench_dark", 174, 122, 10], ["bench_dark", 174, 146, 10],
	["crates", 196, 96, 14],
	["tree", 8, 168, 8],
]
const FLOOR_DECOR := [["rug_red", 82, 84], ["rug_small", 68, 178], ["rug_small", 156, 178]]
const WALL_DECOR := [["window_blue", 34, 7], ["window_blue", 165, 7], ["painting_sun", 98, 8],
	["extinguisher", 8, 12], ["painting_green", 62, 9], ["painting_coast", 126, 9]]

func _init() -> void:
	var tileset := _make_tileset()
	var root := Node2D.new()
	root.name = "DepotInterior"
	root.set_script(load("res://World/Interior/interior_level.gd"))
	root.set("room_size", ROOM)
	root.set_meta("size_px", ROOM)

	var floor_layer := _tile_layer("Floor", tileset, -10, root)
	var wall_layer := _tile_layer("Walls", tileset, -9, root)
	for y in range(2, ROWS - 1):
		for x in COLS:
			floor_layer.set_cell(Vector2i(x, y), 0, FLOOR_BASE + Vector2i(0, y % 2))
	for x in COLS:
		for r in 2:
			var col := 12
			if x == 0: col = 11
			elif x == COLS - 1: col = 13
			wall_layer.set_cell(Vector2i(x, r), 1, Vector2i(col, WALL_TOP + r))
	# Front wall (the room's south edge): solid dark, with a doorway gap where each exit door is.
	for x in COLS:
		if x in DOOR_COLS:
			floor_layer.set_cell(Vector2i(x, ROWS - 1), 0, FLOOR_BASE + Vector2i(0, (ROWS - 1) % 2))
		else:
			var strip := ColorRect.new()
			strip.name = "FrontWall_%d" % x
			strip.color = FRONT_WALL_COLOR
			strip.position = Vector2(x * T, (ROWS - 1) * T)
			strip.size = Vector2(T, T)
			strip.z_index = -8
			_add(root, strip, root)

	var floor_decor := _node2d("FloorDecor", -8, root)
	for d in FLOOR_DECOR:
		_sprite(d[0], Vector2(d[1], d[2]), floor_decor, root)
	var wall_decor := _node2d("WallDecor", -5, root)
	for d in WALL_DECOR:
		_sprite(d[0], Vector2(d[1], d[2]), wall_decor, root)

	# Everything that can stand in front of or behind the player lives in one y-sorted node.
	var entities := _node2d("Entities", 0, root)
	entities.y_sort_enabled = true
	for p in PROPS:
		var tex: Texture2D = load(PROP_DIR + p[0] + ".png")
		var prop := Node2D.new()
		prop.name = "%s_%d_%d" % [p[0], p[1], p[2]]
		# Sort on the base of the sprite: the player sorts on their feet, which are 16 px below their origin.
		prop.position = Vector2(p[1], p[2] - 16)
		_add(entities, prop, root)
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.position = Vector2(0, 16 - tex.get_height())
		_add(prop, s, root)

	var player: Node2D = load("res://Entities/Player/player_forge.tscn").instantiate()
	player.name = "Player"
	player.position = Vector2(56, 150)
	player.set("collision_mask", 6)
	entities.add_child(player)
	player.owner = root

	_build_solids(root)
	_build_exit_doors(root)

	var packed := PackedScene.new()
	var err := packed.pack(root)
	if err != OK:
		push_error("pack failed: %d" % err)
		quit(1)
		return
	err = ResourceSaver.save(packed, SCENE_PATH)
	print("saved ", SCENE_PATH, " err=", err)
	root.free()
	quit(0 if err == OK else 1)

func _make_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(T, T)
	var floors := TileSetAtlasSource.new()
	floors.texture = load(FLOOR_SHEET)
	floors.texture_region_size = Vector2i(T, T)
	for dy in 2:
		floors.create_tile(FLOOR_BASE + Vector2i(0, dy))
	ts.add_source(floors, 0)
	var walls := TileSetAtlasSource.new()
	walls.texture = load(WALL_SHEET)
	walls.texture_region_size = Vector2i(T, T)
	for c in [11, 12, 13]:
		for r in 2:
			walls.create_tile(Vector2i(c, WALL_TOP + r))
	ts.add_source(walls, 1)
	ResourceSaver.save(ts, TILESET_PATH)
	return load(TILESET_PATH)

func _tile_layer(node_name: String, ts: TileSet, z: int, root: Node) -> TileMapLayer:
	var layer := TileMapLayer.new()
	layer.name = node_name
	layer.tile_set = ts
	layer.z_index = z
	_add(root, layer, root)
	return layer

func _node2d(node_name: String, z: int, root: Node) -> Node2D:
	var n := Node2D.new()
	n.name = node_name
	n.z_index = z
	_add(root, n, root)
	return n

func _sprite(tex_name: String, pos: Vector2, parent: Node, root: Node) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = "%s_%d_%d" % [tex_name, pos.x, pos.y]
	s.texture = load(PROP_DIR + tex_name + ".png")
	s.centered = false
	s.position = pos
	_add(parent, s, root)
	return s

func _add(parent: Node, child: Node, root: Node) -> void:
	parent.add_child(child)
	child.owner = root

func _rect_shape(body: StaticBody2D, root: Node, node_name: String, rect: Rect2) -> void:
	var cs := CollisionShape2D.new()
	cs.name = node_name
	var shape := RectangleShape2D.new()
	shape.size = rect.size
	cs.shape = shape
	cs.position = rect.position + rect.size / 2.0
	_add(body, cs, root)

func _build_solids(root: Node) -> void:
	var body := StaticBody2D.new()
	body.name = "Solids"
	body.collision_layer = 4   # "World solids", the same layer the town tiles use
	body.collision_mask = 0
	_add(root, body, root)
	var rects: Array[Rect2] = [
		Rect2(0, 0, ROOM.x, 2 * T),                          # back wall
		Rect2(-8, 0, 8, ROOM.y + 8),                         # left wall
		Rect2(ROOM.x, 0, 8, ROOM.y + 8),                     # right wall
	]
	var fy := (ROWS - 1) * T
	var x0 := 0
	for d in DOORS:
		rects.append(Rect2(x0 * T, fy, (d[0] - x0) * T, T))   # front wall between doorways
		rects.append(Rect2(d[0] * T, ROOM.y, d[1] * T, 8))    # stops anyone walking out past a doorway
		x0 = d[0] + d[1]
	rects.append(Rect2(x0 * T, fy, (COLS - x0) * T, T))
	var i := 0
	for r in rects:
		_rect_shape(body, root, "wall_%d" % i, r)
		i += 1
	for p in PROPS:
		if p[3] <= 0:
			continue
		var tex: Texture2D = load(PROP_DIR + p[0] + ".png")
		var w := tex.get_width()
		_rect_shape(body, root, "prop_%s_%d_%d" % [p[0], p[1], p[2]], Rect2(p[1], p[2] - p[3], w, p[3]))

func _build_exit_doors(root: Node) -> void:
	var door_script := load("res://Components/SceneDoor.gd")
	var i := 0
	for d in DOORS:
		var door := Area2D.new()
		door.name = "ExitDoor_%d" % i
		door.set_script(door_script)
		door.set("target_scene", OUTSIDE_SCENE)
		door.set("target_spawn", OUTSIDE_SPAWN[i])
		door.set("target_facing", &"down")
		door.set("push_action", &"move_down")
		door.position = Vector2((d[0] + d[1] / 2.0) * T, (ROWS - 1) * T + 10)
		_add(root, door, root)
		var cs := CollisionShape2D.new()
		cs.name = "Shape"
		var shape := RectangleShape2D.new()
		shape.size = Vector2(d[1] * T, 12)
		cs.shape = shape
		_add(door, cs, root)
		i += 1
