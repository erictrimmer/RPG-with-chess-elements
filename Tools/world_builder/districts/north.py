"""North band (brief 3.1 Parkway Blvd + creek walk, 3.6 north band, secrets S2/S3/S6, dressing 5).

Owns three rects (nothing is placed outside them):
  A  grove + factory yard       x=38..63,  y=0..23
  B  hilltop houses + overlook  x=136..159, y=0..23
  C  Parkway Blvd + creek walk  x=38..159, y=24..35   (George St junction x=104..113 kept clear)
REGION is the bounding box of the three; the cemetery (x=64..135, y=0..23) belongs to another district.
"""
import random

from PIL import Image, ImageDraw, ImageEnhance

import dress
import synth

REGION = (38, 0, 159, 35)

T = 16
OUT = (0x3D, 0x3D, 0x52, 255)

AREA_A = (38, 0, 63, 23)
AREA_B = (136, 0, 159, 23)
AREA_C = (38, 24, 159, 35)


def _in(rect, x, y):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def _mine(x, y):
    return _in(AREA_A, x, y) or _in(AREA_B, x, y) or _in(AREA_C, x, y)


def _c(*rgb):
    return tuple(rgb) + (255,)


# =========================================================================== synthesized art
def _sawtooth_roof(w_px, h_px):
    """Corrugated blue-grey sawtooth roof seen from the south: rows of sloped sheets, each tooth
    topped by a strip of north-light glazing in shadow. Brick end parapets."""
    img = Image.new("RGBA", (w_px, h_px))
    d = ImageDraw.Draw(img)
    sheet_d, sheet_m, sheet_l = _c(0x5E, 0x66, 0x7A), _c(0x7C, 0x86, 0x9A), _c(0x9C, 0xA6, 0xB6)
    glass_d, glass_l = _c(0x3E, 0x4C, 0x60), _c(0x8C, 0xB0, 0xC4)
    rust = _c(0x9A, 0x6A, 0x50)
    tooth = 16
    for t0 in range(0, h_px, tooth):
        # glazing strip (in shadow) at the top of each tooth
        d.rectangle([0, t0, w_px - 1, t0 + 4], fill=glass_d)
        for x in range(3, w_px - 3, 8):
            d.line([x, t0 + 1, x + 4, t0 + 1], fill=glass_l)
            d.line([x + 6, t0, x + 6, t0 + 4], fill=OUT)
        d.line([0, t0 + 5, w_px - 1, t0 + 5], fill=_c(0xC8, 0xCE, 0xD8))  # ridge cap
        # sloped corrugated sheet: lighter near the ridge, darker toward the gutter
        for y in range(t0 + 6, min(h_px, t0 + tooth)):
            k = (y - t0 - 6) / 9.0
            base = sheet_l if k < 0.3 else (sheet_m if k < 0.75 else sheet_d)
            d.line([0, y, w_px - 1, y], fill=base)
        for x in range(1, w_px, 3):
            d.line([x, t0 + 6, x, min(h_px - 1, t0 + tooth - 2)], fill=sheet_d)
        d.line([0, min(h_px - 1, t0 + tooth - 1), w_px - 1, min(h_px - 1, t0 + tooth - 1)], fill=OUT)
        # a few rust streaks
        for i, x in enumerate(range(17, w_px - 10, 53)):
            xx = x + (t0 * 7) % 23
            d.line([xx, t0 + 8, xx, t0 + 13], fill=rust)
    # brick end parapets
    for x0 in (0, w_px - 6):
        d.rectangle([x0, 0, x0 + 5, h_px - 1], fill=synth.BRICK, outline=OUT)
        for y in range(3, h_px, 4):
            d.line([x0 + 1, y, x0 + 4, y], fill=synth.BRICK_D)
        d.line([x0 + 1, 0, x0 + 1, h_px - 1], fill=synth.BRICK_L)
    d.rectangle([0, 0, w_px - 1, h_px - 1], outline=OUT)
    return img


def _peppermint(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_c(0xF6, 0xF2, 0xEA), outline=OUT)
    for k in range(4):
        a0 = k * 90
        d.pieslice([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], a0, a0 + 45, fill=_c(0xD8, 0x3A, 0x48))
    d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=_c(0xD8, 0x3A, 0x48))


