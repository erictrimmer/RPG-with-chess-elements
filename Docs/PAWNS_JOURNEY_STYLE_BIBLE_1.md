# Pawn's Journey — Art Style Bible
*Living document. Lock decisions here before generating new assets — every AI prompt and every LibreSprite touch-up should trace back to a rule on this page.*

---

## 1. Visual Identity

**Reference point: Earthbound / Mother 2**, filtered through a real place — a lightly fictionalized **York, Pennsylvania**.

What "Earthbound style" means concretely, so it's a checklist and not a vibe:

- **Proportions:** big, round head (~40–45% of total sprite height), short stubby body, small hands/feet. Not full chibi (heads aren't *bigger* than bodies), but heavily simplified compared to realistic RPG proportions.
- **Faces:** minimal. Dot or short-line eyes, rarely a mouth unless the expression needs it. Personality comes from silhouette, hair, and outfit — not facial detail. This is also what makes sprites cheap to reuse across expressions.
- **Outlines:** thin, and usually a *dark shade of the fill color* rather than pure black (e.g., navy outline on a blue jacket, not black). Pure black is reserved for a few grounding details (eyes, deep shadow).
- **Shading:** 2–3 tones per material, flat blocks of color rather than smooth gradients. Where Earthbound uses dithering (alternating pixel patterns) for texture on things like grass or fabric, we can use it sparingly for brick, denim, and grass — it's a texture tool, not a shadow tool.
- **Palette character:** bright and a little heightened, but *not* psychedelic like Earthbound's battle backgrounds — this is a grounded small town, so saturation stays believable (real brick red, real denim blue) while still reading as warm and inviting rather than gritty.
- **Overworld camera:** 3/4 top-down, matching Earthbound's slight-angle perspective rather than a flat top-down grid. Buildings show a bit of their front face, not just roofs.

## 2. Canvas & Resolution Standards

Locking these now avoids the "four spritesheet versions of Max" problem.

| Asset type | Standard | Notes |
|---|---|---|
| Base tile | **16×16px** | Matches your existing `Game_Maker_Studio_Autotiles_16x16` set — keep it, it's already Earthbound-appropriate scale. |
| Character frame | **16×32px** | Matches `NewCharacterSheet.png`, the sheet actually wired into `player.tscn` — and matches genuine SNES-era proportions (Earthbound and its contemporaries built characters from tall 16-wide metasprites, not square frames). This **replaces** the old 32×32 standard — Max's existing 32×32 sheet is not yet used anywhere in the project and needs to be redone at 16×32 to match the Player. |
| Walkable character sheet layout | **7 columns × 4 rows** (28 cells) — one row per direction (Side, Down, Up, Left), ~5 walk frames per row, with one frame in each row doing double duty as the idle pose. Matches `player.tscn` exactly. Use this for any character the player sees move around the overworld. |
| Stationary character sheet layout | **Single row, 2–3 frames** — a simple talk/idle flap (mouth or subtle motion open/closed), matching `Bobby_idle_spritemap.png` and `BobbyNPC.tscn`. Use this for any NPC that stands in place (shopkeepers, mentors at a chessboard, etc.) — no directional walk needed at all. |
| Portrait / dialogue bust | **64×64px** | Needed for NPC dialogue close-ups (chess mentors will need expressive portraits beyond what a 16×32 overworld sprite can convey). |
| Battle/opponent corner sprite | Same as stationary character (single row, 2–3 frames) | Battle scenes are static — chessboard center-stage, opponent portrait in a corner with light idle/reaction animation, not a full rig. Treat exactly like a stationary NPC; don't over-invest here. |
| Chess piece icons | Keep existing `pieces/` set as reference scale | These are more detailed than overworld sprites by necessity; don't force them into the character grid. |

**Which layout does a given character need?** Ask first: does the player ever see this character walk? If yes → walkable (7×4, 16×32, ~24 frames). If no (they're fixed at a counter, a chessboard, a doorway) → stationary (single row, 2–3 frames). Deciding this up front for each character is now step zero before generating anything — it's the difference between a 24-frame job and a 3-frame job.

**Anchor rule:** every character frame's feet sit on the same pixel row within its 16×32 cell, horizontally centered. `sprite_pipeline.py`'s `align` step enforces this automatically by aligning to the *median* observed foot position across a sheet's frames — not a fixed formula — so it corrects genuine outliers without disturbing frames that already agree (see §5 note on the tool's behavior).

## 3. Locked Core Palette

Extracted from your existing Max sprite so new AI generations match what you've already built, not the other way around:

```
#595652  — outline / dark neutral
#000000  — deep shadow / pupils only
#d9a066  — skin tone (base)
#306082  — denim / cool accent
#696a6a  — mid-gray (metal, concrete)
#ffffff  — highlight / eye white
```

This is your **shared base palette** — every character and tile pulls from it for shadows/outlines/neutrals. Each biome or character then adds a **small secondary palette** (4–8 colors) for its own identity — e.g., the Market District might add warm awning reds and market-stall yellows; a character's signature outfit might add one unique accent color. Total colors on screen at once should stay small (Earthbound itself worked in tight palettes); this is also what keeps AI-generated content from looking like generic "AI pixel art" — a locked, distinctive palette is one of the strongest style signals you have.

Stored as JSON at `palette_core.json` (generated below) so it can be fed directly into the processing pipeline or into any AI tool that accepts a reference palette.

## 4. Character Rig System (the actual fix for your animation bottleneck)

Two decisions, in order, before generating anything:

**A. Role first — walkable or stationary?** (see §2.) This determines whether you're signing up for a ~24-frame directional rig or a ~3-frame flap. Most named mentors/shopkeepers who stand at one spot can be stationary; only the protagonist and any wandering NPCs need the full rig.

**B. Body archetype second — for walkable characters only.** Don't generate a full rig per individual. Instead:

1. **Define body archetypes**, not individuals — e.g., `adult_average`, `adult_stocky`, `child`, `elder`. Probably 3–5 total covers your whole walkable cast.
2. **Animate each archetype once**, at 16×32, 7×4: idle-doubling-as-walk-frame in all 4 directions, matching the Player's actual pattern. Hand-finish these in LibreSprite since you're doing this only a handful of times total, not once per character.
3. **Every named walkable character = that archetype's rig + a palette swap + outfit/hair overlay.** Max is `adult_average` + glasses + jacket-blue. The *skeleton and timing* are shared and never regenerated.
4. AI's job shifts from "animate this character" (hard, inconsistent) to "generate an outfit/hairstyle/portrait for this character in our established palette" (much easier to get consistent results on, since it's a single static image, not 24 frames that need to agree with each other).

