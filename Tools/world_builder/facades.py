"""Facade pieces added in the art-director review pass, drawn in the LimeZu outline style:
Market House central gable, striped awnings, station canopy, clock dormer, classical bank,
Gothic church fronts, shop fascia, rowhouse doors + white marble stoops."""
import math
import random

from PIL import Image, ImageDraw

from buildings import flat_roof

T = 16
OUT = (0x3D, 0x3D, 0x52, 255)
SAND = (0xEC, 0xBC, 0x86, 255)
SAND_D = (0xC0, 0x8C, 0x5E, 255)
GLASS = (0x5C, 0x74, 0x92, 255)
GLASS_L = (0x9C, 0xB8, 0xCC, 255)
DOOR_GREEN = (0x2E, 0x5E, 0x48, 255)
DOOR_GREEN_L = (0x4A, 0x82, 0x64, 255)


def _brickwork(d, box, base, line):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=base)
    for y in range(y0 + 3, y1, 4):
        d.line([x0, y, x1, y], fill=line)
        off = 0 if ((y - y0) // 4) % 2 else 4
        for x in range(x0 + off, x1, 8):
            d.line([x, y - 3, x, y - 1], fill=line)


def market_gable(brick=(0x77, 0x52, 0x44, 255), rows=16):
    """Central Market House gable bay, 4 tiles wide, `rows` tall (row 0 = above the roofline).
    Pedimented brick gable, big round-arched multi-pane window, sandstone belt course,
    round-arched entrance with dark-green double doors and voussoirs, stone steps."""
    W, H = 4 * T, rows * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    line = tuple(max(0, c - 22) for c in brick[:3]) + (255,)
    body_top = 2 * T + 8
    _brickwork(d, (2, body_top, W - 3, H - 5), brick, line)
    d.rectangle([2, body_top, W - 3, H - 5], outline=OUT)
    # pediment + oculus + finial
    d.polygon([(0, body_top + 2), (W - 1, body_top + 2), (W // 2, 6)], fill=brick, outline=OUT)
    d.line([(1, body_top + 1), (W // 2, 7), (W - 2, body_top + 1)], fill=SAND, width=3)
    d.ellipse([W // 2 - 4, body_top - 14, W // 2 + 3, body_top - 7], fill=GLASS, outline=SAND)
    d.line([W // 2, 6, W // 2, 1], fill=OUT, width=2)
    d.ellipse([W // 2 - 2, 0, W // 2 + 1, 3], fill=OUT)
    # pilasters
    for x in (2, W - 7):
        d.rectangle([x, body_top, x + 4, H - 5], fill=SAND, outline=OUT)
    # big arched window
    wx0, wx1, wy0 = 12, W - 13, body_top + 20
    wy1 = wy0 + 70
    rr = (wx1 - wx0) // 2
    d.pieslice([wx0 - 3, wy0 - 3, wx1 + 3, wy0 + 2 * rr + 3], 180, 360, fill=SAND, outline=OUT)
    d.rectangle([wx0 - 3, wy0 + rr, wx1 + 3, wy1 + 3], fill=SAND, outline=OUT)
    d.pieslice([wx0, wy0, wx1, wy0 + 2 * rr], 180, 360, fill=GLASS, outline=OUT)
    d.rectangle([wx0, wy0 + rr, wx1, wy1], fill=GLASS, outline=OUT)
    for x in range(wx0 + 6, wx1, 7):
        d.line([x, wy0 + 3, x, wy1 - 1], fill=GLASS_L)
    for y in range(wy0 + rr, wy1, 9):
        d.line([wx0 + 1, y, wx1 - 1, y], fill=GLASS_L)
    # belt course
    by = H - 4 * T - 2
    d.rectangle([0, by, W - 1, by + 4], fill=SAND, outline=OUT)
    # arched entrance (2 tiles wide, centred)
    ex0, ex1 = T - 2, 3 * T + 1
    ey1 = H - 6
    ey0 = H - 3 * T - 2
    r = (ex1 - ex0) // 2
    cx, cy = (ex0 + ex1) / 2, ey0 + r
    d.pieslice([ex0 - 5, ey0 - 5, ex1 + 5, ey0 + 2 * r + 5], 180, 360, fill=SAND, outline=OUT)
    d.rectangle([ex0 - 5, ey0 + r, ex1 + 5, ey1], fill=SAND, outline=OUT)
    for k in range(9):
        a = math.pi + k * math.pi / 8
        d.line([cx + r * math.cos(a), cy + r * math.sin(a), cx + (r + 5) * math.cos(a), cy + (r + 5) * math.sin(a)], fill=SAND_D)
    d.pieslice([ex0, ey0, ex1, ey0 + 2 * r], 180, 360, fill=DOOR_GREEN, outline=OUT)
    d.rectangle([ex0, ey0 + r, ex1, ey1], fill=DOOR_GREEN, outline=OUT)
    mid = (ex0 + ex1) // 2
    d.line([mid, ey0 + 2, mid, ey1], fill=OUT)
    for x in (ex0 + 4, mid + 4):
        d.rectangle([x, ey0 + r + 4, x + 8, ey1 - 6], outline=DOOR_GREEN_L)
    d.ellipse([mid - 6, ey0 + 6, mid + 5, ey0 + 16], fill=GLASS, outline=OUT)
    # steps
    for i, y in enumerate(range(H - 6, H, 2)):
        d.rectangle([ex0 - 8 - i * 2, y, ex1 + 8 + i * 2, y + 1],
                    fill=(0xE0, 0xDA, 0xD0, 255) if i % 2 == 0 else (0xC8, 0xC2, 0xB8, 255))
    return img


def striped_awning(w_px, stripes=((0x3E, 0x8A, 0x5A), (0xF2, 0xEE, 0xE4)), h=9):
    img = Image.new("RGBA", (w_px, h + 3))
    d = ImageDraw.Draw(img)
    for x in range(w_px):
        d.line([x, 0, x, h - 1], fill=stripes[(x // 4) % len(stripes)] + (255,))
    for x in range(0, w_px, 4):
        d.pieslice([x, h - 3, x + 3, h + 2], 0, 180, fill=stripes[(x // 4) % len(stripes)] + (255,))
    d.rectangle([0, 0, w_px - 1, h - 1], outline=OUT)
    d.line([1, 1, w_px - 2, 1], fill=(0, 0, 0, 50))
    return img


def platform_canopy(w, rows=2, posts_every=4):
    """Station platform canopy: green tin roof, white scalloped valance, cast-iron posts."""
    W, H = w * T, rows * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    rb = H - 9
    d.rectangle([0, 0, W - 1, rb - 5], fill=(0x4E, 0x7A, 0x5C, 255), outline=OUT)
    for x in range(3, W - 2, 5):
        d.line([x, 1, x, rb - 6], fill=(0x66, 0x94, 0x72, 255))
    d.rectangle([0, rb - 5, W - 1, rb - 2], fill=(0xEE, 0xE8, 0xDA, 255), outline=OUT)
    for x in range(0, W - 4, 6):
        d.pieslice([x, rb - 5, x + 5, rb + 1], 0, 180, fill=(0xEE, 0xE8, 0xDA, 255), outline=OUT)
    for x in range(8, W - 4, posts_every * T):
        d.rectangle([x, rb, x + 2, H - 1], fill=(0x2E, 0x34, 0x38, 255))
        d.rectangle([x - 1, H - 3, x + 3, H - 1], fill=(0x2E, 0x34, 0x38, 255))
    return img


def clock_dormer(w=4, h=3):
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 17), (W - 3, 17), (W // 2, 1)], fill=(0x92, 0x40, 0x34, 255), outline=OUT)
    d.line([(4, 16), (W // 2, 3), (W - 5, 16)], fill=(0xEE, 0xE8, 0xDA, 255), width=2)
    d.rectangle([7, 17, W - 8, H - 2], fill=(0xEE, 0xE8, 0xDA, 255), outline=OUT)
    cx, cy = W // 2, 31
    d.ellipse([cx - 11, cy - 11, cx + 10, cy + 10], fill=(0xF8, 0xF4, 0xE8, 255), outline=OUT)
    d.ellipse([cx - 9, cy - 9, cx + 8, cy + 8], outline=(0x9A, 0x92, 0x86, 255))
    for k in range(12):
        a = k * math.pi / 6
        d.point((cx + int(round(7 * math.cos(a))), cy + int(round(7 * math.sin(a)))), fill=OUT)
    d.line([cx, cy, cx, cy - 6], fill=OUT)
    d.line([cx, cy, cx + 4, cy + 1], fill=OUT)
    return img


GRANITE = (0xD6, 0xD2, 0xCA, 255)
GRANITE_S = (0xAE, 0xAA, 0xA4, 255)
GRANITE_D = (0x86, 0x82, 0x80, 255)


def bank_facade(w=10, h=12):
    """Classical granite bank: flat roof with parapet, pediment with bronze medallion and dentils,
    4 fluted columns, dark recessed wall with tall windows, bronze doors centred, steps."""
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(flat_roof(w, 3, "gravel", 77, hatch=False), (0, 0))
    d = ImageDraw.Draw(img)
    top = 2 * T + 8
    d.polygon([(4, top + 16), (W - 5, top + 16), (W // 2, top - 6)], fill=GRANITE, outline=OUT)
    d.line([(12, top + 14), (W // 2, top - 1), (W - 13, top + 14)], fill=GRANITE_S)
    d.ellipse([W // 2 - 5, top + 3, W // 2 + 4, top + 11], fill=(0xB0, 0x8A, 0x4A, 255), outline=OUT)
    d.rectangle([0, top + 16, W - 1, top + 26], fill=GRANITE, outline=OUT)
    for x in range(3, W - 3, 4):
        d.rectangle([x, top + 23, x + 1, top + 25], fill=GRANITE_D)
    wall_top, wall_bot = top + 27, H - 14
    d.rectangle([4, wall_top, W - 5, wall_bot], fill=(0x6E, 0x6A, 0x70, 255))
    for wx in (14, W - 26):
        d.rectangle([wx, wall_top + 8, wx + 11, wall_bot - 6], fill=GLASS, outline=OUT)
        d.line([wx + 5, wall_top + 8, wx + 5, wall_bot - 6], fill=GLASS_L)
    dx0, dx1 = W // 2 - 12, W // 2 + 11
    d.rectangle([dx0, wall_top + 14, dx1, wall_bot], fill=(0x9A, 0x70, 0x38, 255), outline=OUT)
    d.line([W // 2, wall_top + 14, W // 2, wall_bot], fill=OUT)
    d.rectangle([dx0 - 2, wall_top + 10, dx1 + 2, wall_top + 14], fill=GRANITE, outline=OUT)
    for f in (0.12, 0.37, 0.63, 0.88):
        cx = int(W * f)
        d.rectangle([cx - 5, wall_top - 1, cx + 5, wall_top + 2], fill=GRANITE, outline=OUT)
        d.rectangle([cx - 4, wall_top + 3, cx + 4, wall_bot - 1], fill=GRANITE, outline=OUT)
        d.line([cx - 1, wall_top + 4, cx - 1, wall_bot - 2], fill=GRANITE_S)
        d.line([cx + 2, wall_top + 4, cx + 2, wall_bot - 2], fill=GRANITE_S)
        d.line([cx - 3, wall_top + 4, cx - 3, wall_bot - 2], fill=(0xEE, 0xEA, 0xE4, 255))
        d.rectangle([cx - 5, wall_bot - 2, cx + 5, wall_bot + 1], fill=GRANITE, outline=OUT)
    for i, y in enumerate(range(wall_bot + 2, H, 3)):
        d.rectangle([2 + i, y, W - 3 - i, min(H - 1, y + 2)], fill=GRANITE if i % 2 == 0 else GRANITE_S, outline=OUT)
    return img


def church_front(w=7, rows=12, material="stone"):
    """Gable-end church facing south: slate roof behind a steep gable, rose window, two lancets,
    pointed central door, corner buttresses. material 'stone' or 'brick' (with white trim)."""
    W, H = w * T, rows * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    if material == "stone":
        base, line, trim = (0xB8, 0xB0, 0xA2, 255), (0x94, 0x8C, 0x80, 255), (0xD8, 0xD2, 0xC6, 255)
    else:
        base, line, trim = (0xA8, 0x4C, 0x3C, 255), (0x86, 0x38, 0x2E, 255), (0xF2, 0xEE, 0xE6, 255)
    gable_base = int(H * 0.45)
    d.polygon([(0, gable_base + 6), (W // 2, 2), (W - 1, gable_base + 6)], fill=(0x55, 0x5E, 0x72, 255), outline=OUT)
    _brickwork(d, (6, gable_base, W - 7, H - 2), base, line)
    d.rectangle([6, gable_base, W - 7, H - 2], outline=OUT)
    d.polygon([(8, gable_base + 1), (W - 9, gable_base + 1), (W // 2, 12)], fill=base, outline=OUT)
    d.line([(8, gable_base), (W // 2, 11), (W - 9, gable_base)], fill=trim, width=2)
    d.line([W // 2, 11, W // 2, 2], fill=OUT, width=2)
    d.line([W // 2 - 3, 5, W // 2 + 3, 5], fill=OUT, width=2)
    rc = (W // 2, gable_base - 8)
    d.ellipse([rc[0] - 11, rc[1] - 11, rc[0] + 10, rc[1] + 10], fill=trim, outline=OUT)
    d.ellipse([rc[0] - 8, rc[1] - 8, rc[0] + 7, rc[1] + 7], fill=(0x8A, 0x3A, 0x5A, 255))
    for k in range(8):
        a = k * math.pi / 4
        d.line([rc[0], rc[1], rc[0] + 7 * math.cos(a), rc[1] + 7 * math.sin(a)], fill=(0xE8, 0xC0, 0x4A, 255))
    for lx in (16, W - 26):
        y0 = gable_base + 14
        d.rectangle([lx, y0 + 6, lx + 9, H - 22], fill=(0x4A, 0x5A, 0x8A, 255), outline=OUT)
        d.polygon([(lx, y0 + 6), (lx + 9, y0 + 6), (lx + 4, y0 - 2)], fill=(0x4A, 0x5A, 0x8A, 255), outline=OUT)
        d.line([lx + 4, y0 + 2, lx + 4, H - 23], fill=trim)
    dx0, dx1 = W // 2 - 9, W // 2 + 8
    d.polygon([(dx0 - 3, H - 2), (dx0 - 3, H - 26), (W // 2, H - 40), (dx1 + 3, H - 26), (dx1 + 3, H - 2)], fill=trim, outline=OUT)
    d.polygon([(dx0, H - 2), (dx0, H - 25), (W // 2, H - 36), (dx1, H - 25), (dx1, H - 2)], fill=(0x6A, 0x2E, 0x26, 255), outline=OUT)
    d.line([W // 2, H - 35, W // 2, H - 2], fill=OUT)
    for bx in (4, W - 10):
        d.rectangle([bx, gable_base + 4, bx + 5, H - 1], fill=trim, outline=OUT)
    return img


def fascia(w, colour=(0xB8, 0x2C, 0x2C), trim=(0xE8, 0xC0, 0x4A)):
    """Five-and-dime shop fascia band, no lettering: red field, gold border and dots."""
    W = w * T
    img = Image.new("RGBA", (W, 10))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, 9], fill=colour + (255,), outline=OUT)
    d.rectangle([2, 2, W - 3, 7], outline=trim + (255,))
    for x in range(8, W - 8, 10):
        d.rectangle([x, 4, x + 3, 5], fill=trim + (255,))
    return img


DOOR_COLOURS = [(0x2E, 0x5E, 0x48), (0x6A, 0x22, 0x26), (0x2A, 0x3A, 0x6A), (0x3A, 0x2A, 0x22), (0x5A, 0x6E, 0x3A)]


def rowhouse_doors(img, n, depth, seed=0):
    """Recolour each rowhouse's wooden door and add a white marble stoop (a York hallmark)."""
    rng = random.Random(seed)
    out = img.copy()
    px = out.load()
    d = ImageDraw.Draw(out)
    for i in range(n):
        mirrored = i % 2 == 1
        dx0 = 4 * i * T + (0 if mirrored else 3 * T)
        col = rng.choice(DOOR_COLOURS)
        for y in range((depth - 3) * T, depth * T):
            for x in range(dx0, dx0 + T):
                r, g, b, a = px[x, y]
                if a and r > 150 and 80 < g < 170 and b < 110:
                    k = (r + g + b) / 450
                    px[x, y] = (int(col[0] * k), int(col[1] * k), int(col[2] * k), a)
        sy = depth * T - 5
        for k, yy in enumerate(range(sy, depth * T, 2)):
            d.rectangle([dx0 + 1 - k, yy, dx0 + 14 + k, min(depth * T - 1, yy + 1)],
                        fill=(0xF2, 0xF0, 0xEA, 255) if k % 2 == 0 else (0xC8, 0xC6, 0xC0, 255))
    return out


def glass_runs(img, y, x0, x1):
    """Centres (px) of window glass runs along pixel row y (bluish, fairly light pixels)."""
    runs, start = [], None
    for x in range(x0, x1):
        r, g, b, a = img.getpixel((x, y))
        isg = a and b > r + 15 and b > 110
        if isg and start is None:
            start = x
        if not isg and start is not None:
            if x - start >= 4:
                runs.append((start + x - 1) // 2)
            start = None
    return runs
