"""Level model + export for the Yorktowne world builder.

Layers (draw order, Godot z_index):
  Ground   (-4)  baked terrain: grass, roads, sidewalks, water, cliffs. Water/walls are solid.
  Decals   (-3)  flat paint & ground clutter: road lines, crosswalks, flower patches, manholes. Never solid.
  Objects  (-2)  buildings and the lower (solid) part of props. Drawn BELOW characters.
  Overhead (+5)  canopies, lamp tops, sign tops: drawn ABOVE characters, never solid.
Characters live between (z 0) in a y-sorted node.
"""
import hashlib
import json
import math
import os

from PIL import Image, ImageDraw

import terrain as TR

T = 16
HERE = os.path.dirname(os.path.abspath(__file__))

FULL_COLLISION_CATS = {"building", "building_module", "roof_module", "wall", "fence", "water", "bridge_wall"}
TALL_PROP_CATS = {"prop", "tree", "sign", "statue", "grave", "vehicle", "hedge", "other"}


# --------------------------------------------------------------------------- prefabs
class Prefab:
    def __init__(self, pid, img, category="prop", solid="all", overhead_rows=0, doors=None, meta=None):
        self.id = pid
        self.img = img
        self.w = img.size[0] // T
        self.h = img.size[1] // T
        self.category = category
        self.doors = doors or []
        self.meta = meta or {}
        self.solid = self._solid_set(solid)
        self.overhead_rows = overhead_rows
        if self.category in TALL_PROP_CATS and self.overhead_rows == 0 and self.solid:
            top_solid = min(y for _, y in self.solid)
            self.overhead_rows = top_solid
        # overhead rows can never be solid
        self.solid = {(x, y) for (x, y) in self.solid if y >= self.overhead_rows}

    def _solid_set(self, s):
        if s == "all":
            return {(x, y) for x in range(self.w) for y in range(self.h)}
        if isinstance(s, str) and s.startswith("bottom:"):
            n = int(s.split(":")[1])
            return {(x, y) for x in range(self.w) for y in range(self.h - n, self.h)}
        if s in (None, "none", ""):
            return set()
        return {tuple(c) for c in s}

    def tile_img(self, rx, ry):
        return self.img.crop((rx * T, ry * T, rx * T + T, ry * T + T))

    def tile_empty(self, rx, ry):
        return self.tile_img(rx, ry).getchannel("A").getbbox() is None


class PrefabLib:
    def __init__(self):
        self.items = {}

    def load_catalogs(self, folder):
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith(".json"):
                continue
            data = json.load(open(os.path.join(folder, fn)))
            for p in data.get("prefabs", []):
                try:
                    if p.get("recipe") and p.get("parts"):
                        img = Image.new("RGBA", (p["assembled_w"] * T, p["assembled_h"] * T))
                        for part in p["parts"]:
                            img.alpha_composite(TR.tile(part["sheet"], part["x"], part["y"], part["w"], part["h"]),
                                                (part["dx"] * T, part["dy"] * T))
                        self.items[p["id"]] = Prefab(p["id"], img, p.get("category", "building"), p.get("solid", "all"),
                                                     p.get("overhead_rows", 0), p.get("doors", []), p)
                        continue
                    img = TR.tile(p["sheet"], p["x"], p["y"], p["w"], p["h"]).copy()
                    for (sx, sy) in p.get("skip_cells", []):
                        img.paste((0, 0, 0, 0), (sx * T, sy * T, sx * T + T, sy * T + T))
                except Exception as ex:  # noqa
                    print("skip", p.get("id"), ex)
                    continue
                self.items[p["id"]] = Prefab(p["id"], img, p.get("category", "prop"), p.get("solid", "all"),
                                             p.get("overhead_rows", 0), p.get("doors", []), p)

    def add_rect(self, pid, sheet, x, y, w, h, category="prop", solid="all", overhead_rows=0, doors=None):
        self.items[pid] = Prefab(pid, TR.tile(sheet, x, y, w, h), category, solid, overhead_rows, doors)
        return self.items[pid]

    def add_img(self, pid, img, category="prop", solid="all", overhead_rows=0, doors=None):
        self.items[pid] = Prefab(pid, img, category, solid, overhead_rows, doors)
        return self.items[pid]

    def __getitem__(self, k):
        return self.items[k]

    def __contains__(self, k):
        return k in self.items