def _barbell(d, cx, cy):
    d.line([cx - 9, cy, cx + 9, cy], fill=_c(0x3A, 0x3A, 0x46), width=2)
    for sx in (-9, 9):
        d.rectangle([cx + sx - 2, cy - 5, cx + sx + 1, cy + 5], fill=_c(0x2A, 0x2A, 0x34))
        d.rectangle([cx + sx - 4 if sx < 0 else cx + sx + 2, cy - 3, cx + sx - 3 if sx < 0 else cx + sx + 3, cy + 3],
                    fill=_c(0x2A, 0x2A, 0x34))


def _factory_img(lib, w_tiles=18, h_tiles=12):
    """Candy & barbell works: sawtooth roof (5 rows) over a 2-storey brick mill whose facade is
    re-sliced from the storefront brick modules so the windows fall on an even rhythm."""
    W = w_tiles * T
    U = lib["sf_brick_upper_8windows"].img          # 112x64
    G = lib["sf_brick_ground_arched_door"].img      # 112x48
    G2 = lib["sf_brick_ground_smallpane_glassdoor"].img
    roll = lib["sf_garage_rollup"].img.crop((6, 92, 60, 127))   # 54x35 roll-up door with frame

    # ---- upper floor: L edge + 3 groups of 3 window bays separated by pilasters + R edge
    up = Image.new("RGBA", (W, 64))
    x = 0

    def put(src, box):
        nonlocal x
        piece = src.crop(box)
        up.alpha_composite(piece, (x, 0))
        x += piece.size[0]
    put(U, (0, 0, 6, 64))
    put(U, (26, 0, 34, 64))
    for g in range(3):
        for b in range(3):
            put(U, (6, 0, 32, 64))
        if g < 2:
            put(U, (104, 0, 112, 64))   # teal pilaster pair = right edge + left edge
            put(U, (0, 0, 6, 64))
    rest = W - 8 - x
    while rest > 0:
        n = min(8, rest)
        put(U, (26, 0, 26 + n, 64))
        rest -= n
    put(U, (104, 0, 112, 64))

    # ---- ground floor: tiled brick, office window + arched door on the west, three roll-up doors
    gr = Image.new("RGBA", (W, 48))
    fill = G.crop((53, 0, 60, 48))
    for xx in range(0, W, 7):
        gr.alpha_composite(fill, (xx, 0))
    gr.alpha_composite(G.crop((0, 0, 6, 48)), (0, 0))
    gr.alpha_composite(G.crop((106, 0, 112, 48)), (W - 6, 0))
    gr.alpha_composite(G2.crop((6, 0, 56, 48)), (6, 0))        # multi-pane office window
    gr.alpha_composite(G.crop((58, 0, 104, 48)), (58, 0))      # arched double door (office entry)
    doors_px = (110, 168, 226)
    for dx in doors_px:
        gr.alpha_composite(roll, (dx, 48 - 35))
        dd = ImageDraw.Draw(gr)
        dd.rectangle([dx + 2, 48 - 39, dx + 51, 48 - 37], fill=_c(0xF0, 0xC0, 0x3A))   # yellow hazard header
        for k in range(dx + 4, dx + 50, 6):
            dd.line([k, 48 - 39, k + 2, 48 - 37], fill=_c(0x2A, 0x2A, 0x34))

    # ---- roof + rooftop sign (peppermint roundel + barbell pictogram, no lettering)
    roof_h = (h_tiles * T) - 64 - 48
    roof = _sawtooth_roof(W, roof_h)
    img = Image.new("RGBA", (W, h_tiles * T))
    img.alpha_composite(roof, (0, 0))
    img.alpha_composite(up, (0, roof_h))
    img.alpha_composite(gr, (0, roof_h + 64))
    d = ImageDraw.Draw(img)
    sx0, sy0 = 116, roof_h - 30
    for px in (sx0 + 8, sx0 + 52):
        d.rectangle([px, sy0 + 20, px + 2, roof_h - 1], fill=_c(0x4A, 0x4A, 0x56), outline=OUT)
    d.rectangle([sx0, sy0, sx0 + 62, sy0 + 21], fill=_c(0xF6, 0xEC, 0xDC), outline=OUT)
    d.rectangle([sx0 + 2, sy0 + 2, sx0 + 60, sy0 + 4], fill=_c(0xE8, 0x7A, 0xA0))
    d.rectangle([sx0 + 2, sy0 + 17, sx0 + 60, sy0 + 19], fill=_c(0xE8, 0x7A, 0xA0))
    _peppermint(d, sx0 + 16, sy0 + 11, 6)
    _barbell(d, sx0 + 44, sy0 + 11)
    door_cells = [[4, h_tiles - 1], [5, h_tiles - 1]] + [[(dx + 27) // T, h_tiles - 1] for dx in doors_px]
    return img, door_cells


def _water_tank():
    """Wooden water tank with conical cap on a braced steel stand (3x5)."""
    img = Image.new("RGBA", (48, 80))
    d = ImageDraw.Draw(img)
    steel, steel_d = _c(0x5A, 0x5E, 0x6A), _c(0x3A, 0x3C, 0x48)
    d.ellipse([4, 74, 44, 79], fill=(0, 0, 0, 60))
    for lx in (7, 18, 29, 40):
        d.rectangle([lx - 1, 44, lx + 1, 77], fill=steel, outline=OUT)
    for (a, b) in ((7, 18), (18, 29), (29, 40)):
        d.line([a, 48, b, 74], fill=steel_d)
        d.line([b, 48, a, 74], fill=steel_d)
    d.line([6, 60, 41, 60], fill=steel)
    d.rectangle([3, 41, 44, 46], fill=_c(0x6A, 0x4E, 0x3A), outline=OUT)   # deck
    wood, wood_d, wood_l = _c(0x9E, 0x6C, 0x46), _c(0x76, 0x4E, 0x32), _c(0xBC, 0x8A, 0x5C)
    d.rectangle([6, 14, 41, 42], fill=wood, outline=OUT)
    for sx in range(9, 41, 4):
        d.line([sx, 15, sx, 41], fill=wood_d)
    d.rectangle([7, 15, 10, 41], fill=wood_l)
    d.rectangle([35, 15, 40, 41], fill=wood_d)
    for hy in (19, 28, 37):
        d.line([6, hy, 41, hy], fill=_c(0x34, 0x30, 0x36))
    d.polygon([(3, 16), (44, 16), (24, 2)], fill=_c(0x5E, 0x4C, 0x4A), outline=OUT)
    d.polygon([(24, 3), (24, 15), (43, 15)], fill=_c(0x4A, 0x3C, 0x3C))
    d.line([24, 0, 24, 3], fill=OUT)
    # ladder up the right side
    for ly in range(18, 77, 4):
        d.line([42, ly, 46, ly], fill=steel)
    d.line([42, 16, 42, 77], fill=steel_d)
    d.line([46, 16, 46, 77], fill=steel_d)
    return img


def _smoke():
    img = Image.new("RGBA", (48, 48))
    d = ImageDraw.Draw(img)
    puffs = [(20, 40, 7, 150), (27, 30, 9, 130), (17, 20, 10, 110), (30, 10, 11, 80)]
    for (cx, cy, r, a) in puffs:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0xB8, 0xB4, 0xB8, a))
        d.ellipse([cx - r + 2, cy - r + 1, cx + r - 4, cy + r - 5], fill=(0xD8, 0xD4, 0xD6, a))
    return img


