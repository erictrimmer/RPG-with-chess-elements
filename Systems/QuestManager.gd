extends Node

# ============================================================
# QuestManager — Global Singleton
# Tracks the stage of every quest in the campaign.
# Access anywhere via: QuestManager.get_stage("job_at_shop")
# ============================================================

signal quest_started(quest_id: String)
signal quest_stage_changed(quest_id: String, old_stage: String, new_stage: String)
signal quest_completed(quest_id: String)

# --- Stage Constants ---
# Use these named constants instead of raw strings to avoid typos.
const STAGE_NOT_STARTED  = "not_started"
const STAGE_ACTIVE       = "active"
const STAGE_COMPLETE     = "complete"

# --- Quest Definitions ---
# Each quest has:
#   "label"       — human-readable name (for debug/UI)
#   "stages"      — ordered list of valid stage names beyond the defaults
#   "description" — what this quest is about
const QUEST_DATA: Dictionary = {

	# Act 1 — Getting the chess set
	"job_at_shop": {
		"label": "Help Wanted",
		"stages": ["cleaning", "paid"],
		"description": "Clean out the storeroom for the new shop owner."
	},

	# Act 1b — Following up on the broken chess set
	"find_tim": {
		"label": "Missing Piece",
		"stages": [],
		"description": "The shop owner mentioned a man in the park building something that looks like the missing chess piece."
	},

	# Act 2 — Tim's errand
	"scrap_metal_run": {
		"label": "Scrap for Tim",
		"stages": [],
		"description": "Tim needs a piece of scrap metal from the landfill to finish his sculpture."
	},

	# Act 2b — Completing Tim's sculpture and getting the piece
	"tims_sculpture": {
		"label": "The Giant Knight",
		"stages": ["sculpture_done"],
		"description": "Tim is building a giant steel chess knight in the park."
	},

	# Act 3 — Finding the clock
	"find_clock": {
		"label": "Tim's Old Clock",
		"stages": ["library_visited", "basement_found"],
		"description": "Tim says he left his old chess clock at the library."
	},

	# Act 3b — The skeleton encounter
	"skeleton_lessons": {
		"label": "The Skeleton's Lessons",
		"stages": ["met_skeleton"],
		"description": "There's something strange in the library basement..."
	},

	# Act 4 — Practice at the landfill
	"landfill_practice": {
		"label": "Ready to Play",
		"stages": ["beat_alpert", "beat_herb"],
		"description": "Alpert and Herb said to come back once you have your chess set and clock."
	},

	# Act 5 — The tournament
	"tournament": {
		"label": "Downtown Chess Tournament",
		"stages": ["known", "round_1_done", "round_2_done"],
		"description": "Win the tournament and take home the motor scooter."
	},
}

# --- Internal State ---
# quest_id -> current stage string
var _quest_stages: Dictionary = {}


# ---------------------------------------------------------------
# Core API
# ---------------------------------------------------------------

## Returns the current stage of a quest. Defaults to "not_started".
func get_stage(quest_id: String) -> String:
	return _quest_stages.get(quest_id, STAGE_NOT_STARTED)


## Returns true if the quest is at exactly this stage.
func is_stage(quest_id: String, stage: String) -> bool:
	return get_stage(quest_id) == stage


## Returns true if the quest has been started (stage != "not_started").
func is_started(quest_id: String) -> bool:
	return get_stage(quest_id) != STAGE_NOT_STARTED


## Returns true if the quest is fully complete.
func is_complete(quest_id: String) -> bool:
	return get_stage(quest_id) == STAGE_COMPLETE


## Advance a quest to a new stage. Emits signals accordingly.
## Will warn (but not crash) if the quest_id is unknown.
func set_stage(quest_id: String, new_stage: String) -> void:
	if not QUEST_DATA.has(quest_id):
		push_warning("QuestManager: Unknown quest id '%s'" % quest_id)
		return

	var old_stage = get_stage(quest_id)
	if old_stage == new_stage:
		return  # No change, no signal spam

	_quest_stages[quest_id] = new_stage
	print("QuestManager: [%s] %s -> %s" % [quest_id, old_stage, new_stage])

	# Emit specific signals for listeners to react
	if old_stage == STAGE_NOT_STARTED:
		emit_signal("quest_started", quest_id)

	emit_signal("quest_stage_changed", quest_id, old_stage, new_stage)

	if new_stage == STAGE_COMPLETE:
		emit_signal("quest_completed", quest_id)


## Shorthand to start a quest (sets to "active").
func start_quest(quest_id: String) -> void:
	set_stage(quest_id, STAGE_ACTIVE)


## Shorthand to complete a quest (sets to "complete").
func complete_quest(quest_id: String) -> void:
	set_stage(quest_id, STAGE_COMPLETE)


## Returns true if ALL of the given quest ids are complete.
func all_complete(quest_ids: Array) -> bool:
	for id in quest_ids:
		if not is_complete(id):
			return false
	return true


## Returns true if ANY of the given quest ids are complete.
func any_complete(quest_ids: Array) -> bool:
	for id in quest_ids:
		if is_complete(id):
			return true
	return false


## Returns a list of all quest ids currently in progress (started but not complete).
func get_active_quests() -> Array:
	var active := []
	for id in QUEST_DATA.keys():
		var stage = get_stage(id)
		if stage != STAGE_NOT_STARTED and stage != STAGE_COMPLETE:
			active.append(id)
	return active


## Returns a list of all completed quest ids.
func get_completed_quests() -> Array:
	var done := []
	for id in QUEST_DATA.keys():
		if is_complete(id):
			done.append(id)
	return done


## Returns the human-readable label for a quest.
func get_label(quest_id: String) -> String:
	if QUEST_DATA.has(quest_id):
		return QUEST_DATA[quest_id]["label"]
	return quest_id


## Returns the description for a quest.
func get_description(quest_id: String) -> String:
	if QUEST_DATA.has(quest_id):
		return QUEST_DATA[quest_id]["description"]
	return ""


## Resets all quest progress (use for new game / debug only).
func clear() -> void:
	_quest_stages.clear()
	print("QuestManager: All quest progress cleared.")


# ---------------------------------------------------------------
# Save / Load support
# ---------------------------------------------------------------

func get_save_data() -> Dictionary:
	return _quest_stages.duplicate()


func load_save_data(data: Dictionary) -> void:
	_quest_stages = data.duplicate()
	print("QuestManager: Loaded %d quest stage(s)." % _quest_stages.size())
