"""Prospect Hill Cemetery (brief 1.4 / 3.6): a Victorian 'rural cemetery' on two terraces.

Lower terrace y=12..21 (gate, gatehouse, carriage drives), rocky bank y=10..11 with stairs at
x=70..73 / 106..111 / 126..129, upper terrace y=0..9 (Soldiers' Circle, chapel, old sections).
South boundary: iron fence on a stone wall (y=22..23) with the Gothic gate on the George St axis.
Secrets: S4 receiving vault in the cliff face (x=90..92), S5 forgotten mausoleum (x=67..69, y=0..3).
"""
import math
import random

from PIL import Image, ImageDraw

import dress
import terrain as TR

REGION = (64, 0, 135, 23)
T = 16
OUT = (0x3A, 0x3A, 0x50, 255)

# chapel stone palette (sampled from the Tileset_84 chapel) so synthesized pieces match it
ST_OUT = (58, 58, 80, 255)
ST_D = (70, 70, 94, 255)
ST_M = (86, 89, 114, 255)
ST_L = (108, 110, 133, 255)
ST_LL = (125, 127, 153, 255)
ST_HI = (139, 139, 171, 255)
MOSS = (26, 82, 73, 255)
MOSS2 = (52, 110, 84, 255)
CURB_L = (185, 158, 134, 255)
CURB_M = (156, 120, 107, 255)
CURB_D = (107, 80, 82, 255)
SLATE = ((0x6A, 0x74, 0x8A, 255), (0x58, 0x61, 0x76, 255), (0x46, 0x4D, 0x5E, 255), (0x8C, 0x96, 0xAA, 255))

GATE_X0 = 106          # 6-wide gate image x=106..111, passable opening x=107..110
AXIS = (107, 110)
DEBUG = False
CIRCLE_C = (81.5, 4.2)  # Soldiers' Circle centre (statue at x=81..82)

# =========================================================================== geometry
# gravel carriage roads: 2-wide bands along smooth curves through these tile-centre points
LOWER_LOOP = [(69.5, 12.5), (76, 12.5), (83, 12.5), (89, 12.5), (93.5, 12.5), (97, 13.4), (100.5, 13.4),
              (104, 12.5), (112, 12.5), (120, 12.5), (124.5, 12.9), (129.5, 12.5)]
UPPER_LOOP = [(69.5, 8.5), (75, 8.5), (84, 8.6), (88.5, 7.8), (92, 7.5), (95.5, 7.9), (99, 8.5),
              (108, 8.5), (115, 8.6), (122, 8.5), (129.5, 8.5)]
WEST_DRIVE = [(106.5, 18.5), (99, 18.6), (92, 18.3), (87.5, 17.2), (84.8, 15.2), (83.5, 13)]
EAST_DRIVE = [(110.5, 20.5), (118, 20.5), (123, 20.3), (126.8, 18.8), (128.8, 16.2), (129.5, 13)]
INNER_LANE = [(97, 8), (98.2, 5.2), (101.5, 2.6), (106, 1.8), (110.5, 2.6), (113.2, 5.2), (113.8, 8)]


def _spline(pts, step=0.04):
    """Catmull-Rom through pts -> dense list of (x,y)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t = 0.0
        while t < 1.0:
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
            t += step
    out.append(pts[-1])
    return out


def band(pts, w=2):
    """Cells of a w-wide gravel drive following a smooth curve through pts (tile centres)."""
    cells = set()
    for (x, y) in _spline(pts):
        x0 = int(round(x + 0.5 - w / 2.0))   # pts are the band's centre in tile-centre coords
        y0 = int(round(y + 0.5 - w / 2.0))
        for dy in range(w):
            for dx in range(w):
                cells.add((x0 + dx, y0 + dy))
    return cells


def circle_ring():
    """(gravel ring cells, lawn cells) of the Soldiers' Circle."""
    cx, cy = CIRCLE_C
    ring, lawn = set(), set()
    for y in range(0, 9):
        for x in range(73, 91):
            o = ((x - cx) / 7.8) ** 2 + ((y - cy) / 4.0) ** 2
            i = ((x - cx) / 5.6) ** 2 + ((y - cy) / 2.6) ** 2
            if i <= 1.0:
                lawn.add((x, y))
            elif o <= 1.0:
                ring.add((x, y))
    return ring, lawn


_ROADS = None


def road_cells():
    global _ROADS
    if _ROADS is not None:
        return _ROADS
    cells = set()
    for pts in (LOWER_LOOP, UPPER_LOOP, WEST_DRIVE, EAST_DRIVE, INNER_LANE):
        cells |= band(pts)
    for y in range(12, 24):
        for x in range(AXIS[0], AXIS[1] + 1):
            cells.add((x, y))
    ring, _ = circle_ring()
    cells |= ring
    for x in range(119, 122):       # chapel forecourt
        cells.add((x, 8))
    cells -= {(90, 9), (91, 9), (92, 9)}   # vault top
    cells -= {(106, y) for y in range(21, 24)} | {(111, y) for y in range(21, 24)}   # gate piers
    _ROADS = {(x, y) for (x, y) in cells if 65 <= x <= 134 and 0 <= y <= 23 and not 10 <= y <= 11}
    return _ROADS


