"""Synthesized pieces the Modern Exteriors pack lacks, drawn in its palette style:
connected fences/railings (any path, incl. diagonals), bunting, rail tracks, bridge parapets,
fair big-top tent, grandstand roof, fair gate pillars, smokestack.
"""
import math

from PIL import Image, ImageDraw

import terrain as TR

T = 16
OUT = (0x3D, 0x3D, 0x52, 255)

FENCE_STYLES = {
    #            rail colour,           rail shade,            post h, rails at y (from cell bottom), post w, mesh
    "white":    ((0xF2, 0xEE, 0xE4, 255), (0xB8, 0xB0, 0xA4, 255), 11, (9, 5), 2, False),   # race-track rail
    "pipe":     ((0xB4, 0xB8, 0xC0, 255), (0x76, 0x7A, 0x86, 255), 10, (9, 4), 1, False),  # galvanized pipe railing
    "chain":    ((0xA8, 0xAC, 0xB4, 255), (0x6E, 0x72, 0x7C, 255), 18, (17, 2), 1, True),  # chain-link, ~1 tile + overhang
    "iron":     ((0x3A, 0x3A, 0x46, 255), (0x24, 0x24, 0x2E, 255), 14, (12, 3), 1, False),  # wrought iron (spear tops)
    "picket":   ((0xF4, 0xF0, 0xE8, 255), (0xBC, 0xB4, 0xA8, 255), 12, (9, 4), 2, False),
    "wood":     ((0xB0, 0x80, 0x52, 255), (0x7A, 0x52, 0x34, 255), 11, (9, 4), 2, False),
}


def _line(d, a, b, col, w=1):
    d.line([a, b], fill=col, width=w)


