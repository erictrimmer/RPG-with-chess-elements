extends Node

# ============================================================
# InventoryManager — Global Singleton
# Tracks all quest items the player is carrying.
# Access anywhere via: InventoryManager.add_item("chess_set")
# ============================================================

signal item_added(item_id: String)
signal item_removed(item_id: String)
signal item_upgraded(old_id: String, new_id: String)

# --- Item Definitions ---
# All known items in the game with display name and description.
const ITEM_DATA: Dictionary = {
	"twenty_dollars": {
		"name": "$20",
		"description": "Payment for cleaning out the storeroom.",
		"icon": ""
	},
	"chess_set_broken": {
		"name": "Chess Set (incomplete)",
		"description": "A nice chess set, but it's missing the black knight.",
		"icon": ""
	},
	"chess_set": {
		"name": "Chess Set",
		"description": "A complete chess set. All 32 pieces.",
		"icon": ""
	},
	"black_knight_piece": {
		"name": "Black Knight",
		"description": "The missing piece. A black knight, just like Tim's sculpture.",
		"icon": ""
	},
	"scrap_metal": {
		"name": "Hunk of Scrap Metal",
		"description": "A solid chunk of scrap. Tim can use this to finish his sculpture.",
		"icon": ""
	},
	"chess_clock": {
		"name": "Chess Clock",
		"description": "An old analog chess clock. Still ticks.",
		"icon": ""
	},
	"scooter": {
		"name": "Motor Scooter",
		"description": "First place prize from the Downtown Chess Tournament. Vroom.",
		"icon": ""
	},
}

# --- Internal State ---
# Stores item_id -> quantity (quantity is almost always 1 for quest items)
var _inventory: Dictionary = {}


# ---------------------------------------------------------------
# Core API
# ---------------------------------------------------------------

## Add an item to inventory. Emits item_added signal.
func add_item(item_id: String, quantity: int = 1) -> void:
	if not ITEM_DATA.has(item_id):
		push_warning("InventoryManager: Unknown item id '%s'" % item_id)
		return
	if _inventory.has(item_id):
		_inventory[item_id] += quantity
	else:
		_inventory[item_id] = quantity
	print("InventoryManager: Added '%s' (qty: %d)" % [item_id, _inventory[item_id]])
	emit_signal("item_added", item_id)


## Remove an item from inventory. Returns true if successful.
func remove_item(item_id: String, quantity: int = 1) -> bool:
	if not has_item(item_id):
		push_warning("InventoryManager: Tried to remove '%s' but player doesn't have it." % item_id)
		return false
	_inventory[item_id] -= quantity
	if _inventory[item_id] <= 0:
		_inventory.erase(item_id)
	print("InventoryManager: Removed '%s'" % item_id)
	emit_signal("item_removed", item_id)
	return true


## Upgrade an item — removes old_id and adds new_id in one atomic step.
## e.g. upgrade_item("chess_set_broken", "chess_set")
func upgrade_item(old_id: String, new_id: String) -> void:
	remove_item(old_id)
	add_item(new_id)
	print("InventoryManager: Upgraded '%s' -> '%s'" % [old_id, new_id])
	emit_signal("item_upgraded", old_id, new_id)


## Returns true if the player has at least one of this item.
func has_item(item_id: String) -> bool:
	return _inventory.has(item_id) and _inventory[item_id] > 0


## Returns the quantity of an item (0 if not in inventory).
func get_quantity(item_id: String) -> int:
	return _inventory.get(item_id, 0)


## Returns the display name of an item id.
func get_item_name(item_id: String) -> String:
	if ITEM_DATA.has(item_id):
		return ITEM_DATA[item_id]["name"]
	return item_id


## Returns the description of an item id.
func get_item_description(item_id: String) -> String:
	if ITEM_DATA.has(item_id):
		return ITEM_DATA[item_id]["description"]
	return ""


## Returns an array of all currently held item ids.
func get_all_items() -> Array:
	return _inventory.keys()


## Returns true if inventory is empty.
func is_empty() -> bool:
	return _inventory.is_empty()


## Clears the entire inventory (use for new game / debug only).
func clear() -> void:
	_inventory.clear()
	print("InventoryManager: Inventory cleared.")


# ---------------------------------------------------------------
# Save / Load support (flat dict — easy to serialize)
# ---------------------------------------------------------------

func get_save_data() -> Dictionary:
	return _inventory.duplicate()


func load_save_data(data: Dictionary) -> void:
	_inventory = data.duplicate()
	print("InventoryManager: Loaded inventory with %d item(s)." % _inventory.size())