def road_edge(x, ylo, yhi, top=True):
    """First road row in column x within [ylo,yhi] scanning from the top (or bottom)."""
    rs = road_cells()
    rng = range(ylo, yhi + 1) if top else range(yhi, ylo - 1, -1)
    for y in rng:
        if (x, y) in rs:
            return y
    return None


# =========================================================================== synthesized art
def _outline(img, col=OUT):
    """Add a 1px outline around opaque pixels (pixel-art style)."""
    W, H = img.size
    src = img.load()
    out = img.copy()
    px = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and src[xx, yy][3] > 200 and src[xx, yy][:3] != col[:3]:
                    px[x, y] = col
                    break
    return out


def wide_gothic_gate():
    """cf_gothic_gate_orb_4w stretched to 6 tiles (4-tile opening) and one pier row taller (6x6)."""
    g = TR.tile("Tileset_84_MV.png", 0, 8, 4, 5).copy()
    W, H = g.size
    cut, split = 24, 32
    out = Image.new("RGBA", (W + 32, H))

    def blk(side):
        b = Image.new("RGBA", (16, H))
        for i in range(16):
            for y in range(H):
                sx = 23 if y < split else 16 + (i % 8)
                if side == "r":
                    b.putpixel((15 - i, y), g.getpixel((W - 1 - sx, y)))
                else:
                    b.putpixel((i, y), g.getpixel((sx, y)))
        return b
    out.paste(g.crop((0, 0, cut, H)), (0, 0))
    out.paste(blk("l"), (cut, 0))
    out.paste(g.crop((cut, 0, W - cut, H)), (cut + 16, 0))
    out.paste(blk("r"), (W - cut + 16, 0))
    out.paste(g.crop((W - cut, 0, W, H)), (W - cut + 32, 0))
    W2 = out.size[0]
    tall = Image.new("RGBA", (W2, H + T))
    tall.paste(out.crop((0, 0, W2, 4 * T)), (0, 0))
    tall.paste(out.crop((0, 3 * T, W2, 4 * T)), (0, 4 * T))
    tall.paste(out.crop((0, 4 * T, W2, 5 * T)), (0, 5 * T))
    return tall


def wall_face(x):
    """Low coursed-stone wall face under the iron fence's stone curb (one tile row)."""
    img = Image.new("RGBA", (T, T), CURB_M)
    d = ImageDraw.Draw(img)
    d.line([0, 0, 15, 0], fill=CURB_D)
    d.line([0, 1, 15, 1], fill=CURB_L)
    for (y0, off) in ((2, 0), (8, 6)):
        if y0 > 2:
            d.line([0, y0, 15, y0], fill=CURB_L)
        d.line([0, y0 + 5, 15, y0 + 5], fill=CURB_D)
        for xx in range((off - x * 16) % 12, 16, 12):
            d.line([xx, y0, xx, y0 + 5], fill=CURB_D)
    d.line([0, 14, 15, 14], fill=CURB_D)
    d.line([0, 15, 15, 15], fill=ST_OUT)
    rnd = random.Random(x * 7 + 3)
    for _ in range(3):
        img.putpixel((rnd.randint(0, 15), rnd.randint(9, 13)), MOSS2)
    return img


def soldier_monument():
    """Bronze Civil War soldier at parade rest on a stepped granite base (Milmore figure nod). 2x4."""
    img = Image.new("RGBA", (2 * T, 4 * T))
    d = ImageDraw.Draw(img)
    G_L, G_M, G_D = (0xB4, 0xAE, 0xB6, 255), (0x92, 0x8C, 0x96, 255), (0x6C, 0x66, 0x72, 255)
    # granite base: plinth step, die with a bronze tablet, cornice
    d.rectangle([2, 55, 29, 62], fill=G_M)
    d.line([2, 55, 29, 55], fill=G_L)
    d.rectangle([22, 56, 29, 62], fill=G_D)
    d.rectangle([6, 40, 25, 54], fill=G_L)
    d.rectangle([20, 40, 25, 54], fill=G_M)
    d.rectangle([10, 44, 17, 50], fill=(0x55, 0x76, 0x66, 255))
    d.line([10, 44, 17, 44], fill=(0x88, 0xAE, 0x96, 255))
    d.rectangle([4, 36, 27, 39], fill=G_L)
    d.line([4, 39, 27, 39], fill=G_D)
    d.rectangle([22, 36, 27, 39], fill=G_M)
    BR_D, BR_M, BR_L, BR_H = (0x2C, 0x44, 0x3C, 255), (0x44, 0x66, 0x58, 255), (0x66, 0x8E, 0x78, 255), (0x9C, 0xC4, 0xA6, 255)
    # bronze plate + boots + legs
    d.rectangle([9, 34, 23, 35], fill=BR_D)
    d.rectangle([12, 29, 14, 33], fill=BR_M)
    d.rectangle([16, 29, 18, 33], fill=BR_D)
    # greatcoat
    d.polygon([(12, 17), (19, 17), (21, 29), (10, 29)], fill=BR_M)
    d.line([12, 18, 10, 28], fill=BR_L)
    d.line([19, 18, 21, 28], fill=BR_D)
    d.line([15, 20, 15, 28], fill=BR_D)
    d.line([11, 23, 20, 23], fill=BR_D)
    # shoulder cape
    d.polygon([(10, 15), (21, 15), (22, 19), (9, 19)], fill=BR_M)
    d.line([9, 19, 22, 19], fill=BR_D)
    d.line([11, 15, 15, 15], fill=BR_L)
    # head + kepi
    d.rectangle([13, 10, 17, 14], fill=BR_L)
    d.point((17, 12), fill=BR_M)
    d.line([13, 14, 17, 14], fill=BR_M)
    d.polygon([(13, 5), (17, 5), (18, 9), (13, 9)], fill=BR_M)
    d.line([12, 9, 17, 9], fill=BR_D)
    d.point((14, 6), fill=BR_H)
    # rifle at parade rest, hands folded over the muzzle
    d.line([23, 10, 23, 34], fill=BR_D)
    d.line([24, 18, 24, 33], fill=BR_M)
    d.point((23, 10), fill=BR_H)
    d.rectangle([20, 15, 23, 17], fill=BR_L)
    d.point((10, 16), fill=BR_H)
    return _outline(img)


