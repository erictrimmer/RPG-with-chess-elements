"""Terrain baking for the Yorktowne world builder.

Produces 16x16 RGBA tile images for ground cells from a terrain-type grid + elevation grid,
using RPG Maker MV A2/A4 autotile rules (quarter tiles) on the Modern Exteriors sheets, plus a
sidewalk/curb synthesizer that reuses the pack's own curb colours (measured from Tileset_16).
"""
import hashlib
import os

from PIL import Image

T = 16
H = 8  # quarter tile
HERE = os.path.dirname(os.path.abspath(__file__))
SHEETS = os.path.abspath(os.path.join(HERE, "..", "..", "Assets", "Modern Exteriors", "16px"))

_sheet_cache = {}


def sheet(name):
    if name not in _sheet_cache:
        _sheet_cache[name] = Image.open(os.path.join(SHEETS, name)).convert("RGBA")
    return _sheet_cache[name]


def tile(name, tx, ty, w=1, h=1):
    return sheet(name).crop((tx * T, ty * T, (tx + w) * T, (ty + h) * T))


def rnd(x, y, salt=0):
    """Deterministic per-cell hash in [0,1)."""
    h = hashlib.md5(f"{x},{y},{salt}".encode()).digest()
    return int.from_bytes(h[:4], "little") / 2**32


# --------------------------------------------------------------------------- A2 autotiles
A2 = "A2_Floors_MV_TILESET.png"
A2b = "A2_Floors_MV_TILESET_2.png"
A4 = "A4_Walls_MV_TILESET.png"


def a2_block(sheet_name, bx, by):
    """Return the 32x48 autotile block at block coords (bx,by) on an A2 sheet."""
    return sheet(sheet_name).crop((bx * 32, by * 48, bx * 32 + 32, by * 48 + 48))


def autotile(block, same):
    """RPG Maker A2 composition. block: 32x48 img (or the 32x48 'top' part of an A4 block).
    same(dx,dy) -> bool : neighbour is the same terrain."""
    out = Image.new("RGBA", (T, T))
    N, S, W, E = same(0, -1), same(0, 1), same(-1, 0), same(1, 0)
    NW, NE, SW, SE = same(-1, -1), same(1, -1), same(-1, 1), same(1, 1)

    def q(qx, qy):
        return block.crop((qx * H, qy * H, qx * H + H, qy * H + H))

    # top-left quadrant
    if N and W:
        tl = q(2, 4) if NW else q(2, 0)
    elif N:
        tl = q(0, 4)
    elif W:
        tl = q(2, 2)
    else:
        tl = q(0, 2)
    # top-right
    if N and E:
        tr = q(1, 4) if NE else q(3, 0)
    elif N:
        tr = q(3, 4)
    elif E:
        tr = q(1, 2)
    else:
        tr = q(3, 2)
    # bottom-left
    if S and W:
        bl = q(2, 3) if SW else q(2, 1)
    elif S:
        bl = q(0, 3)
    elif W:
        bl = q(2, 5)
    else:
        bl = q(0, 5)
    # bottom-right
    if S and E:
        br = q(1, 3) if SE else q(3, 1)
    elif S:
        br = q(3, 3)
    elif E:
        br = q(1, 5)
    else:
        br = q(3, 5)
    out.paste(tl, (0, 0))
    out.paste(tr, (H, 0))
    out.paste(bl, (0, H))
    out.paste(br, (H, H))
    return out


def a4_wall(sheet_name, bx, row, left, right):
    """A4 wall face piece. bx = block column (0..), the wall part is tiles y=3..4 of the block.
    row 0 = upper wall tile, 1 = lower wall tile. left/right = wall continues that way."""
    wall = sheet(sheet_name).crop((bx * 32, 48, bx * 32 + 32, 80))  # 32x32 = 4x4 quarters

    def q(qx, qy):
        return wall.crop((qx * H, qy * H, qx * H + H, qy * H + H))

    out = Image.new("RGBA", (T, T))
    qy0 = row * 2
    lx = 2 if left else 0
    rx = 1 if right else 3
    out.paste(q(lx, qy0), (0, 0))
    out.paste(q(rx, qy0), (H, 0))
    out.paste(q(lx, qy0 + 1), (0, H))
    out.paste(q(rx, qy0 + 1), (H, H))
    return out


# --------------------------------------------------------------------------- palette (from Tileset_16 curb)
OUTLINE = (0x3D, 0x3D, 0x52, 255)
SW_LIGHT = (0xD5, 0xC6, 0xB6, 255)
SW_SHADE = (0xA6, 0x9C, 0x8F, 255)
CURB_A = (0x84, 0x7C, 0x75, 255)
CURB_B = (0x9A, 0x8F, 0x83, 255)
ROAD_SH1 = (0x4A, 0x47, 0x52, 255)
ROAD_SH2 = (0x4D, 0x4B, 0x54, 255)
PAINT_W = (0xE8, 0xE4, 0xDC, 255)
PAINT_W2 = (0xC9, 0xC4, 0xBC, 255)
PAINT_Y = (0xE0, 0xB4, 0x3C, 255)

