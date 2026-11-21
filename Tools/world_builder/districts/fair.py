"""York Fairgrounds (York Interstate Fair), Carlisle Ave - brief 1.3 / 3.4 / 2.6 (S9) / 5 (Fair).

Layout (tile coords, inclusive):
  border trees x=0..1 / y=0..1, green chain-link east fence x=36 (x=37 = weed strip), locked back gate y=63..64
  barns x=2..15 y=3..15, pens + barnyard y=15..19, Memorial Hall x=18..33 y=5..15 (doors x=25..26, y=15)
  covered grandstand x=6..29 y=20..28, front rail y=29
  oval track: ring centred (17.5, 42.5), outer 16x13 / inner 12x9, white rails both edges,
    rail gap x=16..19 on the south straight; infield judges' stand + flagpole x=16..19 y=40..44 (S9)
  east service lane x=34..35 (y=16..57) links midway <-> grandstand/barns/hall
  midway x=2..35 y=56..75, avenue x=16..19 gate -> track, big top x=22..33 y=58..68
  main gate pillars x=14..15 / x=20..21 (y=72..77), opening x=16..19, picket south fence y=77
"""
import math
import random

from PIL import Image, ImageDraw

import dress
import synth

REGION = (0, 0, 37, 77)
T = 16
OUT = (0x3D, 0x3D, 0x52, 255)
CX, CY = 17.5, 42.5
AVENUE = (16, 19)
RING_OUT, RING_IN = (16.4, 13.4), (11.6, 8.6)   # pixel-smooth dirt band radii (tiles)


# ============================================================================ helpers
def _c(rgb, a=255):
    return tuple(rgb[:3]) + (a,)


def _shade(rgb, f):
    return tuple(max(0, min(255, int(v * f))) for v in rgb[:3]) + (255,)


def ring_sets():
    outer = synth.ellipse_fill(CX, CY, 16, 13)
    inner = synth.ellipse_fill(CX, CY, 12, 9)
    ring = outer - inner
    return ring, inner, outer


def rail_sets():
    ring, inner, outer = ring_sets()
    o_rail, i_rail = set(), set()
    for (x, y) in ring:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in inner:
                i_rail.add((x, y))
            elif n not in ring:
                o_rail.add((x, y))
    gap = lambda c: AVENUE[0] <= c[0] <= AVENUE[1] and c[1] > CY
    return {c for c in o_rail if not gap(c)}, {c for c in i_rail - o_rail if not gap(c)}


# ============================================================================ synthesized art
RED = (0xB8, 0x34, 0x2C)
RED_D = (0x8E, 0x22, 0x20)
RED_L = (0xD0, 0x4E, 0x3E)
WHITE = (0xF2, 0xEE, 0xE4)
WHITE_D = (0xC4, 0xBC, 0xB0)
ROOF = (0x6A, 0x68, 0x78)
ROOF_D = (0x52, 0x50, 0x60)
ROOF_L = (0x84, 0x82, 0x92)
HAY = (0xE4, 0xC0, 0x5A)
HAY_D = (0xB8, 0x92, 0x3A)
HAY_L = (0xF4, 0xDC, 0x8A)


