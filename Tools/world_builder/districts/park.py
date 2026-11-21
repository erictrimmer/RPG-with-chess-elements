"""Penn Park (the old town commons) + Carlisle Ave dressing - brief 3.5 / 2.6 (S8) / 5 (Penn Park).

Layout (tile coords, inclusive):
  Carlisle Ave x=0..41, y=78..87: sidewalks 78..79 / 86..87, road 80..85 kept clear,
    sawhorse roadblock x=0..1, crosswalk x=16..19 linking the fair gate to the park gate
  north hedge x=2..37 y=88..89 (gap x=16..19, stone gate piers), east hedge x=36..37 y=88..121 (gap y=106..109)
  south iron fence y=122 (rail bed beyond), border trees x=0..1
  N-S gravel path x=16..19 y=88..121, E-W gravel path x=2..35 y=104..107 (+ jog to the east gap)
  round plaza x=13..22 y=100..109 with the Soldiers & Sailors column x=16..19 y=98..106 (top overhead)
  duck pond x=4..11 y=92..99, bandstand x=24..31 y=92..98, playground x=22..29 y=110..118,
  flood pump house x=30..35 y=113..119 (grated door 32..33,119),
  hobo camp S8 x=2..5 y=116..118 under trees, entered by the gap x=6..7 y=116..117
"""
import math
import random

from PIL import Image, ImageDraw

import buildings
import dress
import synth

REGION = (0, 88, 37, 123)
T = 16
OUT = (0x3D, 0x3D, 0x52, 255)
PLAZA_C = (17.5, 104.5)
WHITE = (0xF4, 0xF0, 0xE8)
WHITE_D = (0xC8, 0xC2, 0xB6)


def _c(rgb, a=255):
    return tuple(rgb[:3]) + (a,)


def _shade(rgb, f):
    return tuple(max(0, min(255, int(v * f))) for v in rgb[:3]) + (255,)


