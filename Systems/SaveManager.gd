extends Node
## SaveManager: multiple save slots, written as JSON under user://saves/.
##
## A save holds the scene the player is in, where they stand, and the state of every system that
## persists: GameState (ratings, flags, play time), QuestManager and InventoryManager.
## The Title Screen and the Pause Menu are the only UI; everything else calls this API.
##
##   SaveManager.start_new_game(slot)   fresh game in a slot
##   SaveManager.load_slot(slot)        load a slot and move to its scene
##   SaveManager.save_to_slot(slot)     save the current scene (needs a player in it)
##   SaveManager.autosave()             re-save the slot this game was started or loaded from

signal saved(slot: int)
signal loaded(slot: int)

const SLOT_COUNT := 3
const SAVE_DIR := "user://saves/"
const SAVE_VERSION := 1

const TITLE_SCENE := "res://Scenes/TitleScreen.tscn"
## Where a new game begins. Swap these when the real opening cutscene exists.
const NEW_GAME_SCENE := "res://World/Downtown/downtown_test.tscn"
const NEW_GAME_SPAWN := Vector2(1944, 1968)
const NEW_GAME_FACING := "up"

## Friendly names shown in the slot list. Add each scene as it is built.
const LOCATION_NAMES := {
	"res://World/Downtown/downtown_test.tscn": "Downtown Yorktowne",
	"res://World/Interior/depot_interior.tscn": "Railroad Depot",
	"res://Scenes/demo.tscn": "Chess Demo",
}

## Slot this game belongs to (-1 = none, e.g. when a scene is run straight from the editor).
var current_slot := -1
var last_error := ""

var _active := false  # true between "new game / load" and "back to title"; play time only counts then

func _process(delta: float) -> void:
	if _active:
		GameState.playtime += delta

# ---------------------------------------------------------------
# Slot files
# ---------------------------------------------------------------

func slot_path(slot: int) -> String:
	return SAVE_DIR + "slot_%d.json" % (slot + 1)

func has_save(slot: int) -> bool:
	return FileAccess.file_exists(slot_path(slot))

## Everything the slot list needs. `exists` false = empty slot; `corrupt` true = file there but unreadable.
func get_slot_info(slot: int) -> Dictionary:
	var info := {"slot": slot, "exists": false, "corrupt": false}
	if not has_save(slot):
		return info
	info["exists"] = true
	var data := _read(slot)
	if data.is_empty():
		info["corrupt"] = true
		return info
	var scene := str(data.get("scene", ""))
	info["location"] = LOCATION_NAMES.get(scene, scene.get_file().get_basename().capitalize())
	info["saved_at"] = int(data.get("saved_at", 0))
	info["playtime"] = float(data.get("game_state", {}).get("playtime", 0.0))
	info["rating"] = float(data.get("game_state", {}).get("player_rating", 0.0))
	info["progress"] = _progress_text(data.get("quests", {}))
	return info

## Slot with the newest save, or -1 when there are none.
func most_recent_slot() -> int:
	var best := -1
	var best_time := -1
	for slot in SLOT_COUNT:
		var info := get_slot_info(slot)
		if info["exists"] and not info["corrupt"] and int(info["saved_at"]) > best_time:
			best_time = int(info["saved_at"])
			best = slot
	return best

func delete_slot(slot: int) -> void:
	if has_save(slot):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(slot_path(slot)))
	if current_slot == slot:
		current_slot = -1

# ---------------------------------------------------------------
# Starting, saving, loading
# ---------------------------------------------------------------

func start_new_game(slot: int) -> bool:
	_reset_everything()
	current_slot = slot
	_active = true
	var data := _collect(NEW_GAME_SCENE, NEW_GAME_SPAWN, NEW_GAME_FACING)
	if not _write(slot, data):
		return false
	_enter_scene(NEW_GAME_SCENE, NEW_GAME_SPAWN, NEW_GAME_FACING)
	return true

func can_save() -> bool:
	return get_tree().current_scene != null and get_tree().get_first_node_in_group("player") != null

func save_to_slot(slot: int) -> bool:
	if not can_save():
		last_error = "There is nothing to save here."
		return false
	var scene := get_tree().current_scene
	var player := get_tree().get_first_node_in_group("player") as Node2D
	var facing := str(player.get("last_direction")) if "last_direction" in player else "down"
	var data := _collect(scene.scene_file_path, player.global_position, facing)
	if not _write(slot, data):
		return false
	current_slot = slot
	_active = true
	saved.emit(slot)
	return true

