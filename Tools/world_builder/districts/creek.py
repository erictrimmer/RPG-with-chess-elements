"""Codorus Creek + railroad district (brief 1.2, 3.1, 3.2, 2.6 S1, 5).

Owns: west bank path + vertical channel x=38..55 (y=36..127), the horizontal creek arm and its
lips x=54..159 (y=36..47, incl. the inner creek walk), and the rail bed y=124..127 (x=0..159).

Mood: cold, grey, industrial and empty. Concrete parapets + 1950s lamp standards on the road
bridges, a rust-red riveted truss footbridge, galvanized pipe railing on the copings, rusty
outfall pipes staining the flood walls, junk in the murky water, one white heron, and the
fisherman on the gravel shoal (secret S1). Railroad: ballast, ties, rails, black steel trestle
over the creek, crossbucks + flashers at George St, two semaphore signals, a telegraph pole line.
"""
import random

from PIL import Image, ImageDraw

import synth

REGION = (0, 36, 159, 127)
T = 16

OUT = (0x3D, 0x3D, 0x52, 255)
RUST = (0x9A, 0x4A, 0x2E, 255)
RUST_D = (0x6A, 0x30, 0x22, 255)
RUST_L = (0xC2, 0x6C, 0x44, 255)
RED = (0xA8, 0x3A, 0x2C, 255)       # bridge red-oxide paint
RED_L = (0xCC, 0x5E, 0x46, 255)
RED_D = (0x6E, 0x26, 0x20, 255)
BLK = (0x2A, 0x2C, 0x34, 255)       # black steel
BLK_L = (0x4C, 0x50, 0x5C, 255)
BLK_H = (0x70, 0x76, 0x84, 255)
CONC = (0xB4, 0xB2, 0xBA, 255)
CONC_D = (0x8E, 0x8C, 0x96, 255)
TIE = (0x6A, 0x4A, 0x36, 255)
TIE_D = (0x4A, 0x32, 0x26, 255)
RAIL = (0xC8, 0xCC, 0xD4, 255)
RAIL_D = (0x5A, 0x5C, 0x66, 255)
WEED = [(0x5E, 0x8A, 0x3E, 255), (0x48, 0x6E, 0x34, 255), (0x7A, 0xA0, 0x4A, 255)]

# bridge decks (brief 3.2)
MARKET_Y = (78, 87)
KING_Y = (104, 111)
FOOT_Y = (62, 65)
GEORGE_X = (104, 113)


# --------------------------------------------------------------------------- helpers
def stamp(L, img, x, y, solid=(), overhead=0, layer="Objects"):
    """Cut an image into 16px tiles at (x,y). Rows < overhead go to Overhead (never solid)."""
    w, h = img.size[0] // T, img.size[1] // T
    solid = set(solid)
    for ry in range(h):
        for rx in range(w):
            t = img.crop((rx * T, ry * T, rx * T + T, ry * T + T))
            if not t.getchannel("A").getbbox():
                continue
            if ry < overhead:
                L.put("Overhead", x + rx, y + ry, t, False, "alpha")
            else:
                s = (rx, ry) in solid and layer == "Objects"
                L.put(layer, x + rx, y + ry, t, s, "alpha")


def canvas(w, h):
    img = Image.new("RGBA", (w * T, h * T))
    return img, ImageDraw.Draw(img)


def rivets(d, x0, x1, y, col, step=3):
    for x in range(x0, x1 + 1, step):
        d.point((x, y), fill=col)


