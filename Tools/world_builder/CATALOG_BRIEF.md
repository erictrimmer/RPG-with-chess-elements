# Prefab Catalog Brief (for cataloging sub-agents)

Project: "Pawn's Journey", an Earthbound-inspired chess RPG in Godot 4.5. We are building a
**1960s downtown of "Yorktowne"** (a fictionalized York, Pennsylvania) from the LimeZu
**Modern Exteriors** 16x16 tileset. Characters are 16x32 (LimeZu Character Generator 2.0), 3/4 top-down view.

Your job: catalog usable **prefabs** (multi-tile objects: buildings, building modules, props,
trees, fences, signs, statues, vehicles...) from an assigned set of sheets, with exact tile rectangles.
A generator script will stamp these rectangles into Godot TileMapLayers, so coordinates must be exact.

## Source sheets
`F:/pawn's-journey/Assets/Modern Exteriors/16px/Tileset_<N>_MV.png` — each 256x256 px = 16x16 tiles.
Tile coordinates are (x = column 0..15, y = row 0..15). Background is transparent.

## Tools (use them, don't guess coordinates)
Run with Bash from any directory; set `WB_OUT` to your own scratch folder so images don't collide:
```
export WB_OUT="<your scratch dir>"
python "F:/pawn's-journey/Tools/world_builder/sheet_tool.py" grid  Tileset_44_MV.png      # 3x enlarged sheet with numbered tile grid
python "F:/pawn's-journey/Tools/world_builder/sheet_tool.py" comps Tileset_44_MV.png      # auto-detect separated objects -> tile rects + overlay image
python "F:/pawn's-journey/Tools/world_builder/sheet_tool.py" crop  Tileset_44_MV.png 0 0 6 7   # zoomed crop of x y w h (tile units), grid labels are absolute
python "F:/pawn's-journey/Tools/world_builder/sheet_tool.py" preview <your catalog.json>   # renders every prefab you cataloged (red = solid cells, blue = overhead rows)
```
Each command prints the path of the PNG it wrote; open it with the Read tool to look at it.
`comps` merges objects that touch, so tightly packed sheets come back as one big region — then use
`grid` + `crop` to find the true edges. Always `crop` a candidate rect to confirm nothing is cut off
and nothing from a neighbouring object bleeds in. **Finish by running `preview` on your JSON and
checking every entry visually; fix any rect that clips or includes junk.**

## Output
Write ONE JSON file to `F:/pawn's-journey/Tools/world_builder/catalog/<group>.json`:
```json
{
  "group": "<group name>",
  "sheets_reviewed": ["Tileset_44_MV.png", "..."],
  "sheet_notes": {"Tileset_44_MV.png": "one line: what the sheet holds, how its modules join"},
  "prefabs": [
    {
      "id": "unique_snake_case (prefix with your group short code, e.g. sf_)",
      "sheet": "Tileset_44_MV.png",
      "x": 0, "y": 0, "w": 6, "h": 7,
      "category": "building | building_module | roof_module | prop | tree | hedge | fence | wall | sign | vehicle | statue | grave | decal | ground | water | bridge | other",
      "desc": "concrete visual description: shape, colours, materials, what's on it",
      "era1960": "good | ok | avoid",
      "solid": "all"  OR  "bottom:2"  OR  [[cx,cy], ...],
      "overhead_rows": 0,
      "doors": [[cx, cy]],
      "needs_ground": true,
      "york_use": "where this fits in a 1960s York downtown / cemetery / fairground / creek",
      "notes": "anything needed to use it correctly (pairs with X, repeat middle column to widen, etc.)"
    }
  ]
}
```
Field rules:
- Coordinates in x/y/w/h are **absolute tile coords on the sheet**. `solid`, `doors` use coords **relative to the prefab** (0,0 = its top-left tile).
- `solid`: which cells block the player. Buildings → usually `"all"`. Trees → the trunk/base cells only. Lamp posts, signs, hydrants → base cell only. Fences → the fence line cells. Flat decals (manhole, paint, flower beds you can walk on) → `[]`.
- `overhead_rows`: number of top rows that should be drawn **above** the player because the player can walk behind them (tree canopies, tops of lamp posts, tall signs, arch tops). Buildings: 0 (whole building is solid). Overhead rows must not be solid.
- `doors`: door tiles on building fronts (empty list if none).
- `needs_ground`: true if transparent pixels inside the rect need grass/pavement under them (almost all props).
- `era1960`: "avoid" for anything clearly post-1980 (glass office towers, EV chargers, smartphones, modern SUVs, satellite dishes, solar panels, modern signage/graffiti, modern playground plastic). "ok" for timeless items. "good" for things that read strongly 1950s/60s small-town America (brick, awnings, wooden poles, neon-ish shop signs, classic cars, phone booths, mailboxes).
- Modular buildings: if a sheet holds building **pieces** (left wall / middle repeatable section / right wall / roof sections), catalog each piece as `building_module` or `roof_module` and explain in `notes` how they assemble (which piece goes above which, which column repeats). If a complete building is assembled on the sheet, also catalog it whole.
- Skip pure clutter of no use (UI icons, tiny sparkles) but do catalog small props — streets need lots of small dressing.
- Quality over quantity, but be thorough: every useful complete object on your sheets should appear once. Typical: 10–40 prefabs per sheet group.

## Don't
- Don't edit any file other than your own catalog JSON. Don't write into the Godot project folders.
- Don't invent coordinates you didn't verify with `crop`/`preview`.

Return (as your final message) a short summary: count of prefabs, the 5–10 most useful ones for a 1960s York downtown, and any sheet that is unusable or tricky.