## Quietly re-save the slot this game belongs to. Called when a level loads (after a door, after a load).
func autosave() -> void:
	if _active and current_slot >= 0 and can_save():
		save_to_slot(current_slot)

func load_slot(slot: int) -> bool:
	var data := _read(slot)
	if data.is_empty():
		last_error = "That save could not be read."
		return false
	var scene := str(data.get("scene", ""))
	if not ResourceLoader.exists(scene):
		last_error = "That save points at a scene that no longer exists."
		return false
	_reset_everything()
	GameState.load_save_data(data.get("game_state", {}))
	QuestManager.load_save_data(data.get("quests", {}))
	InventoryManager.load_save_data(_ints(data.get("inventory", {})))
	current_slot = slot
	_active = true
	var pos_arr: Array = data.get("player", {}).get("pos", [0, 0])
	var pos := Vector2(float(pos_arr[0]), float(pos_arr[1]))
	_enter_scene(scene, pos, str(data.get("player", {}).get("facing", "down")))
	loaded.emit(slot)
	return true

func return_to_title() -> void:
	_active = false
	current_slot = -1
	get_tree().paused = false
	GameManager.go_to_scene(TITLE_SCENE)

# ---------------------------------------------------------------
# Formatting helpers (used by the slot list)
# ---------------------------------------------------------------

static func format_playtime(seconds: float) -> String:
	var total := int(seconds)
	var h := total / 3600
	var m := (total % 3600) / 60
	return "%dh %02dm" % [h, m] if h > 0 else "%dm" % m

static func format_saved_at(unix: int) -> String:
	if unix <= 0:
		return "unknown date"
	var d := Time.get_datetime_dict_from_unix_time(unix + int(Time.get_time_zone_from_system()["bias"]) * 60)
	var months := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	var hour12 := int(d["hour"]) % 12
	if hour12 == 0:
		hour12 = 12
	return "%s %d, %d:%02d %s" % [months[int(d["month"]) - 1], int(d["day"]), hour12, int(d["minute"]), "AM" if int(d["hour"]) < 12 else "PM"]

# ---------------------------------------------------------------
# Internals
# ---------------------------------------------------------------

func _reset_everything() -> void:
	GameState.reset_for_new_game()
	QuestManager.clear()
	InventoryManager.clear()

func _collect(scene_path: String, pos: Vector2, facing: String) -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"saved_at": int(Time.get_unix_time_from_system()),
		"scene": scene_path,
		"player": {"pos": [pos.x, pos.y], "facing": facing},
		"game_state": GameState.get_save_data(),
		"quests": QuestManager.get_save_data(),
		"inventory": InventoryManager.get_save_data(),
	}

## Level scripts pick the hand-off up with SceneDoor.apply_pending_spawn(), the same path doors use.
func _enter_scene(scene_path: String, pos: Vector2, facing: String) -> void:
	GameState.set_meta(&"next_spawn", {"pos": pos, "facing": StringName(facing)})
	get_tree().paused = false
	GameManager.go_to_scene(scene_path)

func _read(slot: int) -> Dictionary:
	var f := FileAccess.open(slot_path(slot), FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	var data: Dictionary = parsed
	if int(data.get("version", 0)) < 1 or int(data.get("version", 0)) > SAVE_VERSION:
		return {}
	if not data.has("scene") or not data.has("player"):
		return {}
	return data

## Write to a temp file first, so a crash mid-save never leaves a half-written slot.
func _write(slot: int, data: Dictionary) -> bool:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(SAVE_DIR))
	var path := slot_path(slot)
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		last_error = "Could not write the save file."
		return false
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	var abs_path := ProjectSettings.globalize_path(path)
	var abs_tmp := ProjectSettings.globalize_path(tmp)
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(abs_path)
	if DirAccess.rename_absolute(abs_tmp, abs_path) != OK:
		last_error = "Could not finish writing the save file."
		return false
	return true

func _progress_text(quests: Dictionary) -> String:
	var label := ""
	var done := false
	for quest_id in QuestManager.QUEST_DATA:
		var stage := str(quests.get(quest_id, QuestManager.STAGE_NOT_STARTED))
		if stage != QuestManager.STAGE_NOT_STARTED:
			label = str(QuestManager.QUEST_DATA[quest_id].get("label", quest_id))
			done = stage == QuestManager.STAGE_COMPLETE
	if label == "":
		return "Just beginning"
	return label + (" (done)" if done else "")

## JSON turns every number into a float; item counts should stay whole numbers.
func _ints(d: Dictionary) -> Dictionary:
	var out := {}
	for k in d:
		out[str(k)] = int(d[k])
	return out