# --------------------------------------------------------------------------- footbridge truss
def truss_cell(i, n):
    """One 16x32 cell of a rust-red riveted pony truss seen side-on (bottom = cell bottom).
    i = index along the span (0..n-1). Upper half goes to the row above."""
    img, d = canvas(1, 2)
    base = 30
    top = 13
    # bottom chord
    d.rectangle([0, base - 4, 15, base], fill=RED)
    d.line([0, base - 4, 15, base - 4], fill=RED_L)
    d.line([0, base + 1, 15, base + 1], fill=OUT)
    d.line([0, base - 5, 15, base - 5], fill=OUT)
    rivets(d, 1, 15, base - 2, RED_D, 3)
    # top chord (end cells: the raked end post takes over)
    tx0 = 8 if i == 0 else 0
    tx1 = 7 if i == n - 1 else 15
    d.rectangle([tx0, top, tx1, top + 3], fill=RED)
    d.line([tx0, top, tx1, top], fill=RED_L)
    d.line([tx0, top - 1, tx1, top - 1], fill=OUT)
    d.line([tx0, top + 4, tx1, top + 4], fill=OUT)
    rivets(d, tx0 + 1, tx1, top + 2, RED_D, 3)
    if i == 0:
        d.line([1, base - 5, 8, top + 1], fill=OUT, width=4)
        d.line([1, base - 5, 8, top + 1], fill=RED, width=2)
    elif i == n - 1:
        d.line([14, base - 5, 7, top + 1], fill=OUT, width=4)
        d.line([14, base - 5, 7, top + 1], fill=RED, width=2)
    else:
        d.rectangle([7, top + 4, 8, base - 5], fill=RED)
        d.line([6, top + 4, 6, base - 5], fill=OUT)
        d.line([9, top + 4, 9, base - 5], fill=RED_D)
        if i < n / 2:
            d.line([9, top + 5, 15, base - 6], fill=RED_D)
            d.line([10, top + 5, 15, base - 7], fill=RED)
        else:
            d.line([0, base - 6, 6, top + 5], fill=RED_D)
            d.line([0, base - 7, 5, top + 5], fill=RED)
        for gy in (top + 4, base - 6):     # gusset plates
            d.rectangle([5, gy - 1, 10, gy + 1], fill=RED_L)
            d.point((7, gy), fill=RED_D)
    return img


def checker_plate(x, y):
    img = Image.new("RGBA", (T, T), (0x6E, 0x6A, 0x70, 255))
    px = img.load()
    for yy in range(0, T, 3):
        for xx in range(T):
            m = (xx + 2 * yy) % 6
            if m == 0:
                px[xx, yy] = (0x8E, 0x8A, 0x92, 255)
            elif m == 1:
                px[xx, yy] = (0x52, 0x50, 0x58, 255)
    if x % 3 == 0:
        for yy in range(T):
            px[0, yy] = (0x4A, 0x46, 0x50, 255)
    r = random.Random(x * 131 + y)
    for _ in range(r.randint(0, 3)):
        px[r.randint(1, 14), r.randint(1, 14)] = RUST
    return img


def footbridge(L):
    x0, x1 = 42, 53
    n = x1 - x0 + 1
    y_n, y_s = FOOT_Y
    for y in range(y_n, y_s + 1):
        for x in range(x0, x1 + 1):
            L.put("Decals", x, y, checker_plate(x, y))
    for i, x in enumerate(range(x0, x1 + 1)):
        for (row, front) in ((y_n, False), (y_s, True)):
            cv = truss_cell(i, n)
            L.put("Objects", x, row, cv.crop((0, T, T, 2 * T)), True, "full")
            L.put("Overhead" if front else "Objects", x, row - 1, cv.crop((0, 0, T, T)), False, "alpha")
    # red fascia girder on the wall face below the deck
    for x in range(44, 52):
        img, d = canvas(1, 1)
        d.rectangle([0, 0, 15, 5], fill=RED)
        d.line([0, 0, 15, 0], fill=RED_L)
        d.line([0, 6, 15, 6], fill=OUT)
        rivets(d, 1, 15, 3, RED_D, 3)
        d.rectangle([0, 7, 15, 12], fill=(0x10, 0x18, 0x20, 90))
        L.put("Decals", x, y_s + 1, img)