def barn_img(wt=7, ht=11, seed=0):
    """Red gambrel barn, gable end facing south, white trim, X-braced doors, hayloft, cupola."""
    W, H = wt * T, ht * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    wall_top = H - 4 * T - 6          # eave line of the front wall
    gh = 34                           # gable rise
    x0, x1 = 3, W - 4
    cx = W // 2
    knee = int((x1 - x0) * 0.17)
    # --- roof seen from above (back part of the barn)
    rt = 6
    d.rectangle([x0 - 1, rt, x1 + 1, wall_top - 4], fill=_c(ROOF), outline=OUT)
    # shingle courses
    for y in range(rt + 3, wall_top - 4, 4):
        d.line([x0, y, x1, y], fill=_c(ROOF_D))
        off = 0 if (y // 4) % 2 else 3
        for x in range(x0 + off, x1, 6):
            d.point((x, y - 1), fill=_c(ROOF_D))
    # gambrel break lines + ridge, lit left / shaded right
    d.rectangle([x0, rt + 1, x0 + knee, wall_top - 5], fill=_c(ROOF_D))
    d.rectangle([x1 - knee, rt + 1, x1, wall_top - 5], fill=_shade(ROOF_D, 0.85))
    for y in range(rt + 3, wall_top - 4, 4):
        d.line([x0, y, x0 + knee, y], fill=_shade(ROOF_D, 0.8))
        d.line([x1 - knee, y, x1, y], fill=_shade(ROOF_D, 0.7))
    d.rectangle([x0 + knee + 1, rt + 1, cx - 1, rt + 2], fill=_c(ROOF_L))
    d.line([x0 + knee, rt, x0 + knee, wall_top - 4], fill=OUT)
    d.line([x1 - knee, rt, x1 - knee, wall_top - 4], fill=OUT)
    d.rectangle([cx - 1, rt, cx + 1, wall_top - 4], fill=_c(ROOF_L))
    d.line([cx + 2, rt + 1, cx + 2, wall_top - 4], fill=_c(ROOF_D))
    # --- cupola on the ridge
    cy0 = rt + 10
    d.rectangle([cx - 6, cy0, cx + 6, cy0 + 12], fill=_c(WHITE), outline=OUT)
    d.rectangle([cx - 3, cy0 + 4, cx + 3, cy0 + 9], fill=_c((0x4A, 0x40, 0x48)))
    for k in (cx - 2, cx, cx + 2):
        d.line([k, cy0 + 4, k, cy0 + 9], fill=_c(WHITE_D))
    d.polygon([(cx - 8, cy0 + 1), (cx, cy0 - 7), (cx + 8, cy0 + 1)], fill=_c(ROOF_D), outline=OUT)
    d.line([cx, cy0 - 7, cx, cy0 - 13], fill=OUT)
    d.line([cx - 3, cy0 - 11, cx + 4, cy0 - 11], fill=OUT)          # weather vane arrow
    d.polygon([(cx + 4, cy0 - 13), (cx + 7, cy0 - 11), (cx + 4, cy0 - 9)], fill=OUT)
    # --- gambrel gable (front face, red boards)
    gy = wall_top
    pts = [(x0, gy), (x0 + 3, gy - int(gh * 0.62)), (x0 + knee + 4, gy - gh + 4), (cx, gy - gh),
           (x1 - knee - 4, gy - gh + 4), (x1 - 3, gy - int(gh * 0.62)), (x1, gy)]
    d.polygon(pts, fill=_c(RED))
    # wall
    d.rectangle([x0, gy, x1, H - 3], fill=_c(RED))
    # board-and-batten
    mask = Image.new("L", (W, H))
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    ImageDraw.Draw(mask).rectangle([x0, gy, x1, H - 3], fill=255)
    lines = Image.new("RGBA", (W, H))
    ld = ImageDraw.Draw(lines)
    for x in range(x0 + 3, x1, 4):
        ld.line([x, 0, x, H], fill=_c(RED_D))
    for x in range(x0 + 1, x0 + 3):
        ld.line([x, 0, x, H], fill=_c(RED_L))
    img.paste(lines, (0, 0), Image.composite(lines, Image.new("RGBA", (W, H)), mask).getchannel("A"))
    d = ImageDraw.Draw(img)
    # right side shade
    shade = Image.new("RGBA", (W, H), (40, 0, 30, 46))
    sm = Image.new("L", (W, H))
    ImageDraw.Draw(sm).rectangle([x1 - 6, 0, x1, H], fill=255)
    sm = Image.composite(sm, Image.new("L", (W, H)), mask)
    img.alpha_composite(Image.composite(shade, Image.new("RGBA", (W, H)), sm))
    d = ImageDraw.Draw(img)
    # white trim on the gable edge (fascia) + outline
    d.line(pts, fill=_c(WHITE), width=3)
    d.line([(p[0], p[1] - 2) for p in pts], fill=OUT)
    # corner boards
    d.rectangle([x0, gy, x0 + 2, H - 3], fill=_c(WHITE))
    d.rectangle([x1 - 2, gy, x1, H - 3], fill=_c(WHITE_D))
    d.line([x0, gy - 1, x1, gy - 1], fill=_c(WHITE))
    d.line([x0, gy, x1, gy], fill=_c(WHITE_D))
    # hayloft door with hay
    hw = 16
    hy = gy - gh + 12
    d.rectangle([cx - hw // 2 - 2, hy - 2, cx + hw // 2 + 1, hy + 15], fill=_c(WHITE), outline=OUT)
    d.rectangle([cx - hw // 2 + 1, hy + 1, cx + hw // 2 - 2, hy + 12], fill=_c((0x3A, 0x2C, 0x30)))
    d.rectangle([cx - hw // 2 + 1, hy + 8, cx + hw // 2 - 2, hy + 12], fill=_c(HAY))
    for k in range(cx - hw // 2 + 2, cx + hw // 2 - 2, 3):
        d.point((k, hy + 7), fill=_c(HAY_L))
    d.line([cx - 4, hy - 6, cx + 4, hy - 6], fill=OUT)                # hay hood beam
    d.polygon([(cx - 6, hy - 3), (cx, hy - 8), (cx + 6, hy - 3)], fill=_c(WHITE), outline=OUT)
    # big X-braced double door
    dw = min(44, int((x1 - x0) * 0.46)) // 2 * 2
    dh = 42
    dx0, dx1 = cx - dw // 2, cx + dw // 2 - 1
    dy0, dy1 = H - 3 - dh, H - 3
    d.rectangle([dx0 - 2, dy0 - 2, dx1 + 2, dy1], fill=_c(WHITE), outline=OUT)
    for (a, b) in ((dx0, cx - 1), (cx, dx1)):
        d.rectangle([a, dy0, b, dy1 - 1], fill=_c(RED))
        for x in range(a + 2, b, 4):
            d.line([x, dy0, x, dy1 - 1], fill=_c(RED_D))
        d.rectangle([a, dy0, b, dy1 - 1], outline=_c(WHITE))
        d.line([a + 1, dy0 + 1, b - 1, dy1 - 2], fill=_c(WHITE), width=2)
        d.line([b - 1, dy0 + 1, a + 1, dy1 - 2], fill=_c(WHITE), width=2)
        d.line([a, dy0 + dh // 2, b, dy0 + dh // 2], fill=_c(WHITE), width=2)
    d.line([cx - 1, dy0, cx - 1, dy1], fill=OUT)
    d.line([dx0 - 3, dy0 - 4, dx1 + 3, dy0 - 4], fill=OUT, width=2)    # sliding-door track
    # prize ribbon (rosette) on the door
    rx, ry = cx + 6, dy0 + 8
    d.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=_c((0x3E, 0x6E, 0xC4)), outline=OUT)
    d.point((rx, ry), fill=_c((0xF0, 0xC0, 0x3A)))
    d.line([rx - 1, ry + 3, rx - 2, ry + 8], fill=_c((0x3E, 0x6E, 0xC4)), width=2)
    d.line([rx + 1, ry + 3, rx + 2, ry + 8], fill=_c((0x3E, 0x6E, 0xC4)), width=2)
    # side windows
    for wx in (x0 + 8, x1 - 17):
        if wx + 9 < dx0 - 3 or wx > dx1 + 3:
            wy = dy0 + 4
            d.rectangle([wx, wy, wx + 9, wy + 10], fill=_c(WHITE), outline=OUT)
            d.rectangle([wx + 2, wy + 2, wx + 7, wy + 8], fill=_c((0x7C, 0x9C, 0xB4)))
            d.line([wx + 4, wy + 2, wx + 4, wy + 8], fill=_c(WHITE))
            d.line([wx + 2, wy + 5, wx + 7, wy + 5], fill=_c(WHITE))
            d.line([wx + 2, wy + 2, wx + 3, wy + 3], fill=_c((0xD8, 0xEC, 0xF4)))
    # stone foundation
    d.rectangle([x0, H - 5, x1, H - 2], fill=_c((0x9C, 0x96, 0x90)), outline=OUT)
    d.rectangle([dx0, H - 5, dx1, H - 2], fill=_c((0x7A, 0x6A, 0x5A)))
    # outline of the whole wall
    d.line([x0 - 1, gy - int(gh * 0.62), x0 - 1, H - 2], fill=OUT)
    d.line([x1 + 1, gy - int(gh * 0.62), x1 + 1, H - 2], fill=OUT)
    d.line([x0, H - 1, x1, H - 1], fill=OUT)
    return img


def hay_bale(kind=0):
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 11, 15, 15], fill=(0, 0, 0, 50))
    if kind == 0:   # square bale
        d.rectangle([1, 4, 14, 13], fill=_c(HAY), outline=OUT)
        d.rectangle([2, 5, 13, 7], fill=_c(HAY_L))
        d.line([2, 8, 13, 8], fill=_c(HAY_D))
        for x in (5, 10):
            d.line([x, 5, x, 12], fill=_c((0x8A, 0x5A, 0x34)))
        for x in range(3, 13, 3):
            d.point((x, 11), fill=_c(HAY_D))
    else:           # round bale, side view
        d.ellipse([1, 3, 14, 14], fill=_c(HAY), outline=OUT)
        d.ellipse([4, 6, 11, 12], outline=_c(HAY_D))
        d.ellipse([6, 8, 9, 10], outline=_c(HAY_D))
        d.arc([2, 4, 13, 13], 200, 300, fill=_c(HAY_L))
    return img


def hay_stack():
    """2x2: three bales stacked."""
    img = Image.new("RGBA", (2 * T, 2 * T))
    b = hay_bale(0)
    img.alpha_composite(b, (1, 14))
    img.alpha_composite(b, (15, 14))
    img.alpha_composite(b, (8, 5))
    return img


def trough():
    img = Image.new("RGBA", (2 * T, T))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 11, 29, 15], fill=(0, 0, 0, 50))
    d.rectangle([2, 4, 29, 12], fill=_c((0x8C, 0x92, 0x9A)), outline=OUT)
    d.rectangle([4, 5, 27, 8], fill=_c((0x5C, 0x8C, 0xB0)))
    d.line([5, 6, 12, 6], fill=_c((0x9C, 0xC8, 0xE0)))
    d.line([3, 10, 28, 10], fill=_c((0x6A, 0x70, 0x78)))
    return img


def chicken(flip=False, col=(0xF4, 0xF0, 0xE8)):
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 12, 12, 15], fill=(0, 0, 0, 50))
    d.ellipse([4, 6, 12, 13], fill=_c(col), outline=OUT)
    d.ellipse([9, 3, 13, 8], fill=_c(col), outline=OUT)
    d.point((11, 5), fill=OUT)
    d.line([12, 2, 11, 3], fill=_c((0xD8, 0x3A, 0x36)), width=2)
    d.point((14, 6), fill=_c((0xF0, 0xA0, 0x30)))
    d.line([3, 7, 5, 9], fill=_shade(col, 0.75))
    d.line([7, 13, 7, 14], fill=_c((0xE0, 0x9A, 0x30)))
    d.line([9, 13, 9, 14], fill=_c((0xE0, 0x9A, 0x30)))
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img


def cow(flip=False):
    """2x2 Holstein cow, side view."""
    img = Image.new("RGBA", (2 * T, 2 * T))
    d = ImageDraw.Draw(img)
    wh, bk = (0xF2, 0xEE, 0xE6), (0x34, 0x30, 0x36)
    d.ellipse([3, 26, 29, 31], fill=(0, 0, 0, 55))
    for lx in (7, 10, 20, 23):
        d.rectangle([lx, 21, lx + 2, 29], fill=_c(wh if lx % 2 else (0xDC, 0xD6, 0xCC)), outline=OUT)
    d.rounded_rectangle([4, 10, 26, 23], 4, fill=_c(wh), outline=OUT)
    d.ellipse([8, 11, 15, 17], fill=_c(bk))
    d.ellipse([17, 15, 23, 21], fill=_c(bk))
    d.ellipse([12, 18, 16, 22], fill=_c(bk))
    d.rounded_rectangle([22, 7, 31, 16], 3, fill=_c(wh), outline=OUT)      # head
    d.rectangle([26, 12, 31, 16], fill=_c((0xE8, 0xA8, 0xA0)), outline=OUT)  # muzzle
    d.point((25, 10), fill=OUT)
    d.line([23, 6, 21, 4], fill=OUT)
    d.line([29, 6, 30, 4], fill=OUT)
    d.ellipse([10, 21, 14, 24], fill=_c((0xF0, 0xB0, 0xB0)), outline=OUT)   # udder
    d.line([4, 12, 1, 20], fill=OUT)                                      # tail
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img


def flagpole(h=5):
    """2 x h: steel flagpole, gold ball, US-style flag (stripes + canton, no text)."""
    img = Image.new("RGBA", (2 * T, h * T))
    d = ImageDraw.Draw(img)
    H = h * T
    px = 4
    d.ellipse([0, H - 6, 10, H - 1], fill=(0, 0, 0, 50))
    d.rectangle([px - 1, 4, px + 1, H - 4], fill=_c((0xC8, 0xCC, 0xD4)), outline=OUT)
    d.line([px, 5, px, H - 5], fill=_c((0xEE, 0xF0, 0xF4)))
    d.ellipse([px - 2, 0, px + 2, 4], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)
    d.rectangle([px - 4, H - 6, px + 4, H - 2], fill=_c((0xB0, 0xAC, 0xA4)), outline=OUT)
    fx, fy, fw, fh = px + 2, 6, 22, 14
    for i in range(7):
        y = fy + i * 2
        wave = [(fx + k, y + int(1.2 * math.sin(k / 3.5))) for k in range(fw)]
        col = (0xC8, 0x30, 0x2C) if i % 2 == 0 else (0xF2, 0xEE, 0xE4)
        for (a, b) in wave:
            d.line([a, b, a, b + 1], fill=_c(col))
    for k in range(9):
        for j in range(8):
            d.point((fx + k, fy + j + int(1.2 * math.sin(k / 3.5))), fill=_c((0x2E, 0x4A, 0x8C)))
    for (a, b) in ((fx + 2, fy + 2), (fx + 5, fy + 2), (fx + 3, fy + 5), (fx + 6, fy + 5)):
        d.point((a, b + int(1.2 * math.sin((a - fx) / 3.5))), fill=_c(WHITE))
    return img


def judges_stand():
    """4x5 raised white judges' stand on posts with a striped roof and pennant."""
    W, H = 4 * T, 5 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.ellipse([4, H - 9, W - 5, H - 1], fill=(0, 0, 0, 55))
    # posts + cross bracing
    for x in (8, 26, 37, 54):
        d.rectangle([x, 46, x + 2, H - 3], fill=_c(WHITE), outline=OUT)
    d.line([11, 52, 26, 70], fill=_c(WHITE_D), width=2)
    d.line([37, 70, 54, 52], fill=_c(WHITE_D), width=2)
    # stair at the front left
    for i in range(5):
        y = H - 4 - i * 5
        d.rectangle([12 + i * 2, y - 2, 24, y], fill=_c((0xB0, 0x80, 0x52)), outline=OUT)
    # platform
    d.rectangle([4, 42, W - 5, 48], fill=_c((0xB0, 0x80, 0x52)), outline=OUT)
    d.line([5, 44, W - 6, 44], fill=_c((0xCC, 0x9C, 0x6A)))
    # booth
    d.rectangle([8, 20, W - 9, 43], fill=_c(WHITE), outline=OUT)
    d.rectangle([11, 24, W - 12, 34], fill=_c((0x3A, 0x34, 0x40)))
    for x in range(11, W - 12, 8):
        d.line([x, 24, x, 34], fill=_c(WHITE_D))
    d.line([12, 25, 20, 25], fill=_c((0x6A, 0x84, 0xA0)))
    d.rectangle([8, 35, W - 9, 37], fill=_c(WHITE_D))
    # bunting on the rail
    for i, x in enumerate(range(9, W - 9, 6)):
        d.polygon([(x, 38), (x + 5, 38), (x + 2, 42)], fill=synth.PENNANT[i % 4])
    # striped hip roof
    d.polygon([(2, 21), (12, 6), (W - 13, 6), (W - 3, 21)], fill=_c(WHITE), outline=OUT)
    for i, x in enumerate(range(2, W - 2, 6)):
        if i % 2 == 0:
            tx = 12 + (x - 2) * (W - 25) / (W - 4)
            d.polygon([(x, 21), (tx, 6), (tx + 4, 6), (x + 6, 21)], fill=_c((0xD8, 0x3A, 0x36)))
    d.polygon([(2, 21), (12, 6), (W - 13, 6), (W - 3, 21)], outline=OUT)
    d.line([2, 21, W - 3, 21], fill=OUT, width=2)
    # pennant
    d.line([W // 2, 6, W // 2, 0], fill=OUT)
    d.polygon([(W // 2 + 1, 0), (W // 2 + 8, 2), (W // 2 + 1, 4)], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)
    return img


def tan_brick(W, H, seed=0):
    base, brick, dark = (0xBD, 0xA7, 0x66), (0xC8, 0xC2, 0x7E), (0xB4, 0x8F, 0x54)
    img = Image.new("RGBA", (W, H), _c(base))
    d = ImageDraw.Draw(img)
    for y in range(1, H, 4):
        off = 0 if (y // 4) % 2 else 4
        for x in range(-off, W, 8):
            d.rectangle([x + 1, y, x + 6, y + 1], fill=_c(brick))
            d.point((x + 6, y + 2), fill=_c(dark))
    return img


def memorial_hall(lib, wt=16, ht=11, door_rx=7):
    """Long, low 1950s exhibition hall: flat roof, tan brick, strip of high windows, wide doors."""
    import buildings
    W, H = wt * T, ht * T
    fr = 4                                          # facade rows
    img = Image.new("RGBA", (W, H))
    roof = buildings.flat_roof(wt, ht - fr + 1, "gravel", seed=7)
    img.alpha_composite(roof, (0, 0))
    d = ImageDraw.Draw(img)
    # roof extras: a long raised clerestory monitor down the middle with sawtooth glazing,
    # ventilators on either side, roof drains
    mx0, mx1, my0, my1 = 3 * T, W - 3 * T, 30, 62
    d.rectangle([mx0 + 2, my1 + 1, mx1 + 2, my1 + 5], fill=(0, 0, 0, 55))          # cast shadow
    d.rectangle([mx0, my0, mx1, my1], fill=_c((0xC8, 0xC0, 0xA8)), outline=OUT)
    d.rectangle([mx0 + 3, my0 + 3, mx1 - 3, my1 - 9], fill=_c((0x8A, 0x86, 0x84)))
    for x in range(mx0 + 3, mx1 - 3, 2):
        if (x // 2) % 3 == 0:
            d.line([x, my0 + 3, x, my1 - 9], fill=_c((0x7A, 0x76, 0x76)))
    for x in range(mx0 + 4, mx1 - 8, 12):                                         # glazing strip on the face
        d.rectangle([x, my1 - 7, x + 9, my1 - 2], fill=_c((0x9E, 0xBE, 0xD2)), outline=_c((0x46, 0x46, 0x5E)))
        d.line([x + 1, my1 - 6, x + 8, my1 - 6], fill=_c((0xD8, 0xEC, 0xF4)))
    for vx in list(range(14, mx0 - 10, 20)) + list(range(mx1 + 10, W - 16, 20)):
        for vy in (34, 70):
            d.ellipse([vx, vy, vx + 9, vy + 9], fill=_c((0xA8, 0xAC, 0xB4)), outline=OUT)
            d.ellipse([vx + 2, vy + 2, vx + 7, vy + 6], fill=_c((0x6A, 0x6E, 0x78)))
            d.line([vx + 4, vy + 2, vx + 4, vy + 6], fill=_c((0xC8, 0xCC, 0xD4)))
    fy = (ht - fr) * T
    wall = tan_brick(W, fr * T)
    img.alpha_composite(wall, (0, fy))
    d = ImageDraw.Draw(img)
    # cornice / cap band (cream) with dark under-shadow
    d.rectangle([0, fy, W - 1, fy + 4], fill=_c((0xEE, 0xE1, 0xB7)))
    d.line([0, fy + 5, W - 1, fy + 5], fill=_c((0xB9, 0x9E, 0x86)))
    d.line([0, fy + 6, W - 1, fy + 6], fill=_c((0x9A, 0x80, 0x5E)))
    # clerestory: continuous strip of high windows
    wy0, wy1 = fy + 10, fy + 21
    d.rectangle([3, wy0 - 1, W - 4, wy1 + 1], fill=_c((0xEE, 0xE1, 0xB7)), outline=OUT)
    for x in range(5, W - 6, 10):
        d.rectangle([x, wy0 + 1, x + 7, wy1 - 1], fill=_c((0x9E, 0xBE, 0xD2)), outline=_c((0x46, 0x46, 0x5E)))
        d.line([x + 1, wy0 + 2, x + 6, wy0 + 2], fill=_c((0xD8, 0xEC, 0xF4)))
        d.line([x + 1, wy1 - 3, x + 6, wy1 - 3], fill=_c((0x7E, 0x9E, 0xB4)))
    # sill
    d.line([2, wy1 + 2, W - 3, wy1 + 2], fill=_c((0xB4, 0x8F, 0x54)))
    # pilasters every 4 tiles
    for px in range(0, W, 4 * T):
        for xx in (px, px + 1, px + 2):
            if 0 <= xx < W:
                d.line([xx, fy + 7, xx, fy + fr * T - 4], fill=_c((0xD8, 0xC8, 0x92)))
        d.line([px + 3, fy + 7, px + 3, fy + fr * T - 4], fill=_c((0x9A, 0x80, 0x5E)))
    # base course
    d.rectangle([0, H - 5, W - 1, H - 1], fill=_c((0xA8, 0xA4, 0xA6)))
    d.line([0, H - 5, W - 1, H - 5], fill=_c((0xC8, 0xC6, 0xCC)))
    # double glass doors (2 tiles wide) with canopy, aluminium frames
    dx0 = door_rx * T
    dy0 = fy + 2 * T - 2
    d.rectangle([dx0 - 6, dy0 - 7, dx0 + 2 * T + 5, dy0 - 3], fill=_c((0xEE, 0xE1, 0xB7)), outline=OUT)   # canopy
    d.rectangle([dx0 - 6, dy0 - 2, dx0 + 2 * T + 5, dy0 - 1], fill=(0, 0, 0, 60))
    d.rectangle([dx0, dy0, dx0 + 2 * T - 1, H - 3], fill=_c((0xB4, 0xB8, 0xC4)), outline=OUT)
    for k in range(4):
        x = dx0 + 2 + k * 7
        d.rectangle([x, dy0 + 2, x + 5, H - 6], fill=_c((0x5C, 0x6C, 0x84)))
        d.line([x + 1, dy0 + 3, x + 1, dy0 + 10], fill=_c((0xA8, 0xC0, 0xD8)))
        d.line([x, dy0 + 14, x + 5, dy0 + 14], fill=_c((0xB4, 0xB8, 0xC4)))
    d.line([dx0 + T - 1, dy0, dx0 + T - 1, H - 3], fill=OUT)
    # wide display windows flanking doors at eye height
    for wx in list(range(T // 2, dx0 - 2 * T, 3 * T)) + list(range(dx0 + 3 * T, W - 2 * T, 3 * T)):
        wy = fy + 2 * T + 2
        d.rectangle([wx, wy, wx + 2 * T - 2, wy + 13], fill=_c((0xEE, 0xE1, 0xB7)), outline=OUT)
        d.rectangle([wx + 2, wy + 2, wx + 2 * T - 4, wy + 11], fill=_c((0x7E, 0x9E, 0xB4)))
        d.line([wx + T - 1, wy + 2, wx + T - 1, wy + 11], fill=_c((0xEE, 0xE1, 0xB7)))
        d.line([wx + 3, wy + 3, wx + 8, wy + 3], fill=_c((0xD8, 0xEC, 0xF4)))
    # bunting under the cornice (fair dressing)
    for i, x in enumerate(range(4, W - 4, 6)):
        y = fy + 7 + int(2 * math.sin(math.pi * ((x - 4) % 48) / 48))
        d.polygon([(x, y), (x + 4, y), (x + 2, y + 3)], fill=synth.PENNANT[i % 4])
    return lib.add_img("fair_memorial_hall", img, "building", "all", 0, [[door_rx, ht - 1], [door_rx + 1, ht - 1]])


def balloon_seller():
    """1x3 balloon bunch on a cart pole (balloons overhead)."""
    img = Image.new("RGBA", (T, 3 * T))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 43, 14, 47], fill=(0, 0, 0, 55))
    d.rectangle([3, 36, 12, 44], fill=_c((0x3E, 0x6E, 0xC4)), outline=OUT)
    d.line([4, 38, 11, 38], fill=_c(WHITE))
    cols = [(0xD8, 0x3A, 0x36), (0xF0, 0xC0, 0x3A), (0x5A, 0xB0, 0x5A), (0xE8, 0x7C, 0xC0), (0x4E, 0x8E, 0xE0)]
    pos = [(3, 3), (9, 2), (6, 9), (1, 12), (11, 11)]
    for (bx, by), c in zip(pos, cols):
        d.line([bx + 2, by + 5, 8, 36], fill=_c((0x6A, 0x60, 0x5A)))
    for (bx, by), c in zip(pos, cols):
        d.ellipse([bx, by, bx + 5, by + 6], fill=_c(c), outline=OUT)
        d.point((bx + 1, by + 1), fill=_c(WHITE))
    return img


def litter_tile(seed):
    rng = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    kind = rng.randint(0, 3)
    for _ in range(6):   # sawdust specks
        x, y = rng.randint(1, 14), rng.randint(1, 14)
        d.point((x, y), fill=_c((0xE6, 0xCE, 0x96), 200))
    if kind == 0:   # popcorn box tipped over
        x, y = rng.randint(3, 9), rng.randint(4, 10)
        d.polygon([(x, y), (x + 5, y - 1), (x + 6, y + 3), (x + 1, y + 4)], fill=_c(WHITE), outline=_c((0xD8, 0x3A, 0x36)))
        for k in range(3):
            d.point((x + 6 + k, y + 2 + (k % 2)), fill=_c((0xFA, 0xF0, 0xC8)))
    elif kind == 1:  # paper cup + straw
        x, y = rng.randint(3, 10), rng.randint(4, 11)
        d.rectangle([x, y, x + 4, y + 2], fill=_c((0xD8, 0x3A, 0x36)))
        d.line([x, y + 1, x + 4, y + 1], fill=_c(WHITE))
    elif kind == 2:  # ticket stubs
        for _ in range(2):
            x, y = rng.randint(2, 12), rng.randint(2, 12)
            d.rectangle([x, y, x + 2, y + 1], fill=_c((0xF0, 0xC0, 0x3A)))
    return img


def sawdust_tile(seed):
    rng = random.Random(seed)
    img = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(img)
    for _ in range(18):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        d.point((x, y), fill=_c(rng.choice([(0xE8, 0xD2, 0x9C), (0xD4, 0xB4, 0x78), (0xF0, 0xE0, 0xB4)]), 210))
    return img


def ticket_booth():
    """2x3 striped ticket booth with a little peaked roof."""
    W, H = 2 * T, 3 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.ellipse([1, H - 6, W - 2, H - 1], fill=(0, 0, 0, 55))
    d.rectangle([3, 18, W - 4, H - 3], fill=_c(WHITE), outline=OUT)
    for x in range(5, W - 4, 6):
        d.rectangle([x, 19, x + 2, H - 4], fill=_c((0xD8, 0x3A, 0x36)))
    d.rectangle([6, 22, W - 7, 31], fill=_c((0x3A, 0x34, 0x40)), outline=OUT)
    d.line([7, 23, 14, 23], fill=_c((0x7C, 0x9C, 0xB4)))
    d.rectangle([4, 32, W - 5, 34], fill=_c((0xB0, 0x80, 0x52)), outline=OUT)   # counter
    d.polygon([(0, 19), (W // 2, 5), (W - 1, 19)], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)
    d.line([W // 2, 6, W // 2, 18], fill=_c((0xD0, 0x9A, 0x2A)))
    d.ellipse([W // 2 - 2, 1, W // 2 + 2, 5], fill=_c((0xD8, 0x3A, 0x36)), outline=OUT)
    return img


def race_car():
    """3x2 1950s sprint car (side view), red with white number roundel (no digits)."""
    W, H = 3 * T, 2 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.ellipse([3, H - 6, W - 4, H - 1], fill=(0, 0, 0, 60))
    body = (0xC8, 0x30, 0x2C)
    d.polygon([(4, 20), (8, 13), (30, 12), (40, 15), (45, 19), (44, 23), (5, 24)], fill=_c(body), outline=OUT)
    d.line([9, 15, 38, 15], fill=_c((0xE8, 0x60, 0x50)))
    d.rectangle([20, 8, 27, 13], fill=_c((0x3A, 0x34, 0x40)), outline=OUT)   # cockpit + driver helmet
    d.ellipse([21, 4, 27, 10], fill=_c(WHITE), outline=OUT)
    d.ellipse([12, 15, 19, 21], fill=_c(WHITE), outline=OUT)
    d.line([8, 11, 6, 7], fill=OUT, width=2)                             # roll bar
    for wx in (7, 35):
        d.ellipse([wx - 1, 17, wx + 10, 28], fill=_c((0x2A, 0x26, 0x2C)), outline=OUT)
        d.ellipse([wx + 3, 21, wx + 6, 24], fill=_c((0xC8, 0xCC, 0xD4)))
    return img


def grandstand_img(lib, wt=24, ht=9):
    """Covered grandstand facing south: green tin roof with pennants, three shaded plank tiers,
    concrete aisle stairs, steel posts, white front fascia."""
    W, H = wt * T, ht * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    seat = lib["cf_plank_tier_seating"].img
    sw = seat.size[0]
    rb = 40
    d.rectangle([0, rb - 8, W - 1, H - 6], fill=_c((0x3E, 0x34, 0x3C)), outline=OUT)
    for i, ty in enumerate((rb - 6, rb + 24, rb + 54)):
        layer = Image.new("RGBA", (W, seat.size[1]))
        for b in range(0, W, sw):
            layer.alpha_composite(seat, (b, 0))
        f = (0.62, 0.8, 1.0)[i]
        if f < 1:
            dark = Image.new("RGBA", layer.size, (0x2A, 0x20, 0x34, int(255 * (1 - f))))
            layer = Image.composite(Image.alpha_composite(layer, dark), layer, layer.getchannel("A"))
        img.alpha_composite(layer, (0, ty))
    d = ImageDraw.Draw(img)
    # aisle stairs
    for ax in range(2 * sw - 7, W - 20, 2 * sw):
        d.rectangle([ax, rb - 2, ax + 13, H - 6], fill=_c((0xA8, 0xA6, 0xAC)), outline=OUT)
        for y in range(rb + 2, H - 6, 5):
            d.line([ax + 1, y, ax + 12, y], fill=_c((0x7C, 0x7A, 0x84)))
            d.line([ax + 1, y + 1, ax + 12, y + 1], fill=_c((0xC8, 0xC6, 0xCC)))
    # steel posts
    for px in list(range(5, W - 4, 3 * sw // 2)) + [W - 8]:
        d.rectangle([px, rb - 4, px + 3, H - 6], fill=_c((0xE8, 0xE2, 0xD0)), outline=OUT)
    # roof
    roof_c, roof_l = (0x4E, 0x7E, 0x5E, 255), (0x6E, 0x9E, 0x7A, 255)
    d.rectangle([0, 5, W - 1, rb - 4], fill=roof_c, outline=OUT)
    for x in range(4, W - 2, 6):
        d.line([x, 6, x, rb - 9], fill=roof_l)
    d.rectangle([0, rb - 8, W - 1, rb - 3], fill=_c((0xE8, 0xE2, 0xD0)), outline=OUT)
    for i, x in enumerate(range(3, W - 3, 8)):
        d.polygon([(x, rb - 2), (x + 6, rb - 2), (x + 3, rb + 2)], fill=synth.PENNANT[i % 4])
    for b in range(wt // 2):
        px = int((b + 0.5) * W / (wt // 2))
        d.line([px, 0, px, 7], fill=OUT)
        d.polygon([(px + 1, 0), (px + 7, 2), (px + 1, 4)], fill=synth.PENNANT[b % 4])
    # front fascia
    d.rectangle([0, H - 7, W - 1, H - 2], fill=_c((0xF2, 0xEE, 0xE4)), outline=OUT)
    for x in range(0, W, 8):
        d.line([x, H - 6, x, H - 3], fill=_c((0xC4, 0xBC, 0xB0)))
    d.line([0, H - 1, W - 1, H - 1], fill=(0, 0, 0, 70))
    return img


def striped_pole(h=4):
    img = Image.new("RGBA", (T, h * T))
    d = ImageDraw.Draw(img)
    H = h * T
    d.ellipse([3, H - 5, 12, H - 1], fill=(0, 0, 0, 55))
    d.rectangle([6, 5, 9, H - 3], fill=_c(WHITE), outline=OUT)
    for y in range(8, H - 4, 6):
        d.polygon([(7, y), (8, y), (8, y + 2), (7, y + 3)], fill=_c((0xD8, 0x3A, 0x36)))
        d.rectangle([7, y, 8, y + 2], fill=_c((0xD8, 0x3A, 0x36)))
    d.ellipse([4, 0, 11, 6], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)
    d.point((6, 2), fill=_c(WHITE))
    return img


def _string(L, x0, y, x1, sag, offset_px, inset, draw_item, step):
    """Hang a sagging string from tile x0 to x1 (row y, 2 rows tall, overhead). `inset` trims the
    ends in px so strings start/end on pole centres (8) or tile edges (0)."""
    W = (x1 - x0 + 1) * T
    cv = Image.new("RGBA", (W, 2 * T))
    d = ImageDraw.Draw(cv)
    a, b = inset, W - 1 - inset
    span = max(1, b - a)
    pts = [(px, offset_px + int(sag * 4 * ((px - a) / span) * (1 - (px - a) / span))) for px in range(a, b + 1)]
    d.line(pts, fill=(0x3A, 0x34, 0x30, 255))
    for i, px in enumerate(range(a + 3, b - 2, step)):
        draw_item(d, i, px, pts[px - a][1])
    for k in range(x1 - x0 + 1):
        for r in range(2):
            tile = cv.crop((k * T, r * T, k * T + T, r * T + T))
            if tile.getchannel("A").getbbox():
                L.put("Overhead", x0 + k, y + r, tile, False)


BULB_COLS = [(0xFF, 0xF1, 0xA8), (0xFF, 0xB8, 0x5A), (0xFF, 0x7A, 0x6A), (0xA8, 0xF0, 0x9A), (0xA0, 0xD0, 0xFF)]


def bulbs(L, x0, y, x1, sag=6, offset_px=3, inset=0):
    """String of round glowing bulbs (warm white / amber / red / green / blue), overhead."""
    def item(d, i, px, py):
        c = BULB_COLS[i % len(BULB_COLS)]
        py += 2
        d.ellipse([px - 3, py - 1, px + 3, py + 5], fill=c + (60,))
        d.ellipse([px - 1, py, px + 1, py + 3], fill=c + (255,))
        d.point((px, py - 1), fill=(0x3A, 0x34, 0x30, 255))
    _string(L, x0, y, x1, sag, offset_px, inset, item, 7)


def pennants(L, x0, y, x1, sag=6, offset_px=2, inset=0):
    def item(d, i, px, py):
        d.polygon([(px - 2, py + 1), (px + 2, py + 1), (px, py + 6)], fill=synth.PENNANT[i % 4])
    _string(L, x0, y, x1, sag, offset_px, inset, item, 6)


def high_striker():
    """1x5 'test your strength' high striker: striped scale post, bell on top, base pad + mallet."""
    img = Image.new("RGBA", (T, 5 * T))
    d = ImageDraw.Draw(img)
    H = 5 * T
    d.ellipse([1, H - 6, 15, H - 1], fill=(0, 0, 0, 55))
    d.rectangle([5, 8, 10, H - 8], fill=_c(WHITE), outline=OUT)
    cols = [(0xD8, 0x3A, 0x36), (0xF0, 0x8A, 0x30), (0xF0, 0xC0, 0x3A), (0x5A, 0xB0, 0x5A), (0x3E, 0x6E, 0xC4)]
    for i, y in enumerate(range(12, H - 10, 11)):
        d.rectangle([6, y, 9, y + 6], fill=_c(cols[i % 5]))
    d.line([7, 10, 7, H - 9], fill=_c((0x3A, 0x34, 0x40)))
    d.ellipse([3, 0, 12, 8], fill=_c((0xF0, 0xC0, 0x3A)), outline=OUT)          # bell
    d.point((5, 2), fill=_c(WHITE))
    d.rectangle([2, H - 9, 13, H - 4], fill=_c((0xB0, 0x80, 0x52)), outline=OUT)  # base
    d.rectangle([5, H - 8, 10, H - 6], fill=_c((0xD8, 0x3A, 0x36)))
    d.line([12, H - 4, 15, H - 14], fill=_c((0x8A, 0x5A, 0x34)), width=2)          # mallet
    d.rectangle([12, H - 18, 15, H - 13], fill=_c((0x6A, 0x4A, 0x36)), outline=OUT)
    return img


def game_booth(lib, kind=0):
    """Ring-toss / bottle-toss booth from the slat-roof stall: prizes hung under the roof,
    milk-bottle pyramid on the counter, striped canvas skirt."""
    base = lib["cf_slat_roof_stall"].img.copy()
    d = ImageDraw.Draw(base)
    W, H = base.size
    cols = [(0xD8, 0x3A, 0x36), (0x3E, 0x6E, 0xC4), (0xF0, 0xC0, 0x3A), (0xE8, 0x7C, 0xC0), (0x5A, 0xB0, 0x5A)]
    for i, x in enumerate(range(6, W - 6, 7)):     # plush prizes hanging from the roof edge
        c = cols[(i + kind) % len(cols)]
        d.line([x + 2, 25, x + 2, 28], fill=OUT)
        d.ellipse([x, 28, x + 5, 34], fill=_c(c), outline=OUT)
        d.point((x + 1, 29), fill=OUT)
        d.point((x + 4, 29), fill=OUT)
    cy = 40
    if kind == 0:       # milk bottles
        for row, n in enumerate((3, 2, 1)):
            for j in range(n):
                bx = W // 2 - n * 3 + j * 6
                by = cy - row * 5
                d.rectangle([bx, by - 4, bx + 3, by], fill=_c((0xF2, 0xEE, 0xE4)), outline=OUT)
    else:               # ring-toss pegs + rings
        for j in range(5):
            bx = 8 + j * 7
            d.line([bx, cy - 5, bx, cy], fill=_c((0x8A, 0x5A, 0x34)), width=2)
            d.ellipse([bx - 3, cy - 2, bx + 3, cy + 1], outline=_c(cols[j % 5]))
    # striped skirt under the counter
    for x in range(1, W - 1, 6):
        d.rectangle([x, H - 13, x + 2, H - 4], fill=_c((0xD8, 0x3A, 0x36)))
    return base


def register(lib):
    if "fair_barn_a" in lib:
        return
    lib.add_img("fair_barn_a", barn_img(7, 11), "building", "all", 0, [[3, 10]])
    lib.add_img("fair_barn_b", barn_img(6, 10, 1), "building", "all", 0, [[3, 9]])
    lib.add_img("fair_hay", hay_bale(0), "prop", [[0, 0]], 0)
    lib.add_img("fair_hay_round", hay_bale(1), "prop", [[0, 0]], 0)
    lib.add_img("fair_hay_stack", hay_stack(), "prop", [[0, 1], [1, 1]], 1)
    lib.add_img("fair_trough", trough(), "prop", [[0, 0], [1, 0]], 0)
    lib.add_img("fair_chicken", chicken(), "prop", [], 0)
    lib.add_img("fair_chicken_l", chicken(True, (0xC8, 0x8A, 0x4E)), "prop", [], 0)
    lib.add_img("fair_cow", cow(), "prop", [[0, 1], [1, 1]], 1)
    lib.add_img("fair_cow_l", cow(True), "prop", [[0, 1], [1, 1]], 1)
    lib.add_img("fair_flagpole", flagpole(5), "prop", [[0, 4]], 4)
    lib.add_img("fair_judges_stand", judges_stand(), "prop", [[0, 3], [1, 3], [2, 3], [3, 3], [0, 4], [1, 4], [2, 4], [3, 4]], 3)
    lib.add_img("fair_balloons", balloon_seller(), "prop", [[0, 2]], 2)
    lib.add_img("fair_ticket_booth", ticket_booth(), "prop", [[0, 2], [1, 2]], 2)
    lib.add_img("fair_race_car", race_car(), "vehicle", [[0, 1], [1, 1], [2, 1]], 1)
    memorial_hall(lib)
    # main gate: brick pillars + pennant arch, pillar bases solid, arch rows overhead
    gate = synth.gate_arch(4, 2, 6)
    solid = [[x, y] for y in (3, 4, 5) for x in (0, 1, 6, 7)]
    lib.add_img("fair_gate", gate, "prop", solid, 3)
    # covered grandstand: cf_plank_tier_seating tiers under a synthesized tin roof (read better than
    # synth.grandstand with cf_plank_bleacher_full, whose stepped log posts break the stand into bays)
    lib.add_img("fair_grandstand_tier", synth.grandstand2(24, 9), "building", "all", 0)
    lib.add_img("fair_pole", striped_pole(4), "prop", [[0, 3]], 3)
    lib.add_img("fair_high_striker", high_striker(), "prop", [[0, 4]], 4)
    wm = lib["rr_windmill_water_pump"]
    im = wm.img.copy()
    px = im.load()
    for yy in range(im.size[1]):
        for xx in range(im.size[0]):
            if px[xx, yy][3] and px[xx, yy][3] < 200:
                px[xx, yy] = (0, 0, 0, 0)
    lib.add_img("fair_windmill", im, "prop", sorted(wm.solid), wm.overhead_rows)
    stall = lib["cf_slat_roof_stall"]
    lib.add_img("fair_game_bottles", game_booth(lib, 0), "building", sorted(stall.solid), stall.overhead_rows)
    lib.add_img("fair_game_rings", game_booth(lib, 1), "building", sorted(stall.solid), stall.overhead_rows)
    for i in range(6):
        lib.add_img(f"fair_litter_{i}", litter_tile(100 + i), "decal", [], 0)
        lib.add_img(f"fair_sawdust_{i}", sawdust_tile(200 + i), "decal", [], 0)
    synth.FENCE_STYLES.setdefault("chain_green", ((0x6A, 0x9E, 0x62, 255), (0x3E, 0x6A, 0x44, 255), 18, (17, 2), 1, True))
    synth.FENCE_STYLES.setdefault("gate_green", ((0x4E, 0x7E, 0x52, 255), (0x2E, 0x52, 0x36, 255), 18, (17, 2, 9), 2, False))


# ============================================================================ ground
def build_ground(L, lib):
    L.fill("grass", 0, 0, 37, 77)
    full, _partial = synth.smooth_ring_cells(CX, CY, RING_OUT, RING_IN)
    for (x, y) in full:
        L.set_kind(x, y, "track")
    L.fill("dirt", 2, 56, 35, 75)                 # midway
    L.fill("dirt", 16, 76, 19, 77)                # gate threshold
    L.fill("dirt", 34, 16, 35, 55)                # east service lane
    L.fill("dirt", 8, 15, 15, 19)                 # barnyard
    L.fill("dirt", 8, 18, 33, 19)                 # lane along the grandstand back
    L.fill("sidewalk", 18, 16, 33, 17)            # concrete apron in front of Memorial Hall
    L.fill("dirt", 16, 45, 19, 51)                # infield path to the judges' stand
    L.fill("dirt", 15, 44, 20, 46)


# ============================================================================ build
def _trees_border(L):
    # west border x=0..1 and north border y=0..1: dense trees, invisible blockers
    L.block(0, 0, 1, 77)
    L.block(0, 0, 37, 1)
    seq = ["nt_s26_conifer_tall", "nt_s1_round_tree", "nt_s26_tree_round_small", "nt_s27_spruce_tall"]
    i = 0
    for y in range(3, 78, 2):
        pid = seq[i % len(seq)]
        p = L.lib[pid]
        L.place(pid, 0, y - p.h + 1)
        i += 1
    for x in range(2, 37, 2):
        pid = seq[(x // 2) % len(seq)]
        p = L.lib[pid]
        L.place(pid, x, 1 - p.h + 1)


def _fences(L):
    # east fence (green chain-link) at x=36, back gate y=63..64 locked
    east = [(36, y) for y in range(2, 78) if y not in (63, 64)]
    synth.paint_fence(L, east + [(35, 77)], "chain_green")
    synth.paint_fence(L, [(36, 62), (36, 63), (36, 64), (36, 65)], "gate_green")
    for y in range(2, 78):
        L.extra_solid.add((36, y))
        L.extra_solid.add((37, y))
    L.marker("locked_gate", 36, 63, id="fair_back_gate", locked=True)
    # padlock + chain on the back gate
    pad = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(pad)
    d.line([8, 0, 8, 6], fill=(0xA8, 0xAC, 0xB4, 255))
    d.arc([5, 4, 11, 10], 180, 360, fill=OUT)
    d.rectangle([5, 7, 11, 12], fill=(0xD8, 0xB0, 0x40, 255), outline=OUT)
    d.point((8, 9), fill=OUT)
    L.put("Objects", 36, 64, pad, False)
    # weed strip x=37 between the fence and the levee
    rng = random.Random(37)
    for y in range(3, 77, 3):
        pid = rng.choice(["nt_s1_flower_bush_small", "nt_s81_fern", "nt_s69_bush_ball_small"])
        if L.lib[pid].h == 1:
            L.place(pid, 37, y)
    # south fence: picket, ornamental, y=77 (gate pillars at 14..15 / 20..21)
    south = [(x, 77) for x in range(2, 14)] + [(x, 77) for x in range(22, 36)]
    synth.paint_fence(L, south, "picket")
    for c in south:
        L.extra_solid.add(c)
    # flower border just inside the picket fence
    flow = ["rr_flower_planter_red", "rr_flower_planter_yellow", "rr_flower_planter_pink", "rr_flower_planter_white"]
    k = 0
    for x in list(range(3, 12, 3)) + list(range(23, 34, 3)):
        L.place(flow[k % 4], x, 76)
        k += 1
    L.place("fair_gate", 14, 72)


def _barns(L):
    L.place("fair_barn_a", 2, 4)            # x=2..8, y=4..14, door (5,14) opens into the pen
    L.place("fair_barn_b", 10, 5)           # x=10..15, y=5..14, door (13,14) onto the barnyard
    L.place("fair_flagpole", 16, 11)        # Memorial Hall flagpole, base (16,15)
    for (pid, x, y) in [("fair_hay", 2, 3), ("fair_hay_round", 3, 3), ("fair_hay", 9, 4), ("fair_hay_round", 9, 13),
                        ("fair_hay", 15, 15), ("fair_hay_round", 14, 15), ("fair_hay", 9, 14)]:
        L.place(pid, x, y)
    # closed livestock pen x=2..7, y=15..19 (barn A's wall closes the top)
    pen = {(x, 19) for x in range(2, 8)} | {(2, y) for y in range(15, 20)} | {(7, y) for y in range(15, 20)}
    synth.paint_fence(L, pen, "wood")
    for c in pen:
        L.extra_solid.add(c)
    L.place("fair_cow", 3, 15)
    L.place("fair_cow_l", 5, 16)
    L.place("fair_trough", 3, 18)
    L.place("fair_hay", 6, 18)
    # barnyard: coop, chickens; windmill in the pocket west of the grandstand
    L.place("rr_shed_coop_red", 8, 15)      # x=8..10, y=15..18
    for (pid, x, y) in [("fair_chicken", 11, 17), ("fair_chicken_l", 12, 16), ("fair_chicken", 14, 18),
                        ("fair_chicken_l", 11, 19)]:
        L.place(pid, x, y)
    L.place("fair_windmill", 2, 21)
    L.place("fair_trough", 2, 28)


def _hall(L):
    L.place("fair_memorial_hall", 18, 5)    # x=18..33, y=5..15, doors (25..26, 15)
    L.place("nt_s17_flower_hedge_box_pink", 18, 16)
    L.place("nt_s17_flower_hedge_box_blue", 32, 16)
    L.place("sf_bench_wood_long", 20, 16)
    L.place("sf_bench_wood_long", 29, 16)
    L.place("sp_trashcan_metal", 23, 16)
    L.place("sp_trashcan_metal", 28, 16)
    # lawn behind / beside the hall: shade trees along the east fence, shrubs at the corners
    for (pid, x, y) in [("nt_s26_tree_small", 34, 3), ("nt_s1_round_tree", 34, 7), ("nt_s26_tree_small", 34, 11),
                        ("nt_s69_bush_round", 12, 3), ("nt_s69_bush_flowering_small", 5, 2)]:
        L.place(pid, x, y)


def _grandstand(L):
    L.place_b("fair_grandstand_tier", 6, 28)          # x=6..29, y=20..28
    synth.paint_fence(L, [(x, 29) for x in range(5, 31)], "white")
    for x in range(5, 31):
        L.extra_solid.add((x, 29))
    L.place("cf_floodlight_tower", 31, 21)            # base (31..32, 25)
    L.place("fair_race_car", 30, 27)
    L.place("fair_hay", 33, 27)
    L.place("fair_hay", 33, 28)
    L.place("sp_barrel_rust", 32, 22)
    L.place("sp_barrel_metal_empty", 33, 22)


def _track(L):
    # pixel-smooth oval rails (outer + inner), gap on the south straight for the midway crossing
    gap = (AVENUE[0] * 16, (AVENUE[1] + 1) * 16)
    synth.oval_rail(L, CX, CY, 15.6, 12.6, gap_x=gap)
    synth.oval_rail(L, CX, CY, 12.4, 9.4, gap_x=gap)
    _full, partial = synth.smooth_ring_cells(CX, CY, RING_OUT, RING_IN)
    synth.smooth_ring_decals(L, CX, CY, RING_OUT, RING_IN, partial, tex=("A2_Floors_MV_TILESET.png", 12, 4))
    o_rail, i_rail = rail_sets()   # cell sets, used below only to keep the finish line off the rails
    # start / finish line in front of the grandstand (north straight)
    chk = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(chk)
    for yy in range(0, T, 4):
        for xx in range(4, 12, 4):
            if ((xx // 4) + (yy // 4)) % 2 == 0:
                d.rectangle([xx, yy, xx + 3, yy + 3], fill=(0xF2, 0xEE, 0xE4, 230))
            else:
                d.rectangle([xx, yy, xx + 3, yy + 3], fill=(0x30, 0x2C, 0x34, 210))
    ring, inner, outer = ring_sets()
    for y in range(29, 36):
        if (18, y) in ring and (18, y) not in o_rail | i_rail:
            L.put("Decals", 18, y, chk)
    # infield: judges' stand + flagpole (secret S9)
    L.place("fair_judges_stand", 16, 40)          # x=16..19, y=40..44, base solid 43..44
    L.place("fair_flagpole", 20, 40)              # base (20,44)
    L.marker("secret", 18, 45, id="S9", desc="judges' stand: item at the foot of the stand stairs")
    for (pid, x, y) in [("nt_s17_flowers_red", 13, 42), ("nt_s17_flowers_yellow", 22, 42),
                        ("nt_s17_flowers_pink", 9, 46), ("nt_s17_flowers_blue", 25, 46),
                        ("nt_s17_flowers_purple", 8, 39), ("nt_s17_flowers_crimson", 26, 39)]:
        L.place(pid, x, y)
    for (pid, x, y) in [("nt_s26_tree_medium", 8, 35), ("nt_s26_tree_medium", 24, 35),
                        ("nt_s26_tree_small", 11, 36), ("nt_s1_round_tree", 21, 36)]:
        L.place(pid, x, y)
    for (pid, x, y) in [("fair_hay", 7, 43), ("fair_hay", 7, 44), ("fair_hay_round", 28, 43), ("fair_hay", 28, 44),
                        ("fair_hay_stack", 11, 49), ("fair_hay_stack", 23, 49)]:
        L.place(pid, x, y)
    # framing trees in the corner pockets outside the oval
    for (pid, x, y) in [("nt_s26_oak_large_b", 2, 29), ("nt_s1_round_tree", 2, 33), ("nt_s26_tree_small", 4, 30),
                        ("nt_s1_round_tree", 31, 30), ("nt_s26_tree_small", 32, 33),
                        ("nt_s26_tree_wide", 2, 52), ("nt_s26_tree_small", 7, 53),
                        ("nt_s26_tree_wide", 28, 52), ("nt_s26_tree_small", 26, 53)]:
        if dress.can_place(L, pid, x, y, pad=0):
            L.place(pid, x, y)


def _pole_string(L, xl, xr, ybase, kind):
    L.place("fair_pole", xl, ybase - 3)
    L.place("fair_pole", xr, ybase - 3)
    if kind == "bulbs":
        bulbs(L, xl, ybase - 3, xr, sag=7, inset=8)
    else:
        pennants(L, xl, ybase - 3, xr, sag=7, inset=8)


def _midway(L):
    L.place("sy_bigtop", 22, 58)                   # x=22..33, y=58..68
    L.marker("door", 27, 68, prefab="sy_bigtop")
    L.marker("door", 28, 68, prefab="sy_bigtop")
    # west stands, row A (y=57..61)
    L.place("fair_game_bottles", 2, 58)
    L.place("cf_slat_roof_stall_drinks", 5, 58)
    L.place("fair_game_rings", 8, 58)
    L.place("cf_food_cart_red_awning", 11, 59)
    # row B (y=64..67)
    L.place("cf_canvas_wall_tent_green", 2, 65)
    L.place("cf_food_cart_pink_awning", 6, 65)
    L.place("sf_vendor_cart_candy", 9, 65)
    L.place("fair_hay", 12, 67)
    L.place("fair_balloons", 13, 65)
    # row C (y=70..72) + gate side
    L.place("cf_canvas_wall_tent_beige", 2, 70)
    L.place("cf_food_cart_tan_awning", 6, 70)
    L.place("sf_vendor_cart_toys", 9, 70)
    L.place("fair_ticket_booth", 12, 72)           # x=12..13, base y=74
    L.place("cf_picnic_table", 3, 74)
    L.place("cf_picnic_table", 7, 74)
    L.place("sp_trashcan_metal_overflow", 10, 74)
    # east side: kiosk ticket booth, ice-cream truck, produce cart
    L.place("cf_wood_kiosk_booth", 22, 73)
    L.place("cf_ice_cream_truck", 24, 69)          # x=24..30, y=69..74
    L.place("cf_produce_cart_umbrella_fruit", 31, 70)
    L.place("fair_balloons", 21, 66)
    L.place("sp_trashcan_metal", 21, 69)
    # pennant and bulb strings across the avenue on striped poles (x=15 / x=20)
    _pole_string(L, 15, 20, 59, "bunting")
    _pole_string(L, 15, 20, 65, "bulbs")
    _pole_string(L, 15, 20, 71, "bunting")
    bulbs(L, 15, 59, 20, sag=5, offset_px=10, inset=8)
    bulbs(L, 15, 71, 20, sag=5, offset_px=10, inset=8)
    L.place("fair_high_striker", 21, 59)          # base (21,63)
    # long strings over the stalls and along the top of the midway
    bulbs(L, 2, 56, 13, sag=8)
    pennants(L, 2, 62, 13, sag=6, offset_px=6)
    pennants(L, 2, 68, 13, sag=6, offset_px=6)
    bulbs(L, 21, 56, 33, sag=8)
    # litter + sawdust on the midway dirt
    rng = random.Random(56)
    for _ in range(90):
        x, y = rng.randint(2, 35), rng.randint(56, 75)
        if L.kind[y][x] == "dirt" and (x, y) not in L.cells["Objects"] and (x, y) not in L.cells["Decals"]:
            pid = f"fair_litter_{rng.randint(0, 5)}" if rng.random() < 0.4 else f"fair_sawdust_{rng.randint(0, 5)}"
            L.place(pid, x, y)
    # NPC spots
    L.marker("npc", 18, 63, role="barker")
    L.marker("npc", 14, 75, role="ticket_taker")


def build(L, lib):
    register(lib)
    _trees_border(L)
    _fences(L)
    _barns(L)
    _hall(L)
    _grandstand(L)
    _track(L)
    _midway(L)