def paint_fence(L, cells, style="white", solid=True, tall_overhead=True):
    """cells: iterable of (x,y). Each cell gets a post at its centre and rails toward every
    8-neighbour fence cell (diagonals only if neither orthogonal shortcut exists).
    Rails are drawn near the bottom of the cell (3/4 view: fence stands on the cell)."""
    rail, shade, post_h, rails_y, post_w, mesh = FENCE_STYLES[style]
    S = set(cells)
    for (x, y) in S:
        nbrs = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) in S:
                nbrs.append((dx, dy))
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            if (x + dx, y + dy) in S and (x + dx, y) not in S and (x, y + dy) not in S:
                nbrs.append((dx, dy))
        # draw on a 16x32 canvas (cell + one row above for tall posts), bottom = cell bottom
        cv = Image.new("RGBA", (T, 2 * T))
        d = ImageDraw.Draw(cv)
        base = 2 * T - 3            # ground line inside the cell
        cx = T // 2
        for (dx, dy) in nbrs:
            ex, ey = cx + dx * 8, dy * 8
            for ry in rails_y:
                y0 = base - ry
                _line(d, (cx, y0), (ex, y0 + ey), rail, 1)
                _line(d, (cx, y0 + 1), (ex, y0 + ey + 1), shade, 1)
            if mesh:
                for k in range(0, 9, 2):
                    px = cx + int(dx * k)
                    py = int(dy * k)
                    _line(d, (px, base - rails_y[0] + py), (px, base - rails_y[1] + py), shade, 1)
        # post
        top = base - post_h
        d.rectangle([cx - post_w // 2 - 1, top - 1, cx + (post_w - 1) // 2 + 1, base], fill=OUT)
        d.rectangle([cx - post_w // 2, top, cx + (post_w - 1) // 2, base - 1], fill=rail)
        if style == "iron":
            d.polygon([(cx - 1, top - 1), (cx + 1, top - 1), (cx, top - 4)], fill=rail)
            # pickets between posts
            for (dx, dy) in nbrs:
                if dy == 0:
                    for k in (3, 6):
                        px = cx + dx * k
                        _line(d, (px, base - rails_y[0] - 2), (px, base - 1), rail)
        if style == "picket":
            for (dx, dy) in nbrs:
                if dy == 0:
                    for k in (3, 6):
                        px = cx + dx * k
                        d.rectangle([px - 1, base - 11, px, base - 1], fill=rail)
                        d.point((px - 1, base - 12), fill=rail)
        lower = cv.crop((0, T, T, 2 * T))
        upper = cv.crop((0, 0, T, T))
        L.put("Objects", x, y, lower, solid, "full" if style == "chain" else "alpha")
        if upper.getchannel("A").getbbox():
            L.put("Overhead" if tall_overhead else "Objects", x, y - 1, upper, False, "alpha")


def ellipse_cells(cx, cy, rx, ry):
    """Cells on an ellipse outline (8-connected, no gaps)."""
    cells = set()
    n = int(2 * math.pi * max(rx, ry) * 3)
    for i in range(n):
        a = 2 * math.pi * i / n
        cells.add((int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))))
    # thin: drop cells that have both an orthogonal horizontal and vertical neighbour forming an L
    thin = set(cells)
    for (x, y) in list(cells):
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            if (x + dx, y) in thin and (x, y + dy) in thin and (x + dx, y + dy) not in thin:
                pass
    return thin


def ellipse_fill(cx, cy, rx, ry):
    cells = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                cells.add((x, y))
    return cells


# ------------------------------------------------------------------ bunting / pennant strings
PENNANT = [(0xD8, 0x3A, 0x36, 255), (0xF2, 0xEE, 0xE4, 255), (0x3E, 0x6E, 0xC4, 255), (0xF0, 0xC0, 0x3A, 255)]


def bunting(L, x0, y, x1, sag=6, offset_px=2, colours=PENNANT, layer="Overhead"):
    """Pennant string hung across tile row y from x0 to x1 (overhead, non-solid)."""
    W = (x1 - x0 + 1) * T
    cv = Image.new("RGBA", (W, T * 2))
    d = ImageDraw.Draw(cv)
    pts = []
    for px in range(W):
        t = px / max(1, W - 1)
        py = offset_px + int(sag * 4 * t * (1 - t))
        pts.append((px, py))
    d.line(pts, fill=(0x4A, 0x40, 0x3A, 255))
    i = 0
    for px in range(3, W - 3, 6):
        py = pts[px][1]
        c = colours[i % len(colours)]
        d.polygon([(px - 2, py + 1), (px + 2, py + 1), (px, py + 5)], fill=c)
        i += 1
    for k in range(x1 - x0 + 1):
        for r in range(2):
            tile = cv.crop((k * T, r * T, k * T + T, r * T + T))
            if tile.getchannel("A").getbbox():
                L.put(layer, x0 + k, y + r, tile, False)


def bulb_string(L, x0, y, x1, sag=5):
    bunting(L, x0, y, x1, sag, colours=[(0xFF, 0xF1, 0xA8, 255), (0xFF, 0xC8, 0x6A, 255)])


# ------------------------------------------------------------------ railroad
def rail_track_h(L, x0, x1, y_top):
    """3-row track band: ballast (ground cobble) + ties + two rails across rows y_top..y_top+2."""
    for x in range(x0, x1 + 1):
        for r in range(3):
            img = Image.new("RGBA", (T, T))
            d = ImageDraw.Draw(img)
            # ties: vertical brown sleepers every 8px spanning the band
            for tx in (2, 10):
                d.rectangle([tx, 0, tx + 3, 15], fill=(0x6A, 0x4A, 0x36, 255))
                d.line([tx + 3, 0, tx + 3, 15], fill=(0x4A, 0x32, 0x26, 255))
            if r == 0:
                img = img.crop((0, 0, 16, 16))
                # top tie ends fade: cut the top 4px
                img.paste((0, 0, 0, 0), (0, 0, 16, 5))
            if r == 2:
                img.paste((0, 0, 0, 0), (0, 11, 16, 16))
            # rails
            ry = {0: [11], 1: [], 2: [4]}[r]
            for yy in ry:
                d = ImageDraw.Draw(img)
                d.line([0, yy, 15, yy], fill=(0xC8, 0xCC, 0xD4, 255))
                d.line([0, yy + 1, 15, yy + 1], fill=(0x5A, 0x5C, 0x66, 255))
            L.put("Decals", x, y_top + r, img, False)
            L.extra_solid.add((x, y_top + r))


# ------------------------------------------------------------------ bridge parapets
def parapet_h(L, x0, x1, y, style="concrete"):
    """Low solid parapet wall along row y (seen from above + 4px front face)."""
    top = (0xC4, 0xC2, 0xC8, 255) if style == "concrete" else (0x9A, 0x4E, 0x3E, 255)
    face = (0x8E, 0x8C, 0x96, 255) if style == "concrete" else (0x6E, 0x34, 0x2A, 255)
    for x in range(x0, x1 + 1):
        img = Image.new("RGBA", (T, T))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 3, 15, 10], fill=top)
        d.rectangle([0, 11, 15, 14], fill=face)
        d.line([0, 2, 15, 2], fill=OUT)
        d.line([0, 15, 15, 15], fill=OUT)
        if x == x0:
            d.line([0, 2, 0, 15], fill=OUT)
        if x == x1:
            d.line([15, 2, 15, 15], fill=OUT)
        if (x - x0) % 4 == 0 and x not in (x0,):
            d.line([0, 3, 0, 14], fill=face)
        L.put("Objects", x, y, img, True, "full")