# --------------------------------------------------------------------------- flood wall details
def outfall(big=False, seed=0):
    """3 rows (wall face rows 0..1 + water row 2): rusty pipe mouth, stain, murky plume."""
    r = random.Random(seed)
    img, d = canvas(2 if big else 1, 3)
    W = img.size[0]
    cx = W // 2
    st = Image.new("RGBA", img.size)
    sd = ImageDraw.Draw(st)
    sd.polygon([(cx - 3, 10), (cx + 3, 10), (cx + 4 + r.randint(0, 2), 32), (cx - 4 - r.randint(0, 2), 32)],
               fill=(0x2E, 0x26, 0x1E, 120))
    sd.polygon([(cx - 1, 12), (cx + 2, 12), (cx + 2, 31), (cx - 2, 31)], fill=(0x4A, 0x2C, 0x1C, 110))
    sd.ellipse([cx - 7, 31, cx + 7, 40], fill=(0x4E, 0x46, 0x30, 90))
    sd.ellipse([cx - 4, 33, cx + 5, 38], fill=(0x5A, 0x50, 0x36, 90))
    img.alpha_composite(st)
    d = ImageDraw.Draw(img)
    for k in range(5):
        d.point((cx - 6 + r.randint(0, 12), 32 + r.randint(0, 7)), fill=(0xC8, 0xC4, 0xA8, 200))
    if big:
        d.rectangle([2, 1, W - 3, 14], fill=CONC, outline=OUT)
        d.rectangle([2, 1, W - 3, 3], fill=(0xC8, 0xC6, 0xCC, 255), outline=OUT)
        d.ellipse([cx - 9, 4, cx + 8, 18], fill=(0x18, 0x18, 0x1E, 255), outline=OUT)
        for bx in range(cx - 7, cx + 8, 3):
            d.line([bx, 5, bx, 16], fill=RUST)
        d.line([cx - 8, 10, cx + 7, 10], fill=RUST_D)
    else:
        d.ellipse([cx - 5, 3, cx + 4, 12], fill=RUST, outline=OUT)
        d.ellipse([cx - 3, 5, cx + 2, 10], fill=(0x16, 0x14, 0x18, 255))
        d.arc([cx - 5, 3, cx + 4, 12], 200, 300, fill=RUST_L)
        d.line([cx - 1, 11, cx - 1, 14], fill=(0x5E, 0x5A, 0x3E, 255))
    return img


def flood_gauge():
    """Painted staff gauge on the wall face: white board, black ticks, red/amber flood bands."""
    img, d = canvas(1, 2)
    d.rectangle([5, 1, 10, 31], fill=(0xE6, 0xE4, 0xDA, 255), outline=OUT)
    for y in range(3, 31, 2):
        d.line([6, y, 7 if y % 6 else 9, y], fill=(0x2A, 0x2A, 0x30, 255))
    d.rectangle([6, 2, 9, 6], fill=(0xC0, 0x34, 0x2C, 255))
    d.rectangle([6, 12, 9, 13], fill=(0xE0, 0xB0, 0x3C, 255))
    d.line([11, 4, 11, 30], fill=(0x50, 0x48, 0x40, 160))
    return img