def cannon():
    """Small Civil War field gun (black barrel on a brown carriage), 1x1."""
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.polygon([(3, 9), (12, 5), (13, 7), (4, 11)], fill=(0x3A, 0x3E, 0x46, 255))
    d.line([4, 9, 12, 5], fill=(0x6E, 0x74, 0x80, 255))
    d.rectangle([2, 9, 5, 12], fill=(0x2E, 0x30, 0x38, 255))
    d.ellipse([5, 8, 11, 14], fill=(0x6A, 0x4A, 0x36, 255))
    d.ellipse([7, 10, 9, 12], fill=(0x3A, 0x2A, 0x22, 255))
    d.line([1, 13, 6, 13], fill=(0x5A, 0x40, 0x30, 255))
    return _outline(img)


def soldier_marker():
    """Small white marble government-issue headstone, 1x1."""
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.rectangle([5, 4, 10, 13], fill=(0xEA, 0xE8, 0xF0, 255))
    d.rectangle([9, 4, 10, 13], fill=(0xC2, 0xC2, 0xD0, 255))
    d.line([5, 3, 9, 3], fill=(0xEA, 0xE8, 0xF0, 255))
    d.line([6, 7, 8, 7], fill=(0xA4, 0xA4, 0xB6, 255))
    d.line([6, 9, 8, 9], fill=(0xA4, 0xA4, 0xB6, 255))
    img = _outline(img)
    d = ImageDraw.Draw(img)
    d.line([4, 14, 11, 14], fill=(0x3E, 0x6A, 0x3E, 120))
    return img


def obelisk(h_tiles=4):
    """White marble obelisk on a stepped base, 1 tile wide."""
    H = h_tiles * T
    img = Image.new("RGBA", (T, H))
    d = ImageDraw.Draw(img)
    MW, MM, MD = (0xEC, 0xEA, 0xF0, 255), (0xC6, 0xC6, 0xD4, 255), (0x98, 0x98, 0xAC, 255)
    d.rectangle([1, H - 6, 14, H - 2], fill=MM)
    d.line([1, H - 6, 14, H - 6], fill=MW)
    d.rectangle([3, H - 10, 12, H - 7], fill=MW)
    d.rectangle([9, H - 10, 12, H - 7], fill=MM)
    top, bot = 7, H - 11
    d.polygon([(5, top), (10, top), (11, bot), (4, bot)], fill=MW)
    d.polygon([(8, top), (10, top), (11, bot), (8, bot)], fill=MM)
    d.polygon([(5, top), (7, 1), (10, top)], fill=MW)
    d.polygon([(7, 1), (10, top), (8, top)], fill=MM)
    d.line([4, bot, 11, bot], fill=MD)
    d.line([1, H - 2, 14, H - 2], fill=MD)
    return _outline(img)


def mausoleum():
    """Forgotten Gothic mausoleum: narrow orb pediment over the vault arch, ivy-grown. 3x4."""
    ped = TR.tile("Tileset_84_MV.png", 8, 1, 3, 2).copy()
    vault = TR.tile("Tileset_84_MV.png", 13, 12, 3, 3).copy()
    img = Image.new("RGBA", (3 * T, 4 * T))
    img.alpha_composite(vault, (0, 1 * T))
    img.alpha_composite(ped.crop((0, 0, 3 * T, T + 10)), (0, 0))
    rnd = random.Random(55)
    px = img.load()
    for _ in range(110):
        x, y = rnd.randint(0, 47), rnd.randint(4, 60)
        if px[x, y][3] > 200 and px[x, y][:3] != ST_OUT[:3]:
            c = MOSS if rnd.random() < 0.5 else MOSS2
            for (dx, dy) in ((0, 0), (1, 0), (0, 1)):
                if 0 <= x + dx < 48 and 0 <= y + dy < 64 and px[x + dx, y + dy][3] > 200:
                    px[x + dx, y + dy] = c
    return img


