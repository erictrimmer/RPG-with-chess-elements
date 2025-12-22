extends CharacterBody2D

# The Knight NPC is currently stationary and acts as a collision trigger.
# All interaction logic is handled by the GameManager.

func _ready():
	# Ensure the NPC starts snapped to the grid, matching the player's grid size
	const TILE_SIZE = 32.0 
	global_position = global_position.snapped(Vector2(TILE_SIZE, TILE_SIZE))
	print("KnightNPC ready at: ", global_position)