def weed(seed, wall=False):
    r = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    bx = r.randint(2, 12)
    by = r.randint(4, 13) if wall else r.randint(6, 14)
    for _ in range(r.randint(3, 5)):
        c = WEED[r.randint(0, 2)]
        dx = r.randint(-3, 3)
        d.line([bx + dx // 2, by, bx + dx, by - r.randint(2, 5)], fill=c)
    d.point((bx, by + 1), fill=(0x3A, 0x4A, 0x2C, 255))
    return img


def crack(seed):
    r = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    x, y = r.randint(2, 13), r.randint(2, 13)
    for _ in range(r.randint(3, 5)):
        nx, ny = x + r.randint(-3, 3), y + r.randint(-3, 3)
        d.line([x, y, nx, ny], fill=(0x7A, 0x74, 0x70, 180))
        x, y = max(0, min(15, nx)), max(0, min(15, ny))
    return img


# --------------------------------------------------------------------------- water junk / heron
def tyre_in_water():
    img, d = canvas(1, 1)
    d.ellipse([0, 9, 15, 14], outline=(0x7A, 0xA8, 0xA8, 160))
    d.ellipse([2, 5, 13, 12], fill=(0x22, 0x22, 0x26, 255), outline=OUT)
    d.ellipse([5, 7, 10, 10], fill=(0x3C, 0x6A, 0x70, 255))
    d.arc([2, 5, 13, 12], 190, 260, fill=(0x55, 0x55, 0x5E, 255))
    return img


def cart_in_water():
    """Tipped shopping cart, half sunk: wire basket corner and the handle sticking out."""
    img, d = canvas(1, 1)
    wire = (0xA8, 0xAC, 0xB4, 255)
    d.polygon([(2, 11), (9, 4), (14, 7), (8, 13)], outline=wire)
    for k in range(3, 10, 2):
        d.line([2 + k * 0.6, 11 - k * 0.6, 8 + k * 0.6, 13 - k * 0.6], fill=(0x86, 0x8A, 0x94, 255))
    d.line([9, 4, 12, 1], fill=wire)
    d.line([11, 0, 14, 2], fill=(0xC0, 0x34, 0x2C, 255))
    d.line([1, 12, 10, 14], fill=(0x7A, 0xA8, 0xA8, 170))
    return img


def flotsam(seed):
    r = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    kind = seed % 4
    x, y = r.randint(3, 10), r.randint(4, 11)
    if kind == 0:
        d.rectangle([x - 2, y, x + 5, y + 1], fill=(0x7A, 0x5A, 0x3E, 255))
        d.line([x - 2, y + 2, x + 5, y + 2], fill=(0x2A, 0x4A, 0x50, 200))
    elif kind == 1:
        d.line([x, y, x + 3, y], fill=(0x5C, 0x8A, 0x4E, 255))
        d.point((x + 4, y), fill=(0xD8, 0xD0, 0xB0, 255))
    elif kind == 2:
        d.ellipse([x - 3, y - 1, x + 5, y + 3], outline=(0x8A, 0x6E, 0x9A, 120))
        d.arc([x - 2, y, x + 4, y + 2], 0, 180, fill=(0xA8, 0x98, 0x5A, 120))
    else:
        for _ in range(6):
            d.point((x + r.randint(-3, 3), y + r.randint(-1, 2)), fill=(0xB8, 0xB4, 0x98, 190))
    return img


def heron():
    """The one bird: a pale heron standing in the shallows. 1x2."""
    img, d = canvas(1, 2)
    wh = (0xEC, 0xEC, 0xE8, 255)
    gr = (0xA8, 0xAE, 0xBC, 255)
    dk = (0x5A, 0x60, 0x70, 255)
    d.ellipse([3, 27, 14, 31], outline=(0x7A, 0xA8, 0xA8, 200))
    d.line([8, 21, 8, 28], fill=dk)
    d.line([10, 21, 11, 28], fill=dk)
    d.ellipse([5, 13, 14, 22], fill=wh, outline=OUT)
    d.line([8, 19, 14, 21], fill=gr)
    d.line([12, 15, 15, 21], fill=gr)
    d.line([7, 14, 5, 10], fill=OUT, width=3)
    d.line([5, 10, 7, 6], fill=OUT, width=3)
    d.line([7, 14, 5, 10], fill=wh)
    d.line([5, 10, 7, 6], fill=wh)
    d.ellipse([5, 3, 9, 7], fill=wh, outline=OUT)
    d.line([4, 5, 1, 6], fill=(0xE0, 0xB4, 0x3C, 255))
    d.line([8, 4, 11, 3], fill=dk)
    d.point((6, 4), fill=OUT)
    return img


# --------------------------------------------------------------------------- shoal gear
def pebbles(seed):
    r = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    for _ in range(r.randint(2, 4)):
        x, y = r.randint(1, 13), r.randint(2, 13)
        c = r.choice([(0x8A, 0x84, 0x7C, 255), (0xA4, 0x9C, 0x90, 255), (0x6E, 0x68, 0x64, 255)])
        d.ellipse([x, y, x + r.randint(1, 3), y + r.randint(1, 2)], fill=c, outline=None)
        d.point((x, y + 3), fill=(0x4A, 0x46, 0x44, 160))
    if r.random() < 0.3:   # driftwood twig
        x, y = r.randint(2, 9), r.randint(4, 12)
        d.line([x, y, x + 5, y + 1], fill=(0x8A, 0x74, 0x5A, 255))
    return img


def deck_shadow():
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 3, 15], fill=(0x0E, 0x1A, 0x22, 110))
    d.rectangle([4, 0, 5, 15], fill=(0x0E, 0x1A, 0x22, 55))
    return img


