# District Builder Brief (for district sub-agents)

You are dressing one district of **Downtown Yorktowne**, a 1960s fictional York, PA, 160x128 tiles of
16px, for an Earthbound-inspired RPG in Godot 4.5 (3/4 top-down, characters 16x32). Quality bar:
a commercial 1990s+ game (Earthbound's Onett/Twoson, Pokémon gen 3-4 towns, Stardew Valley's town).
Look must be dense, intentional and lived-in: clusters and composition, not random sprinkles.

## Read first
- `F:/pawn's-journey/Tools/world_builder/design/downtown_brief.md` — the art director's master brief.
  Your district's section has exact tile coordinates; follow them (small deviations are fine if
  they look better — keep roads, bridges, gates and stairs exactly where they are).
- Catalogs (prefab ids, sizes, solid cells, overhead rows): `F:/pawn's-journey/Tools/world_builder/catalog/*.json`.
  Use `sheet_tool.py preview <catalog.json>` (see CATALOG_BRIEF.md) to SEE prefabs before using them.
  Prefer `era1960` "good"/"ok"; never use "avoid".

## Code you write
Create ONE file: `F:/pawn's-journey/Tools/world_builder/districts/<your_district>.py` with
```python
REGION = (x0, y0, x1, y1)          # inclusive tile rect you own; do not place anything outside it
def build_ground(L, lib):          # optional: terrain edits BEFORE the ground is baked
    ...                            #   L.fill(kind, x0, y0, x1, y1), L.set_kind(x, y, kind)
def build(L, lib):                 # props/buildings AFTER baking
    ...
```
Do not edit any other file. You may import `dress`, `synth`, `buildings`, `terrain`, `decals`
(all in Tools/world_builder; the harness puts that folder on sys.path).

### Terrain kinds (for build_ground)
`grass, sidewalk, road, plaza (red-brown herringbone brick), plaza_grey, cobble, dirt (packed dirt/gravel
path with grass fringe — autotiles), track (flat orange dirt), water, pond (natural pond, solid),
shoal`. Elevation is preset (creek sunken, cemetery upper terrace and NE overlook raised, cliff faces
at y=10..11 with stairs) — don't change elevation.

### Level API (L)
- `L.place(pid, x, y)` — stamp prefab with top-left at (x,y). Rows above a prop's solid base go to the
  Overhead layer automatically (drawn over characters); buildings are fully solid.
- `L.place_b(pid, x, ybottom)` — same, aligned by bottom row.
- `L.put(layer, x, y, img16, solid=False)` — raw 16x16 tile ("Decals" for flat ground details).
- `L.extra_solid.add((x,y))` — invisible blocker. `L.marker(name, x, y, **data)` — Godot Marker2D
  (use for NPC spots, interactables, secrets: e.g. `L.marker("secret", 152, 3, id="S6")`).
- `lib.add_img(pid, PIL_image, category, solid, overhead_rows, doors)` / `lib.add_rect(pid, sheet, x, y, w, h, ...)`
  — register a new prefab (e.g. something cataloged badly, or a composite you built).
- `L.kind[y][x]`, `L.inb(x,y)`, `L.cells[layer]` (dict of placed cells).

### Helpers
- `dress.can_place / try_place / scatter / place_b / rect_outline` — collision-aware placement that keeps
  props off solid ground and off each other (`pad` = empty ring around each object; `reserved` = cells
  to keep clear, e.g. paths).
- `synth.paint_fence(L, cells, style)` with styles `white` (race rail), `pipe` (creek railing), `chain`
  (chain-link), `iron` (wrought iron), `picket`, `wood`. Cells can be any path incl. diagonals;
  `synth.ellipse_cells(cx, cy, rx, ry)`, `synth.ellipse_fill(...)`.
- `synth.bunting(L, x0, y, x1)`, `synth.bulb_string(...)`, `synth.big_top(w,h)` (image),
  `synth.grandstand(lib, seat_pid, bays, roof_rows)` (image), `synth.gate_arch(span)` (image: brick
  pillars + pennant arch), `synth.brick_pillar(w,h)`, `synth.smokestack(h)`, `synth.parapet_h/v`,
  `synth.rail_track_h`. Register images with `lib.add_img(...)` then `L.place(...)`.
- `buildings.flat_roof(w, d, style)`, `buildings.stack(...)`, `buildings.building(...)` — compose
  buildings from catalog facade modules + synthesized flat roofs (see buildings.py docstring).

### Collision rules (user requirement)
Grass, streets, sidewalks, paths: walkable. Buildings, walls, fences, trunks, statues, stones, booths:
solid. Keep every path, gate and stair 2+ tiles clear. Tall tops (canopies, lamp heads, arch tops,
steeples) must be overhead and non-solid.

## Check your work (mandatory, iterate until it looks shippable)
```
export WB_OUT=<your scratch dir>
python "F:/pawn's-journey/Tools/world_builder/run_region.py" <your_district> x0 y0 x1 y1 "$WB_OUT/<name>"
```
Open both PNGs with Read. `_debug` shows solid collision in red and chunk seams in yellow. Look
critically, like an art director: composition, density, variety, era fit, readability of the
landmark, paths clear, nothing floating/clipped/overlapping, no prop on water or a wall. Iterate at
least 3 times. Deterministic randomness only (fixed seeds).

Final message: what you built, where the key features/markers are, and any asset gaps you hit.
