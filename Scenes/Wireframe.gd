extends Node2D

@export var line_color: Color = Color.BLACK
@export var line_width: float = 2.0
@export var world_size: Vector2 = Vector2(3000, 3000) # Size will be auto-calculated

var tile_size = 16
var block_size = 18 * tile_size     # 576
var central_road_w = 6 * tile_size  # 192px
var standard_road_w = 4 * tile_size # 128px
var sidewalk_w = 2 * tile_size      # 64px

func _draw():
	# 1. Background
	draw_rect(Rect2(Vector2.ZERO, world_size), Color.WHITE)
	
	# Layout: Road - Block - Road - Block - CentralRoad - Block - Road - Block - Road
	var r = standard_road_w
	var c = central_road_w
	var road_widths = [r, r, c, r, r]
	
	# Current drawing position
	var cur_y = 0
	
	for row in range(4):
		# Draw Horizontal Road above this block row
		var h_road_w = road_widths[row]
		_draw_road(Vector2(0, cur_y), Vector2(world_size.x, cur_y + h_road_w), h_road_w)
		cur_y += h_road_w
		
		var cur_x = 0
		for col in range(4):
			# Draw Vertical Road left of this block
			var v_road_w = road_widths[col]
			if col == 0: # Only draw the far left road once per row
				_draw_road(Vector2(cur_x, 0), Vector2(cur_x + v_road_w, world_size.y), v_road_w)
			cur_x += v_road_w
			
			# Block Area
			var block_rect = Rect2(cur_x, cur_y, block_size, block_size)
			_draw_block(block_rect, row, col)
			
			cur_x += block_size
			
			# If last column, draw the final vertical road
			if col == 3:
				var last_v_w = road_widths[4]
				_draw_road(Vector2(cur_x, 0), Vector2(cur_x + last_v_w, world_size.y), last_v_w)
				
		cur_y += block_size
		
		# If last row, draw final horizontal road
		if row == 3:
			var last_h_w = road_widths[4]
			_draw_road(Vector2(0, cur_y), Vector2(world_size.x, cur_y + last_h_w), last_h_w)

func _draw_road(rect_pos, rect_end, width):
	# Roads are defined by their boundaries. 
	# Drawing the "sidewalk" inner lines
	draw_line(rect_pos, Vector2(rect_end.x if rect_pos.y == rect_end.y else rect_pos.x, rect_end.y if rect_pos.x == rect_end.x else rect_pos.y), line_color, line_width)
	
	# Draw sidewalk lines (2 tiles in from road edge)
	# This is handled naturally by the block drawing, as blocks are surrounded by sidewalks

func _draw_block(rect: Rect2, row: int, col: int):
	# 1. Draw Sidewalk Boundary (inner edge of road)
	draw_rect(rect, line_color, false, line_width)
	
	# 2. Draw Building Area (2 tiles in from sidewalk edge)
	var build_area = rect.grow(-sidewalk_w)
	
	# 3. Special Buildings
	if row == 1 and col == 1: # NW Corner of Square
		_draw_building(build_area, "THEATER")
	elif row == 1 and col == 2: # NE Corner of Square
		_draw_building(build_area, "COURTHOUSE")
	elif row == 2 and col == 1: # SW Corner of Square
		_draw_building(build_area, "INN")
	elif row == 2 and col == 2: # SE Corner of Square
		# Four buildings
		var hw = build_area.size.x / 2
		var hh = build_area.size.y / 2
		_draw_building(Rect2(build_area.position, Vector2(hw, hh)).grow(-tile_size/2), "SHOP A")
		_draw_building(Rect2(build_area.position + Vector2(hw, 0), Vector2(hw, hh)).grow(-tile_size/2), "SHOP B")
		_draw_building(Rect2(build_area.position + Vector2(0, hh), Vector2(hw, hh)).grow(-tile_size/2), "SHOP C")
		_draw_building(Rect2(build_area.position + Vector2(hw, hh), Vector2(hw, hh)).grow(-tile_size/2), "SHOP D")
	else:
		# Assortment of other buildings
		var seed_val = row * 4 + col
		_draw_random_block(build_area, seed_val)

func _draw_building(rect: Rect2, label: String = ""):
	draw_rect(rect, line_color, false, line_width)
	# Simple X to indicate building volume/structure
	draw_line(rect.position, rect.end, Color(0.8, 0.8, 0.8, 0.5), 1.0)
	draw_line(Vector2(rect.end.x, rect.position.y), Vector2(rect.position.x, rect.end.y), Color(0.8, 0.8, 0.8, 0.5), 1.0)

func _draw_random_block(rect: Rect2, s: int):
	# Logic for varied building sizes
	var type = s % 3
	if type == 0:
		# 4 Quarters
		var hw = rect.size.x / 2
		var hh = rect.size.y / 2
		_draw_building(Rect2(rect.position, Vector2(hw, hh)).grow(-tile_size/2))
		_draw_building(Rect2(rect.position + Vector2(hw, 0), Vector2(hw, hh)).grow(-tile_size/2))
		_draw_building(Rect2(rect.position + Vector2(0, hh), Vector2(hw, hh)).grow(-tile_size/2))
		_draw_building(Rect2(rect.position + Vector2(hw, hh), Vector2(hw, hh)).grow(-tile_size/2))
	elif type == 1:
		# Vertical Halves
		var hw = rect.size.x / 2
		_draw_building(Rect2(rect.position, Vector2(hw, rect.size.y)).grow(-tile_size/2))
		_draw_building(Rect2(rect.position + Vector2(hw, 0), Vector2(hw, rect.size.y)).grow(-tile_size/2))
	else:
		# Horizontal Halves
		var hh = rect.size.y / 2
		_draw_building(Rect2(rect.position, Vector2(rect.size.x, hh)).grow(-tile_size/2))
		_draw_building(Rect2(rect.position + Vector2(0, hh), Vector2(rect.size.x, hh)).grow(-tile_size/2))

	# Optional: Draw a thin border around the edge of the world
	draw_rect(Rect2(Vector2.ZERO, world_size), line_color, false, 5.0)

func _ready():
	# Total width calculation: 4 blocks + 5 roads
	var total_size = (4 * block_size) + (4 * standard_road_w) + central_road_w
	world_size = Vector2(total_size, total_size)
	print("Wireframe: Calculated world size: ", world_size)
	queue_redraw()
