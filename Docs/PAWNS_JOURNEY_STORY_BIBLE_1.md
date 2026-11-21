# Pawn's Journey — Story Bible
*Living document, companion to the Style Bible. Reconciles the existing `QuestManager.gd` quest chain with the newer dirt-bike/Death/Frankensteinitz story notes — this is the merged, current canon.*

---

## 1. Logline

A kid who runs with a dirt-bike crew in Yorktowne wrecks his bike doing a stunt and needs money he doesn't have. A tournament poster promises a cash prize that would cover it — but he's not good enough to win. Chasing a rumor of a great player, he finds only a grave — and something stranger. What starts as a scramble for repair money becomes a real chess education, guided by a mentor nobody else can see.

## 2. Tone & Themes

- **The dirt-bike crew are people, not a problem to be solved.** They're riding illegally, it's a genuine nuisance to some of the town, and it's also a real community and a real skill. Don't flatten them into "troubled youth" set dressing — give them specific personalities, banter, and pride in what they do. The game's stance on them should be affectionate, not judgmental, and not preachy either.
- **The "reaching people on the margins" goal is a craft problem, not a message to state out loud.** The thesis — a kid written off as a troublemaker turns out to have real discipline and intelligence — should come through the plot structure (he takes the chess tournament as seriously as he takes riding) rather than through any character delivering a speech about it.
- **Death is affectionate, not grim.** Visual reference is Bergman's *The Seventh Seal*, but the tonal target is closer to "a strange, dry, ultimately kind figure who happens to be Death" than genuine horror. He should fit the town's Earthbound-warm visual identity — striking and a little eerie, not frightening. Earthbound itself gets away with surprisingly dark beats (Threed's zombie infestation) inside a warm-looking world; same balance applies here.
- **Frankensteinitz is friendly.** He looks like a monster, references Frankenstein visually/thematically, but wants nothing except a good game. The horror-movie iconography is a fake-out — the actual encounter should feel like meeting an eccentric, gentle giant.

## 3. Act Structure

Quest IDs below match `Systems/QuestManager.gd` exactly, so the doc and the code can be cross-referenced directly. Items in *italics* need a code change to match the merged story (see §6).

**Act 1 — Wheelies & the Crash** *(new — not yet its own quest_id; likely an intro cutscene/sequence rather than a tracked quest)*
Player's crew does stunts around Yorktowne on dirt bikes — a little illegal, a little beloved, a real community. Player crashes attempting a stunt. Bike's wrecked. Needs money.

**Act 1a — `job_at_shop`: Help Wanted** *(existing, unchanged)*
Takes a cash job cleaning the storeroom for the Pawn Shop's owner. Somewhere in this act, the player notices the **King of the Hill tournament poster** in a window — first sight of the way out of his money problem. (The pawn shop setting quietly rhymes with the theme — a shop built on other people's hard luck — without needing to say so.)

**Act 1b — `find_tim`: Missing Piece** *(existing, unchanged)*
Shop owner mentions Tim, a man in the park building something that looks like the set's missing piece.

**Act 2 — `scrap_metal_run`: Scrap for Tim** *(existing, unchanged)*
Fetch scrap metal from the landfill for Tim's sculpture.

**Act 2b — `tims_sculpture`: The Giant Knight** *(existing, unchanged)*
Tim finishes his giant steel chess knight — in the same park the tournament will later be held in. Player gets the missing black knight piece, completing the set.

**Act 3 — `find_clock`: Tim's Old Clock** *(existing, unchanged)*
Tim mentions he left his old chess clock at the library.

**Act 3b — `skeleton_lessons` → rename to `dead_master`: The Dead Master** *(merge point — renamed and re-motivated, same structural beat)*
In the library basement, alongside the old chess clock, the player finds the remains of a once-great chess player. That discovery is what draws **Death's** attention. Death challenges the player on the spot — the player loses; Death is simply much stronger. Death then gives the first real lesson: **how the pieces move.** He vanishes afterward. From here on, he appears intermittently around the world (§4) — interacting again continues the lesson sequence. The cemetery version of this beat is dropped; this library encounter is the sole origin of Death's presence in the story.

