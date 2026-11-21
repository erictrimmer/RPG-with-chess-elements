"""Downtown Yorktowne (1960s York, PA) - level 1.

Design source: design/downtown_brief.md (art director), base grid design/brief_grid.json.
Run:  python build_downtown.py            -> preview PNGs only
      python build_downtown.py --godot    -> also export to res://World/Downtown and build scenes
"""
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decals as DC  # noqa: E402
import terrain as TR  # noqa: E402
from level import Level, PrefabLib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 160, 128
OUT_PREVIEW = os.environ.get("WB_PREVIEW", os.path.join(HERE, "_preview"))

GRID_KIND = {
    "=": "road", "x": "road", "k": "road",
    ".": "sidewalk",
    '"': "grass", "+": "grass", "T": "grass", "f": "grass",
    "a": "plaza", "p": "plaza_grey",
    "g": "dirt", "m": "dirt", "o": "dirt",
    "H": "cobble",
}

# street table (brief 3.1): (name, full rect, road rect) inclusive x0,x1,y0,y1
STREETS_H = [  # horizontal: road rows
    ("market", (0, 159, 78, 87), (0, 159, 80, 85)),
    ("philadelphia", (54, 159, 60, 67), (56, 159, 62, 65)),
    ("king", (38, 159, 104, 111), (42, 159, 106, 109)),
    ("parkway", (38, 159, 24, 31), (42, 159, 26, 29)),
]
STREETS_V = [
    ("george", (104, 113, 24, 123), (106, 111, 26, 123)),
    ("water", (54, 61, 46, 123), (56, 59, 48, 123)),
    ("beaver", (80, 87, 60, 123), (82, 85, 62, 123)),  # ends at the Market House (T at Philadelphia)
    ("duke", (132, 139, 46, 123), (134, 137, 48, 123)),
]


def build_terrain(L):
    grid = json.load(open(os.path.join(HERE, "design", "brief_grid.json")))
    for y in range(H):
        row = grid[y]
        for x in range(W):
            c = row[x]
            L.kind[y][x] = GRID_KIND.get(c, "grass" if not c.isupper() else "sidewalk")
    # building footprints: downtown blocks sit on pavement, outer districts on lawn
    for y in range(H):
        for x in range(W):
            c = grid[y][x]
            if c in "RE GXVLD".replace(" ", "") or (c == "#" and x < 40):
                L.kind[y][x] = "grass"
    # cemetery + hilltop: lawn, gravel roads come from 'g'
    # ---- streets: sidewalks first, then roads on top so intersections are clean
    for _, (x0, x1, y0, y1), _r in STREETS_H + STREETS_V:
        L.fill("sidewalk", x0, y0, x1, y1)
    for _, _f, (x0, x1, y0, y1) in STREETS_H + STREETS_V:
        L.fill("road", x0, y0, x1, y1)
    # creek-side walks
    L.fill("sidewalk", 38, 34, 155, 35)       # outer creek walk (north)
    L.fill("sidewalk", 54, 46, 155, 47)       # inner creek walk (south)
    L.fill("sidewalk", 54, 46, 55, 123)       # inner creek walk (west of Water St)
    L.fill("dirt", 38, 22, 39, 123)           # west bank gravel path
    L.fill("sidewalk", 40, 22, 41, 123)       # levee top
    for _, _f, (x0, x1, y0, y1) in STREETS_H:  # roads cross the levee path
        L.fill("road", max(x0, 38), y0, x1, y1) if x0 <= 42 else None
    L.fill("cobble", 54, 122, 155, 123)       # rail-side lane
    L.fill("plaza", 114, 122, 131, 123)       # depot platform
    L.fill("cobble", 0, 124, 159, 127)        # rail bed


def build_creek(L):
    L.wall_style[0] = 2     # walls below street level: concrete
    # water (sunken, e=-1): horizontal arm incl. its 2 wall-face rows, vertical arm
    for (x0, x1, y0, y1) in [(44, 159, 36, 43), (44, 51, 36, 127)]:
        L.fill("water", x0, y0, x1, y1)
        L.set_elev(x0, y0, x1, y1, -1)
    # coping lips (street level, solid concrete wall tops)
    for (x0, x1, y0, y1) in [(42, 43, 36, 127), (52, 53, 44, 127), (52, 159, 44, 45)]:
        L.fill("lip", x0, y0, x1, y1)
    L.fill("lip", 42, 36, 43, 37)
    # bridges: decks at street level over the channel
    def deck(x0, x1, y0, y1, kinds):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                L.set_elev(x, y, x, y, 0)
                L.kind[y][x] = kinds(x, y)
    # Market St bridge (x=42..53, y=78..87): sidewalks 78..79 / 86..87, road 80..85
    deck(42, 53, 78, 87, lambda x, y: "road" if 80 <= y <= 85 else "sidewalk")
    # King St bridge (x=42..53, y=104..111)
    deck(42, 53, 104, 111, lambda x, y: "road" if 106 <= y <= 109 else "sidewalk")
    # Philadelphia St footbridge (y=62..65): steel deck
    deck(42, 53, 62, 65, lambda x, y: "sidewalk")
    # George St bridge over the horizontal arm (x=104..113, y=36..45)
    deck(104, 113, 36, 45, lambda x, y: "road" if 106 <= x <= 111 else "sidewalk")
    # service stairs down to the shoal (S1) through the west lip
    for y in (92, 93):
        for x in (42, 43):
            L.stairs.add((x, y))
    # gravel shoal (secret S1): stays sunken, walkable
    L.fill("shoal", 44, 90, 46, 99)
    # rail trestle over the creek: keep water visible, rails drawn as objects later