Stationary characters skip archetype rigging entirely — each just needs its own 2–3 frame flap, closer to a portrait job than an animation job.

This is exactly the pattern your own `Pixel Crawler` asset pack already uses (Orc / Orc-Rogue / Orc-Warrior sharing Run/Idle/Death structure) — apply it to your own walkable cast.

## 5. AI Generation Workflow

> **Precondition for the pipeline below:** `sprite_pipeline.py`'s `align` step assumes frames don't overlap each other in the raw source pixels — it fixes *off-center drift*, not *overlapping/bled-together frames*. If a raw AI sheet has characters wider than their nominal cell, no post-processing can recover it; that has to be prevented at generation time (ask for extra padding between frames, or generate one frame per file and let the pipeline assemble the sheet with guaranteed spacing).

1. **Reference-lock every prompt.** Always include: the locked palette swatch, one existing approved sprite as a style reference image, and the target canvas size. Tools that accept an image reference (img2img, PixelLab, Retro Diffusion) will track your style far better than text description alone ("Earthbound style" as a text prompt drifts fast over many generations).
2. **Generate statics, not animations**, wherever possible (portraits, outfit variants, one-off environment props) — this is where general AI tools are strong.
3. **Generate rig animations only through purpose-built tools** (PixelLab, or hand-finish in LibreSprite) — this is where general text-to-image tools produce the frame-drift problem you were fighting.
4. **Every raw AI output passes through `sprite_pipeline.py`** before it touches LibreSprite: grid-align, then palette-lock. This turns "close enough" AI output into something that's actually on-grid and on-palette, so your manual touch-up time in LibreSprite goes toward *artistic* fixes, not alignment math.
5. **Final manual pass in LibreSprite** for anything the pipeline can't judge — silhouette clarity at a glance, personality in the face/hair, making sure nothing reads ambiguous at a tiny 16×32 scale.

## 6. File Naming & Versioning

Replaces the `max_spritesheet.png` / `_fixed` / `_centered` / `New_` chaos:

```
Assets/Sprites/Characters/<name>/<name>_<action>.png       # final, in-game asset
Assets/Sprites/Characters/<name>/_raw/<name>_<action>_v01.png   # AI output, pre-pipeline
Assets/Sprites/Characters/<name>/_raw/<name>_<action>_v02.png   # iteration, etc.
```

Only the top-level file (no `_raw`, no version suffix) ever gets referenced by a `.tscn` file. Iterations live in `_raw/` and get deleted once superseded — no more ambiguity about which file is "the real one."

## 7. Setting: Yorktowne (fictional, loosely inspired by York, PA)

