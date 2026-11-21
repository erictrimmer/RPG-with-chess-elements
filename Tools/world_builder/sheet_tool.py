"""Inspection helpers for the Modern Exteriors 16px sheets.

Usage (run from anywhere):
  python sheet_tool.py grid  <sheet.png> [out.png]            enlarged sheet with tile grid + col/row labels
  python sheet_tool.py comps <sheet.png> [out.png]            detect connected opaque tile regions, print rects, draw overlay
  python sheet_tool.py crop  <sheet.png> x y w h [out.png]    zoomed crop (tile units) with grid, for close inspection
  python sheet_tool.py preview <catalog.json> [out.png]       render every prefab in a catalog file, labelled, for self-check

<sheet.png> may be a bare file name (e.g. Tileset_44_MV.png); it is looked up in the 16px folder.
Output images default to the scratch dir given by env WB_OUT or ./_wb_out.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(ROOT, "..", ".."))
SHEETS = os.path.join(PROJECT, "Assets", "Modern Exteriors", "16px")
T = 16
OUT = os.environ.get("WB_OUT", os.path.join(ROOT, "_wb_out"))


def sheet_path(name):
    if os.path.isfile(name):
        return name
    p = os.path.join(SHEETS, name)
    if os.path.isfile(p):
        return p
    raise SystemExit(f"sheet not found: {name}")


def load(name):
    return Image.open(sheet_path(name)).convert("RGBA")


def font(sz=12):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def checker(w, h, a=(52, 52, 60), b=(70, 70, 80), s=8):
    im = Image.new("RGBA", (w, h), a)
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=b)
    return im


def gridded(img, scale, x0=0, y0=0, margin=26):
    """img: RGBA crop. Draw enlarged with grid; labels show absolute tile coords starting at (x0,y0)."""
    w, h = img.size
    big = img.resize((w * scale, h * scale), Image.NEAREST)
    canvas = checker(w * scale + margin, h * scale + margin)
    bg = checker(w * scale, h * scale)
    bg.alpha_composite(big)
    canvas.paste(bg, (margin, margin))
    d = ImageDraw.Draw(canvas)
    f = font(11)
    tw, th = w // T, h // T
    for i in range(tw + 1):
        x = margin + i * T * scale
        d.line([x, margin, x, margin + h * scale], fill=(255, 0, 255, 140) if (x0 + i) % 4 else (255, 255, 0, 220), width=1)
        if i < tw:
            d.text((x + 3, 2), str(x0 + i), fill=(255, 255, 0), font=f)
    for j in range(th + 1):
        y = margin + j * T * scale
        d.line([margin, y, margin + w * scale, y], fill=(255, 0, 255, 140) if (y0 + j) % 4 else (255, 255, 0, 220), width=1)
        if j < th:
            d.text((2, y + 3), str(y0 + j), fill=(255, 255, 0), font=f)
    return canvas


def occupied(img):
    tw, th = img.size[0] // T, img.size[1] // T
    a = img.getchannel("A")
    occ = [[False] * tw for _ in range(th)]
    for ty in range(th):
        for tx in range(tw):
            box = a.crop((tx * T, ty * T, tx * T + T, ty * T + T))
            occ[ty][tx] = box.getbbox() is not None
    return occ


def components(img):
    occ = occupied(img)
    th, tw = len(occ), len(occ[0])
    seen = [[False] * tw for _ in range(th)]
    comps = []
    for y in range(th):
        for x in range(tw):
            if occ[y][x] and not seen[y][x]:
                stack = [(x, y)]
                seen[y][x] = True
                cells = []
                while stack:
                    cx, cy = stack.pop()
                    cells.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < tw and 0 <= ny < th and occ[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((nx, ny))
                xs = [c[0] for c in cells]
                ys = [c[1] for c in cells]
                comps.append((min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, len(cells)))
    comps.sort(key=lambda c: (c[1], c[0]))
    return comps


def outpath(default_name, given):
    if given:
        return given
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, default_name)


def cmd_grid(args):
    img = load(args[0])
    scale = 3 if img.size[0] <= 256 else 2
    out = outpath(os.path.basename(args[0]).replace(".png", "_grid.png"), args[1] if len(args) > 1 else None)
    gridded(img, scale).convert("RGB").save(out)
    print(out)


def cmd_comps(args):
    img = load(args[0])
    comps = components(img)
    scale = 3
    canvas = gridded(img, scale)
    d = ImageDraw.Draw(canvas)
    f = font(13)
    m = 26
    for i, (x, y, w, h, n) in enumerate(comps):
        r = [m + x * T * scale, m + y * T * scale, m + (x + w) * T * scale - 1, m + (y + h) * T * scale - 1]
        d.rectangle(r, outline=(0, 255, 255), width=2)
        d.rectangle([r[0], r[1], r[0] + 22, r[1] + 15], fill=(0, 0, 0))
        d.text((r[0] + 2, r[1]), str(i), fill=(0, 255, 255), font=f)
        print(f"#{i}: x={x} y={y} w={w} h={h} (tiles={n})")
    out = outpath(os.path.basename(args[0]).replace(".png", "_comps.png"), args[1] if len(args) > 1 else None)
    canvas.convert("RGB").save(out)
    print(out)


def cmd_crop(args):
    img = load(args[0])
    x, y, w, h = map(int, args[1:5])
    crop = img.crop((x * T, y * T, (x + w) * T, (y + h) * T))
    scale = max(2, min(8, 640 // max(w * T, h * T)))
    out = outpath(f"{os.path.basename(args[0])[:-4]}_crop_{x}_{y}_{w}x{h}.png", args[5] if len(args) > 5 else None)
    gridded(crop, scale, x, y).convert("RGB").save(out)
    print(out)


def cmd_preview(args):
    cat = json.load(open(args[0]))
    prefabs = cat["prefabs"] if isinstance(cat, dict) else cat
    f = font(11)
    cells = []
    for p in prefabs:
        img = load(p["sheet"]).crop((p["x"] * T, p["y"] * T, (p["x"] + p["w"]) * T, (p["y"] + p["h"]) * T))
        sc = 2
        big = img.resize((img.size[0] * sc, img.size[1] * sc), Image.NEAREST)
        tile = checker(max(big.size[0], 150), big.size[1] + 16)
        tile.alpha_composite(big, (0, 16))
        d = ImageDraw.Draw(tile)
        # solid footprint (red) and overhead rows (blue)
        sol = p.get("solid", [])
        if sol == "all":
            sol = [[x, y] for x in range(p["w"]) for y in range(p["h"])]
        elif isinstance(sol, str) and sol.startswith("bottom:"):
            n = int(sol.split(":")[1])
            sol = [[x, y] for x in range(p["w"]) for y in range(p["h"] - n, p["h"])]
        elif not isinstance(sol, list):
            sol = []
        for (sx, sy) in sol:
            d.rectangle([sx * T * sc, 16 + sy * T * sc, (sx + 1) * T * sc - 1, 16 + (sy + 1) * T * sc - 1], outline=(255, 40, 40), width=1)
        oh = p.get("overhead_rows", 0)
        if oh:
            d.rectangle([0, 16, p["w"] * T * sc - 1, 16 + oh * T * sc - 1], outline=(60, 160, 255), width=2)
        d.rectangle([0, 0, tile.size[0], 15], fill=(0, 0, 0))
        d.text((2, 1), p["id"][:24], fill=(255, 255, 0), font=f)
        cells.append(tile)
    W = 1400
    rows, cur, x, rh = [], [], 0, 0
    for c in cells:
        if x + c.size[0] > W and cur:
            rows.append((cur, rh))
            cur, x, rh = [], 0, 0
        cur.append((x, c))
        x += c.size[0] + 6
        rh = max(rh, c.size[1])
    if cur:
        rows.append((cur, rh))
    H = sum(r[1] + 6 for r in rows) or 10
    sheet = Image.new("RGBA", (W, H), (20, 20, 24, 255))
    y = 0
    for cur, rh in rows:
        for x, c in cur:
            sheet.alpha_composite(c, (x, y))
        y += rh + 6
    out = outpath(os.path.basename(args[0]).replace(".json", "_preview.png"), args[1] if len(args) > 1 else None)
    sheet.convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    {"grid": cmd_grid, "comps": cmd_comps, "crop": cmd_crop, "preview": cmd_preview}[sys.argv[1]](sys.argv[2:])