def build_hills(L):
    L.wall_style[1] = 0     # rocky cliff
    L.rim_style[1] = 0
    # cemetery upper terrace + hilltop overlook (e=1); cliff faces auto at y=10..11
    L.set_elev(66, 0, 159, 9, 1)
    for x0, x1 in [(70, 73), (106, 111), (126, 129), (146, 147)]:
        for y in (10, 11):
            for x in range(x0, x1 + 1):
                L.walk_override.add((x, y))
                L.stairs.add((x, y))
        for x in range(x0, x1 + 1):   # stair top cells must be walkable too
            L.walk_override.add((x, 9))
            L.walk_override.add((x, 8))


def paint_roads(L):
    # dashed centre lines; skip intersections
    v_spans = [(f[0], f[1]) for _, f, _r in STREETS_V]
    h_spans = [(f[2], f[3]) for _, f, _r in STREETS_H]
    for name, full, (x0, x1, y0, y1) in STREETS_H:
        DC.paint_road_h(L, x0, x1, y0, y1, skip=[(a - 1, b + 1) for a, b in v_spans])
    for name, full, (x0, x1, y0, y1) in STREETS_V:
        DC.paint_road_v(L, x0, x1, y0, y1, skip=[(a - 1, b + 1) for a, b in h_spans] + [(36, 45)])
    # two-line crosswalks at every intersection, 1 tile outside the junction box
    for _, vf, (vx0, vx1, vy0, vy1) in STREETS_V:
        for _, hf, (hx0, hx1, hy0, hy1) in STREETS_H:
            if not (hx0 <= vx0 and vx1 <= hx1 and vy0 <= hy0 and hy1 <= vy1):
                continue
            # across the vertical road, north and south of the junction
            for yc in (hf[2] - 1, hf[3] + 1):
                if vy0 <= yc - 1 and yc + 1 <= vy1:
                    pass
            if vy0 < hf[2]:   # vertical road continues north of the junction
                DC.crosswalk_across_v_road(L, vx0, vx1, hf[2], hf[2] + 1)
            if vy1 > hf[3]:
                DC.crosswalk_across_v_road(L, vx0, vx1, hf[3] - 1, hf[3])
            if hx0 < vf[0]:
                DC.crosswalk_across_h_road(L, hy0, hy1, vf[0], vf[0] + 1)
            if hx1 > vf[1]:
                DC.crosswalk_across_h_road(L, hy0, hy1, vf[1] - 1, vf[1])


DISTRICTS = ["creek", "downtown", "rowhouses", "north", "cemetery", "fair", "park"]


def build_base():
    lib = PrefabLib()
    lib.load_catalogs(os.path.join(HERE, "catalog"))
    import synth
    synth.register_all(lib)
    L = Level(W, H, lib)
    build_terrain(L)
    build_creek(L)
    build_hills(L)
    return L, lib


def run_districts(L, lib, only=None):
    """Districts may edit terrain (L.fill / set_kind) in build_ground(), then place props in build()."""
    import importlib
    mods = []
    for name in DISTRICTS:
        if only and name not in only:
            continue
        path = os.path.join(HERE, "districts", f"{name}.py")
        if not os.path.exists(path):
            continue
        mods.append(importlib.import_module(f"districts.{name}"))
    for m in mods:
        if hasattr(m, "build_ground"):
            m.build_ground(L, lib)
    L.bake_ground()
    paint_roads(L)
    for m in mods:
        m.build(L, lib)
    return mods


def main():
    L, lib = build_base()
    run_districts(L, lib)
    os.makedirs(OUT_PREVIEW, exist_ok=True)
    L.render(os.path.join(OUT_PREVIEW, "downtown_full.png"), scale=0.5)
    L.render(os.path.join(OUT_PREVIEW, "downtown_debug.png"), scale=0.5, debug=True)
    for (n, r) in [("square", (88, 60, 136, 104)), ("creek", (30, 30, 78, 72)), ("cemetery", (60, 0, 120, 34))]:
        L.render(os.path.join(OUT_PREVIEW, f"detail_{n}.png"), scale=1, region=r)
    if "--godot" in sys.argv:
        from pipeline import to_godot
        to_godot(L, "World/Downtown", "downtown")
    return L


if __name__ == "__main__":
    main()
