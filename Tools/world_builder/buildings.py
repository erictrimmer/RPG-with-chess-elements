"""Building composer: assemble catalog facade modules into complete buildings with roofs.

3/4 view rule: a building occupies a block from its back line down to its front row.
Facade rows (ground floor + upper floors) sit at the bottom; whatever depth is left above the
facade shows as roof. Flat tar roofs with stone parapet coping are synthesized at any size, so
every building in a block can share a back line while having different storey counts.
"""
from PIL import Image, ImageDraw

import terrain as TR

T = 16

OUT = (0x3D, 0x3D, 0x52, 255)

ROOF_STYLES = {
    # fill base, fill speckle, coping light, coping dark
    "tar": ((0x6B, 0x63, 0x68), (0x5B, 0x54, 0x5A), (0xD9, 0xCC, 0xB0), (0xA8, 0x99, 0x82)),
    "tar_red": ((0x7A, 0x5E, 0x58), (0x6A, 0x50, 0x4C), (0xDC, 0xCF, 0xB4), (0xAA, 0x98, 0x80)),
    "gravel": ((0x8E, 0x88, 0x84), (0x7A, 0x74, 0x72), (0xE0, 0xD6, 0xC2), (0xB0, 0xA4, 0x92)),
    "tin_green": ((0x5E, 0x7E, 0x6A), (0x50, 0x6E, 0x5C), (0xD6, 0xCF, 0xB8), (0xA2, 0x9A, 0x84)),
    "slate": ((0x5C, 0x66, 0x7A), (0x4E, 0x57, 0x6A), (0xC8, 0xC4, 0xBA), (0x96, 0x92, 0x8A)),
}