def rod_holder():
    """3x2: forked stick in the gravel, rod reaching out over the water, line + red/white bobber."""
    img, d = canvas(3, 2)
    stick = (0x7A, 0x5A, 0x3E, 255)
    d.line([6, 30, 6, 22], fill=stick, width=2)
    d.line([6, 22, 4, 19], fill=stick)
    d.line([6, 22, 9, 19], fill=stick)
    d.line([3, 29, 40, 4], fill=(0x3A, 0x3A, 0x42, 255))
    d.line([3, 30, 9, 26], fill=(0x8A, 0x5A, 0x34, 255), width=2)
    d.ellipse([7, 24, 10, 27], fill=(0x9A, 0x9E, 0xA8, 255), outline=OUT)
    d.line([40, 4, 42, 22], fill=(0xD8, 0xD8, 0xD0, 200))
    d.ellipse([37, 24, 47, 28], outline=(0x7A, 0xA8, 0xA8, 200))
    d.ellipse([40, 21, 44, 25], fill=(0xD8, 0x3A, 0x36, 255), outline=OUT)
    d.line([41, 21, 43, 21], fill=(0xF2, 0xEE, 0xE4, 255))
    return img


def bait_bucket():
    img, d = canvas(1, 1)
    d.ellipse([3, 12, 13, 15], fill=(0, 0, 0, 60))
    d.polygon([(4, 6), (12, 6), (11, 14), (5, 14)], fill=(0x9A, 0x9E, 0xA8, 255), outline=OUT)
    d.ellipse([4, 4, 12, 8], fill=(0x3C, 0x5A, 0x60, 255), outline=OUT)
    d.arc([4, 0, 12, 10], 180, 360, fill=OUT)
    d.line([6, 8, 6, 13], fill=(0xC4, 0xC8, 0xD0, 255))
    return img


# --------------------------------------------------------------------------- railroad
def trestle_tile(x, r):
    """Rows r=0..3 (y=124..127) of the open-deck black steel trestle over the creek."""
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    over_water = 44 <= x <= 51
    if r in (0, 1, 2):
        ya = 4 if r == 0 else 0
        yb = 15 if r < 2 else 10
        if not over_water:   # deck on the abutment: ballast-grey
            d.rectangle([0, ya, 15, yb], fill=(0x5A, 0x5C, 0x64, 255))
        if r == 0:   # north plate girder (continues up into row 123)
            d.rectangle([0, 0, 15, 4], fill=BLK)
            d.line([0, 5, 15, 5], fill=OUT)
            rivets(d, 1, 15, 2, BLK_L, 3)
            for sx in (0, 8):
                d.line([sx, 0, sx, 4], fill=BLK_L)
            d.rectangle([0, 9, 15, 13], fill=BLK)           # stringer under the north rail
        if r == 2:
            d.rectangle([0, 2, 15, 6], fill=BLK)            # stringer under the south rail
        for tx in (2, 10):
            t0 = ya + 2 if r == 0 else ya
            d.rectangle([tx, t0, tx + 3, yb], fill=TIE)
            d.line([tx + 3, t0, tx + 3, yb], fill=TIE_D)
        for yy in {0: [11], 1: [], 2: [4]}[r]:
            d.line([0, yy, 15, yy], fill=RAIL)
            d.line([0, yy + 1, 15, yy + 1], fill=RAIL_D)
        if r == 2:   # south plate girder face begins
            d.rectangle([0, 11, 15, 15], fill=BLK)
            d.line([0, 11, 15, 11], fill=BLK_H)
            rivets(d, 1, 15, 13, BLK_L, 3)
    else:
        d.rectangle([0, 0, 15, 6], fill=BLK)
        d.line([0, 7, 15, 7], fill=OUT)
        rivets(d, 1, 15, 2, BLK_L, 3)
        for sx in (0, 8):                      # stiffeners + lattice bracing
            d.line([sx, 0, sx, 6], fill=BLK_L)
            d.line([sx + 1, 1, sx + 7, 5], fill=(0x3A, 0x3E, 0x48, 255))
            d.line([sx + 1, 5, sx + 7, 1], fill=(0x3A, 0x3E, 0x48, 255))
        if x in (43, 52):
            d.rectangle([4, 4, 11, 9], fill=BLK_L, outline=OUT)
        if over_water:
            d.rectangle([0, 8, 15, 15], fill=(0x0E, 0x1A, 0x22, 110))
    return img


