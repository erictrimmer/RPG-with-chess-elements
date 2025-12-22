# NPC Dialog System Implementation Guide

## Overview
This guide will help you add the Pawn Tutor NPC to the overworld with interactive dialogs and scene transitions.

## Files Already Created
- ✅ `Entities/NPCs/PawnTutor.gd` - NPC interaction script
- ✅ `Systems/DialogManager.gd` - Dialog UI system

---

## Step 1: Add DialogManager to Autoload

1. Open **Project → Project Settings → Autoload**
2. Add new autoload:
   - **Path**: `res://Systems/DialogManager.gd`
   - **Name**: `DialogManager`
   - **Enable**: ✓
3. Click **Add** and **Close**

---

## Step 2: Create Pawn Tutor NPC in world.tscn

### A. Open world.tscn
1. Open `Scenes/world.tscn` in Godot editor

### B. Create NPC Node Structure
1. Right-click on root node → **Add Child Node**
2. Search for **CharacterBody2D** → Create
3. Rename to `PawnTutor`
4. With `PawnTutor` selected, add children:

```
PawnTutor (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
└── InteractionArea (Area2D)
    └── InteractionCollision (CollisionShape2D)
```

### C. Configure Sprite2D
1. Select `Sprite2D`
2. In Inspector → **Texture**: 
   - Use a pawn sprite or create a simple colored rectangle
   - **Modulate**: Set to white/cream color for pawn
3. **Transform → Scale**: `(2, 2)` to make it visible

### D. Configure CollisionShape2D (NPC Body)
1. Select `CollisionShape2D`
2. In Inspector → **Shape**: Create **RectangleShape2D**
3. Set **Size**: `(16, 16)`

### E. Configure InteractionArea
1. Select `InteractionArea`
2. In Inspector → **Collision → Layer**: Uncheck all
3. **Collision → Mask**: Check layer 1 (player layer)
4. Right-click `InteractionArea` → **Add Child** → **CollisionShape2D**
5. Rename to `InteractionCollision`
6. **Shape**: Create **CircleShape2D**
7. **Radius**: `30` (interaction range)

### F. Attach Script
1. Select `PawnTutor` (root CharacterBody2D)
2. In Inspector → **Script**: Attach `res://Entities/NPCs/PawnTutor.gd`
3. **Position**: Place near player spawn (e.g., `(100, 100)`)

### G. Connect Signals
1. Select `InteractionArea`
2. Go to **Node** tab (next to Inspector)
3. Double-click `body_entered` signal
4. Connect to `PawnTutor` → `_on_area_entered`
5. Double-click `body_exited` signal
6. Connect to `PawnTutor` → `_on_area_exited`

---

## Step 3: Create World Controller Script

Create `Scenes/World.gd`:

```gdscript
extends Node2D

var player_node
var pawn_tutor_npc
var player_saved_position = Vector2.ZERO
var current_npc_interaction = null

func _ready():
	player_node = $Player  # Adjust path to your player node
	pawn_tutor_npc = $PawnTutor
	
	# Connect NPC signals
	pawn_tutor_npc.interaction_requested.connect(_on_npc_interaction)
	
	# Connect dialog signals
	DialogManager.dialog_choice_made.connect(_on_dialog_choice)

func _on_npc_interaction(interaction_type: String):
	current_npc_interaction = "pawn_tutor"
	
	match interaction_type:
		"show_initial":
			DialogManager.show_dialog(
				"Want to learn how pawns move?",
				["Yes", "Not now"]
			)
		"show_completed":
			DialogManager.show_dialog("Good job!", [])
		"show_failed":
			DialogManager.show_dialog(
				"Try again?",
				["Yes", "No"]
			)
		"close_dialog":
			DialogManager.close_dialog()
			current_npc_interaction = null

func _on_dialog_choice(choice: String):
	if current_npc_interaction == "pawn_tutor":
		match choice:
			"Yes":
				start_pawn_tutorial()
			"Not now", "No":
				DialogManager.close_dialog()

func start_pawn_tutorial():
	# Save player position
	player_saved_position = player_node.global_position
	
	# Load tutorial scene
	get_tree().change_scene_to_file("res://Scenes/Puzzles/Pawns/PawnTutorial.tscn")

func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		# Handle scene return
		pass
```

### Attach World.gd to world.tscn:
1. Select root node of `world.tscn`
2. **Script**: Attach `res://Scenes/World.gd`

---

## Step 4: Update PawnTutorial to Return to World

Modify `Scenes/Puzzles/Pawns/PawnTutorial.gd`:

```gdscript
extends "res://Systems/GameManager.gd"

func _ready():
	super._ready()
	
	await get_tree().create_timer(0.1).timeout
	start_puzzle(
		"rnbqkbnr/pppppppp/8/8/8/8/P6P/RNBQKBNR w KQkq - 0 1",
		"e2e3",
		"Move the pawn forward one square.",
		"Great! Pawns can move forward one square."
	)

# Override to return to world on success
func _end_game(reason: String):
	super._end_game(reason)
	
	if reason.contains("Success"):
		# Mark tutorial as completed
		await get_tree().create_timer(2.0).timeout
		return_to_world("completed")

# Override resign to return to world on give up
func _on_resign_requested():
	return_to_world("failed")

func return_to_world(result: String):
	# Store result for world to read
	# Use a global/autoload or file
	var world_data = {
		"tutorial_result": result,
		"npc": "pawn_tutor"
	}
	# For now, just change scene
	get_tree().change_scene_to_file("res://Scenes/world.tscn")
```

---

## Step 5: Handle Scene Return in World

Update `World.gd` to handle returns:

```gdscript
func _ready():
	player_node = $Player
	pawn_tutor_npc = $PawnTutor
	
	# Connect signals
	pawn_tutor_npc.interaction_requested.connect(_on_npc_interaction)
	DialogManager.dialog_choice_made.connect(_on_dialog_choice)
	
	# Check if returning from tutorial
	check_tutorial_result()

func check_tutorial_result():
	# You'll need to implement persistent state
	# For now, check a simple flag or file
	# Example: if tutorial was completed, update NPC state
	pass
```

---

## Step 6: Add Player Interaction Detection

Update player script to add to "player" group:

```gdscript
# In player.gd _ready():
func _ready():
	add_to_group("player")
```

---

## Optional Enhancements

### Persistent State
Create `Systems/GameState.gd` autoload:

```gdscript
extends Node

var tutorial_states = {
	"pawn_tutorial": "not_started"  # not_started, completed, failed
}

func set_tutorial_state(tutorial_name: String, state: String):
	tutorial_states[tutorial_name] = state

func get_tutorial_state(tutorial_name: String) -> String:
	return tutorial_states.get(tutorial_name, "not_started")
```

### Visual Feedback
- Add exclamation mark sprite above NPC when interactable
- Animate NPC sprite on interaction
- Add sound effects for dialog open/close

---

## Troubleshooting

**Dialog doesn't appear:**
- Check InteractionArea collision layers/masks
- Verify player is in "player" group
- Check signal connections

**Scene doesn't change:**
- Verify scene paths are correct
- Check for errors in Output console

**Player position not restored:**
- Implement persistent state system
- Save/load player position properly

---

## Next Steps

After basic implementation works:
1. Add more NPCs with different tutorials
2. Implement quest/progression system
3. Add visual indicators for completed tutorials
4. Create NPC dialog trees for multiple interactions