def flat_roof(w, d, style="tar", seed=0, hatch=True):
    """w x d tiles of flat roof seen from above, with parapet coping all round."""
    base, speck, light, dark = ROOF_STYLES[style]
    W, H = w * T, d * T
    img = Image.new("RGBA", (W, H), base + (255,))
    px = img.load()
    for y in range(H):
        for x in range(W):
            if TR.rnd(x + seed * 977, y, 21) < 0.16:
                px[x, y] = speck + (255,)
    dr = ImageDraw.Draw(img)
    # parapet: outline, 3px light coping, 1px dark inner shadow (inner shadow heavier on top edge = depth)
    dr.rectangle([0, 0, W - 1, H - 1], outline=OUT)
    for i in range(1, 4):
        dr.rectangle([i, i, W - 1 - i, H - 1 - i], outline=light + (255,))
    dr.rectangle([4, 4, W - 5, H - 5], outline=dark + (255,))
    dr.line([5, 5, W - 6, 5], fill=dark + (255,))
    dr.line([5, 6, W - 6, 6], fill=tuple(int(c * 0.85) for c in base) + (255,))
    if hatch and w >= 3 and d >= 2:
        # roof hatch / skylight
        hx = int(TR.rnd(seed, w, 3) * (W - 28)) + 10
        hy = int(TR.rnd(seed, d, 4) * max(1, H - 26)) + 9
        dr.rectangle([hx, hy, hx + 9, hy + 7], fill=(0x9A, 0x96, 0x9C, 255), outline=OUT)
        dr.line([hx + 1, hy + 1, hx + 8, hy + 1], fill=(0xC4, 0xC0, 0xC6, 255))
        if w >= 5:  # chimney stack
            cx = int(TR.rnd(seed, w, 5) * (W - 24)) + 8
            if abs(cx - hx) < 16:
                cx = (cx + W // 2) % (W - 16) + 4
            cy = 10
            dr.rectangle([cx, cy, cx + 7, cy + 9], fill=(0xA4, 0x4C, 0x3A, 255), outline=OUT)
            dr.rectangle([cx + 1, cy + 1, cx + 6, cy + 3], fill=(0x3A, 0x32, 0x34, 255))
            dr.line([cx + 1, cy + 8, cx + 6, cy + 8], fill=(0x7E, 0x38, 0x2C, 255))
    return img


def stack(pieces, lib):
    """pieces: list of (pid_or_img, y_offset_adjust) from TOP to BOTTOM; all same width.
    A negative adjust overlaps the previous piece by that many rows (for sign-topped shops)."""
    imgs = []
    for p in pieces:
        if isinstance(p, tuple):
            src, adj = p
        else:
            src, adj = p, 0
        img = lib[src].img if isinstance(src, str) else src
        imgs.append((img, adj))
    width = max(i.size[0] for i, _ in imgs)
    y = 0
    placements = []
    for img, adj in imgs:
        y += adj * T
        placements.append((img, y))
        y += img.size[1]
    out = Image.new("RGBA", (width, y))
    for img, yy in placements:
        out.alpha_composite(img, ((width - img.size[0]) // 2, yy))
    return out


def hcat(imgs):
    """Join facades side by side, aligned at the bottom."""
    W = sum(i.size[0] for i in imgs)
    Hh = max(i.size[1] for i in imgs)
    out = Image.new("RGBA", (W, Hh))
    x = 0
    for i in imgs:
        out.alpha_composite(i, (x, Hh - i.size[1]))
        x += i.size[0]
    return out


def building(lib, pid, facade_pieces, depth, roof="tar", seed=0, doors=None, extra=None):
    """Compose a building `depth` rows deep: roof on top, facade (top->bottom pieces) at the bottom.
    Registers and returns the Prefab. `extra`: list of (pid, rx, ry) overlays (signs, awnings)."""
    fac = stack(facade_pieces, lib)
    w = fac.size[0] // T
    fr = fac.size[1] // T
    rr = depth - fr
    img = Image.new("RGBA", (w * T, depth * T))
    if rr > 0:
        img.alpha_composite(flat_roof(w, rr + 1, roof, seed), (0, 0))  # +1 row tucks under the coping
    img.alpha_composite(fac, (0, max(0, rr) * T))
    for (opid, rx, ry) in (extra or []):
        img.alpha_composite(lib[opid].img, (rx * T, ry * T))
    if rr < 0:
        img = img.crop((0, -rr * T, w * T, -rr * T + depth * T))
    return lib.add_img(pid, img, "building", "all", 0, doors or [])


def row_of_buildings(lib, pid, specs, depth):
    """specs: list of dicts {pieces:[...], roof:'tar', seed:int}. Joined left-to-right as one prefab."""
    parts = []
    doors = []
    x = 0
    for i, s in enumerate(specs):
        b = building(lib, f"{pid}__{i}", s["pieces"], depth, s.get("roof", "tar"), s.get("seed", i), extra=s.get("extra"))
        parts.append(b.img)
        for d in s.get("doors", []):
            doors.append([x + d[0], d[1]])
        x += b.w
    img = hcat(parts)
    return lib.add_img(pid, img, "building", "all", 0, doors)


# ------------------------------------------------------------------ image surgery
def cut_rows(img, start, n):
    """Remove n tile rows starting at tile row `start` (use on uniform roof areas to shorten a building)."""
    W, H = img.size
    out = Image.new("RGBA", (W, H - n * T))
    out.alpha_composite(img.crop((0, 0, W, start * T)), (0, 0))
    out.alpha_composite(img.crop((0, (start + n) * T, W, H)), (0, start * T))
    return out


def cut_cols(img, start, n):
    W, H = img.size
    out = Image.new("RGBA", (W - n * T, H))
    out.alpha_composite(img.crop((0, 0, start * T, H)), (0, 0))
    out.alpha_composite(img.crop(((start + n) * T, 0, W, H)), (start * T, 0))
    return out


def warm_brick(img, amt=0.55):
    """Shift brown/maroon brick toward York's warm red-orange brick, leaving greys/slate alone."""
    out = img.copy()
    px = out.load()
    for y in range(out.size[1]):
        for x in range(out.size[0]):
            r, g, b, a = px[x, y]
            if a and r > g + 12 and r > b + 12:
                nr = min(255, int(r + (r * 0.38) * amt))
                ng = int(g + (g * 0.05) * amt)
                nb = int(b - (b * 0.22) * amt)
                px[x, y] = (nr, ng, max(0, nb), a)
    return out


# ------------------------------------------------------------------ synthesized civic pieces
COPPER = [(0x5E, 0xA8, 0x8E, 255), (0x48, 0x8A, 0x74, 255), (0x34, 0x6A, 0x5A, 255), (0x9C, 0xD4, 0xBC, 255)]
GOLD = (0xE8, 0xC2, 0x4A, 255)


def dome(w=4, h=4, drum=True):
    """Verdigris copper dome on a stone drum with a lantern cupola + gold finial."""
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    base_y = H - 2
    if drum:
        d.rectangle([4, base_y - 14, W - 5, base_y], fill=(0xD8, 0xCE, 0xB4, 255), outline=OUT)
        for x in range(8, W - 6, 6):
            d.rectangle([x, base_y - 11, x + 2, base_y - 3], fill=(0x6E, 0x6A, 0x7A, 255))
        base_y -= 14
    r = (W - 4) // 2
    d.pieslice([2, base_y - r, W - 3, base_y + r], 180, 360, fill=COPPER[1], outline=OUT)
    d.pieslice([6, base_y - r + 4, W // 2 + 2, base_y + r - 8], 190, 290, fill=COPPER[0])
    for x in range(10, W - 8, 7):
        d.line([x, base_y - 2, W // 2, base_y - r + 1], fill=COPPER[2])
    top = base_y - r
    d.rectangle([W // 2 - 4, top - 8, W // 2 + 3, top], fill=(0xE8, 0xE2, 0xD0, 255), outline=OUT)
    d.pieslice([W // 2 - 5, top - 13, W // 2 + 4, top - 3], 180, 360, fill=COPPER[1], outline=OUT)
    d.line([W // 2, top - 13, W // 2, top - 17], fill=GOLD, width=2)
    d.ellipse([W // 2 - 2, top - 20, W // 2 + 1, top - 17], fill=GOLD)
    return img


def white_steeple(h=11):
    """Colonial white wooden steeple: clapboard tower, louvered belfry, clock, spire. 3 tiles wide."""
    W, H = 3 * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    wht, wsh, wdk = (0xF2, 0xEE, 0xE6, 255), (0xC8, 0xC2, 0xB8, 255), (0x92, 0x8C, 0x86, 255)
    tower_top = H - 5 * T
    d.rectangle([6, tower_top, W - 7, H - 1], fill=wht, outline=OUT)
    for y in range(tower_top + 3, H - 1, 3):
        d.line([7, y, W - 8, y], fill=wsh)
    d.rectangle([W - 14, tower_top + 1, W - 8, H - 2], fill=wsh)
    d.rectangle([W // 2 - 5, H - 22, W // 2 + 4, H - 2], fill=(0x5A, 0x3A, 0x2A, 255), outline=OUT)
    d.pieslice([W // 2 - 5, H - 27, W // 2 + 4, H - 17], 180, 360, fill=(0x5A, 0x3A, 0x2A, 255), outline=OUT)
    d.ellipse([W // 2 - 6, tower_top + 10, W // 2 + 5, tower_top + 21], fill=(0xF8, 0xF6, 0xEE, 255), outline=OUT)
    d.line([W // 2, tower_top + 15, W // 2, tower_top + 12], fill=OUT)
    d.line([W // 2, tower_top + 15, W // 2 + 3, tower_top + 15], fill=OUT)
    bt = tower_top - 2 * T
    d.rectangle([9, bt, W - 10, tower_top], fill=wht, outline=OUT)
    for x in (12, W // 2 + 2):
        d.rectangle([x, bt + 6, x + 8, tower_top - 4], fill=wdk, outline=OUT)
        for y in range(bt + 8, tower_top - 4, 3):
            d.line([x + 1, y, x + 7, y], fill=wsh)
    d.rectangle([7, bt - 3, W - 8, bt + 1], fill=wht, outline=OUT)
    d.rectangle([5, tower_top - 2, W - 6, tower_top + 2], fill=wht, outline=OUT)
    sp_base = bt - 3
    d.polygon([(11, sp_base), (W - 12, sp_base), (W // 2, 4)], fill=wht, outline=OUT)
    d.polygon([(W // 2, 4), (W - 12, sp_base), (W // 2 + 3, sp_base)], fill=wsh)
    d.line([W // 2, 4, W // 2, 0], fill=GOLD)
    d.line([W // 2 - 2, 2, W // 2 + 2, 2], fill=GOLD)
    return img


def stone_steeple(h=12):
    """Gothic grey-stone bell tower with a slate spire (Episcopal-style). 3 tiles wide."""
    W, H = 3 * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    st, sts = (0xB8, 0xB0, 0xA2, 255), (0x94, 0x8C, 0x80, 255)
    tower_top = H - 7 * T
    d.rectangle([5, tower_top, W - 6, H - 1], fill=st, outline=OUT)
    for y in range(tower_top + 4, H - 1, 4):
        d.line([6, y, W - 7, y], fill=sts)
        off = 0 if (y // 4) % 2 else 4
        for x in range(6 + off, W - 7, 8):
            d.line([x, y - 3, x, y], fill=sts)
    d.rectangle([W - 13, tower_top + 1, W - 7, H - 2], fill=sts)
    for (yy, hh) in ((tower_top + 10, 16), (tower_top + 40, 14)):
        d.rectangle([W // 2 - 4, yy, W // 2 + 3, yy + hh], fill=(0x3A, 0x40, 0x52, 255), outline=OUT)
        d.polygon([(W // 2 - 4, yy), (W // 2 + 3, yy), (W // 2, yy - 5)], fill=(0x3A, 0x40, 0x52, 255), outline=OUT)
    d.rectangle([W // 2 - 6, H - 20, W // 2 + 5, H - 1], fill=(0x5A, 0x3A, 0x2A, 255), outline=OUT)
    d.polygon([(W // 2 - 6, H - 20), (W // 2 + 5, H - 20), (W // 2, H - 28)], fill=(0x5A, 0x3A, 0x2A, 255), outline=OUT)
    for x in (5, W - 9):
        d.polygon([(x, tower_top), (x + 4, tower_top), (x + 2, tower_top - 9)], fill=st, outline=OUT)
    d.polygon([(10, tower_top), (W - 11, tower_top), (W // 2, 3)], fill=(0x5C, 0x66, 0x7A, 255), outline=OUT)
    d.polygon([(W // 2, 3), (W - 11, tower_top), (W // 2 + 2, tower_top)], fill=(0x4A, 0x52, 0x64, 255))
    d.line([W // 2, 3, W // 2, 0], fill=GOLD)
    return img


def gable_roof(w, d_rows, style="slate", ridge_frac=0.42):
    """Pitched roof seen in 3/4: short dark back slope above the ridge, long lit front slope below,
    shingle courses and a light eave board. Ridge runs left-right."""
    pal = {
        "slate": ((0x6A, 0x74, 0x8A), (0x55, 0x5E, 0x72), (0x44, 0x4B, 0x5C)),
        "red": ((0xB0, 0x52, 0x42), (0x92, 0x40, 0x34), (0x72, 0x30, 0x28)),
        "green": ((0x5E, 0x82, 0x6A), (0x4A, 0x6C, 0x58), (0x3A, 0x56, 0x46)),
    }[style]
    W, H = w * T, d_rows * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    ry = int(H * ridge_frac)
    d.rectangle([0, 2, W - 1, ry], fill=pal[2] + (255,))
    d.rectangle([0, ry, W - 1, H - 3], fill=pal[0] + (255,))
    for y in range(ry + 4, H - 3, 4):
        d.line([1, y, W - 2, y], fill=pal[1] + (255,))
        off = 0 if (y // 4) % 2 else 3
        for x in range(1 + off, W - 2, 6):
            d.point((x, y - 1), fill=pal[1] + (255,))
    d.line([0, ry, W - 1, ry], fill=(0xD0, 0xCC, 0xC4, 255))
    d.rectangle([0, H - 3, W - 1, H - 1], fill=(0xE4, 0xDE, 0xD0, 255))
    d.rectangle([0, 2, W - 1, H - 1], outline=OUT)
    return img


def brick_shade(img, k):
    """Per-house brick variation: k in [-1, 1]; negative = darker maroon, positive = lighter orange."""
    out = img.copy()
    px = out.load()
    for y in range(out.size[1]):
        for x in range(out.size[0]):
            r, g, b, a = px[x, y]
            if a and r > g + 12 and r > b + 12:
                if k < 0:
                    f = 1 + 0.22 * k
                    px[x, y] = (int(r * f), int(g * (f - 0.04)), int(b * (f + 0.02)), a)
                else:
                    px[x, y] = (min(255, int(r * (1 + 0.10 * k))), min(255, int(g * (1 + 0.16 * k))), b, a)
    return out


ROW_UPPERS = ["sf_brick_upper_4tall_windows", "sf_brick_upper_ornate_3windows", "sf_brick_upper_8windows",
              "sf_brick_upper_teal_bay"]


def rowhouse_row(lib, n, depth=10, seed=0, roof="tar"):
    """York brick rowhouses: n houses, 4 tiles wide each, alternately mirrored so doors pair up.
    Ground = slice of the teal-trim entrance floor (pilaster, window, door); upper = slice of a
    brick upper floor; flat roof with parapet on top. Returns (image, door cells relative)."""
    import random as _r
    rng = _r.Random(seed)
    ground = lib["sf_brick_ground_teal_entrance"].img.crop((0, 0, 4 * T, 3 * T))
    units = []
    doors = []
    for i in range(n):
        up = lib[rng.choice(ROW_UPPERS)].img.crop((0, 0, 4 * T, 4 * T))
        fac = Image.new("RGBA", (4 * T, 7 * T))
        fac.alpha_composite(up, (0, 0))
        fac.alpha_composite(ground, (0, 4 * T))
        fac = brick_shade(fac, rng.uniform(-1, 0.8))
        mirrored = i % 2 == 1
        if mirrored:
            fac = fac.transpose(Image.FLIP_LEFT_RIGHT)
        roof_rows = depth - 7
        unit = Image.new("RGBA", (4 * T, depth * T))
        if roof_rows > 0:
            unit.alpha_composite(flat_roof(4, roof_rows + 1, roof, seed * 31 + i, hatch=(i % 2 == 0)), (0, 0))
        unit.alpha_composite(fac, (0, roof_rows * T))
        units.append(unit)
        doors.append([4 * i + (0 if mirrored else 3), depth - 1])
    return hcat(units), doors
