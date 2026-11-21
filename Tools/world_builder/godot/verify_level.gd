extends SceneTree
## Loads a generated level, screenshots a few camera positions, and probes collision.
## Run (NOT headless, needs a renderer):
##   Godot_console.exe --path <project> --resolution 960x540 --script res://Tools/world_builder/godot/verify_level.gd -- <level.tscn> <out_dir_abs> x,y x,y ...
## Positions are in tiles (camera centre). Also prints a collision report: for each probe a ray/point query.

var level_path := ""
var out_dir := ""
var shots: Array = []
var frame := 0
var idx := 0
var cam: Camera2D
var level: Node

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	level_path = args[0]
	out_dir = args[1]
	for i in range(2, args.size()):
		var p = args[i].split(",")
		shots.append(Vector2(float(p[0]), float(p[1])))
	level = (load(level_path) as PackedScene).instantiate()
	root.add_child(level)
	cam = Camera2D.new()
	cam.zoom = Vector2(1, 1)   # project stretch already maps 480x270 to the window
	root.add_child(cam)
	cam.enabled = true

func _process(_d: float) -> bool:
	frame += 1
	if idx >= shots.size():
		_probe_collision()
		return true
	if frame == 1:
		cam.position = shots[idx] * 16.0
	elif frame == 4:
		var img := root.get_texture().get_image()
		img.save_png("%s/shot_%02d.png" % [out_dir, idx])
		print("shot ", idx, " at ", shots[idx])
		idx += 1
		frame = 0
	return false

func _probe_collision() -> void:
	var space := root.world_2d.direct_space_state
	var solid := 0
	var probes := 0
	var meta = level.get_meta("size_px", Vector2i(2560, 2048))
	for ty in range(0, meta.y / 16, 4):
		for tx in range(0, meta.x / 16, 4):
			var q := PhysicsPointQueryParameters2D.new()
			q.position = Vector2(tx * 16 + 8, ty * 16 + 12)
			q.collision_mask = 4
			probes += 1
			if space.intersect_point(q, 1).size() > 0:
				solid += 1
	print("collision probes: ", probes, " solid: ", solid)