def gatehouse():
    """Small Gothic stone lodge: steep slate roof, front cross-gable, lancet windows. 7x6, door col 3."""
    W, H = 7 * T, 6 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    s_l, s_m, s_d, s_hi = SLATE
    wt = 3 * T - 2                       # wall top
    # main roof: short back slope, ridge, long front slope with slate courses
    d.rectangle([2, 6, W - 3, 13], fill=s_d)
    d.rectangle([0, 13, W - 1, wt], fill=s_l)
    d.line([1, 13, W - 2, 13], fill=s_hi)
    for i, y in enumerate(range(17, wt - 1, 4)):
        d.line([1, y, W - 2, y], fill=s_m)
        for x in range(2 + (i % 2) * 3, W - 2, 6):
            d.point((x, y - 1), fill=s_m)
    d.polygon([(0, 13), (2, 6), (2, 13)], fill=s_d)
    d.polygon([(W - 1, 13), (W - 3, 6), (W - 3, 13)], fill=s_d)
    d.line([(0, wt), (0, 13), (2, 6), (W - 3, 6), (W - 1, 13), (W - 1, wt)], fill=ST_OUT)
    # chimney
    d.rectangle([16, 0, 24, 12], fill=ST_L, outline=ST_OUT)
    d.rectangle([15, 0, 25, 2], fill=ST_LL, outline=ST_OUT)
    # wall in coursed stone with quoins
    d.rectangle([0, wt, W - 1, H - 1], fill=ST_L)
    for i, y in enumerate(range(wt + 6, H - 4, 6)):
        d.line([1, y, W - 2, y], fill=ST_M)
        off = 0 if i % 2 else 6
        for x in range(off, W, 12):
            d.line([x, y - 5, x, y - 1], fill=ST_M)
    for k, y in enumerate(range(wt + 1, H - 5, 6)):
        for x0 in (0, W - 7):
            d.rectangle([x0 + (1 if x0 else 0), y, x0 + 6 - (0 if x0 else 1), y + 4], fill=ST_HI if k % 2 else ST_LL)
    d.rectangle([0, H - 5, W - 1, H - 1], fill=ST_M)
    d.line([0, H - 5, W - 1, H - 5], fill=ST_LL)
    d.rectangle([0, wt, W - 1, wt + 2], fill=ST_D)          # eave shadow
    # front cross-gable over the door
    cx = 3 * T + 8
    gb = wt + 3
    d.polygon([(cx - 21, gb), (cx, 9), (cx + 21, gb)], fill=ST_L)
    for y in range(15, gb, 6):
        half = int(21 * (y - 9) / (gb - 9))
        d.line([cx - half + 2, y, cx + half - 2, y], fill=ST_M)
    d.line([(cx - 25, gb + 1), (cx, 6), (cx + 25, gb + 1)], fill=s_m, width=3)
    d.line([(cx - 26, gb + 2), (cx, 4), (cx + 26, gb + 2)], fill=ST_OUT)
    d.line([(cx - 22, gb), (cx, 10), (cx + 22, gb)], fill=ST_OUT)
    d.line([cx, 0, cx, 5], fill=ST_OUT)
    d.line([cx - 2, 2, cx + 2, 2], fill=ST_OUT)
    d.ellipse([cx - 4, 22, cx + 4, 30], fill=(0x3A, 0x40, 0x58, 255), outline=ST_OUT)
    d.point((cx, 26), fill=(0xE8, 0xC8, 0x70, 255))
    # pointed-arch door with stone surround + step
    d.polygon([(cx - 8, H - 4), (cx - 8, H - 24), (cx, H - 34), (cx + 8, H - 24), (cx + 8, H - 4)], fill=ST_HI, outline=ST_OUT)
    d.polygon([(cx - 5, H - 4), (cx - 5, H - 23), (cx, H - 30), (cx + 5, H - 23), (cx + 5, H - 4)], fill=(0x5A, 0x3A, 0x2A, 255), outline=ST_OUT)
    d.line([cx, H - 28, cx, H - 5], fill=(0x3E, 0x28, 0x1E, 255))
    d.point((cx + 2, H - 14), fill=(0xE8, 0xC2, 0x4A, 255))
    d.rectangle([cx - 10, H - 4, cx + 10, H - 1], fill=ST_LL, outline=ST_OUT)
    # lancet windows, warm lamplight
    for wx in (18, W - 26):
        d.polygon([(wx, H - 8), (wx, H - 24), (wx + 4, H - 30), (wx + 8, H - 24), (wx + 8, H - 8)], fill=(0x3A, 0x40, 0x58, 255), outline=ST_OUT)
        d.rectangle([wx + 1, H - 22, wx + 7, H - 9], fill=(0xD8, 0xB8, 0x68, 255))
        d.line([wx + 4, H - 27, wx + 4, H - 9], fill=ST_OUT)
        d.line([wx + 1, H - 16, wx + 7, H - 16], fill=ST_OUT)
        d.rectangle([wx - 1, H - 8, wx + 9, H - 6], fill=ST_HI, outline=ST_OUT)
    d.line([0, wt, 0, H - 1], fill=ST_OUT)
    d.line([W - 1, wt, W - 1, H - 1], fill=ST_OUT)
    d.line([0, H - 1, W - 1, H - 1], fill=ST_OUT)
    return img