# ============================================================================ synthesized art
def gazebo_img(wt=8, ht=7):
    """White octagonal bandstand, 3/4 view: stone base, lattice skirt, white posts + railings,
    red shingled octagonal roof with white trim, gold finial and bunting."""
    W, H = wt * T, ht * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    cx = W // 2

    def octo(cy, rx, ry):
        return [(cx + rx * math.cos(math.pi / 8 + k * math.pi / 4), cy + ry * math.sin(math.pi / 8 + k * math.pi / 4))
                for k in range(8)]

    deck_cy, deck_rx, deck_ry = H - 30, W // 2 - 4, 20
    # shadow
    d.ellipse([6, H - 22, W - 6, H - 2], fill=(0, 0, 0, 50))
    # skirt (front face of the raised base): lattice
    base = octo(deck_cy, deck_rx, deck_ry)
    skirt = [p for p in base if p[1] >= deck_cy - 1]
    skirt.sort(key=lambda p: p[0])
    poly = skirt + [(p[0], p[1] + 9) for p in reversed(skirt)]
    d.polygon(poly, fill=_c(WHITE_D), outline=OUT)
    for x in range(int(skirt[0][0]) + 2, int(skirt[-1][0]) - 1, 4):
        d.line([x, deck_cy + 8, x + 4, deck_cy + 24], fill=_c((0x9C, 0x96, 0x8C)))
        d.line([x + 4, deck_cy + 8, x, deck_cy + 24], fill=_c((0x9C, 0x96, 0x8C)))
    d.polygon(poly, outline=OUT)
    # deck
    d.polygon(base, fill=_c((0xC8, 0xAA, 0x7E)), outline=OUT)
    for y in range(deck_cy - deck_ry + 3, deck_cy + deck_ry, 3):
        d.line([cx - deck_rx + 6, y, cx + deck_rx - 6, y], fill=_c((0xB4, 0x94, 0x68)))
    d.polygon(base, outline=OUT)
    # steps at the front
    for i in range(3):
        y = deck_cy + deck_ry - 2 + i * 4
        d.rectangle([cx - 12 - i * 2, y, cx + 11 + i * 2, y + 4], fill=_c((0xD8, 0xD4, 0xCC)), outline=OUT)
    # posts + railings
    eave_cy, eave_ry = 44, 20
    posts = octo(deck_cy, deck_rx - 5, deck_ry - 4)
    back = [p for p in posts if p[1] < deck_cy]
    front = [p for p in posts if p[1] >= deck_cy]
    # shade under the roof (interior)
    d.polygon(octo(deck_cy - 6, deck_rx - 8, deck_ry - 6), fill=(0x40, 0x34, 0x3C, 70))
    for (px, py) in back:
        d.rectangle([px - 2, eave_cy + 4, px + 2, py], fill=_c(WHITE_D), outline=OUT)
    # railing (back arc, low)
    for (a, b) in zip(sorted(back), sorted(back)[1:]):
        d.line([a[0], a[1] - 9, b[0], b[1] - 9], fill=_c(WHITE), width=2)
    for (px, py) in front:
        d.rectangle([px - 2, eave_cy + 6, px + 2, py + 2], fill=_c(WHITE), outline=OUT)
    fr = sorted(front)
    for (a, b) in zip(fr, fr[1:]):
        if abs((a[0] + b[0]) / 2 - cx) < 12:
            continue                       # front opening over the steps
        d.line([a[0] + 2, a[1] - 9, b[0] - 2, b[1] - 9], fill=_c(WHITE), width=2)
        d.line([a[0] + 2, a[1] - 7, b[0] - 2, b[1] - 7], fill=OUT)
        n = int(abs(b[0] - a[0]) // 4)
        for k in range(1, n):
            t = k / n
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            d.line([x, y - 9, x, y], fill=_c(WHITE))
    # roof: octagonal pyramid
    eave = octo(eave_cy, W // 2 - 1, eave_ry)
    apex = (cx, 4)
    red, red_d, red_l = (0xB8, 0x3A, 0x34), (0x8E, 0x2A, 0x28), (0xD0, 0x56, 0x48)
    order = sorted(range(8), key=lambda k: eave[k][1])
    for k in order:
        a, b = eave[k], eave[(k + 1) % 8]
        midx = (a[0] + b[0]) / 2
        col = red_l if midx < cx - 20 else (red if midx < cx + 20 else red_d)
        d.polygon([apex, a, b], fill=_c(col))
        # shingle courses
        for t in (0.35, 0.55, 0.75):
            p = (apex[0] + (a[0] - apex[0]) * t, apex[1] + (a[1] - apex[1]) * t)
            q = (apex[0] + (b[0] - apex[0]) * t, apex[1] + (b[1] - apex[1]) * t)
            d.line([p, q], fill=_shade(col, 0.8))
    for k in range(8):
        a = eave[k]
        if a[1] > eave_cy - 6:
            d.line([apex, a], fill=_c(WHITE))
    front_eave = sorted([p for p in eave if p[1] >= eave_cy - eave_ry * 0.75], key=lambda p: p[0])
    d.line(front_eave, fill=_c(WHITE), width=3)
    d.line([(p[0], p[1] + 2) for p in front_eave], fill=OUT)
    d.polygon([apex] + front_eave, outline=OUT)
    # bunting under the front eave
    for i in range(len(front_eave) - 1):
        a, b = front_eave[i], front_eave[i + 1]
        for k in range(0, int(abs(b[0] - a[0])) - 2, 6):
            t = k / max(1, abs(b[0] - a[0]))
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t + 3
            col = synth.PENNANT[(i * 3 + k // 6) % 3]
            d.polygon([(x, y), (x + 4, y), (x + 2, y + 4)], fill=col)
    # finial
    d.line([cx, 4, cx, 0], fill=OUT, width=2)
    d.ellipse([cx - 3, 0, cx + 2, 5], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)
    return img


def soldier_statue():
    """2x2 bronze (verdigris) Civil-War soldier at parade rest on a capstone."""
    img = Image.new("RGBA", (2 * T, 2 * T))
    d = ImageDraw.Draw(img)
    g, gd, gl = (0x5E, 0x8E, 0x7C), (0x3C, 0x62, 0x58), (0x86, 0xB4, 0x9E)
    cx = 16
    # legs + greatcoat
    d.polygon([(cx - 5, 30), (cx - 4, 17), (cx + 4, 17), (cx + 5, 30)], fill=_c(g), outline=OUT)
    d.line([cx, 23, cx, 30], fill=_c(gd))
    # torso
    d.rectangle([cx - 5, 9, cx + 4, 18], fill=_c(g), outline=OUT)
    d.line([cx - 4, 10, cx - 4, 17], fill=_c(gl))
    d.line([cx - 5, 13, cx + 4, 13], fill=_c(gd))       # belt
    # head + kepi
    d.ellipse([cx - 3, 3, cx + 2, 9], fill=_c(g), outline=OUT)
    d.rectangle([cx - 3, 1, cx + 2, 4], fill=_c(gd), outline=OUT)
    d.line([cx - 4, 4, cx + 3, 4], fill=OUT)
    # rifle held vertically at the right side, hands crossed on the muzzle
    d.line([cx + 7, 2, cx + 7, 30], fill=_c(gd), width=2)
    d.line([cx + 8, 3, cx + 8, 29], fill=OUT)
    d.rectangle([cx + 4, 10, cx + 8, 13], fill=_c(gl), outline=OUT)
    # base slab
    d.rectangle([cx - 8, 29, cx + 9, 31], fill=_c((0xB8, 0xB4, 0xB0)), outline=OUT)
    return img


def monument(lib, ht=11):
    """Soldiers & Sailors column: stepped granite plinth with bronze plaque + wreaths, tall fluted
    marble column (catalog pier with its shaft lengthened), soldier statue on top. 4 x ht."""
    W, H = 4 * T, ht * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    gr, grd, grl = (0xA8, 0xA6, 0xAC), (0x7C, 0x7A, 0x84), (0xCC, 0xCA, 0xD0)
    d.ellipse([0, H - 12, W - 1, H - 1], fill=(0, 0, 0, 50))
    # steps
    d.rectangle([1, H - 12, W - 2, H - 3], fill=_c(gr), outline=OUT)
    d.line([2, H - 11, W - 3, H - 11], fill=_c(grl))
    d.rectangle([6, H - 20, W - 7, H - 12], fill=_c(gr), outline=OUT)
    d.line([7, H - 19, W - 8, H - 19], fill=_c(grl))
    # die block
    d.rectangle([12, H - 44, W - 13, H - 20], fill=_c(gr), outline=OUT)
    d.rectangle([12, H - 44, 15, H - 21], fill=_c(grl))
    d.rectangle([W - 16, H - 44, W - 13, H - 21], fill=_c(grd))
    d.rectangle([10, H - 47, W - 11, H - 43], fill=_c(grl), outline=OUT)     # cornice
    d.rectangle([20, H - 40, W - 21, H - 29], fill=_c((0x6E, 0x8E, 0x6E)), outline=OUT)   # bronze plaque
    for y in range(H - 37, H - 31, 2):
        d.line([23, y, W - 24, y], fill=_c((0x9C, 0xBC, 0x98)))
    # column: catalog marble pier, shaft lengthened by repeating a fluted slice
    col = lib["cf_pier_capstone_marble_a"].img
    col = col.crop((0, col.getbbox()[1], col.size[0], col.size[1]))
    cw = col.size[0]
    top, mid, bot = col.crop((0, 0, cw, 26)), col.crop((0, 26, cw, 48)), col.crop((0, 48, cw, col.size[1] - 6))
    extra = H - 47 - 26 - (top.size[1] + mid.size[1] + bot.size[1])
    parts = [top, mid] + [mid] * max(0, extra // mid.size[1]) + [mid.crop((0, 0, cw, max(1, extra % mid.size[1])))] + [bot]
    shaft = Image.new("RGBA", (cw, sum(p.size[1] for p in parts)))
    yy = 0
    for p in parts:
        shaft.alpha_composite(p, (0, yy))
        yy += p.size[1]
    sx = (W - cw) // 2
    img.alpha_composite(shaft, (sx, H - 47 - shaft.size[1] + 2))
    img.alpha_composite(soldier_statue(), ((W - 32) // 2, H - 47 - shaft.size[1] - 26))
    # wreaths leaning on the steps
    for (wx, wy) in ((6, H - 20), (W - 18, H - 20)):
        d.ellipse([wx, wy, wx + 11, wy + 11], outline=_c((0x3E, 0x7A, 0x3E)), width=3)
        d.ellipse([wx - 1, wy - 1, wx + 12, wy + 12], outline=OUT)
        d.ellipse([wx + 3, wy + 3, wx + 8, wy + 8], outline=OUT)
        for k in range(0, 360, 60):
            px = wx + 5.5 + 4.5 * math.cos(math.radians(k))
            py = wy + 5.5 + 4.5 * math.sin(math.radians(k))
            d.point((px, py), fill=_c((0x6A, 0xA8, 0x5A)))
        d.polygon([(wx + 3, wy + 9), (wx + 8, wy + 9), (wx + 5, wy + 13)], fill=_c((0xC8, 0x30, 0x2C)))
    return img


def pump_house(wt=6, ht=7):
    """Small 1930s flood-control pump house: flat concrete roof, board-formed walls, grated steel
    door facing south, louvre vents, a stub of discharge pipe, hazard pictogram."""
    W, H = wt * T, ht * T
    fr = 3
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(buildings.flat_roof(wt, ht - fr + 1, "gravel", seed=3, hatch=False), (0, 0))
    d = ImageDraw.Draw(img)
    # roof vent + conduit
    d.rectangle([W - 30, 14, W - 18, 26], fill=_c((0xA8, 0xAC, 0xB4)), outline=OUT)
    for y in range(17, 25, 2):
        d.line([W - 28, y, W - 20, y], fill=_c((0x6A, 0x6E, 0x78)))
    d.rectangle([12, 20, 20, 28], fill=_c((0x8A, 0x8E, 0x96)), outline=OUT)
    fy = (ht - fr) * T
    con, cond, conl = (0xB8, 0xB6, 0xB0), (0x96, 0x94, 0x90), (0xD4, 0xD2, 0xCC)
    d.rectangle([0, fy, W - 1, H - 2], fill=_c(con), outline=OUT)
    for y in range(fy + 6, H - 4, 5):
        d.line([1, y, W - 2, y], fill=_c(cond))
        d.line([1, y + 1, W - 2, y + 1], fill=_c(conl))
    for x in range(12, W, 24):
        for y in range(fy + 4, H - 4, 10):
            d.point((x, y), fill=_c((0x6E, 0x6C, 0x6A)))
    d.rectangle([0, fy, W - 1, fy + 3], fill=_c(conl), outline=OUT)
    # water-stain streaks
    for x in (8, 30, 70):
        d.line([x, fy + 4, x, fy + 14], fill=_c((0x8E, 0x8C, 0x82)))
    # grated steel door (centre, 2 tiles)
    dx0 = (wt // 2 - 1) * T + 2
    dx1 = dx0 + 2 * T - 5
    dy0 = fy + 8
    d.rectangle([dx0 - 2, dy0 - 2, dx1 + 2, H - 2], fill=_c(cond), outline=OUT)
    d.rectangle([dx0, dy0, dx1, H - 3], fill=_c((0x2A, 0x2C, 0x32)))
    for x in range(dx0 + 2, dx1, 3):
        d.line([x, dy0, x, H - 3], fill=_c((0x6E, 0x74, 0x7E)))
    for y in (dy0 + 4, dy0 + 18, H - 8):
        d.line([dx0, y, dx1, y], fill=_c((0x8A, 0x90, 0x9A)), width=2)
    d.rectangle([dx0 + 11, dy0 + 12, dx0 + 15, dy0 + 16], fill=_c((0xD8, 0xB0, 0x40)), outline=OUT)   # padlock
    # hazard pictogram (yellow triangle + bolt) beside the door
    hx, hy = dx1 + 8, fy + 12
    d.rectangle([hx, hy + 1, hx + 10, hy + 9], fill=_c((0xE8, 0xE4, 0xD8)), outline=OUT)   # plain enamel placard
    d.line([hx + 2, hy + 4, hx + 8, hy + 4], fill=_c((0x3A, 0x5C, 0x9C)))
    d.line([hx + 2, hy + 6, hx + 7, hy + 6], fill=_c((0x3A, 0x5C, 0x9C)))
    # louvre vents high on the wall
    for vx in (6, W - 22):
        d.rectangle([vx, fy + 8, vx + 14, fy + 16], fill=_c((0x7E, 0x80, 0x86)), outline=OUT)
        for y in range(fy + 10, fy + 16, 2):
            d.line([vx + 1, y, vx + 13, y], fill=_c((0x4E, 0x50, 0x58)))
    # discharge pipe stub on the east wall
    d.rectangle([W - 8, H - 18, W - 1, H - 10], fill=_c((0x7A, 0x6A, 0x62)), outline=OUT)
    d.line([W - 7, H - 16, W - 2, H - 16], fill=_c((0xA8, 0x8A, 0x70)))
    d.line([0, H - 1, W - 1, H - 1], fill=(0, 0, 0, 60))
    return img


def drinking_fountain():
    img = Image.new("RGBA", (T, 2 * T))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 26, 14, 31], fill=(0, 0, 0, 50))
    d.rectangle([5, 14, 10, 29], fill=_c((0xB8, 0xB6, 0xB0)), outline=OUT)
    d.line([6, 15, 6, 28], fill=_c((0xD4, 0xD2, 0xCC)))
    d.ellipse([1, 8, 14, 16], fill=_c((0xC8, 0xC6, 0xC2)), outline=OUT)
    d.ellipse([4, 10, 11, 14], fill=_c((0x6C, 0x9C, 0xC4)))
    d.line([8, 11, 9, 6], fill=_c((0xC8, 0xE8, 0xF8)))
    d.point((10, 7), fill=_c((0xC8, 0xE8, 0xF8)))
    return img


def duck(kind=0, flip=False):
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    body = (0xF4, 0xF0, 0xE8) if kind == 0 else (0x9A, 0x7A, 0x5E)
    head = (0xF4, 0xF0, 0xE8) if kind == 0 else (0x2E, 0x7A, 0x4E)
    d.ellipse([2, 11, 13, 15], fill=(0xA8, 0xD4, 0xE8, 160))           # ripple
    d.ellipse([3, 7, 12, 13], fill=_c(body), outline=OUT)
    d.ellipse([9, 3, 13, 8], fill=_c(head), outline=OUT)
    d.point((11, 5), fill=OUT)
    d.line([13, 6, 15, 6], fill=_c((0xF0, 0xA0, 0x30)))
    d.line([3, 8, 2, 7], fill=OUT)
    if kind == 1:
        d.line([9, 8, 12, 8], fill=_c(WHITE))
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img


def bedroll():
    """2x1 rolled-out army blanket with a rolled pillow, top view."""
    img = Image.new("RGBA", (2 * T, T))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 3, 29, 13], 3, fill=_c((0x6A, 0x6E, 0x48)), outline=OUT)
    for x in range(6, 28, 5):
        d.line([x, 4, x, 12], fill=_c((0x58, 0x5C, 0x3C)))
    d.line([3, 6, 28, 6], fill=_c((0x8C, 0x5A, 0x3A)))
    d.rounded_rectangle([3, 4, 9, 12], 2, fill=_c((0xC8, 0xB8, 0x98)), outline=OUT)
    d.line([20, 13, 26, 13], fill=(0, 0, 0, 60))
    return img


def tin_cans():
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.rectangle([3, 7, 7, 13], fill=_c((0xB4, 0xB8, 0xC0)), outline=OUT)
    d.line([4, 9, 6, 9], fill=_c((0xC8, 0x30, 0x2C)))
    d.ellipse([8, 10, 14, 14], fill=_c((0x9A, 0x9E, 0xA8)), outline=OUT)
    d.line([10, 6, 12, 2], fill=_c((0x6A, 0x4A, 0x36)), width=2)       # bindle stick
    d.ellipse([10, 0, 15, 5], fill=_c((0xC8, 0x30, 0x2C)), outline=OUT)
    d.point((12, 2), fill=_c(WHITE))
    return img


def flower_ring(rx=2.6, ry=2.0, seed=0):
    """Round flower bed decal (5x4) for the monument plaza corners."""
    rng = random.Random(seed)
    W, H = 5 * T, 4 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, W - 3, H - 3], fill=_c((0x6E, 0x50, 0x3A)), outline=_c((0x9C, 0x98, 0x94)))
    d.ellipse([4, 4, W - 5, H - 5], outline=_c((0x58, 0x40, 0x30)))
    cols = [(0xE0, 0x4C, 0x4C), (0xF4, 0xF0, 0xE8), (0xE8, 0x7C, 0xC0), (0xF0, 0xC0, 0x3A)]
    for _ in range(140):
        a = rng.random() * 2 * math.pi
        r = math.sqrt(rng.random())
        x = W / 2 + (W / 2 - 6) * r * math.cos(a)
        y = H / 2 + (H / 2 - 6) * r * math.sin(a)
        d.point((x, y), fill=_c((0x4E, 0x8A, 0x3E)))
        if rng.random() < 0.45:
            c = cols[rng.randint(0, 3)]
            d.rectangle([x, y, x + 1, y + 1], fill=_c(c))
    return img


def register(lib):
    if "park_gazebo" in lib:
        return
    # bandstand: roof rows overhead, raised base solid
    lib.add_img("park_gazebo", gazebo_img(8, 7), "prop",
                [[x, y] for y in (3, 4, 5, 6) for x in range(8) if not (y == 6 and x in (0, 7))], 3)
    lib.add_img("park_monument", monument(lib, 11), "statue",
                [[x, y] for y in (9, 10) for x in range(4)] + [[1, 8], [2, 8]], 8)
    lib.add_img("park_pump_house", pump_house(6, 7), "building", "all", 0, [[2, 6], [3, 6]])
    lib.add_img("park_fountain", drinking_fountain(), "prop", [[0, 1]], 1)
    lib.add_img("park_duck_w", duck(0), "prop", [], 0)
    lib.add_img("park_duck_wl", duck(0, True), "prop", [], 0)
    lib.add_img("park_duck_m", duck(1), "prop", [], 0)
    lib.add_img("park_duck_ml", duck(1, True), "prop", [], 0)
    lib.add_img("park_bedroll", bedroll(), "decal", [], 0)
    lib.add_img("park_tin_cans", tin_cans(), "prop", [], 0)
    lib.add_img("park_flower_ring_a", flower_ring(seed=1), "decal", [], 0)
    lib.add_img("park_flower_ring_b", flower_ring(seed=2), "decal", [], 0)
    lib.add_img("park_soldier", soldier_statue(), "statue", [], 0)
    # hedge pieces cut from the boxwood maze reference (Tileset_69)
    from terrain import tile
    hp = {
        "top_l": (1, 0), "top_m": (2, 0), "top_r": (3, 0),
        "face_l": (1, 1), "face_m": (2, 1), "face_r": (3, 1),
        "side_l": (1, 4), "side_r": (3, 4),
    }
    for k, (tx, ty) in hp.items():
        lib.add_img(f"park_hedge_{k}", tile("Tileset_69_MV.png", tx, ty).copy(), "hedge", "all", 0)
    sl, sr = tile("Tileset_69_MV.png", 1, 4), tile("Tileset_69_MV.png", 3, 4)
    inner = Image.new("RGBA", (T, T))
    inner.alpha_composite(sr.crop((0, 0, 8, 16)), (0, 0))
    inner.alpha_composite(sl.crop((8, 0, 16, 16)), (8, 0))
    lib.add_img("park_hedge_in", inner, "hedge", "all", 0)


# ============================================================================ ground
def plaza_cells():
    return synth.ellipse_fill(PLAZA_C[0], PLAZA_C[1], 5, 5)


def pond_cells():
    return synth.ellipse_fill(7.5, 95.5, 4.2, 4.0)


def build_ground(L, lib):
    L.fill("grass", 2, 88, 37, 123)
    L.fill("dirt", 16, 88, 19, 121)            # N-S gravel path (incl. hedge gap)
    L.fill("dirt", 2, 104, 35, 107)            # E-W gravel path
    L.fill("dirt", 32, 104, 37, 109)           # jog to the east hedge gap / King St bridge path
    for (x, y) in plaza_cells():
        L.set_kind(x, y, "plaza_grey")
    for (x, y) in pond_cells():
        L.set_kind(x, y, "pond")
    L.fill("dirt", 22, 111, 28, 117)           # playground sand
    L.fill("dirt", 3, 116, 7, 118)             # hobo camp trampled clearing
    L.fill("dirt", 29, 118, 35, 120)           # gravel apron in front of the pump house
    L.fill("dirt", 20, 119, 28, 120)           # service track from the N-S path to the pump house
    L.fill("dirt", 26, 99, 29, 103)            # short gravel walk from the bandstand steps to the E-W path


# ============================================================================ build
def _hedge(L, cells):
    H = set(cells)
    for (x, y) in H:
        N, S, W_, E = (x, y - 1) in H, (x, y + 1) in H, (x - 1, y) in H, (x + 1, y) in H
        if not S:
            k = "face_l" if not W_ else ("face_r" if not E else "face_m")
        elif not N:
            k = "top_l" if not W_ else ("top_r" if not E else "top_m")
        else:
            k = "side_l" if not W_ else ("side_r" if not E else "in")
        p = L.lib[f"park_hedge_{k}"]
        L.put("Objects", x, y, p.img, True, "full", (p.id, 0, 0))


def _carlisle(L):
    # sawhorse roadblock at the west map edge
    L.block(0, 78, 1, 87)
    for (pid, y) in [("sp_sawhorse_plain", 78), ("sp_sawhorse_no_entry", 80), ("sp_sawhorse_plain", 82),
                     ("sp_sawhorse_no_entry_big", 84), ("sp_sawhorse_plain", 86)]:
        L.place(pid, 0, y)
    # crosswalk fair gate <-> park gate, clear the centre dashes inside it
    for x in range(16, 20):
        for y in range(80, 86):
            L.clear_cell("Decals", x, y)
    import decals as DC
    DC.crosswalk_across_h_road(L, 80, 85, 15, 20)
    # curb-row furniture only (inner sidewalk row stays clear)
    L.place("sy_lamp_cobra_r", 7, 75)          # base (7,79)
    L.place("sy_lamp_cobra_r", 27, 75)         # base (27,79)
    L.place("sp_bus_stop_sign_pictogram", 23, 77)   # base (23,79) by the fair gate
    L.place("sy_hydrant", 12, 85)              # base (12,86)
    L.place("sp_utility_pole_crossarm", 4, 83)     # base (4,86)
    L.place("sp_utility_pole_crossarm", 31, 83)    # base (31,86)
    L.place("sp_mailbox_blue", 23, 85)          # base (23,86)
    L.place("sp_trashcan_metal", 9, 85)         # base (9,86)
    L.place("sf_newspaper_box", 25, 78)         # base (25,79)
    L.place("sp_utility_pole_crossarm", 39, 83)    # base (39,86)


def _boundaries(L):
    L.block(0, 88, 1, 123)
    # border trees x=0..1
    seq = ["nt_s26_conifer_tall", "nt_s26_tree_round_small", "nt_s1_round_tree", "nt_s27_spruce_tall"]
    for i, y in enumerate(range(90, 122, 2)):
        pid = seq[i % 4]
        L.place(pid, 0, y - L.lib[pid].h + 1)
    # hedges
    north = {(x, y) for x in range(2, 38) for y in (88, 89) if not 14 <= x <= 21}
    east = {(x, y) for x in (36, 37) for y in range(88, 122) if not 106 <= y <= 109}
    _hedge(L, north | east)
    # stone gate piers framing the north gap
    L.place("cf_pier_capstone_sandstone_b", 14, 86)
    L.place("cf_pier_capstone_sandstone_b", 20, 86)
    for x in (14, 15, 20, 21):
        L.extra_solid.add((x, 88))
        L.extra_solid.add((x, 89))
    # south iron fence (rail bed beyond)
    synth.paint_fence(L, [(x, 122) for x in range(0, 38)], "iron")
    L.block(0, 122, 37, 123)
    for x in range(2, 37, 4):
        L.place("nt_s81_fern", x, 123)


def _monument_plaza(L):
    L.place("park_monument", 16, 96)                # x=16..19, y=96..106; plinth 105..106, shaft overhead
    L.marker("landmark", 17, 107, id="soldiers_sailors_column")
    # flower beds at the plaza diagonals, benches facing the column, lamps
    for (pid, x, y) in [("nt_s17_flowers_red", 13, 101), ("nt_s17_flowers_red", 21, 101),
                        ("nt_s17_flowers_pink", 13, 107), ("nt_s17_flowers_pink", 21, 107)]:
        L.place(pid, x, y)
    L.place("sy_lamp_iron", 14, 99)                 # base (14,101)
    L.place("sy_lamp_iron", 21, 99)
    L.place("sy_lamp_iron", 14, 106)                # base (14,108)
    L.place("sy_lamp_iron", 21, 106)


def _pond(L):
    # reeds, lily pads, ducks, a bench facing the pond
    L.place("nt_s78_lilypads_big", 8, 94, layer_override="Decals")
    L.place("park_duck_w", 6, 95)
    L.place("park_duck_m", 5, 96)
    L.place("park_duck_wl", 9, 98)
    L.place("park_duck_ml", 7, 93)
    L.place("nt_s78_reeds_tall", 3, 97)
    L.place("nt_s78_reeds_tall", 10, 91)
    L.place("sf_bench_wood_long", 5, 100)           # facing the pond from the south (y=100..101)
    for (pid, x, y) in [("nt_s26_tree_dark_round", 11, 91), ("nt_s26_maple_med", 2, 89),
                        ("nt_s69_bush_flowering", 12, 96), ("nt_s69_bush_round", 2, 99)]:
        if dress.can_place(L, pid, x, y, pad=0):
            L.place(pid, x, y)


def _bandstand(L):
    L.place("park_gazebo", 24, 92)                  # x=24..31, y=92..98
    L.marker("npc", 27, 99, role="band")
    # audience on blankets on the lawn, a side bench pair either side of the bandstand
    L.place("rr_picnic_blanket_blue_lunch", 23, 100)
    L.place("rr_picnic_blanket_pink_small", 31, 100)
    L.place("nt_s69_bush_flowering", 22, 96)
    L.place("nt_s69_bush_flowering", 32, 96)
    for (pid, x, y) in [("nt_s26_oak_large", 32, 90), ("nt_s26_tree_round_small", 21, 90),
                        ("nt_s69_bush_flowering_wide", 33, 99), ("nt_s17_flowers_crimson", 22, 95)]:
        if dress.can_place(L, pid, x, y, pad=0):
            L.place(pid, x, y)


def _playground(L):
    L.place("cf_swing_set_metal", 22, 112)
    L.place("cf_swing_set_metal", 25, 112)
    L.place("cf_seesaw_log", 23, 116)
    L.place("cf_seesaw_log", 26, 115)


def _pump_house(L):
    L.place("park_pump_house", 30, 113)             # x=30..35, y=113..119
    L.place("nt_s78_no_swimming_sign", 29, 117)     # pictogram only


def _hobo_camp(L):
    """S8: tiny clearing x=2..5, y=116..118 ringed by trees; entrance gap x=6..7, y=116..117."""
    # north wall of the thicket: trunks (2..7, 115)
    for (pid, x, y) in [("nt_s26_conifer_tall", 2, 112), ("nt_s26_tree_round_small", 4, 113),
                        ("nt_s26_conifer_tall", 6, 112)]:
        L.place(pid, x, y)
    # south + east walls (trunks / bushes); canopies overhead hide the camp
    L.place("nt_s27_oak_huge", 3, 114)              # big canopy over the clearing, trunk (4..5,119)
    L.place("nt_s26_conifer_short", 6, 116)         # trunk (6..7,118)
    L.extra_solid.update({(2, 119), (3, 119), (6, 119), (7, 119)})
    L.place("nt_s69_bush_round", 6, 119)
    L.place("nt_s69_bush_round_b", 2, 119)
    # camp props
    L.place("cf_campfire", 4, 116)                  # fire at (4,117)
    L.place("nt_s28_crates_pair", 2, 116)           # x=2..3, y=116..117
    L.place("park_bedroll", 3, 118)
    L.place("park_tin_cans", 5, 118)
    L.marker("secret", 5, 117, id="S8", desc="hobo camp: item by the bedroll")
    L.marker("npc", 5, 116, role="hobo")


def _trees_and_benches(L):
    # path-side lamps and benches
    for (x, ybase) in [(15, 93), (20, 93), (15, 115), (20, 115), (6, 103), (31, 108)]:
        L.place("sy_lamp_iron", x, ybase - 2)
    for (x, y) in [(11, 102), (3, 102), (30, 102)]:
        L.place("sf_bench_wood_long", x, y)          # north edge of the E-W path, facing it
    L.place("park_fountain", 15, 109)                # base (15,110) by the plaza
    big = [("nt_s27_oak_huge", 9, 108), ("nt_s26_oak_large", 2, 108), ("nt_s26_maple_med", 11, 113),
           ("nt_s26_tree_dark_round", 8, 117), ("nt_s26_oak_large_b", 12, 117), ("nt_s26_tree_wide", 30, 108),
           ("nt_s26_tree_medium", 21, 117), ("nt_s1_round_tree", 34, 90), ("nt_s26_tree_small", 13, 92)]
    for (pid, x, y) in big:
        if dress.can_place(L, pid, x, y, pad=0, reserved=_paths()):
            L.place(pid, x, y)
    # picnic spot on the lawn
    L.place("rr_picnic_blanket_pink_lunch", 4, 110)
    keep_clear = _paths() | dress.rect_cells(22, 99, 34, 102) | dress.rect_cells(3, 109, 8, 112)
    dress.scatter(L, ["nt_s1_flower_bush_small", "nt_s69_bush_ball_small", "nt_s81_fern"], (2, 90, 35, 121), 18,
                  seed=12, kinds={"grass"}, pad=1, reserved=keep_clear)


def _paths():
    r = set()
    for y in range(88, 122):
        for x in range(16, 20):
            r.add((x, y))
    for y in range(104, 108):
        for x in range(2, 38):
            r.add((x, y))
    for y in range(104, 110):
        for x in range(32, 38):
            r.add((x, y))
    r |= plaza_cells()
    return r


def build(L, lib):
    register(lib)
    _carlisle(L)
    _boundaries(L)
    _monument_plaza(L)
    _pond(L)
    _bandstand(L)
    _playground(L)
    _pump_house(L)
    _hobo_camp(L)
    _trees_and_benches(L)
