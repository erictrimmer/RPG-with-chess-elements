#!/usr/bin/env python3
"""Generates the original 24x24 Staunton-style piece sprites for Pawn's Journey.
Run:  python3 Tools/make_pieces.py   (needs Pillow). Output: Assets/Sprites/pieces_staunton/*.png
Flat style: outline + base fill + one light and one shade column per row. No third-party art is used."""
import os, sys
from PIL import Image

N = 24
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Assets", "Sprites", "pieces_staunton")

PAL = {
    "w": dict(outline=(38, 36, 52), fill=(240, 232, 214), light=(255, 252, 244), shade=(196, 184, 164)),
    "b": dict(outline=(14, 14, 22), fill=(74, 78, 98), light=(112, 118, 142), shade=(46, 48, 64)),
}

def new(): return [[False] * N for _ in range(N)]

def rows(m, spec):
    """spec: {y: halfwidth}; symmetric around the gap between x=11 and x=12."""
    for y, w in spec.items():
        for x in range(12 - w, 12 + w):
            m[y][x] = True

def rect(m, x0, y0, x1, y1, v=True):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m[y][x] = v

def disc(m, cx, cy, r):
    for y in range(N):
        for x in range(N):
            if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r: m[y][x] = True

def base(m, top=17):
    """Shared Staunton foot: collar, stem flare, plinth."""
    rows(m, {top: 5, top + 1: 5, top + 2: 6, top + 3: 7, top + 4: 8})   # top+4 = 21
    # plinth line
def pawn():
    m = new()
    disc(m, 12, 6.2, 3.3)
    rows(m, {9: 4, 10: 4, 11: 2, 12: 2, 13: 3, 14: 3, 15: 4, 16: 4})
    base(m, 17)
    return m, []

def rook():
    m = new()
    rows(m, {y: 6 for y in range(2, 5)})
    for x in (10, 11, 12, 13):          # crenel gaps
        pass
    rect(m, 9, 2, 9, 3, False); rect(m, 14, 2, 14, 3, False)  # two notches -> three merlons
    rows(m, {5: 5, 6: 4, 7: 4, 8: 4, 9: 4, 10: 4, 11: 4, 12: 4, 13: 4, 14: 4, 15: 5, 16: 5})
    base(m, 17)
    return m, [("h", 6, 4, 5, 0), ("h", 15, 15, 5, 0)]

def bishop():
    m = new()
    disc(m, 12, 2.6, 1.5)               # finial
    rows(m, {4: 2, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4, 10: 3, 11: 2, 12: 3, 13: 5, 14: 5, 15: 3, 16: 4})
    rows(m, {17: 5})
    rows(m, {18: 5, 19: 6, 20: 7, 21: 8})
    return m, [("slit", 0)]

def queen():
    m = new()
    rect(m, 11, 1, 12, 2)                       # ball on top of the crown
    for x in (4, 7, 16, 19):                    # four crown points
        m[3][x] = True
        m[2][x] = True
    for x in (5, 8, 15, 18):
        m[3][x] = True
    rect(m, 11, 3, 12, 3)
    rect(m, 5, 4, 18, 4)                        # crown band
    rows(m, {5: 6, 6: 5, 7: 3, 8: 2, 9: 2, 10: 3, 11: 3, 12: 4, 13: 4, 14: 5, 15: 5, 16: 5})
    rows(m, {17: 6})
    rows(m, {18: 5, 19: 6, 20: 7, 21: 8})
    return m, []

def king():
    m = new()
    rect(m, 11, 1, 12, 5)               # cross upright
    rect(m, 9, 2, 14, 3)                # cross arms
    rows(m, {6: 3, 7: 5, 8: 6, 9: 6, 10: 5, 11: 4, 12: 3, 13: 3, 14: 4, 15: 4, 16: 5})
    rows(m, {17: 6})
    rows(m, {18: 5, 19: 6, 20: 7, 21: 8})
    return m, []

KNIGHT = [
"........................",
".........##.##..........",
"........###.###.........",
"........#########.......",
".......###########......",
"......#############.....",
".....##############.....",
"....###############.....",
"...################.....",
"..#################.....",
".###################....",
".##################.....",
".##...############......",
".......###########......",
".......############.....",
"......##############....",
"......###############...",
"........................",
"........................",
"........................",
"........................",
"........................",
"........................",
"........................",
]

def knight():
    m = new()
    for y, line in enumerate(KNIGHT):
        for x, c in enumerate(line):
            if c == "#": m[y][x] = True
    rows(m, {17: 5, 18: 5, 19: 6, 20: 7, 21: 8})
    return m, []

def build(kind):
    return {"p": pawn, "r": rook, "b": bishop, "q": queen, "k": king, "n": knight}[kind]()

def render(kind, side):
    m, deco = build(kind)
    pal = PAL[side]
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = img.load()
    inside = lambda x, y: 0 <= x < N and 0 <= y < N and m[y][x]
    for y in range(N):
        xs = [x for x in range(N) if m[y][x]]
        if not xs: continue
        x0, x1 = min(xs), max(xs)
        for x in xs:
            c = pal["fill"]
            if x - x0 <= 1 and x1 - x0 >= 4: c = pal["light"] if x == x0 or (x == x0 + 1 and x1 - x0 >= 7) else c
            if x1 - x <= 1 and x1 - x0 >= 4: c = pal["shade"]
            px[x, y] = c + (255,)
    # outline: transparent pixels touching the shape (4-neighbour)
    for y in range(N):
        for x in range(N):
            if not m[y][x] and any(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = pal["outline"] + (255,)
    # decorations
    for d in deco:
        if d[0] == "h":                 # horizontal line across the shape at row y
            y = d[1]
            for x in range(N):
                if m[y][x] and m[y][x - 1] and m[y][min(x + 1, N - 1)]: px[x, y] = pal["outline"] + (255,)
        elif d[0] == "slit":
            for i, (x, y) in enumerate(((13, 6), (12, 7), (11, 8))):
                px[x, y] = pal["outline"] + (255,)
    # plinth separator for standing pieces
    if kind != "knight":
        y = 20
        for x in range(N):
            if m[y][x] and m[y][max(x - 1, 0)] and m[y][min(x + 1, N - 1)]: px[x, y] = pal["shade"] + (255,) if side == "w" else pal["outline"] + (255,)
    # knight eye and mane detail
    if kind == "knight":
        px[7, 7] = pal["outline"] + (255,)
        for (x, y) in ((14, 6), (15, 7), (15, 8), (16, 9)): px[x, y] = pal["shade"] + (255,)
    return img

def main():
    os.makedirs(OUT, exist_ok=True)
    for side in "wb":
        for kind in "prnbqk":
            render(kind, side).save(os.path.join(OUT, f"{side}{kind}.png"))
    # preview sheet
    sheet = Image.new("RGBA", (N * 6, N * 2), (0, 0, 0, 0))
    for r, side in enumerate("wb"):
        for c, kind in enumerate("kqrbnp"):
            sheet.alpha_composite(render(kind, side), (c * N, r * N))
    sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pieces_preview.png"))
    print("ok")

if __name__ == "__main__":
    main()