def register(lib):
    if "cem_gate_wide" in lib:
        return
    lib.add_img("cem_gate_wide", wide_gothic_gate(), "building_module", [[0, 3], [0, 4], [0, 5], [5, 3], [5, 4], [5, 5]], 3)
    lib.add_img("cem_soldier_monument", soldier_monument(), "statue", [[0, 2], [1, 2], [0, 3], [1, 3]], 2)
    lib.add_img("cem_cannon", cannon(), "prop", "all", 0)
    lib.add_img("cem_marker", soldier_marker(), "grave", "all", 0)
    lib.add_img("cem_obelisk_tall", obelisk(5), "statue", [[0, 4]], 4)
    lib.add_img("cem_obelisk", obelisk(4), "statue", [[0, 3]], 3)
    lib.add_img("cem_obelisk_small", obelisk(3), "statue", [[0, 2]], 2)
    lib.add_img("cem_mausoleum", mausoleum(), "building", "all", 0)
    lib.add_img("cem_gatehouse", gatehouse(), "building", "all", 0)


# =========================================================================== ground
def build_ground(L, lib):
    L.fill("grass", 64, 0, 135, 23)
    for (x, y) in road_cells():
        if (x, y) not in L.stairs:
            L.set_kind(x, y, "dirt")


# =========================================================================== props
HEAD_MARBLE = ["cf_headstone_tall_marble_plain", "cf_headstone_tall_marble_wreath", "cf_headstone_cross_marble", "cf_headstone_round_marble"]
HEAD_SAND = ["cf_headstone_tall_sandstone_plain", "cf_headstone_tall_sandstone_wreath", "cf_headstone_cross_sandstone", "cf_headstone_round_sandstone"]
HEAD_SMALL = ["nt_s81_headstone_grey", "nt_s81_headstone_grey_cross", "nt_s81_headstone_tan", "nt_s81_headstone_tan_cross"]
HEAD_SLATE = ["cf_headstone_slate_cross_small", "cf_headstone_slate_panel_small"]


def boundary(L):
    f = "Tileset_55_MV.png"
    mid = [TR.tile(f, 2, 6), TR.tile(f, 3, 6)]
    corner_l, corner_r = TR.tile(f, 1, 6), TR.tile(f, 4, 6)
    side_l, side_r = TR.tile(f, 1, 4), TR.tile(f, 4, 4)
    end_r, end_l = TR.tile(f, 5, 6), TR.tile(f, 0, 6)
    for x in range(64, 136):
        if 105 <= x <= 112:
            continue
        img = {64: corner_l, 135: corner_r, 104: end_r, 113: end_l}.get(x, mid[x % 2])
        L.put("Objects", x, 22, img, True, "full")
        L.put("Objects", x, 23, wall_face(x), True, "full")
    for yy in range(0, 22):
        L.put("Objects", 64, yy, side_l, True, "full")
        if not (10 <= yy <= 11):
            L.put("Objects", 135, yy, side_r, True, "full")
    # the 1-tile strip between the west fence and the upper terrace rim is a dead end: block it
    for yy in range(0, 12):
        L.extra_solid.add((65, yy))


def gate(L):
    L.place("cem_gate_wide", GATE_X0, 18)
    for x in (105, 112):
        L.place_b("cf_column_short_marble", x, 23)
        L.extra_solid.add((x, 22))
    L.marker("gate", 108, 22, id="cemetery_gate", note="Gothic gate on the George St axis; opening x=107..110")