def crossing_panel(r):
    """Timber grade-crossing planks at George St (the rails stay solid / uncrossable)."""
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    ya, yb = (6, 15) if r == 0 else ((0, 15) if r == 1 else (0, 9))
    d.rectangle([0, ya, 15, yb], fill=(0x7E, 0x6E, 0x5C, 255))
    for yy in range(ya + 2, yb + 1, 3):
        d.line([0, yy, 15, yy], fill=(0x5E, 0x50, 0x44, 255))
    for yy in {0: [11], 1: [], 2: [4]}[r]:
        d.line([0, yy, 15, yy], fill=RAIL)
        d.line([0, yy + 1, 15, yy + 1], fill=RAIL_D)
    return img


def crossbuck():
    """1960s crossbuck: white X boards (no text) over twin red flasher lamps. 1x3."""
    img, d = canvas(1, 3)
    wh = (0xF2, 0xEE, 0xE4, 255)
    d.rectangle([7, 8, 8, 46], fill=(0xD8, 0xD8, 0xDC, 255))
    d.line([6, 8, 6, 46], fill=OUT)
    d.line([9, 8, 9, 46], fill=(0x8A, 0x8C, 0x96, 255))
    for (a, b) in (((0, 1), (15, 13)), ((15, 1), (0, 13))):
        d.line([a, b], fill=OUT, width=4)
    for (a, b) in (((0, 1), (15, 13)), ((15, 1), (0, 13))):
        d.line([a, b], fill=wh, width=2)
    d.rectangle([1, 19, 14, 20], fill=OUT)
    for lx in (3, 12):
        d.ellipse([lx - 3, 17, lx + 3, 23], fill=(0x22, 0x22, 0x28, 255), outline=OUT)
        d.ellipse([lx - 1, 19, lx + 1, 21], fill=(0xE0, 0x30, 0x28, 255))
    d.rectangle([6, 26, 9, 29], fill=(0x2A, 0x2A, 0x30, 255))
    d.rectangle([4, 44, 11, 47], fill=(0x8A, 0x8C, 0x96, 255), outline=OUT)
    return img


def semaphore():
    """Semaphore signal: lattice mast + ladder, red blade with white band, lamp spectacle. 1x4."""
    img, d = canvas(1, 4)
    d.rectangle([6, 6, 9, 61], fill=BLK)
    d.line([5, 6, 5, 61], fill=OUT)
    d.line([10, 6, 10, 61], fill=OUT)
    for y in range(10, 60, 4):
        d.line([6, y, 9, y + 3], fill=BLK_L)
    d.ellipse([5, 2, 10, 7], fill=BLK_L, outline=OUT)
    d.line([12, 18, 12, 61], fill=BLK_L)
    d.line([14, 18, 14, 61], fill=BLK_L)
    for y in range(20, 61, 4):
        d.line([12, y, 14, y], fill=BLK_L)
    d.polygon([(0, 11), (8, 11), (8, 15), (0, 15)], fill=(0xC8, 0x30, 0x2C, 255), outline=OUT)
    d.line([2, 12, 2, 14], fill=(0xF2, 0xEE, 0xE4, 255))
    d.rectangle([9, 12, 15, 17], fill=BLK, outline=OUT)
    d.point((11, 14), fill=(0xE0, 0x30, 0x28, 255))
    d.point((13, 14), fill=(0x4A, 0xC0, 0x6A, 255))
    d.rectangle([6, 20, 10, 24], fill=BLK_L, outline=OUT)
    d.point((8, 22), fill=(0xFF, 0xE0, 0x90, 255))
    d.rectangle([3, 58, 12, 63], fill=CONC_D, outline=OUT)
    return img


def ballast_edge(seed):
    r = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    for _ in range(10):
        d.point((r.randint(0, 15), r.randint(0, 15)),
                fill=r.choice([(0x5A, 0x56, 0x5A, 255), (0x7E, 0x78, 0x76, 255), (0x48, 0x40, 0x3E, 255)]))
    if r.random() < 0.18:
        x = r.randint(2, 12)
        d.line([x, 9, x + 2, 9], fill=RUST_D)
    return img


# --------------------------------------------------------------------------- build
def build_ground(L, lib):
    # Market St sidewalks continue across the gravel strip of the west bank path
    for y in (78, 79, 86, 87):
        for x in (38, 39):
            L.set_kind(x, y, "sidewalk")