**Town name: Yorktowne.** Confirmed approach: **analogous, not literal** — real York locations inspire fictional counterparts; exact real-world accuracy isn't the goal. Reference photos can still sharpen the visual flavor of any given district whenever you want to share them, but nothing here requires a 1:1 real-world match.

Starting hooks based on York's actual character, kept loose on purpose:

- **Central Market House** → a natural social hub / quest-giver district (market stalls, gossip, maybe where correspondence-chess games get set up between NPCs).
- **Colonial Courthouse** → could anchor a "town square" chess-hall — formal matches, tournament framing, a stern-but-fair mentor NPC.
- **Row houses / brick residential streets** → the walkable overworld backbone; brick-red becomes a secondary palette anchor for the whole town (paired with the locked core palette above).
- **Codorus Creek / industrial heritage** → good texture for a "working-class" district with a different secondary palette (grittier, cooler tones) if you want visual variety between neighborhoods without breaking the core palette rule.

None of this is fixed — it's scaffolding, to be named and placed concretely as each district actually gets built (starting with the Town Square).

---
*Next: name and place Yorktowne's Town Square as the first concrete scene; expand this section with real district names as they're built.*

## 8. Environment Object Classification

Formalizes a pattern your own NPC scenes (`BobbyNPC`, `Visitor`, `PawnTutor`, `Bot200NPC`) already use independently and identically, without a name for it. Use this table before building any new environment object, so the pattern is chosen deliberately instead of copy-pasted-and-hoped.

**The underlying logic — two independent questions per object:**
1. Does it block movement? (Solid vs. Passable)
2. Does it do anything? (Inert vs. Interactive) — and if interactive, is it *player-initiated* (walk up, press a button) or *automatic* (fires just by walking through it)?

| | Inert | Interactive (explicit) | Interactive (automatic) |
|---|---|---|---|
| **Passable** | Grass, road, sidewalk paint — pure decoration | *(rare: a floor switch)* | **Doorways, scene transitions, cutscene/tutorial-start zones** |
| **Solid** | Walls, fences, lampposts, trees | Chessboards, signs, locked doors, shop counters | *(rare edge case)* |

**Godot physics layer scheme** — names the convention already implicit in the NPC scenes and adds the one missing piece (layer 5):

| Layer # | Bit value | Meaning | Status |
|---|---|---|---|
| 1 | 1 | Player | Already in use |
| 2 | 2 | NPC/actor bodies | Already in use (Bobby, Visitor, PawnTutor, Bot200NPC) |
| 3 | 4 | World solids (walls, buildings) | Already in use (`Market.tscn`) |
| 4 | 8 | Interaction zones (explicit) | Already in use (every NPC's `InteractionArea`) |
| 5 | 16 | **Trigger zones (automatic)** | **New — not yet used anywhere in the project** |

**Node recipe per class:**

- **Decoration (passable, inert):** no physics node at all — just a `TileMapLayer` cell or plain `Sprite2D`.
- **Obstacle (solid, inert):** `StaticBody2D` + `CollisionShape2D` on layer 3, `mask=0`.
- **Interactive prop (solid, explicit):** `StaticBody2D` (layer 3) + child `Area2D` "InteractionArea" (layer 4, `mask=1`) — Bobby's exact pattern, generalized to non-NPC props (chessboards, signs).
- **Trigger zone (passable, automatic):** just an `Area2D` on layer 5, `mask=1`, firing on `body_entered` with no button-press check, no `StaticBody2D`. Use for building entries, scene transitions, tutorial/cutscene starts.
- **Conditional solid:** an interactive-prop object whose `CollisionShape2D.disabled` gets toggled by script from a quest flag (e.g. a gate that opens once a quest completes) — not a new node type, just added state on the solid-interactive recipe.

**Rendering concern, separate from collision:** flat ground decoration (grass, road) never needs draw-order sorting, but *tall* decoration (trees, lampposts, building facades) does, so the player can walk behind a canopy but in front of a trunk. Put all tall objects under a parent with `y_sort_enabled = true`.

**Scaling recommendation:** build one reusable `InteractableProp.tscn` base scene (StaticBody2D + Area2D + signal wiring already done, `interaction_id` and `prompt_text` exposed as exported fields) and have every specific interactive prop instance/inherit it, rather than hand-wiring the Area2D and signals from scratch per object the way the four NPC scenes currently do independently.

**Honest scope note:** this is a development-time efficiency and consistency win (fewer hand-copied scenes, one place to change the convention later), not a meaningful runtime performance win at this game's likely scale — worth doing because you're about to build many environment objects, not because the game would otherwise run slowly.

---
*Next: once reference photos are in, expand §7 with actual named districts; build `InteractableProp.tscn` as the first real application of §8.*