def chain_ring(L, cx, cy, rx, ry, gap_deg=(55, 125), n=22):
    """Stone bollards linked by sagging iron chain on an ellipse (tile coords), gap at the south."""
    x0, y0 = int(cx - rx) - 1, int(cy - ry) - 2
    x1, y1 = int(cx + rx) + 2, int(cy + ry) + 2
    W, H = (x1 - x0 + 1) * T, (y1 - y0 + 1) * T
    cv = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(cv)
    posts = []
    for i in range(n):
        a = 360.0 * i / n
        if gap_deg[0] < a < gap_deg[1]:
            continue
        r = math.radians(a)
        px = (cx + rx * math.cos(r) - x0) * T + 8
        py = (cy + ry * math.sin(r) - y0) * T + 12
        posts.append((a, int(px), int(py)))
    chain = (0x2A, 0x2C, 0x34, 255)
    for (a1, xa, ya), (a2, xb, yb) in zip(posts, posts[1:] + posts[:1]):
        if (a2 - a1) % 360 > 360.0 / n * 1.5:
            continue
        pts = []
        for k in range(9):
            t = k / 8
            pts.append((xa + (xb - xa) * t, ya - 5 + (yb - ya) * t + 2.5 * 4 * t * (1 - t)))
        d.line(pts, fill=chain)
    solid = set()
    for (_a, px, py) in sorted(posts, key=lambda p: p[2]):
        d.rectangle([px - 3, py - 8, px + 2, py], fill=(0xA8, 0xA4, 0xA6, 255), outline=ST_OUT)
        d.rectangle([px, py - 7, px + 1, py - 1], fill=(0x82, 0x7E, 0x84, 255))
        d.line([px - 2, py - 7, px - 1, py - 7], fill=(0xD0, 0xCC, 0xCC, 255))
        solid.add((x0 + px // T, y0 + py // T))
    for ty in range(y1 - y0 + 1):
        for tx in range(x1 - x0 + 1):
            tile = cv.crop((tx * T, ty * T, tx * T + T, ty * T + T))
            if tile.getchannel("A").getbbox():
                L.put("Objects", x0 + tx, y0 + ty, tile, (x0 + tx, y0 + ty) in solid, "alpha")


def soldiers_circle(L):
    cx, cy = CIRCLE_C
    L.place("cem_soldier_monument", 81, 2)                  # granite base on y=4..5, bronze figure above
    for (x, y) in ((79, 3), (84, 3), (79, 6), (84, 6)):     # four guns at the diagonals
        L.place("cem_cannon", x, y)
    # concentric arcs of small white government stones
    for (x, y) in ((78, 4), (78, 5), (85, 4), (85, 5), (80, 4), (83, 4), (80, 3), (83, 3)):
        L.place("cem_marker", x, y)
    chain_ring(L, cx, cy - 0.2, 4.9, 2.2)
    L.marker("sign", 81, 7, id="soldiers_lot", text="Soldiers' Lot, 1862")


def chapel(L):
    L.place("cf_gothic_chapel_with_vault", 118, -1)   # catalog doors -> markers at (120,7) and (124,7)


def secrets(L):
    # S4 receiving vault: arched iron door set into the rocky bank, reached from the lower loop
    L.place("cf_receiving_vault_arch", 90, 9)
    L.marker("secret", 91, 11, id="S4", note="receiving vault door in the cliff face; interact from (91,12)")
    # S5 forgotten mausoleum in the overgrown NW corner of the upper terrace (via the west stairs)
    L.place("cem_mausoleum", 67, 0)
    L.marker("secret", 68, 3, id="S5", note="forgotten mausoleum; interact from (68,4)")


def fits(L, pid, x, y, roads, pad=0, canopy_ok=False):
    """Strict placement test: base cells in bounds, on walkable ground, off the roads, clear of other
    objects (+pad ring) and not hidden under another prop's overhead; overhead cells may run off the
    map top, and only overlap other canopies when canopy_ok (tree groves)."""
    return why_not(L, pid, x, y, roads, pad, canopy_ok) is None


def why_not(L, pid, x, y, roads, pad=0, canopy_ok=False):
    obj, ovh = dress.footprint(L, pid, x, y)
    for (cx, cy) in obj:
        if not L.inb(cx, cy) or dress.ground_solid(L, cx, cy):
            return f"base {cx},{cy} out/solid ground"
        if (cx, cy) in roads:
            return f"base {cx},{cy} on road"
        if (cx, cy) in L.cells["Overhead"]:
            return f"base {cx},{cy} under overhead"
        for dy in range(-pad, pad + 1):
            for dx in range(-pad, pad + 1):
                c = (cx + dx, cy + dy)
                if c in L.cells["Objects"] or c in L.extra_solid:
                    return f"base {c} hits object"
    for c in ovh:
        if not L.inb(*c):
            continue
        if c in L.cells["Objects"] and not canopy_ok:
            return f"top {c} hits object"
        if c in L.cells["Overhead"] and not canopy_ok:
            return f"top {c} hits overhead"
    return None


def place_list(L, items, roads, pad=0, tag="", canopy_ok=False):
    n = 0
    for (pid, x, yb) in items:
        y = yb - L.lib[pid].h + 1
        if fits(L, pid, x, y, roads, pad, canopy_ok):
            L.place(pid, x, y)
            n += 1
        else:
            print(f"  [cemetery] {tag} skipped {pid} @({x},{yb}): {why_not(L, pid, x, y, roads, pad, canopy_ok)}")
    return n


def hush(img):
    """Deepen foliage toward the cemetery's hushed blue-green (leaves trunks/stone alone)."""
    out = img.copy()
    px = out.load()
    for y in range(out.size[1]):
        for x in range(out.size[0]):
            r, g, b, a = px[x, y]
            if a and g > r + 8 and g >= b:
                px[x, y] = (int(r * 0.78), int(g * 0.84), min(255, int(b * 0.92 + 14)), a)
    return out


TREE_IDS = ["nt_s27_oak_huge", "nt_s26_oak_large", "nt_s26_tree_dark_round", "nt_s27_tree_tall_canopy",
            "nt_s20_oak_spreading", "nt_s17_oak_round_big", "nt_s26_conifer_tall", "nt_s27_spruce_tall",
            "nt_s26_conifer_short"]


def register_trees(lib):
    for pid in TREE_IDS:
        cid = "cem_" + pid[3:]
        if cid not in lib:
            p = lib[pid]
            lib.add_img(cid, hush(p.img), "tree", sorted(p.solid), p.overhead_rows)


def trees(L, roads):
    t = lambda pid: "cem_" + pid[3:]
    big = [
        # upper terrace: older, darker, denser
        ("nt_s27_spruce_tall", 70, 3), ("nt_s26_conifer_tall", 72, 6),
        ("nt_s27_oak_huge", 90, 5), ("nt_s26_tree_dark_round", 95, 2),
        ("nt_s27_tree_tall_canopy", 111, 1),
        ("nt_s27_spruce_tall", 115, 5), ("nt_s26_conifer_tall", 116, 1),
        ("nt_s27_spruce_tall", 126, 1), ("nt_s26_conifer_tall", 133, 4), ("nt_s26_conifer_tall", 131, 1),
        ("nt_s26_conifer_short", 101, 6), ("nt_s26_conifer_short", 110, 6),
        ("nt_s26_oak_large", 73, 1), ("nt_s26_conifer_short", 87, 1),
        # lower terrace
        ("nt_s20_oak_spreading", 70, 15), ("nt_s26_conifer_tall", 69, 18), ("nt_s27_oak_huge", 85, 21),
        ("nt_s27_spruce_tall", 104, 16), ("nt_s27_spruce_tall", 112, 18), ("nt_s26_tree_dark_round", 121, 17),
        ("nt_s26_conifer_tall", 133, 21), ("nt_s17_oak_round_big", 101, 21), ("nt_s26_conifer_short", 125, 16),
        ("nt_s26_conifer_short", 76, 21), ("nt_s26_conifer_tall", 66, 21),
    ]
    return place_list(L, [(t(p), x, y) for (p, x, y) in big], roads, tag="tree", canopy_ok=True)


def headstone_rows(L, roads, rng):
    """Loose curved rows that follow the drives: each stone's base row tracks the nearest road edge."""
    count = [0]

    def row(xs, yfun, family, jitter=(0, 0, 0, 1, -1), skip=0.1):
        for x in xs:
            if rng.random() < skip:
                continue
            yb = yfun(x)
            if yb is None:
                continue
            pid = rng.choice(family)
            p = L.lib[pid]
            for j in (rng.choice(jitter), 0):
                y = yb + j - p.h + 1
                if fits(L, pid, x, y, roads):
                    L.place(pid, x, y)
                    count[0] += 1
                    break
            else:
                if DEBUG:
                    print("   row miss", pid, x, yb, why_not(L, pid, x, yb - p.h + 1, roads))

    def below(ylo, yhi, gap=2):
        """Base row `gap` rows below the road's lower edge in [ylo,yhi] (stone faces the road)."""
        def f(x):
            e = road_edge(x, ylo, yhi, top=False)
            return None if e is None else e + gap
        return f

    def above(ylo, yhi, gap=2):
        """Base row `gap` rows above the road's upper edge in [ylo,yhi]."""
        def f(x):
            e = road_edge(x, ylo, yhi, top=True)
            return None if e is None else e - gap
        return f

    mixed = HEAD_MARBLE * 2 + HEAD_SAND
    # --- lower terrace
    row(range(86, 106, 2), below(12, 14), mixed)                       # under the lower loop
    row(range(87, 106, 2), above(16, 21), HEAD_SAND + HEAD_MARBLE)      # above the west drive
    row(range(66, 106, 2), lambda x: 21, HEAD_SAND + HEAD_MARBLE + HEAD_SMALL, jitter=(0,))   # along the wall
    row(range(74, 84, 2), below(12, 14), HEAD_SMALL + HEAD_SLATE, jitter=(0, 1))
    row(range(66, 76, 2), lambda x: 18, HEAD_MARBLE, jitter=(0, 1))
    row(range(122, 134, 2), below(12, 14), HEAD_SAND, jitter=(0, 1))
    row(range(114, 128, 2), lambda x: 21 if x < 122 else None, HEAD_SMALL, jitter=(0,))
    row(range(130, 134, 2), lambda x: 18, HEAD_MARBLE + HEAD_SMALL, jitter=(0,))
    # --- upper terrace
    row(range(89, 120, 2), above(5, 9), mixed)                          # north of the upper loop
    row(range(99, 113, 2), lambda x: 6, HEAD_MARBLE, jitter=(0, -1))    # inside the teardrop lane
    # --- hand-set clusters in the remaining pockets (loose, slightly curved)
    def cluster(pos, family):
        for (x, yb) in pos:
            pid = rng.choice(family)
            y = yb - L.lib[pid].h + 1
            if fits(L, pid, x, y, roads):
                L.place(pid, x, y)
                count[0] += 1
            elif DEBUG:
                print("   cluster miss", pid, x, yb, why_not(L, pid, x, y, roads))
    old = HEAD_SLATE * 2 + HEAD_SMALL
    cluster([(67, 6), (70, 6), (71, 4), (74, 3), (74, 6), (72, 7), (66, 4)], old)                 # NW old ground
    cluster([(94, 4), (96, 4)], HEAD_MARBLE)                                              # under the oaks
    cluster([(128, 7), (130, 7), (132, 7), (127, 4), (131, 4), (133, 7)], HEAD_SAND + HEAD_SLATE)   # east of chapel
    cluster([(82, 17), (84, 19), (86, 19), (82, 15)], HEAD_MARBLE + HEAD_SAND)          # by the drive fork
    cluster([(128, 21), (132, 21), (127, 18), (129, 19)], HEAD_MARBLE + HEAD_SMALL)       # east corner
    cluster([(87, 3), (93, 6)], HEAD_SAND)                                                # beside the circle
    cluster([(89, 14), (91, 14), (95, 14), (99, 16)], HEAD_MARBLE)                        # strip under the loop
    cluster([(121, 19), (127, 15), (122, 21 - 2)], HEAD_SAND + HEAD_SMALL)              # gatehouse lawn
    cluster([(102, 3), (108, 3), (99, 6), (112, 6)], HEAD_MARBLE + HEAD_SLATE)            # teardrop
    cluster([(66, 21), (68, 21), (70, 21), (74, 19), (72, 18)], HEAD_SMALL + HEAD_MARBLE)  # west corner
    cluster([(91, 17), (94, 17), (99, 17), (101, 17), (103, 17)], HEAD_SMALL)          # second, humbler row
    cluster([(100, 7), (112, 7), (121, 18), (123, 19)], HEAD_SAND + HEAD_SMALL)
    # floral tributes at a few graves
    for (x, y, pid) in ((80, 21, "nt_s81_flower_box_red"), (96, 21, "nt_s81_flower_box_yellow"),
                        (126, 21, "nt_s81_flower_box_red"), (69, 19, "nt_s81_flower_box_yellow")):
        if fits(L, pid, x, y, roads):
            L.place(pid, x, y)
    return count[0]


def monuments(L, roads):
    items = [
        ("cem_obelisk_tall", 96, 16),                 # the tall white obelisk (brief: ~(96,15))
        ("cem_obelisk", 74, 17), ("cem_obelisk", 117, 6), ("cem_obelisk", 129, 4),
        ("cem_obelisk_small", 90, 21),
        ("cf_angel_praying_vines", 77, 19), ("nt_s70_angel_statue", 104, 6),
        ("cf_urn_maiden_basin_vines_marble", 92, 21), ("nt_s70_urn_statue", 130, 21),
        ("cf_broken_column_marble", 102, 16), ("cf_broken_column_sandstone", 95, 6),
        ("nt_s81_cross_grey_tall", 93, 15), ("nt_s81_cross_tan_tall", 82, 17),
        ("cf_column_short_marble", 88, 16),
    ]
    return place_list(L, items, roads, tag="monument")


def family_plots(L, roads):
    n = 0
    for (x, y, stones) in ((65, 14, ("nt_s81_headstone_grey", "nt_s81_headstone_grey_cross")),
                           (131, 14, ("nt_s81_headstone_tan", "nt_s81_headstone_tan_cross"))):
        if fits(L, "cf_iron_railed_family_plot", x, y, roads):
            L.place("cf_iron_railed_family_plot", x, y)
            L.place(stones[0], x + 1, y + 2)
            L.place(stones[1], x + 2, y + 2)
            n += 1
        else:
            print("  [cemetery] family plot skipped", x, y)
    return n


def furniture(L, roads):
    items = [
        ("sf_bench_wood_long", 97, 21),
        ("sf_bench_wood_small", 72, 21), ("sf_bench_wood_small", 126, 7),
        ("sy_lamp_iron", 106, 15), ("sy_lamp_iron", 111, 15),
        ("sp_wheelbarrow_tools", 79, 21),
    ]
    place_list(L, items, roads, tag="furniture")
    L.marker("npc", 82, 20, id="groundskeeper", note="tending graves beside the wheelbarrow")


def build(L, lib):
    register(lib)
    register_trees(lib)
    rng = random.Random(1849)
    roads = road_cells() | set(L.stairs)
    boundary(L)
    gate(L)
    chapel(L)
    secrets(L)
    L.place("cem_gatehouse", 114, 14)
    L.marker("door", 117, 19, id="gatehouse")
    soldiers_circle(L)
    nm = monuments(L, roads)
    nf = family_plots(L, roads)
    nt = trees(L, roads)
    furniture(L, roads)
    nh = headstone_rows(L, roads, rng)
    print(f"  [cemetery] trees {nt}, monuments {nm}, family plots {nf}, headstones {nh}")