def on_deck(x, y):
    if 42 <= x <= 53 and any(a <= y <= b for a, b in (FOOT_Y, MARKET_Y, KING_Y)):
        return True
    return GEORGE_X[0] <= x <= GEORGE_X[1] and 36 <= y <= 47


def build(L, lib):
    rng = random.Random(1933)
    # ------------------------------------------------ road bridge parapets + lamp standards
    for y in MARKET_Y + KING_Y:
        synth.parapet_h(L, 42, 53, y)
    for x in GEORGE_X:
        synth.parapet_v(L, x, 36, 45)
    for yb in MARKET_Y:                    # Market St (1951): cobra-heads, leaning over the deck
        L.place("sy_lamp_cobra_r", 42, yb - 4)
        L.place("sy_lamp_cobra_l", 52, yb - 4)
    for yb in KING_Y:                      # King St: single-globe iron standards
        L.place("sy_lamp_iron", 42, yb - 2)
        L.place("sy_lamp_iron", 53, yb - 2)
    for x in GEORGE_X:                     # George St: four lamps near the corners
        for yb in (38, 44):
            L.place("sy_lamp_iron", x, yb - 2)

    # ------------------------------------------------ Philadelphia St steel footbridge
    footbridge(L)

    # ------------------------------------------------ pipe railing on the copings
    def run(x, ys, skip):
        return [(x, y) for y in ys if not any(a <= y <= b for a, b in skip)]
    deck_skip = [FOOT_Y, MARKET_Y, KING_Y]
    west = run(42, range(36, 123), deck_skip + [(92, 93)])     # levee side; gap = shoal stairs
    inner_v = run(53, range(45, 123), deck_skip)               # inner lip beside the Water St walk
    inner_h = [(x, 45) for x in range(53, 160) if not GEORGE_X[0] <= x <= GEORGE_X[1]]
    synth.paint_fence(L, west, "pipe")
    synth.paint_fence(L, inner_v + inner_h, "pipe")

    # ------------------------------------------------ flood wall: outfalls, culverts, gauge, weeds
    pipes = [47, 58, 66, 79, 93, 117, 125, 141, 150, 157]
    for i, x in enumerate(pipes):
        stamp(L, outfall(False, 40 + i), x, 36, layer="Decals")
    stamp(L, outfall(True, 7), 131, 36, layer="Decals")
    stamp(L, outfall(True, 8), 70, 36, layer="Decals")
    stamp(L, flood_gauge(), 102, 36, layer="Decals")
    stamp(L, outfall(False, 90), 49, FOOT_Y[1] + 1, layer="Decals")
    stamp(L, outfall(False, 91), 46, KING_Y[1] + 1, layer="Decals")
    stamp(L, outfall(False, 92), 50, MARKET_Y[1] + 1, layer="Decals")
    used = set(pipes) | {131, 132, 70, 71, 102}
    for x in range(44, 160):
        if x in used or GEORGE_X[0] <= x <= GEORGE_X[1]:
            continue
        if rng.random() < 0.22:
            L.put("Decals", x, 36 + rng.randint(0, 1), weed(x * 7, wall=True))
    # weeds + cracks on the copings and the walks
    for y in range(36, 124):
        for x in (38, 39, 40, 41, 42, 43, 52, 53, 54, 55):
            if (x, y) in L.stairs or L.kind[y][x] == "road" or on_deck(x, y):
                continue
            v = rng.random()
            if v < 0.06:
                L.put("Decals", x, y, weed(x * 1000 + y))
            elif v < 0.10 and x in (40, 41, 54, 55):
                L.put("Decals", x, y, crack(x * 1000 + y))
    for x in range(52, 160):
        for y in (44, 46, 47):
            if on_deck(x, y) or L.kind[y][x] == "road":
                continue
            v = rng.random()
            if v < 0.05:
                L.put("Decals", x, y, weed(x * 1000 + y))
            elif v < 0.08 and y >= 46:
                L.put("Decals", x, y, crack(x * 1000 + y))
    for (x, y) in [(55, 52), (55, 96), (54, 117), (90, 47), (128, 47), (41, 48), (40, 100)]:
        L.place("sf_manhole_brown", x, y)

    # ------------------------------------------------ junk in the water + reeds + heron
    L.put("Objects", 63, 41, tyre_in_water(), True, "full")
    L.put("Objects", 49, 119, tyre_in_water(), True, "full")
    L.put("Objects", 98, 42, cart_in_water(), True, "full")
    for i, (x, y) in enumerate([(60, 40), (84, 42), (116, 39), (122, 41), (146, 40), (155, 42),
                                (50, 57), (45, 74), (48, 103), (46, 122), (88, 39), (138, 42)]):
        L.put("Decals", x, y, flotsam(200 + i))
    L.place("nt_s78_reeds_tall", 44, 100)          # silt tail of the shoal
    L.place("nt_s78_cattails", 47, 90)
    L.place("nt_s78_cattails", 47, 98)
    L.place("nt_s78_rock_in_water", 47, 102)
    L.place("nt_s78_cattails", 44, 38)             # elbow eddy
    L.place("nt_s78_cattails", 45, 39)
    L.place("nt_s78_cattails", 74, 38)             # heron's mud bar
    L.place("nt_s78_cattails", 76, 38)
    L.place("nt_s78_rock_in_water", 77, 40)
    stamp(L, heron(), 75, 39)
    L.place("nt_s78_cattails", 143, 38)
    L.place("nt_s78_rock_in_water", 144, 40)

    # ------------------------------------------------ 'No swimming' pictograms on the copings
    for (x, y) in [(52, 69), (52, 114), (43, 55), (43, 116), (88, 43), (126, 43)]:
        L.place("nt_s78_no_swimming_sign", x, y)
    L.place("nt_s78_no_swimming_sign", 41, 89)     # top of the shoal stairs
    L.place("sp_barrel_rust", 38, 89)

    # ------------------------------------------------ west levee: wooden utility pole line
    for y in (47, 59, 72, 98, 117):
        L.place("sp_utility_pole_crossarm", 38, y - 3)

    # ------------------------------------------------ secret S1: gravel shoal + fisherman
    for y in range(90, 100):
        for x in range(44, 47):
            if rng.random() < 0.45:
                L.put("Decals", x, y, pebbles(x * 77 + y))
    for y in range(38, 44):                        # George St deck shadow on the water
        L.put("Decals", GEORGE_X[1] + 1, y, deck_shadow())
    L.put("Objects", 46, 93, lib["rr_cooler_blue"].img, True, "alpha")
    stamp(L, rod_holder(), 46, 96, solid={(0, 1)})
    L.put("Objects", 46, 99, bait_bucket(), True, "alpha")
    L.marker("npc", 46, 95, id="fisherman", facing="east", note="old fisherman on the gravel shoal (S1)")
    L.marker("secret", 44, 98, id="S1", note="gravel shoal below the Market St bridge")
    L.marker("interact", 46, 97, id="S1_rod", note="propped fishing rod")

    # ------------------------------------------------ railroad
    synth.rail_track_h(L, 0, 41, 124)
    synth.rail_track_h(L, 54, 159, 124)
    for x in range(42, 54):
        for r in range(4):
            L.put("Objects", x, 124 + r, trestle_tile(x, r), True, "full")
        cap = Image.new("RGBA", (T, T))
        cd = ImageDraw.Draw(cap)
        cd.rectangle([0, 10, 15, 15], fill=BLK)
        cd.line([0, 10, 15, 10], fill=BLK_H)
        cd.line([0, 9, 15, 9], fill=OUT)
        if x in (42, 53):
            cd.line([0 if x == 42 else 15, 9, 0 if x == 42 else 15, 15], fill=OUT)
        L.put("Objects", x, 123, cap, False, "alpha")
    for x in range(GEORGE_X[0], GEORGE_X[1] + 1):
        for r in range(3):
            L.put("Decals", x, 124 + r, crossing_panel(r))
    stamp(L, crossbuck(), 105, 120, solid={(0, 2)}, overhead=2)
    stamp(L, crossbuck(), 112, 120, solid={(0, 2)}, overhead=2)
    for x in range(0, 160):
        if not 42 <= x <= 53:
            L.put("Decals", x, 127, ballast_edge(500 + x))
        L.extra_solid.add((x, 127))
    # (telegraph poles removed from the rail band: their tops read as standing on the ties)
    stamp(L, semaphore(), 58, 124, solid={(0, 3)}, overhead=3)
    stamp(L, semaphore(), 150, 124, solid={(0, 3)}, overhead=3)