ROAD_SHEET = "Tileset_16_MV.png"


def asphalt(x, y):
    # A2 block (2,0): seamless asphalt fill (tiles 4..5, 1..2)
    return tile(A2, 4 + (x % 2), 1 + (y % 2))


def sidewalk_base(x, y):
    # (6..7, 4..11) is a beige concrete pavement strip; use rows 4..9, pick per 2x2 block
    tx = 6 + (x % 2)
    rows = [4, 5, 6, 7, 8, 9]
    blk = int(rnd(x // 2, y // 2, 7) * 3)
    ty = rows[(blk * 2 + (y % 2)) % len(rows)]
    return tile(ROAD_SHEET, tx, ty)


def _hline(img, y, color, x0=0, x1=15):
    for x in range(x0, x1 + 1):
        img.putpixel((x, y), color)


def _vline(img, x, color, y0=0, y1=15):
    for y in range(y0, y1 + 1):
        img.putpixel((x, y), color)


CURB_EDGE = {"road", "water", "track"}
SOFT_EDGE = {"grass", "dirt", "hill"}


def sidewalk_tile(x, y, kind_at):
    img = sidewalk_base(x, y).copy()
    n, s, w, e = kind_at(x, y - 1), kind_at(x, y + 1), kind_at(x - 1, y), kind_at(x + 1, y)
    nw, ne, sw_, se = kind_at(x - 1, y - 1), kind_at(x + 1, y - 1), kind_at(x - 1, y + 1), kind_at(x + 1, y + 1)
    road_n, road_s, road_w, road_e = (k in CURB_EDGE for k in (n, s, w, e))
    soft_n, soft_s, soft_w, soft_e = (k in SOFT_EDGE for k in (n, s, w, e))
    bottom = 15
    if road_s:
        # curb face seen from the front: light lip, outline, 2px face, outline
        _hline(img, 11, SW_SHADE)
        _hline(img, 12, OUTLINE)
        _hline(img, 13, CURB_A)
        _hline(img, 14, CURB_B)
        _hline(img, 15, OUTLINE)
        bottom = 11
    elif soft_s:
        _hline(img, 15, SW_SHADE)
    if road_n:
        _hline(img, 0, OUTLINE)
        _hline(img, 1, SW_LIGHT)
    elif soft_n:
        _hline(img, 0, SW_SHADE)
    if road_w:
        _vline(img, 0, OUTLINE)
        _vline(img, 1, SW_LIGHT, 1 if road_n else 0, bottom)
        if road_s:
            _vline(img, 0, OUTLINE, 11, 15)
            for yy in (13, 14):
                img.putpixel((1, yy), CURB_A)
    elif soft_w:
        _vline(img, 0, SW_SHADE, 0, bottom)
    if road_e:
        _vline(img, 15, OUTLINE)
        _vline(img, 14, SW_LIGHT, 1 if road_n else 0, bottom)
        if road_s:
            for yy in (13, 14):
                img.putpixel((14, yy), CURB_A)
    elif soft_e:
        _vline(img, 15, SW_SHADE, 0, bottom)
    # rounded outer corners: knock the corner pixel back to asphalt colour
    asp = asphalt(x, y)
    if road_n and road_w:
        img.putpixel((0, 0), asp.getpixel((0, 0)))
        img.putpixel((1, 1), OUTLINE)
    if road_n and road_e:
        img.putpixel((15, 0), asp.getpixel((15, 0)))
        img.putpixel((14, 1), OUTLINE)
    # inner corners (diagonal is road, both sides are pavement)
    if not road_n and not road_w and nw in CURB_EDGE:
        img.putpixel((0, 0), OUTLINE)
    if not road_n and not road_e and ne in CURB_EDGE:
        img.putpixel((15, 0), OUTLINE)
    if not road_s and not road_w and sw_ in CURB_EDGE:
        for yy in range(12, 16):
            img.putpixel((0, yy), OUTLINE)
    if not road_s and not road_e and se in CURB_EDGE:
        for yy in range(12, 16):
            img.putpixel((15, yy), OUTLINE)
    return img


def road_tile(x, y, kind_at):
    img = asphalt(x, y).copy()
    n = kind_at(x, y - 1)
    if n in ("sidewalk", "plaza"):
        _hline(img, 0, ROAD_SH1)
        _hline(img, 1, ROAD_SH2)
    return img


# --------------------------------------------------------------------------- terrain registry
# name -> (style, params)
# a2: A2 autotile block; 'flat': always the centre quarters (no borders)
TERRAIN = {
    "grass": ("grass", None),
    "dirt": ("a2", (A2, 3, 2)),          # dirt patch on grass, with grassy fringe
    "track": ("a2", (A2, 6, 1)),         # plain orange dirt (race track) - borderless
    "plaza": ("a2", (A2, 0, 1)),         # herringbone brick pavers
    "plaza_grey": ("a2", (A2, 6, 0)),    # grey herringbone pavers
    "cobble": ("a2", (A2, 4, 1)),        # cobblestone
    "water": ("water", None),
    "pond": ("a2", (A2, 4, 2)),          # natural pond with dirt rim (on grass)
    "hill": ("a4top", (A4, 0)),          # raised grass plateau with dirt rim
}


def grass_tile(x, y):
    # fine-textured seamless grass: A2 block (4,0), tiles 8..9, 1..2
    return tile(A2, 8 + (x % 2), 1 + (y % 2))


_dominant_cache = {}


def _dominant_green(img_key, img):
    if img_key not in _dominant_cache:
        counts = {}
        for px in img.getdata():
            if px[3] == 255 and px[1] > px[0] + 20 and px[1] > px[2] + 10:
                counts[px] = counts.get(px, 0) + 1
        top = sorted(counts.items(), key=lambda kv: -kv[1])
        _dominant_cache[img_key] = {c for c, _ in top[:2]}
    return _dominant_cache[img_key]


def regrass(img, x, y, block_key, block_img):
    """Replace the autotile block's own flat grass colour with the shared grass texture,
    so dirt paths / hill tops blend with the surrounding lawn (keeps fringe shading)."""
    greens = _dominant_green(block_key, block_img)
    g = grass_tile(x, y)
    out = img.copy()
    px = out.load()
    gp = g.load()
    for yy in range(T):
        for xx in range(T):
            if px[xx, yy] in greens:
                px[xx, yy] = gp[xx, yy]
    return out


WATER_HI = (0x7A, 0xA8, 0xA8, 255)
WATER_LO = (0x2E, 0x8F, 0xA8, 255)


MURK = (0x3C, 0x6A, 0x70)


def murky(img, amt=0.42):
    """Codorus in the 60s was polluted: pull the bright pool-blue toward slate teal."""
    out = img.copy()
    px = out.load()
    for yy in range(out.size[1]):
        for xx in range(out.size[0]):
            r, g, b, a = px[xx, yy]
            px[xx, yy] = (int(r + (MURK[0] - r) * amt), int(g + (MURK[1] - g) * amt), int(b + (MURK[2] - b) * amt), a)
    return out


def shoal_tile(x, y):
    base = murky(tile(A2, 6 + (x % 2), 10 + (y % 2)))
    grav = tile(A2, 12 + (x % 2), 4 + (y % 2)).copy()   # orange dirt -> tinted to grey gravel
    px = grav.load()
    for yy in range(T):
        for xx in range(T):
            r, g, b, a = px[xx, yy]
            v = (r + g + b) // 3
            px[xx, yy] = (int(v * 0.85) + 10, int(v * 0.83) + 10, int(v * 0.78) + 8, a)
    base.alpha_composite(grav)
    return base


def water_tile(x, y):
    img = murky(tile(A2, 6 + (x % 2), 10 + (y % 2)))
    r = rnd(x, y, 3)
    if r < 0.30:  # small ripple glints, Earthbound-style
        ox = int(rnd(x, y, 4) * 10) + 1
        oy = int(rnd(x, y, 5) * 12) + 2
        for i in range(4):
            img.putpixel((ox + i, oy), WATER_HI)
        if r < 0.12:
            for i in range(3):
                img.putpixel((ox + 2 + i, oy + 3 if oy < 12 else oy - 3), WATER_HI)
    return img


def coping(img):
    """Recolour the A4 concrete wall-top's dark centre to a light concrete coping."""
    out = img.copy()
    px = out.load()
    for yy in range(T):
        for xx in range(T):
            r, g, b, a = px[xx, yy]
            if a and r < 80 and g < 80 and b < 100:
                px[xx, yy] = (0xA9, 0xA7, 0xB2, a)
    return out


STONE = [(0xB9, 0xB4, 0xAA, 255), (0xA0, 0x9A, 0x90, 255), (0x7A, 0x74, 0x6E, 255), (0x55, 0x50, 0x55, 255)]


def stair_tile(x, y, left, right):
    """Stone steps cut into a wall/cliff (3/4 view): 4 risers per tile."""
    img = Image.new("RGBA", (T, T), STONE[1])
    for yy in range(T):
        m = yy % 4
        c = STONE[0] if m == 0 else (STONE[1] if m in (1, 2) else STONE[2])
        for xx in range(T):
            img.putpixel((xx, yy), c)
    if left:
        for yy in range(T):
            img.putpixel((0, yy), STONE[3])
            img.putpixel((1, yy), STONE[2])
    if right:
        for yy in range(T):
            img.putpixel((15, yy), STONE[3])
            img.putpixel((14, yy), STONE[2])
    return img