**Act 4 — `landfill_practice`: Ready to Play** *(existing, unchanged)*
Practice matches against Alpert and Herb at the landfill, now that the player has a complete set and clock.

**Act 5 — `tournament` → reward changed: King of the Hill** *(existing structure, reward reframed)*
Same tournament beats (`known` → `round_1_done` → `round_2_done` → complete), held in the same park as Tim's sculpture. Reward changes from the old "Motor Scooter" item to **cash sufficient to fix the bike** (see §6 for the inventory-item change this implies).

**Endgame — Frankensteinitz** *(entirely new, beyond the existing 5 acts — no quest_id yet)*
Post-tournament (or as very-late-game optional content), word spreads of the strongest player alive, far to the north. A long overworld journey to the top of the map ends at the North Pole, where the player meets **Frankensteinitz** — assembled from pieces of history's great chess players, presenting the ultimate challenge. He's monstrous in appearance, gentle in nature, and wants nothing but a serious game.

## 4. Death — Mechanical & Narrative Notes

- **First appearance** is fixed: the library basement, immediately after the player finds the dead master's remains (`dead_master` quest). Not before.
- **After that, he's a recurring wandering encounter**, not tied to a specific quest stage — he "lurks" around Yorktowne's overworld. Reuses the ambient-challenger NPC pattern already being built (§8 of the Style Bible / the `BotProfile`-driven challenger template), but as a **unique, story-flagged instance** rather than a random one — he needs his own dialogue states and lesson-sequencing, not just a rating.
- **Each encounter after the first advances one lesson** (piece movement → check/checkmate → basic tactics → openings → endgame technique, or whatever curriculum order makes sense once the actual chess-curriculum pillar gets designed). Track progress the same way `GameState.tutorial_states` already tracks `pawn_tutorial` — Death's lesson stage is a natural extension of that exact dictionary, not a new system.
- **Open question:** how many total Death lessons are there, and do they gate story progress (must complete lesson N before some later act) or are they fully optional/side-track? Worth deciding once the chess-curriculum pillar is scoped.

## 5. Character Roster

| Character | Role | Status |
|---|---|---|
| Player | Protagonist, dirt-bike crew member | Named? — TBD |
| Dirt-bike crew (others) | Player's friends/community | Unnamed placeholders — worth giving at least 1-2 named, specific personalities per §2 |
| Pawn Shop owner | Act 1 employer, poster source | Unnamed — TBD |
| Tim | Sculptor in the park, chess-set quest chain | Named, established |
| Alpert, Herb | Landfill practice opponents | Named, established |
| Death | Recurring mentor, first met in library basement | Established in concept; needs actual sprite (stationary rig, per Style Bible §4) and dialogue writing |
| Frankensteinitz | Endgame final challenge | Established in concept; needs design pass on appearance and whether his "assembled from great players" concept extends into mechanics (e.g., a stitched-together opening book) |

## 6. Implementation Checklist (for when we update the code)

- [ ] Rename `skeleton_lessons` quest_id → `dead_master` (or similar) in `QuestManager.gd`, update label/description to reflect Death rather than a generic skeleton.
- [ ] Remove/replace the `Motor Scooter` inventory item (`Systems/InventoryManager.gd`) with a cash reward, and update `tournament` quest's description accordingly.
- [ ] Add `death_lesson_stage` (or fold into `tutorial_states`) to `GameState.gd` to track which lesson Death has most recently given.
- [ ] Design Death as a unique NPC instance — likely built on the same consolidated `ChessChallengerNPC.tscn` + `BotProfile` template being planned (§8 discussion), but flagged as story-unique rather than random/ambient.
- [ ] No quest_id yet exists for the Frankensteinitz endgame arc — add one once it's ready to be tracked.
- [ ] Dirt-bike Act 1 crash sequence has no quest_id yet either — decide whether it needs one or is purely a cutscene/intro with no tracked state.

---
*Next: name the pawn shop owner and at least one dirt-bike crew member; scope out Death's actual lesson curriculum alongside the chess-curriculum pillar; revisit Frankensteinitz's design once the endgame is closer.*