# --------------------------------------------------------------------------- level
class Level:
    LAYERS = ["Ground", "Decals", "Objects", "Overhead"]

    def __init__(self, w, h, lib, default="grass"):
        self.w, self.h = w, h
        self.lib = lib
        self.kind = [[default] * w for _ in range(h)]
        self.elev = [[0] * w for _ in range(h)]
        self.wall_style = {}  # elevation level -> A4 block index for the wall face (0 rock, 1 dirt, 2 concrete, 3 concrete tiles)
        self.rim_style = {}   # elevation level -> A4 block index for the plateau top rim (0 grass/dirt rim)
        self.walk_override = set()  # cells forced walkable (stairs over walls, ramps)
        self.stairs = set()         # cells drawn as stone steps (also walkable)
        # per layer: (x,y) -> list of entries  entry = (img, solid, colmode, key)
        self.cells = {L: {} for L in self.LAYERS}
        self.extra_solid = set()   # invisible blockers (map edge, etc.)
        self.markers = []          # (name, x, y, data) spawn points, doors, triggers for Godot
        self.placed = []

    # ---- terrain painting
    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def fill(self, kind, x0, y0, x1, y1):
        """inclusive rect"""
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.kind[y][x] = kind

    def set_kind(self, x, y, kind):
        if self.inb(x, y):
            self.kind[y][x] = kind

    def kind_at(self, x, y):
        if not self.inb(x, y):
            x = min(max(x, 0), self.w - 1)
            y = min(max(y, 0), self.h - 1)
        return self.kind[y][x]

    def set_elev(self, x0, y0, x1, y1, e):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.elev[y][x] = e

    def elev_at(self, x, y):
        if not self.inb(x, y):
            x = min(max(x, 0), self.w - 1)
            y = min(max(y, 0), self.h - 1)
        return self.elev[y][x]

    # ---- layer writes
    def put(self, layer, x, y, img, solid=False, colmode="full", key=None):
        if not self.inb(x, y):
            return
        self.cells[layer].setdefault((x, y), []).append((img, solid, colmode, key))

    def clear_cell(self, layer, x, y):
        self.cells[layer].pop((x, y), None)

    def place(self, pid, x, y, solid_override=None, layer_override=None):
        """Stamp prefab with its top-left at tile (x,y)."""
        p = self.lib[pid]
        colmode = "full" if p.category in FULL_COLLISION_CATS else ("tree" if p.category == "tree" else "alpha")
        for ry in range(p.h):
            for rx in range(p.w):
                if p.tile_empty(rx, ry):
                    continue
                tx, ty = x + rx, y + ry
                if layer_override:
                    layer = layer_override
                    solid = False if layer_override in ("Decals", "Overhead") else (rx, ry) in p.solid
                elif ry < p.overhead_rows:
                    layer, solid = "Overhead", False
                elif not p.solid:
                    layer, solid = ("Decals" if p.category in ("decal", "ground") else "Objects"), False
                else:
                    layer, solid = "Objects", (rx, ry) in p.solid
                if solid_override is not None and layer == "Objects":
                    solid = solid_override
                self.put(layer, tx, ty, p.tile_img(rx, ry), solid, colmode, (pid, rx, ry))
        for d in p.doors:
            self.markers.append(("door", x + d[0], y + d[1], {"prefab": pid}))
        self.placed.append((pid, x, y))
        return p

    def place_b(self, pid, x, ybottom, **kw):
        """Stamp prefab so its bottom row sits on tile row ybottom."""
        p = self.lib[pid]
        return self.place(pid, x, ybottom - p.h + 1, **kw)

    def occupied(self, x0, y0, w, h, layers=("Objects",)):
        for L in layers:
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    if (x, y) in self.cells[L]:
                        return True
        return False

    def block(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.extra_solid.add((x, y))

    def marker(self, name, x, y, **data):
        self.markers.append((name, x, y, data))

    # ---- ground baking
    def bake_ground(self):
        g = self.cells["Ground"]
        for y in range(self.h):
            for x in range(self.w):
                g.pop((x, y), None)
                img, solid = self._ground_tile(x, y)
                self.put("Ground", x, y, img, solid, "full")

    def _wall_info(self, x, y):
        """If (x,y) is a wall face below higher ground, return (row 0|1, higher elev) else None."""
        e = self.elev_at(x, y)
        if y - 1 >= 0 and self.elev_at(x, y - 1) > e:
            return 0, self.elev_at(x, y - 1)
        if y - 2 >= 0 and self.elev_at(x, y - 2) > e and self.elev_at(x, y - 1) <= e:
            # second wall row only if the row above is the first wall row
            if self.elev_at(x, y - 2) > self.elev_at(x, y - 1):
                return 1, self.elev_at(x, y - 2)
        return None

    def _ground_tile(self, x, y):
        if (x, y) in self.stairs:
            return TR.stair_tile(x, y, (x - 1, y) not in self.stairs, (x + 1, y) not in self.stairs), False
        wi = self._wall_info(x, y)
        if wi:
            row, hi = wi
            style = self.wall_style.get(hi, 0)

            def is_wall(xx):
                w2 = self._wall_info(xx, y)
                return bool(w2) and w2[0] == row
            img = TR.a4_wall(TR.A4, style, row, is_wall(x - 1), is_wall(x + 1))
            return img, (x, y) not in self.walk_override
        k = self.kind[y][x]
        e = self.elev[y][x]
        if e > 0 and any(self.elev_at(x + dx, y + dy) < e for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            # plateau rim (A4 top autotile), solid where you could step off the edge
            bx = self.rim_style.get(e, 0)
            blk = TR.sheet(TR.A4).crop((bx * 32, 0, bx * 32 + 32, 48))
            img = TR.regrass(TR.autotile(blk, lambda dx, dy: self.elev_at(x + dx, y + dy) >= e), x, y, ("a4", bx), blk)
            edge = any(self.elev_at(x + dx, y + dy) < e for dx, dy in ((0, -1), (-1, 0), (1, 0), (-1, -1), (1, -1)))
            return img, edge and (x, y) not in self.walk_override
        same_kind =lambda dx, dy: self.kind_at(x + dx, y + dy) == k and self.elev_at(x + dx, y + dy) == e
        if k == "grass":
            img = TR.grass_tile(x, y)
        elif k == "sidewalk":
            img = TR.sidewalk_tile(x, y, self._kind_for_curbs)
        elif k == "road":
            img = TR.road_tile(x, y, self._kind_for_curbs)
        elif k == "water":
            img = TR.water_tile(x, y)
            return img, True
        elif k == "lip":
            blk = TR.sheet(TR.A4).crop((2 * 32, 0, 2 * 32 + 32, 48))
            img = TR.coping(TR.autotile(blk, lambda dx, dy: self.kind_at(x + dx, y + dy) == "lip"))
            return img, (x, y) not in self.walk_override
        elif k == "shoal":
            img = TR.shoal_tile(x, y)
        else:
            style, params = TR.TERRAIN[k]
            if style == "a2":
                sheet, bx, by = params
                base = TR.grass_tile(x, y)
                blk = TR.a2_block(sheet, bx, by)
                top = TR.regrass(TR.autotile(blk, same_kind), x, y, (sheet, bx, by), blk)
                base = base.copy()
                base.alpha_composite(top)
                img = base
                if k == "pond":
                    return img, True
            elif style == "a4top":
                sheet, bx = params
                blk = TR.sheet(sheet).crop((bx * 32, 0, bx * 32 + 32, 48))
                same_hill = lambda dx, dy: self.elev_at(x + dx, y + dy) == e
                img = TR.regrass(TR.autotile(blk, same_hill), x, y, (sheet, "a4", bx), blk)
            else:
                img = TR.grass_tile(x, y)
        # south bank lip: land directly south of lower ground (the far side of a channel)
        if y - 1 >= 0 and self.elev_at(x, y - 1) < e and k != "water":
            img = img.copy()
            for xx in range(16):
                img.putpixel((xx, 0), TR.OUTLINE)
                img.putpixel((xx, 1), (0x8E, 0x8C, 0x99, 255))
                img.putpixel((xx, 2), (0xB4, 0xB2, 0xBC, 255))
                img.putpixel((xx, 3), (0x8E, 0x8C, 0x99, 255))
            return img, False
        return img, False

    def _kind_for_curbs(self, x, y):
        k = self.kind_at(x, y)
        if self._wall_info(x, y) or k == "water":
            return "water"
        return k

    # ---- export
    def compose_layer(self, layer):
        """Flatten each cell's stacked entries into one (img, solid, colmode, key) entry."""
        out = {}
        for (x, y), entries in self.cells[layer].items():
            if len(entries) == 1:
                out[(x, y)] = entries[0]
            else:
                img = Image.new("RGBA", (T, T))
                solid = False
                modes = []
                for (im, s, cm, _k) in entries:
                    img.alpha_composite(im)
                    solid = solid or s
                    if s:
                        modes.append(cm)
                cm = "full" if "full" in modes else (modes[0] if modes else "full")
                out[(x, y)] = (img, solid, cm, None)
        return out

    def export(self, out_dir, res_dir, name="downtown", chunk=32):
        """Write atlas PNGs + level JSON for the Godot builder. res_dir is the res:// path of out_dir."""
        os.makedirs(out_dir, exist_ok=True)
        layers = {L: self.compose_layer(L) for L in self.LAYERS}
        for (x, y) in self.extra_solid:
            # invisible blocker: transparent tile on Objects with full collision
            if (x, y) not in layers["Objects"]:
                layers["Objects"][(x, y)] = (Image.new("RGBA", (T, T)), True, "full", ("__blocker__", 0, 0))
            else:
                im, s, cm, k = layers["Objects"][(x, y)]
                layers["Objects"][(x, y)] = (im, True, "full", k)

        # ---- source 0: terrain atlas (deduped), source 1: objects atlas (prefab blocks + composites)
        terrain_tiles, terrain_index = [], {}
        obj_blocks = {}      # pid -> (bx, by) origin in objects atlas (tile units)
        obj_misc, obj_misc_index = [], {}

        def tkey(img, solid, cm):
            return hashlib.md5(img.tobytes() + bytes([solid]) + cm.encode()).hexdigest()

        cell_refs = {L: {} for L in self.LAYERS}
        for L in self.LAYERS:
            for (x, y), (img, solid, cm, key) in layers[L].items():
                if L == "Ground":
                    k = tkey(img, solid, cm)
                    if k not in terrain_index:
                        terrain_index[k] = len(terrain_tiles)
                        terrain_tiles.append((img, solid, cm))
                    cell_refs[L][(x, y)] = (0, terrain_index[k])
                else:
                    if key is not None and key[0] != "__blocker__" and self._entry_matches_prefab(img, solid, key, L):
                        cell_refs[L][(x, y)] = (1, ("pf", key))
                        obj_blocks.setdefault(key[0], None)
                    else:
                        k = tkey(img, solid, cm)
                        if k not in obj_misc_index:
                            obj_misc_index[k] = len(obj_misc)
                            obj_misc.append((img, solid, cm))
                        cell_refs[L][(x, y)] = (1, ("misc", obj_misc_index[k]))

        # pack terrain atlas
        tcols = 32
        trows = max(1, math.ceil(len(terrain_tiles) / tcols))
        tatlas = Image.new("RGBA", (tcols * T, trows * T))
        tmeta = []
        for i, (img, solid, cm) in enumerate(terrain_tiles):
            ax, ay = i % tcols, i // tcols
            tatlas.paste(img, (ax * T, ay * T))
            tmeta.append({"a": [ax, ay], "col": self._col_rect(img, cm) if solid else None})

        # pack objects atlas: shelf-pack prefab blocks
        ocols = 64
        pids = sorted(obj_blocks.keys(), key=lambda p: (-self.lib[p].h, p))
        shelf_x, shelf_y, shelf_h = 0, 0, 0
        for pid in pids:
            p = self.lib[pid]
            if shelf_x + p.w > ocols:
                shelf_x, shelf_y, shelf_h = 0, shelf_y + shelf_h, 0
            obj_blocks[pid] = (shelf_x, shelf_y)
            shelf_x += p.w
            shelf_h = max(shelf_h, p.h)
        misc_y0 = shelf_y + shelf_h + (1 if shelf_h else 0)
        orows = misc_y0 + max(1, math.ceil(len(obj_misc) / ocols))
        oatlas = Image.new("RGBA", (ocols * T, orows * T))
        ometa = {}
        # which prefab tiles are referenced as solid vs not: a prefab tile has ONE collision in the atlas
        for pid, (bx, by) in obj_blocks.items():
            p = self.lib[pid]
            oatlas.paste(p.img, (bx * T, by * T))
            cm = "full" if p.category in FULL_COLLISION_CATS else ("tree" if p.category == "tree" else "alpha")
            for ry in range(p.h):
                for rx in range(p.w):
                    if p.tile_empty(rx, ry):
                        continue
                    solid = (rx, ry) in p.solid
                    ometa[(bx + rx, by + ry)] = self._col_rect(p.tile_img(rx, ry), cm) if solid else None
        for i, (img, solid, cm) in enumerate(obj_misc):
            ax, ay = i % ocols, misc_y0 + i // ocols
            oatlas.paste(img, (ax * T, ay * T))
            ometa[(ax, ay)] = self._col_rect(img, cm) if solid else None

        tpng = os.path.join(out_dir, f"{name}_terrain.png")
        opng = os.path.join(out_dir, f"{name}_objects.png")
        tatlas.save(tpng)
        oatlas.save(opng)

        def resolve(ref):
            src, r = ref
            if src == 0:
                ax, ay = tmeta[r]["a"]
                return 0, ax, ay
            kind, v = r
            if kind == "pf":
                pid, rx, ry = v
                bx, by = obj_blocks[pid]
                return 1, bx + rx, by + ry
            return 1, v % ocols, misc_y0 + v // ocols

        spec = {
            "name": name, "tile_size": T, "width": self.w, "height": self.h, "chunk": chunk,
            "sources": [
                {"id": 0, "name": "terrain", "png": f"{res_dir}/{name}_terrain.png",
                 "tiles": [{"a": m["a"], "col": m["col"]} for m in tmeta]},
                {"id": 1, "name": "objects", "png": f"{res_dir}/{name}_objects.png",
                 "tiles": [{"a": [ax, ay], "col": c} for (ax, ay), c in sorted(ometa.items())]},
            ],
            "layers": [],
            "markers": [{"name": n, "x": x, "y": y, "data": d} for (n, x, y, d) in self.markers],
        }
        z = {"Ground": -4, "Decals": -3, "Objects": -2, "Overhead": 5}
        for L in self.LAYERS:
            cells = []
            for (x, y), ref in cell_refs[L].items():
                s, ax, ay = resolve(ref)
                cells.append([x, y, s, ax, ay])
            cells.sort()
            spec["layers"].append({"name": L, "z": z[L], "cells": cells})
        json.dump(spec, open(os.path.join(out_dir, f"{name}.json"), "w"))
        stats = {L: len(cell_refs[L]) for L in self.LAYERS}
        print(f"terrain tiles {len(terrain_tiles)} ({tatlas.size}), object atlas {oatlas.size}, prefabs {len(obj_blocks)}, misc {len(obj_misc)}; cells {stats}")
        return spec

    def _entry_matches_prefab(self, img, solid, key, layer):
        pid, rx, ry = key
        p = self.lib[pid]
        if solid != ((rx, ry) in p.solid):
            return False
        return img.tobytes() == p.tile_img(rx, ry).tobytes()

    @staticmethod
    def _col_rect(img, cm):
        if cm == "full":
            return [0, 0, 16, 16]
        bb = img.getchannel("A").getbbox()
        if not bb:
            return [0, 0, 16, 16]
        x0, y0, x1, y1 = bb
        if cm == "tree":
            cx = (x0 + x1) // 2
            return [max(0, cx - 5), 6, 10, 10]
        # alpha: trim a little so characters can tuck close to props
        w, h = x1 - x0, y1 - y0
        if w < 6:
            x0, w = max(0, x0 - (6 - w) // 2), 6
        if h < 6:
            y0, h = max(0, y1 - 6), 6
        return [x0, y0, min(w, 16 - x0), min(h, 16 - y0)]

    # ---- preview
    def render(self, path, scale=1, debug=False, region=None):
        x0, y0, x1, y1 = region or (0, 0, self.w, self.h)
        W, Hh = (x1 - x0) * T, (y1 - y0) * T
        img = Image.new("RGBA", (W, Hh), (0, 0, 0, 255))
        for L in self.LAYERS:
            comp = self.compose_layer(L)
            for (x, y), (im, solid, cm, key) in comp.items():
                if x0 <= x < x1 and y0 <= y < y1:
                    img.alpha_composite(im, ((x - x0) * T, (y - y0) * T))
        if debug:
            d = ImageDraw.Draw(img, "RGBA")
            for L in ("Ground", "Objects"):
                for (x, y), (im, solid, cm, key) in self.compose_layer(L).items():
                    if solid and x0 <= x < x1 and y0 <= y < y1:
                        r = self._col_rect(im, cm)
                        px, py = (x - x0) * T + r[0], (y - y0) * T + r[1]
                        d.rectangle([px, py, px + r[2] - 1, py + r[3] - 1], fill=(255, 0, 0, 70))
            for (x, y) in self.extra_solid:
                if x0 <= x < x1 and y0 <= y < y1:
                    d.rectangle([(x - x0) * T, (y - y0) * T, (x - x0) * T + 15, (y - y0) * T + 15], fill=(255, 0, 255, 60))
            for c in range(0, self.w, 32):
                d.line([((c - x0) * T, 0), ((c - x0) * T, Hh)], fill=(255, 255, 0, 120))
            for r in range(0, self.h, 32):
                d.line([(0, (r - y0) * T), (W, (r - y0) * T)], fill=(255, 255, 0, 120))
        if scale != 1:
            img = img.resize((int(W * scale), int(Hh * scale)), Image.NEAREST if scale >= 1 else Image.BOX)
        img.convert("RGB").save(path)
        return path