def _coal_pile():
    img = Image.new("RGBA", (48, 32))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 22, 47, 31], fill=(0, 0, 0, 70))
    d.polygon([(2, 29), (10, 14), (20, 6), (30, 9), (40, 17), (46, 29)], fill=_c(0x2A, 0x28, 0x30), outline=OUT)
    rng = random.Random(7)
    for _ in range(70):
        x, y = rng.randint(6, 42), rng.randint(9, 28)
        if img.getpixel((x, y))[3]:
            d.point((x, y), fill=rng.choice([_c(0x4A, 0x48, 0x54), _c(0x6A, 0x68, 0x76), _c(0x1C, 0x1A, 0x22)]))
    return img


def _delivery_truck():
    """1960s cab-over delivery box truck, candy-works livery (pink stripe, peppermint roundel). 6x3, faces left."""
    img = Image.new("RGBA", (96, 48))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 40, 94, 47], fill=(0, 0, 0, 70))
    cream, cream_d = _c(0xF2, 0xEA, 0xD8), _c(0xC8, 0xBE, 0xAC)
    pink, pink_d = _c(0xE4, 0x70, 0x92), _c(0xB4, 0x4C, 0x6C)
    # box body
    d.rectangle([30, 4, 93, 37], fill=cream, outline=OUT)
    d.rectangle([31, 31, 92, 36], fill=cream_d)
    d.rectangle([31, 19, 92, 24], fill=pink)
    d.line([31, 25, 92, 25], fill=pink_d)
    _peppermint(d, 62, 12, 6)
    d.line([88, 6, 88, 36], fill=cream_d)
    # cab (rounded nose, two-tone)
    d.polygon([(4, 37), (4, 18), (8, 10), (30, 10), (30, 37)], fill=pink, outline=OUT)
    d.polygon([(6, 19), (9, 12), (22, 12), (22, 20)], fill=_c(0x8C, 0xB8, 0xC8), outline=OUT)
    d.line([10, 14, 14, 18], fill=_c(0xD8, 0xF0, 0xF8))
    d.rectangle([24, 13, 28, 20], fill=_c(0x8C, 0xB8, 0xC8), outline=OUT)
    d.rectangle([5, 24, 29, 37], fill=cream, outline=OUT)
    d.line([24, 22, 24, 36], fill=pink_d)
    d.rectangle([1, 32, 8, 36], fill=_c(0xC8, 0xCC, 0xD4), outline=OUT)        # chrome bumper
    d.ellipse([5, 26, 9, 30], fill=_c(0xFF, 0xF4, 0xC0), outline=OUT)          # headlight
    d.rectangle([30, 36, 93, 38], fill=_c(0x3A, 0x3A, 0x46))
    for wx in (18, 74):
        d.ellipse([wx - 7, 31, wx + 7, 45], fill=_c(0x22, 0x22, 0x2A), outline=OUT)
        d.ellipse([wx - 3, 35, wx + 3, 41], fill=_c(0xB8, 0xBC, 0xC4))
    return img