def parapet_v(L, x, y0, y1, style="concrete"):
    top = (0xC4, 0xC2, 0xC8, 255)
    face = (0x8E, 0x8C, 0x96, 255)
    for y in range(y0, y1 + 1):
        img = Image.new("RGBA", (T, T))
        d = ImageDraw.Draw(img)
        d.rectangle([4, 0, 11, 15], fill=top)
        d.line([3, 0, 3, 15], fill=OUT)
        d.line([12, 0, 12, 15], fill=OUT)
        if y == y0:
            d.line([3, 0, 12, 0], fill=OUT)
        if y == y1:
            d.rectangle([4, 11, 11, 14], fill=face)
            d.line([3, 15, 12, 15], fill=OUT)
        L.put("Objects", x, y, img, True, "full")


# ------------------------------------------------------------------ big top tent
def big_top(w=12, h=11, c1=(0xD8, 0x3A, 0x36), c2=(0xF4, 0xEE, 0xE2)):
    """Striped circus tent, 3/4 view: conical striped roof over a short striped wall with an entrance."""
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    cx = W // 2
    wall_top = int(H * 0.62)
    wall_bot = H - 3
    # wall (vertical stripes)
    for x in range(8, W - 8):
        col = c1 if ((x - 8) // 8) % 2 == 0 else c2
        shade = tuple(int(v * 0.82) for v in col)
        d.line([x, wall_top, x, wall_bot], fill=(col if x < W - 30 else shade) + (255,))
    d.rectangle([8, wall_top, W - 9, wall_bot], outline=OUT)
    # scalloped valance
    for x in range(8, W - 8, 8):
        d.pieslice([x, wall_top - 5, x + 8, wall_top + 5], 0, 180, fill=(0xF0, 0xC0, 0x3A, 255), outline=OUT)
    # entrance
    d.polygon([(cx - 10, wall_bot), (cx + 10, wall_bot), (cx + 6, wall_top + 8), (cx - 6, wall_top + 8)], fill=(0x2A, 0x22, 0x2A, 255), outline=OUT)
    d.polygon([(cx - 10, wall_bot), (cx - 6, wall_top + 8), (cx - 14, wall_top + 6)], fill=c2 + (255,), outline=OUT)
    d.polygon([(cx + 10, wall_bot), (cx + 6, wall_top + 8), (cx + 14, wall_top + 6)], fill=c2 + (255,), outline=OUT)
    # roof: fan of stripes from the peak to the eave ellipse
    peak = (cx, 10)
    eave_y = wall_top
    n = 14
    for i in range(n):
        a0 = i / n
        a1 = (i + 1) / n
        x0 = 2 + a0 * (W - 4)
        x1 = 2 + a1 * (W - 4)
        y0 = eave_y + int(6 * math.sin(math.pi * a0))
        y1 = eave_y + int(6 * math.sin(math.pi * a1))
        col = c1 if i % 2 == 0 else c2
        if i >= n * 0.7:
            col = tuple(int(v * 0.86) for v in col)
        d.polygon([peak, (x0, y0), (x1, y1)], fill=col + (255,))
    d.line([peak, (2, eave_y)], fill=OUT)
    d.line([peak, (W - 3, eave_y)], fill=OUT)
    pts = [(2 + t * (W - 4) / 40, eave_y + int(6 * math.sin(math.pi * t / 40))) for t in range(41)]
    d.line(pts, fill=OUT)
    # pole + pennant
    d.line([cx, 10, cx, 0], fill=OUT)
    d.polygon([(cx + 1, 1), (cx + 9, 3), (cx + 1, 5)], fill=(0xF0, 0xC0, 0x3A, 255), outline=OUT)
    return img


# ------------------------------------------------------------------ grandstand
def grandstand(lib, seat_pid, bays=3, roof_rows=3):
    """Covered grandstand: repeated bleacher sections with a green tin roof on posts above."""
    seat = lib[seat_pid].img
    sw, sh = seat.size
    W = sw * bays
    H = sh + roof_rows * T
    img = Image.new("RGBA", (W, H))
    for b in range(bays):
        img.alpha_composite(seat, (b * sw, roof_rows * T))
    d = ImageDraw.Draw(img)
    roof_c = (0x4E, 0x7E, 0x5E, 255)
    roof_l = (0x6E, 0x9E, 0x7A, 255)
    rb = roof_rows * T - 4
    d.rectangle([0, 4, W - 1, rb], fill=roof_c, outline=OUT)
    for x in range(4, W - 2, 6):
        d.line([x, 5, x, rb - 1], fill=roof_l)
    d.rectangle([0, rb - 3, W - 1, rb], fill=(0xE8, 0xE2, 0xD0, 255), outline=OUT)
    # posts down into the seating
    for x in range(6, W, sw // 2):
        d.rectangle([x, rb, x + 2, rb + 14], fill=(0xE8, 0xE2, 0xD0, 255), outline=OUT)
    # pennants on every bay
    for b in range(bays * 2):
        px = int((b + 0.5) * W / (bays * 2))
        d.line([px, 0, px, 6], fill=OUT)
        d.polygon([(px + 1, 0), (px + 7, 2), (px + 1, 4)], fill=PENNANT[b % 4])
    return img


# ------------------------------------------------------------------ brick gate pillar / smokestack
BRICK = (0xA8, 0x4A, 0x3A, 255)
BRICK_D = (0x82, 0x36, 0x2C, 255)
BRICK_L = (0xC4, 0x66, 0x50, 255)
STONE_C = (0xE0, 0xD6, 0xC0, 255)


def brick_pillar(w=2, h=5):
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 8, W - 3, H - 2], fill=BRICK, outline=OUT)
    for y in range(12, H - 2, 4):
        d.line([3, y, W - 4, y], fill=BRICK_D)
        off = 0 if (y // 4) % 2 else 4
        for x in range(3 + off, W - 4, 8):
            d.line([x, y - 3, x, y], fill=BRICK_D)
    d.rectangle([3, 9, 5, H - 3], fill=BRICK_L)                       # lit left face
    d.rectangle([W - 7, 9, W - 4, H - 3], fill=BRICK_D)               # shaded right face
    d.rectangle([0, 5, W - 1, 10], fill=STONE_C, outline=OUT)        # stone coping
    d.line([1, 9, W - 2, 9], fill=(0xB8, 0xAE, 0x98, 255))
    d.ellipse([W // 2 - 4, -1, W // 2 + 3, 6], fill=STONE_C, outline=OUT)   # ball finial
    d.point((W // 2 - 2, 1), fill=(0xFF, 0xFF, 0xF8, 255))
    d.rectangle([1, H - 6, W - 2, H - 1], fill=STONE_C, outline=OUT)  # plinth
    return img


def gate_arch(span_tiles, pillar_w=2, h=5):
    """Fair main gate: 2 brick pillars carrying a timber arch (double curved beam with lattice),
    a blank painted sign board, bunting and pennants. Returns image (arch lives in the top ~3 rows)."""
    W = (span_tiles + 2 * pillar_w) * T
    H = h * T
    img = Image.new("RGBA", (W, H))
    top = 18                                     # pillars start a little lower so the arch rises above them
    p = brick_pillar(pillar_w, h - 1)
    img.alpha_composite(p, (0, H - p.size[1]))
    img.alpha_composite(p, (W - pillar_w * T, H - p.size[1]))
    d = ImageDraw.Draw(img)
    wood, wood_d, wood_l = (0xB0, 0x7A, 0x48, 255), (0x7A, 0x50, 0x30, 255), (0xD4, 0xA0, 0x68, 255)
    x0, x1 = 6, W - 7
    rise = 14

    def arc_y(x, base):
        return base - int(rise * math.sin(math.pi * (x - x0) / (x1 - x0)))

    # lattice between the two beams
    for x in range(x0 + 4, x1 - 3, 6):
        d.line([x, arc_y(x, top + 2), x + 3, arc_y(x, top + 12)], fill=wood_d)
        d.line([x + 3, arc_y(x, top + 2), x, arc_y(x, top + 12)], fill=wood_d)
    for base, hgt in ((top, 4), (top + 12, 3)):          # outer + inner curved beams
        for x in range(x0, x1 + 1):
            y = arc_y(x, base)
            d.line([x, y, x, y + hgt], fill=wood)
            d.point((x, y - 1), fill=OUT)
            d.point((x, y + hgt + 1), fill=OUT)
            d.point((x, y), fill=wood_l)
    # blank sign board hung from the crown (no lettering)
    bx0, bx1 = W // 2 - 22, W // 2 + 21
    by0 = arc_y(W // 2, top + 12) + 6
    for x in (bx0 + 6, bx1 - 6):
        d.line([x, by0 - 6, x, by0], fill=OUT)
    d.rectangle([bx0, by0, bx1, by0 + 11], fill=(0xF4, 0xEE, 0xE2, 255), outline=OUT)
    d.rectangle([bx0 + 2, by0 + 2, bx1 - 2, by0 + 9], outline=(0xD8, 0x3A, 0x36, 255))
    for x in range(bx0 + 6, bx1 - 4, 8):
        d.rectangle([x, by0 + 5, x + 3, by0 + 6], fill=(0x3E, 0x6E, 0xC4, 255))
    # bunting swag + pennants under the inner beam
    for i, x in enumerate(range(x0 + 6, x1 - 4, 7)):
        if bx0 - 2 <= x <= bx1 + 2:
            continue
        y = arc_y(x, top + 12) + 6
        d.polygon([(x - 2, y), (x + 2, y), (x, y + 5)], fill=PENNANT[i % 4])
    for x in (x0 + 2, x1 - 2):                               # flags on the beam ends
        d.line([x, top - 12, x, top], fill=OUT)
        d.polygon([(x + 1, top - 12), (x + 8, top - 10), (x + 1, top - 8)], fill=PENNANT[0])
    return img


def smokestack(h=9):
    W, H = 2 * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.polygon([(7, 6), (W - 8, 6), (W - 5, H - 2), (4, H - 2)], fill=BRICK, outline=OUT)
    for y in range(10, H - 2, 4):
        d.line([6, y, W - 7, y], fill=BRICK_D)
    d.line([8, 8, 6, H - 3], fill=BRICK_L)
    d.rectangle([5, 2, W - 6, 7], fill=(0x5A, 0x50, 0x50, 255), outline=OUT)
    d.rectangle([7, 3, W - 8, 5], fill=(0x22, 0x1E, 0x22, 255))
    for y in (H // 3, 2 * H // 3):
        d.rectangle([5, y, W - 6, y + 2], fill=(0x50, 0x50, 0x58, 255), outline=OUT)
    return img


# ------------------------------------------------------------------ small 1960s street furniture
def _cv(w, h):
    img = Image.new("RGBA", (w * T, h * T))
    return img, ImageDraw.Draw(img)


def hydrant():
    img, d = _cv(1, 2)
    red, redd, redl = (0xC8, 0x30, 0x2C, 255), (0x8A, 0x1E, 0x1E, 255), (0xE8, 0x60, 0x50, 255)
    d.ellipse([3, 27, 12, 31], fill=(0, 0, 0, 60))
    d.rectangle([5, 16, 10, 29], fill=red, outline=OUT)
    d.rectangle([3, 19, 12, 22], fill=red, outline=OUT)          # side nozzles
    d.pieslice([4, 12, 11, 20], 180, 360, fill=red, outline=OUT)  # dome
    d.rectangle([7, 11, 8, 13], fill=redd)
    d.line([6, 17, 6, 27], fill=redl)
    d.rectangle([4, 27, 11, 29], fill=redd, outline=OUT)
    return img


def phone_booth():
    img, d = _cv(2, 3)
    body, bodyd = (0xD8, 0xD4, 0xC8, 255), (0x9C, 0x98, 0x8E, 255)
    glass = (0x8C, 0xB8, 0xC8, 255)
    d.rectangle([5, 4, 26, 45], fill=body, outline=OUT)
    d.rectangle([5, 4, 26, 11], fill=(0x3A, 0x5C, 0x9C, 255), outline=OUT)   # blue header band
    d.rectangle([12, 6, 19, 9], fill=(0xF0, 0xEE, 0xE4, 255))                 # bell-ish plate
    d.rectangle([8, 14, 23, 41], fill=glass, outline=OUT)
    d.line([15, 14, 15, 41], fill=OUT)
    d.line([9, 15, 13, 23], fill=(0xD8, 0xF0, 0xF8, 255))
    d.rectangle([5, 42, 26, 46], fill=bodyd, outline=OUT)
    return img


def parking_meter():
    img, d = _cv(1, 2)
    d.line([7, 18, 7, 30], fill=OUT, width=2)
    d.rectangle([4, 9, 11, 18], fill=(0x8A, 0x8E, 0x96, 255), outline=OUT)
    d.rectangle([5, 11, 10, 14], fill=(0xE0, 0xE4, 0xD8, 255))
    d.point((8, 13), fill=(0xC8, 0x30, 0x2C, 255))
    d.rectangle([5, 29, 9, 30], fill=OUT)
    return img


def lamp_cobra(facing=1):
    """1950s cobra-head street light on a tall steel pole (1x5). facing=+1 arm to the right."""
    img, d = _cv(2, 5)
    x = 8 if facing > 0 else 23
    pole = (0x9A, 0x9E, 0xA8, 255)
    d.rectangle([x - 1, 10, x + 1, 77], fill=pole, outline=OUT)
    ax = x + 13 * facing
    d.line([x, 12, ax, 8], fill=OUT, width=3)
    d.line([x, 12, ax, 8], fill=pole, width=1)
    hx0, hx1 = sorted((ax - 2 * facing, ax + 6 * facing))
    d.ellipse([hx0, 5, hx1, 11], fill=(0x7A, 0x7E, 0x88, 255), outline=OUT)
    d.line([hx0 + 1, 11, hx1 - 1, 11], fill=(0xFF, 0xF4, 0xC0, 255))
    d.rectangle([x - 3, 74, x + 3, 78], fill=(0x6E, 0x72, 0x7C, 255), outline=OUT)
    return img


def lamp_iron():
    """Cast-iron single-globe lamp post (1x3), downtown / bridges."""
    img, d = _cv(1, 3)
    iron = (0x2E, 0x34, 0x38, 255)
    d.rectangle([6, 14, 9, 44], fill=iron)
    d.rectangle([4, 40, 11, 46], fill=iron, outline=OUT)
    d.rectangle([5, 12, 10, 15], fill=iron)
    d.ellipse([3, 2, 12, 13], fill=(0xFF, 0xF4, 0xD0, 255), outline=OUT)
    d.point((6, 5), fill=(0xFF, 0xFF, 0xFF, 255))
    d.rectangle([6, 0, 9, 2], fill=iron)
    return img


def register_all(lib):
    """Shared synthesized prefabs every district may use (ids prefixed sy_)."""
    lib.add_img("sy_hydrant", hydrant(), "prop", [[0, 1]], 1)
    lib.add_img("sy_phone_booth", phone_booth(), "prop", [[0, 2], [1, 2]], 2)
    lib.add_img("sy_parking_meter", parking_meter(), "prop", [[0, 1]], 1)
    lib.add_img("sy_lamp_cobra_r", lamp_cobra(1), "prop", [[0, 4]], 4)
    lib.add_img("sy_lamp_cobra_l", lamp_cobra(-1), "prop", [[1, 4]], 4)
    lib.add_img("sy_lamp_iron", lamp_iron(), "prop", [[0, 2]], 2)
    lib.add_img("sy_bigtop", big_top(12, 11), "building", "all", 3)
    lib.add_img("sy_smokestack", smokestack(9), "building", [[0, 8], [1, 8]], 7)


def oval_rail(L, cx, cy, rx, ry, gap_x=None, style="white", post_every=9):
    """Pixel-smooth white racetrack rail along an ellipse (tile-unit centre/radii, cell-centre
    convention like ellipse_fill). Drawn as one overlay and sliced into tiles: cells the ground line
    passes through go to Objects (solid), cells holding only post tops / upper rail go to Overhead.
    gap_x = (px0, px1) leaves an opening on the south half between those pixel x's."""
    rail, shade, post_h, rails_y, post_w, _ = FENCE_STYLES[style]
    pcx, pcy = cx * T + 8, cy * T + 8
    prx, pry = rx * T, ry * T
    x0, y0 = int(pcx - prx) - 4, int(pcy - pry) - post_h - 4
    x1, y1 = int(pcx + prx) + 4, int(pcy + pry) + 4
    ox, oy = (x0 // T) * T, (y0 // T) * T
    W = ((x1 // T) + 1) * T - ox
    H = ((y1 // T) + 1) * T - oy
    cv = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(cv)
    n = int(2 * math.pi * max(prx, pry))
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        px, py = pcx + prx * math.cos(a), pcy + pry * math.sin(a)
        in_gap = gap_x and py > pcy and gap_x[0] <= px < gap_x[1]
        pts.append((px, py, in_gap))
    ground_cells = set()
    # rails (two, at rails_y above ground)
    for (pa, pb) in zip(pts, pts[1:]):
        if pa[2] or pb[2]:
            continue
        for k, ry_off in enumerate(rails_y):
            d.line([(pa[0] - ox, pa[1] - oy - ry_off), (pb[0] - ox, pb[1] - oy - ry_off)], fill=rail)
            d.line([(pa[0] - ox, pa[1] - oy - ry_off + 1), (pb[0] - ox, pb[1] - oy - ry_off + 1)], fill=shade)
        ground_cells.add((int(pa[0] // T), int((pa[1] - 2) // T)))
    # posts at regular arc length, plus end posts at the gap
    acc = 0.0
    prev = pts[0]
    for p in pts[1:]:
        acc += math.hypot(p[0] - prev[0], p[1] - prev[1])
        edge = p[2] != prev[2]
        if (acc >= post_every and not p[2]) or edge:
            q = p if not p[2] else prev
            acc = 0.0
            qx, qy = q[0] - ox, q[1] - oy
            d.rectangle([qx - 1, qy - post_h - 1, qx + 1, qy], fill=OUT)
            d.line([qx, qy - post_h, qx, qy - 1], fill=rail)
        prev = p
    # slice
    for ty in range(H // T):
        for tx in range(W // T):
            tile = cv.crop((tx * T, ty * T, tx * T + T, ty * T + T))
            if not tile.getchannel("A").getbbox():
                continue
            cx_, cy_ = ox // T + tx, oy // T + ty
            if (cx_, cy_) in ground_cells:
                L.put("Objects", cx_, cy_, tile, True, "alpha")
            else:
                L.put("Overhead", cx_, cy_, tile, False, "alpha")


def _ring_inside(px, py, pcx, pcy, ro, ri):
    dx, dy = px - pcx, py - pcy
    return (dx / ro[0]) ** 2 + (dy / ro[1]) ** 2 <= 1.0 and (dx / ri[0]) ** 2 + (dy / ri[1]) ** 2 > 1.0


def smooth_ring_cells(cx, cy, ro, ri):
    """Classify cells against a pixel-accurate elliptical ring (radii in tiles, (rx, ry) tuples).
    Returns (full, partial): cells entirely inside the ring, and cells it only partly covers."""
    pcx, pcy = cx * T + 8, cy * T + 8
    rop, rip = (ro[0] * T, ro[1] * T), (ri[0] * T, ri[1] * T)
    full, partial = set(), set()
    for y in range(int(cy - ro[1]) - 2, int(cy + ro[1]) + 3):
        for x in range(int(cx - ro[0]) - 2, int(cx + ro[0]) + 3):
            n = 0
            for sy in range(1, 16, 3):
                for sx in range(1, 16, 3):
                    n += _ring_inside(x * T + sx, y * T + sy, pcx, pcy, rop, rip)
            if n == 36:
                full.add((x, y))
            elif n:
                partial.add((x, y))
    return full, partial


def smooth_ring_decals(L, cx, cy, ro, ri, cells, tex=("A2_Floors_MV_TILESET.png", 12, 4)):
    """Paint the partially covered cells of a ring as masked dirt decals with a soft dark edge."""
    pcx, pcy = cx * T + 8, cy * T + 8
    rop, rip = (ro[0] * T, ro[1] * T), (ri[0] * T, ri[1] * T)
    edge = (0x8A, 0x5A, 0x34, 255)
    for (x, y) in cells:
        src = TR.tile(tex[0], tex[1] + (x % 2), tex[2] + (y % 2))
        out = Image.new("RGBA", (T, T))
        sp, op = src.load(), out.load()
        for yy in range(T):
            for xx in range(T):
                if _ring_inside(x * T + xx + 0.5, y * T + yy + 0.5, pcx, pcy, rop, rip):
                    border = not all(_ring_inside(x * T + xx + 0.5 + ddx, y * T + yy + 0.5 + ddy, pcx, pcy, rop, rip)
                                     for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    op[xx, yy] = edge if border else sp[xx, yy]
        L.put("Decals", x, y, out)


def grandstand2(w=24, h=9, seed=0):
    """Covered wooden grandstand facing south: green tin roof with shaded underside and press box,
    stepped bench tiers (light planks / dark risers) with a sparse crowd, concrete aisles, steel posts."""
    import random as _r
    rng = _r.Random(seed)
    W, H = w * T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    roof_b = 2 * T + 6
    # seating tiers
    tier_h = 8
    y = roof_b
    k = 0
    while y + tier_h <= H - 6:
        d.rectangle([2, y, W - 3, y + 2], fill=(0xDC, 0xC8, 0xA4, 255))          # bench plank
        d.rectangle([2, y + 3, W - 3, y + tier_h - 1], fill=(0x6E, 0x58, 0x46, 255))  # riser
        d.line([2, y + 3, W - 3, y + 3], fill=(0x4E, 0x3E, 0x32, 255))
        # crowd
        for x in range(6, W - 6, 5):
            if rng.random() < 0.38:
                shirt = rng.choice([(0xC8, 0x3A, 0x34), (0x3A, 0x6A, 0xB4), (0xF0, 0xE8, 0xD8), (0x5A, 0x8A, 0x4A),
                                    (0xE8, 0xB8, 0x3A), (0x8A, 0x5A, 0x9A)])
                skin = rng.choice([(0xE8, 0xB8, 0x8C), (0xC8, 0x8C, 0x5C), (0x8C, 0x5A, 0x3A)])
                d.rectangle([x, y - 4, x + 2, y - 2], fill=skin + (255,))
                d.rectangle([x - 1, y - 1, x + 3, y + 2], fill=shirt + (255,))
                if rng.random() < 0.3:
                    d.rectangle([x - 1, y - 6, x + 3, y - 5], fill=(0x4A, 0x3A, 0x30, 255))   # hat
        y += tier_h
        k += 1
    # aisles + posts
    for ax in range(5 * T, W - 4 * T, 7 * T):
        d.rectangle([ax, roof_b, ax + 9, H - 6], fill=(0xB4, 0xB0, 0xAA, 255))
        for yy in range(roof_b + 2, H - 6, 4):
            d.line([ax, yy, ax + 9, yy], fill=(0x8C, 0x88, 0x84, 255))
    for px in range(8, W, 4 * T):
        d.rectangle([px, roof_b, px + 2, H - 4], fill=(0x5A, 0x5E, 0x68, 255), outline=OUT)
    # front rail
    d.rectangle([0, H - 6, W - 1, H - 3], fill=(0xF2, 0xEE, 0xE4, 255), outline=OUT)
    for px in range(4, W, 8):
        d.line([px, H - 6, px, H - 1], fill=(0xC4, 0xBC, 0xB0, 255))
    # roof: tin top, white fascia, shaded underside
    d.rectangle([0, 6, W - 1, roof_b - 6], fill=(0x4E, 0x7E, 0x5E, 255), outline=OUT)
    for x in range(4, W - 2, 6):
        d.line([x, 7, x, roof_b - 7], fill=(0x6E, 0x9E, 0x7A, 255))
    d.rectangle([0, roof_b - 6, W - 1, roof_b - 3], fill=(0xEC, 0xE6, 0xD6, 255), outline=OUT)
    d.rectangle([2, roof_b - 2, W - 3, roof_b + 1], fill=(0x2E, 0x2A, 0x2E, 160))
    # press box on the roof centre
    bx = W // 2 - 20
    d.rectangle([bx, 0, bx + 40, 14], fill=(0xEC, 0xE6, 0xD6, 255), outline=OUT)
    d.rectangle([bx - 2, 0, bx + 42, 3], fill=(0xB8, 0x34, 0x2C, 255), outline=OUT)
    for wx in range(bx + 4, bx + 37, 8):
        d.rectangle([wx, 6, wx + 5, 11], fill=(0x6A, 0x8C, 0xA8, 255), outline=OUT)
    # pennants along the roof edge
    for i, px in enumerate(range(10, W - 6, 20)):
        if bx - 4 <= px <= bx + 44:
            continue
        d.line([px, 0, px, 7], fill=OUT)
        d.polygon([(px + 1, 0), (px + 7, 2), (px + 1, 4)], fill=PENNANT[i % 4])
    return img