def _telescope():
    """Coin-operated binocular viewer on a post (1x2)."""
    img = Image.new("RGBA", (16, 32))
    d = ImageDraw.Draw(img)
    g, gd, gl = _c(0x4E, 0x7E, 0x6A), _c(0x34, 0x58, 0x4A), _c(0x78, 0xA8, 0x90)
    d.ellipse([3, 28, 13, 31], fill=(0, 0, 0, 70))
    d.rectangle([6, 14, 9, 29], fill=g, outline=OUT)
    d.rectangle([4, 27, 11, 30], fill=gd, outline=OUT)
    d.rectangle([2, 5, 13, 13], fill=g, outline=OUT)            # head
    d.rectangle([3, 6, 6, 8], fill=gl)
    d.rectangle([1, 2, 5, 6], fill=gd, outline=OUT)             # eyepieces
    d.rectangle([10, 2, 14, 6], fill=gd, outline=OUT)
    d.rectangle([6, 15, 9, 18], fill=_c(0xC8, 0xA4, 0x48), outline=OUT)   # coin box
    return img


def _wagon():
    img = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 12, 14, 15], fill=(0, 0, 0, 60))
    d.rectangle([2, 6, 12, 11], fill=_c(0xD0, 0x30, 0x2C), outline=OUT)
    d.line([3, 7, 11, 7], fill=_c(0xEC, 0x60, 0x50))
    for wx in (4, 10):
        d.ellipse([wx - 2, 10, wx + 2, 14], fill=_c(0x2A, 0x2A, 0x32))
    d.line([12, 8, 15, 4], fill=OUT)
    return img


def _weather_vane():
    """Rooster weather vane for a roof ridge (32x16, mast on the centre line)."""
    img = Image.new("RGBA", (32, 16))
    d = ImageDraw.Draw(img)
    iron = _c(0x2E, 0x30, 0x3A)
    d.line([16, 4, 16, 15], fill=iron)
    d.line([9, 9, 23, 9], fill=iron)
    d.polygon([(23, 7), (26, 9), (23, 11)], fill=iron)
    d.rectangle([8, 7, 10, 11], fill=iron)
    d.polygon([(13, 5), (18, 5), (20, 2), (19, 1), (17, 3), (14, 1), (12, 3)], fill=_c(0x3A, 0x34, 0x30))
    d.point((19, 2), fill=_c(0xC8, 0x30, 0x2C))
    d.rectangle([15, 14, 17, 15], fill=iron)
    return img


def _weeds():
    img = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(img)
    for (x, y) in ((3, 12), (5, 11), (7, 13), (11, 10), (12, 12)):
        d.line([x, y + 2, x - 1, y - 2], fill=_c(0x5E, 0x8A, 0x3C))
        d.line([x, y + 2, x + 2, y - 1], fill=_c(0x4A, 0x72, 0x32))
    return img


def _oil_stain(seed):
    img = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(img)
    r = random.Random(seed)
    for _ in range(3):
        cx, cy, rr = r.randint(4, 11), r.randint(4, 11), r.randint(2, 4)
        d.ellipse([cx - rr, cy - rr // 2 - 1, cx + rr, cy + rr // 2 + 1], fill=(0x30, 0x2C, 0x34, 70))
    return img


def _slate_house(lib, src):
    """Re-tint a clapboard house's roof toward Victorian slate blue-grey."""
    img = lib[src].img.copy()
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            if a and b > r + 25 and b > g:      # blue roof planks
                m = (r + g + b) // 3
                px[x, y] = (int(m * 0.55 + r * 0.45 * 0.9 + 6), int(m * 0.55 + g * 0.45 * 0.9 + 6),
                            int(m * 0.5 + b * 0.5 * 0.85), a)
    return img


def _register(lib):
    if "no_factory" in lib:
        return
    fimg, fdoors = _factory_img(lib)
    lib.add_img("no_factory", fimg, "building", "all", 0, fdoors)
    lib.add_img("no_water_tank", _water_tank(), "prop", [[0, 4], [1, 4], [2, 4]], 4)
    lib.add_img("no_smoke", _smoke(), "decal", [], 3)
    lib.add_img("no_coal_pile", _coal_pile(), "prop", [[0, 1], [1, 1], [2, 1]], 1)
    lib.add_img("no_truck", _delivery_truck(), "vehicle", [[x, y] for x in range(6) for y in (1, 2)], 1)
    lib.add_img("no_telescope", _telescope(), "prop", [[0, 1]], 1)
    lib.add_img("no_wagon", _wagon(), "prop", [[0, 0]], 0)
    # Victorian houses: top 3 rows (roof peak) overlap the cliff face -> overhead, never solid
    house_solid = [list(c) for c in lib["rr_house_gable_red"].solid]
    lib.add_img("no_house_slate", _slate_house(lib, "rr_house_gable_blue"), "building", house_solid, 3, [[2, 10]])
    mar = Image.new("RGBA", (8 * T, 13 * T))
    mar.alpha_composite(lib["rr_house_gable_maroon_rooftop"].img, (0, 0))
    mar.alpha_composite(lib["rr_house_gable_maroon_lower"].img, (0, 3 * T))
    lib.add_img("no_house_maroon", mar, "building", house_solid, 3, [[2, 10]])


# =========================================================================== ground
def build_ground(L, lib):
    # factory yard: concrete everywhere (tank pad, S3 corner and the footprint included)
    L.fill("sidewalk", 42, 2, 63, 23)
    # grove floor: grass, the hidden trail stays packed dirt (x=40, y=10..21)
    L.fill("grass", 38, 0, 41, 21)
    L.fill("dirt", 40, 10, 40, 21)
    # hilltop: brick-paved overlook, brick walk between the houses down to Parkway
    L.fill("plaza", 140, 2, 155, 8)
    L.fill("plaza", 146, 12, 147, 23)


# =========================================================================== build
def build(L, lib):
    _register(lib)
    before = {lay: {c: len(v) for c, v in L.cells[lay].items()} for lay in L.LAYERS}
    solid_before = set(L.extra_solid)
    _build_grove(L, lib)
    _build_factory(L, lib)
    _build_hilltop(L, lib)
    _build_parkway(L, lib)
    # guard: anything that spilled outside my three rects (canopies off the map top, etc.) is trimmed
    for lay in L.LAYERS:
        for c in list(L.cells[lay].keys()):
            if _mine(*c):
                continue
            n0 = before[lay].get(c, 0)
            if len(L.cells[lay][c]) > n0:
                if n0:
                    L.cells[lay][c] = L.cells[lay][c][:n0]
                else:
                    del L.cells[lay][c]
    for c in list(L.extra_solid - solid_before):
        if not _mine(*c):
            L.extra_solid.discard(c)


def _tree(L, pid, x, ybottom):
    """Place a tree by its trunk row (bypasses bounds check: canopies may leave the map top)."""
    p = L.lib[pid]
    L.place(pid, x, ybottom - p.h + 1)


# --------------------------------------------------------------------------- grove + S2
def _build_grove(L, lib):
    # canopies alternate west (trunk x=39) / east (trunk x=41) so every trail cell x=40 is roofed
    # explicit layout (trunk rows): west trees x=38 (trunk 39), east trees x=40 (trunk 41)
    for pid, yb in (("nt_s26_tree_medium", 21), ("sf_tree_large", 18), ("nt_s26_tree_medium", 15),
                    ("sf_tree_large", 12)):
        _tree(L, pid, 38, yb)
    for pid, yb in (("sf_tree_large", 20), ("nt_s26_tree_medium", 17), ("sf_tree_large", 14),
                    ("nt_s26_tree_medium", 11)):
        _tree(L, pid, 40, yb)
    # fill the remaining grove cells beside the trail with shrubs (keeps the trail a trail)
    trail = {(40, y) for y in range(10, 22)}
    glade = {(39, 8), (40, 8), (39, 9), (40, 9)}
    shrubs = ["nt_s69_bush_ball_small", "nt_s69_shrub_columnar", "nt_s69_bush_flowering_small"]
    k = 0
    for y in range(21, 7, -1):
        for x in (38, 39, 41):
            if (x, y) in glade or (x, y) in L.extra_solid:
                continue
            if any(e[1] for e in L.cells["Objects"].get((x, y), [])):
                continue
            pid = shrubs[k % 3]
            k += 1
            p = lib[pid]
            if dress.can_place(L, pid, x, y - p.h + 1, reserved=trail | glade, allow_overhead_overlap=True):
                L.place(pid, x, y - p.h + 1)
            else:
                L.extra_solid.add((x, y))     # tangled undergrowth under the canopy
    # glade S2 (x=39..40, y=8..9): sunlit clearing ringed by trees on the north
    _tree(L, "nt_s27_spruce_tall", 38, 7)
    _tree(L, "nt_s26_conifer_tall", 40, 7)
    _tree(L, "nt_s26_conifer_short", 38, 4)
    _tree(L, "nt_s27_spruce_tall", 40, 4)
    _tree(L, "nt_s26_tree_round_small", 38, 1)
    _tree(L, "nt_s26_conifer_tall", 40, 1)
    L.put("Decals", 39, 9, lib["nt_s17_flowers_yellow"].tile_img(0, 0))
    L.put("Decals", 40, 8, lib["nt_s17_flowers_blue"].tile_img(1, 1))
    L.put("Decals", 39, 8, lib["nt_s17_flowers_pink"].tile_img(0, 1))
    for c in ((38, 8), (38, 9), (41, 8), (41, 9)):
        if not any(e[1] for e in L.cells["Objects"].get(c, [])):
            L.extra_solid.add(c)
    L.place("nt_s69_bush_round", 41, 8) if dress.can_place(L, "nt_s69_bush_round", 41, 8) else None
    L.marker("secret", 40, 8, id="S2", desc="grove glade, reached by the hidden trail x=40 y=10..21")


# --------------------------------------------------------------------------- factory + yard + S3
def _build_factory(L, lib):
    L.place("no_factory", 44, 10)
    # smokestack rising from the back of the roof over the north yard; smoke puffs above it
    L.place_b("sy_smokestack", 58, 11)
    L.place("no_smoke", 57, 0)
    # wooden water tanks on stands (north yard)
    L.place("no_water_tank", 53, 4)
    L.place("no_water_tank", 60, 4)
    # north border trees (trunks on y=1, canopies leave the map)
    for x, pid in ((44, "nt_s26_conifer_tall"), (47, "nt_s26_tree_round_small"), (50, "nt_s27_spruce_tall"),
                   (56, "nt_s26_tree_round_small")):
        _tree(L, pid, x, 1)
    # S3: back corner (x=42..43, y=2..4) walled off by crate stacks; squeeze in along y=2..3 from the east
    L.place("nt_s28_crates_stack", 42, 5)
    L.place("sp_boxes_on_pallet_b", 44, 4)
    L.place("nt_s28_crates_pair", 44, 6)
    L.put("Decals", 42, 3, _weeds())
    L.put("Decals", 43, 2, _weeds())
    L.marker("secret", 42, 3, id="S3", desc="factory back corner behind the crate stacks")
    # coal heap by the boiler end + drums, pallets
    L.place("no_coal_pile", 46, 7)
    L.place("sp_barrel_rust", 49, 7)
    L.place("sp_barrel_metal_dented", 50, 7)
    L.place("sp_barrel_rust_trash", 50, 4)
    L.place("sp_pallet_upright", 47, 2)
    L.place("nt_s28_crates_pair", 51, 2)
    L.place("nt_s28_barrels_pile", 49, 2)
    L.place("sp_scrap_pipes", 57, 8)
    for c in ((48, 4), (55, 2), (61, 2), (52, 9), (43, 8)):
        L.put("Decals", c[0], c[1], _oil_stain(c[0] * 31 + c[1]))
    # west strip (x=42..43) stays a clear 2-wide lane; east strip: drums against the cemetery wall
    L.place("sp_barrel_metal_empty", 63, 12)
    L.place("sp_barrel_rust", 63, 14)
    L.place("sp_boxes_on_pallet_a", 62, 17)
    # loading apron (y=22..23): delivery truck at door 3, crates + pallets beside the doors
    L.place("no_truck", 56, 21)
    L.place("sp_boxes_on_pallet_a", 44, 22)
    L.place("nt_s28_crates_stack", 48, 22)
    L.place("sp_barrel_metal_empty", 46, 22)
    for c in ((51, 22), (53, 23), (55, 22)):
        L.put("Decals", c[0], c[1], _oil_stain(c[0] * 17 + c[1]))
    L.marker("npc", 52, 22, role="factory_foreman")


# --------------------------------------------------------------------------- hilltop + S6
def _build_hilltop(L, lib):
    # east border woods x=156..159 (upper and lower)
    for yb, pid in ((1, "nt_s26_conifer_tall"), (4, "nt_s27_spruce_tall"), (7, "nt_s26_tree_round_small"),
                    (9, "nt_s26_conifer_short")):
        _tree(L, pid, 156, yb)
        _tree(L, "nt_s26_conifer_tall" if yb % 2 else "nt_s26_tree_round_small", 158, yb + 1 if yb < 9 else 9)
    for yb, pid in ((14, "nt_s26_maple_med"), (19, "nt_s26_tree_dark_round"), (23, "nt_s26_conifer_tall")):
        _tree(L, pid, 156, yb)
    # north border
    for x in (136, 140, 144, 150):
        _tree(L, "nt_s26_tree_round_small" if x % 8 else "nt_s27_spruce_tall", x, 1)

    # ---- the two Victorian houses (roof peaks overhang the cliff face as overhead rows)
    L.place_b("no_house_slate", 137, 21)
    L.place_b("no_house_maroon", 148, 21)
    L.place("rr_porch_rocking_chair", 140, 19) if dress.can_place(L, "rr_porch_rocking_chair", 140, 19) else None
    # side lawn of house 1 (x=136, x=145) and front yards (y=22)
    _tree(L, "nt_s69_shrub_columnar", 136, 21)
    _tree(L, "nt_s69_shrub_columnar", 145, 21)
    L.place("nt_s69_bush_flowering", 136, 13)
    for (x, pid) in ((137, "rr_flower_planter_pink"), (142, "rr_flower_planter_red"),
                     (152, "rr_flower_planter_pink"), (154, "rr_flower_planter_white")):
        dress.try_place(L, pid, x, 22)
    L.place("no_wagon", 144, 22)
    vane = _weather_vane()
    L.put("Overhead", 140, 8, vane.crop((0, 0, 16, 16)))
    L.put("Overhead", 141, 8, vane.crop((16, 0, 32, 16)))
    L.place("sp_mailbox_blue", 136, 21) if dress.can_place(L, "sp_mailbox_blue", 136, 21) else None
    # picket fences along y=23 with gates at the porch entries (x0+1..x0+2) and the walk x=146..147
    fence1 = [(x, 23) for x in range(136, 146) if x not in (138, 139, 140)]
    fence2 = [(x, 23) for x in range(148, 156) if x not in (148, 149, 150)]
    synth.paint_fence(L, fence1, "picket")
    synth.paint_fence(L, fence2, "picket")
    # walk lamps
    L.place_b("sy_lamp_iron", 145, 13) if dress.can_place(L, "sy_lamp_iron", 145, 11) else None

    # ---- overlook (elev 1): rose garden west, benches, telescope, railing over the cliff
    beds = [("nt_s17_flowers_pink", 136, 3), ("nt_s17_flowers_crimson", 138, 3),
            ("nt_s17_flowers_red", 136, 6), ("nt_s17_flowers_pink", 138, 6)]
    for pid, x, y in beds:
        L.place(pid, x, y)
    for (x, y) in ((136, 2), (138, 5), (136, 8)):
        dress.try_place(L, "nt_s69_bush_flowering", x, y - 1)
    dress.try_place(L, "nt_s69_topiary_cone", 139, 7)
    dress.try_place(L, "nt_s69_topiary_double_ball", 139, 2)
    synth.paint_fence(L, [(x, 9) for x in range(136, 140)], "picket")
    synth.paint_fence(L, [(x, 9) for x in range(140, 146)] + [(x, 9) for x in range(148, 156)], "iron")
    # benches face the view (south); telescope at the S6 spot
    L.place("sf_bench_wood_long", 142, 2)
    L.place("sf_bench_wood_long", 147, 2)
    L.place("no_telescope", 153, 3)
    L.marker("secret", 152, 3, id="S6", desc="overlook coin telescope + item")
    L.place("sy_lamp_iron", 141, 6)
    L.place("sy_lamp_iron", 155, 6)
    L.place("sp_trashcan_metal", 151, 2)
    L.place("rr_flower_planter_pink", 144, 7)
    L.place("rr_flower_planter_red", 149, 7)
    L.place("nt_s69_topiary_potted_ball", 145, 7)
    L.place("nt_s69_topiary_potted_ball", 148, 7)
    L.marker("npc", 148, 5, role="overlook_old_couple")


# --------------------------------------------------------------------------- Parkway Blvd + creek walk
def _build_parkway(L, lib):
    junction = range(103, 115)     # George St (x=104..113) plus a cell of breathing room
    # galvanized pipe railing along the creek edge (row 35); bridge deck x=104..113 stays open
    rail = [(x, 35) for x in range(42, 160) if x not in range(104, 114)]
    synth.paint_fence(L, rail, "pipe")

    # verge furniture (y=32..33): street trees every 6 tiles, furniture between them
    trees = ["nt_s26_tree_medium", "nt_s26_tree_medium", "sf_tree_large", "nt_s26_tree_medium"]
    bus = range(114, 123)
    furn_cycle = ["lamp", "pole", "hydrant", "pole_t", "lamp", "pole", "bin", "pole"]
    ti = fi = 0
    for x in range(43, 156, 6):
        if any(xx in junction or xx in bus for xx in (x, x + 1, x + 2)):
            continue
        pid = trees[ti % len(trees)]
        ti += 1
        p = lib[pid]
        if dress.can_place(L, pid, x, 34 - p.h, allow_overhead_overlap=True):
            _tree(L, pid, x, 33)
        fx = x + 3
        if fx in junction or fx in bus or fx > 155:
            continue
        kind = furn_cycle[fi % len(furn_cycle)]
        fi += 1
        if kind == "lamp":
            L.place_b("sy_lamp_cobra_r", fx, 32)
        elif kind == "pole":
            L.place_b("sp_utility_pole_crossarm", fx, 32)
        elif kind == "pole_t":
            L.place_b("sp_utility_pole_transformer", fx, 32)
        elif kind == "hydrant":
            L.place_b("sy_hydrant", fx, 32)
        elif kind == "bin":
            L.place_b("sp_trashcan_metal", fx, 33)

    # bus stop by the cemetery gate (east of the junction): shelter + flag sign in the verge
    L.place("sf_bench_wood_long", 116, 31)
    L.place_b("sp_bus_stop_sign_pictogram", 121, 32)
    L.marker("npc", 118, 30, role="bus_stop_commuter")

    # north side furniture lives in my own strips just off the sidewalk (factory front, hilltop front)
    L.place_b("sy_hydrant", 51, 23)

    # parked cars at the curbs (boxy sedans)
    L.place("sp_car_sedan_mint_right", 62, 25)        # north curb, rows 26..27 solid
    L.place("sp_car_sedan_beige_left", 130, 27)       # south curb, rows 28..29 solid
    L.place("sp_car_sedan_lilac_left", 86, 25)

    # sawhorse roadblock at the east edge (x=158..159, y=26..29)
    for y, pid in ((26, "sp_sawhorse_plain"), (27, "sp_sawhorse_no_entry_big"), (28, "sp_sawhorse_plain"),
                   (29, "sp_sawhorse_no_entry")):
        L.place(pid, 158, y)
    L.place("sp_cone_orange", 157, 26)
    L.place("sp_cone_orange", 157, 29)
    # map-edge woods beyond the creek walk (x=156..159, y=30..33) and sidewalk ends sealed
    _tree(L, "nt_s26_conifer_tall", 156, 33)
    _tree(L, "nt_s26_tree_round_small", 158, 33)
    for y in (24, 25, 30, 31):
        L.extra_solid.add((159, y))
