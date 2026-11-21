#!/usr/bin/env python3
"""
sprite_pipeline.py — Grid-align and palette-lock AI-generated sprite sheets.

Replaces heuristic per-character fixes (e.g. detecting glasses to re-center
frames) with two general, content-based operations that work on ANY character:

  1. align   — finds each frame's actual artwork via alpha channel, then
               shifts it so a chosen anchor point (default: bottom-center,
               i.e. "feet") lands on the same pixel in every cell.
  2. palette — snaps every opaque pixel to the nearest color in a locked
               palette, and (optionally) binarizes alpha so AI-model
               anti-aliasing fuzz doesn't leave soft halos on your pixel art.

Also includes `extract-palette`, which pulls a palette straight out of an
existing sprite (so your NEW AI-generated assets can be locked to match
sprites you already like, e.g. Max or Bobby).

USAGE
-----
  # Pull the palette Max already uses, save it as a reusable swatch file
  python3 sprite_pipeline.py extract-palette \\
      --input Max_spritesheet.png --out palette_core.json

  # Fix a freshly-generated 4x4 walk-cycle sheet in one pass:
  python3 sprite_pipeline.py process \\
      --input new_character_raw.png \\
      --cols 4 --rows 4 \\
      --palette palette_core.json \\
      --out new_character_fixed.png

  # Steps individually:
  python3 sprite_pipeline.py align   --input in.png --cols 4 --rows 4 --out aligned.png
  python3 sprite_pipeline.py palette --input aligned.png --palette palette_core.json --out final.png

Requires: pillow, numpy   (pip install pillow numpy --break-system-packages)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


# --------------------------------------------------------------------------
# Core: grid alignment
# --------------------------------------------------------------------------

def split_grid(arr: np.ndarray, cols: int, rows: int):
    """Slice an (H, W, 4) array into a rows x cols grid of equal-size cells."""
    h, w = arr.shape[0], arr.shape[1]
    if h % rows != 0 or w % cols != 0:
        raise ValueError(
            f"Image size {w}x{h} does not divide evenly into a {cols}x{rows} grid "
            f"(cell would be {w/cols}x{h/rows}). Pad or crop the sheet first."
        )
    cw, ch = w // cols, h // rows
    cells = []
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            y0, x0 = r * ch, c * cw
            row_cells.append(arr[y0:y0 + ch, x0:x0 + cw].copy())
        cells.append(row_cells)
    return cells, cw, ch


def content_bbox(cell: np.ndarray, alpha_threshold: int = 10):
    """Bounding box of non-transparent pixels in a cell. None if empty."""
    alpha = cell[:, :, 3]
    mask = alpha > alpha_threshold
    if not mask.any():
        return None
    ys, xs = np.where(mask)
    return xs.min(), xs.max(), ys.min(), ys.max()


def anchor_point(bbox, anchor: str):
    x0, x1, y0, y1 = bbox
    cx = (x0 + x1) / 2.0
    if anchor == "bottom-center":
        return cx, y1
    if anchor == "top-center":
        return cx, y0
    if anchor == "center":
        return cx, (y0 + y1) / 2.0
    raise ValueError(f"Unknown anchor '{anchor}'")


def shift_cell(cell: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """Shift cell contents by integer (dx, dy), filling with transparency."""
    ch, cw = cell.shape[0], cell.shape[1]
    out = np.zeros_like(cell)
    src_x0, src_x1 = max(0, -dx), min(cw, cw - dx)
    dst_x0, dst_x1 = max(0, dx), min(cw, cw + dx)
    src_y0, src_y1 = max(0, -dy), min(ch, ch - dy)
    dst_y0, dst_y1 = max(0, dy), min(ch, ch + dy)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return out
    out[dst_y0:dst_y1, dst_x0:dst_x1] = cell[src_y0:src_y1, src_x0:src_x1]
    return out


def align_sheet(img: Image.Image, cols: int, rows: int,
                 anchor: str = "bottom-center",
                 target: tuple[float, float] | None = None,
                 alpha_threshold: int = 10, margin: int = 2) -> Image.Image:
    """
    Re-center every frame in a sprite sheet so its content anchor point
    (default: bottom-center = 'feet') lands on the same pixel across frames.

    target: (x, y) within a cell to align to. If not given, it is computed
            as the MEDIAN of each frame's own anchor point — meaning frames
            that already agree with each other are left alone, and only
            genuine outliers get moved. (A fixed formula based on cell
            geometry, e.g. "cell_height - margin", is wrong whenever the
            source art already uses the full cell with no headroom — it
            would force a shift that has nowhere to go but into cropping
            real content. This bit us on a sheet where every frame was
            already bottom-anchored at the same pixel.)
    """
    arr = np.array(img.convert("RGBA"))
    cells, cw, ch = split_grid(arr, cols, rows)

    # First pass: find each frame's anchor point.
    anchors = {}
    for r in range(rows):
        for c in range(cols):
            bbox = content_bbox(cells[r][c], alpha_threshold)
            if bbox is not None:
                anchors[(r, c)] = anchor_point(bbox, anchor)

    if target is None:
        if anchors:
            xs = sorted(a[0] for a in anchors.values())
            ys = sorted(a[1] for a in anchors.values())
            target = (xs[len(xs) // 2], ys[len(ys) // 2])
        elif anchor == "bottom-center":
            target = (cw / 2.0, ch - 1 - margin)
        elif anchor == "top-center":
            target = (cw / 2.0, margin)
        else:
            target = (cw / 2.0, ch / 2.0)

    out = np.zeros_like(arr)
    report = []
    for r in range(rows):
        for c in range(cols):
            cell = cells[r][c]
            y0, x0 = r * ch, c * cw
            if (r, c) not in anchors:
                report.append((r, c, "empty — left as-is"))
                out[y0:y0 + ch, x0:x0 + cw] = cell
                continue
            ax, ay = anchors[(r, c)]
            dx = round(target[0] - ax)
            dy = round(target[1] - ay)
            out[y0:y0 + ch, x0:x0 + cw] = shift_cell(cell, dx, dy)
            report.append((r, c, f"shifted ({dx:+d}, {dy:+d})"))

    for r, c, msg in report:
        print(f"  frame ({r},{c}): {msg}")

    return Image.fromarray(out, "RGBA")


# --------------------------------------------------------------------------
# Core: palette locking
# --------------------------------------------------------------------------

def extract_palette(img: Image.Image, max_colors: int = 24, alpha_threshold: int = 128):
    """Pull the N most common opaque colors out of an image, as hex strings."""
    arr = np.array(img.convert("RGBA"))
    mask = arr[:, :, 3] >= alpha_threshold
    pixels = arr[mask][:, :3]
    colors, counts = np.unique(pixels, axis=0, return_counts=True)
    order = np.argsort(-counts)
    top = colors[order][:max_colors]
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in top]


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lock_palette(img: Image.Image, palette_hex: list[str],
                  alpha_threshold: int | None = 128) -> Image.Image:
    """
    Snap every opaque pixel to the nearest color in palette_hex (RGB distance).
    If alpha_threshold is set, binarize alpha (removes soft AA halos typical
    of AI-generated pixel art); pass None to preserve original alpha.
    """
    # int32 is required here: channel differences up to 255 square to 65025,
    # which overflows int16 (max 32767) and wraps negative, silently corrupting
    # the nearest-color search (this bit us on pure black vs. white).
    arr = np.array(img.convert("RGBA")).astype(np.int32)
    palette = np.array([hex_to_rgb(h) for h in palette_hex], dtype=np.int32)

    h, w = arr.shape[0], arr.shape[1]
    rgb = arr[:, :, :3].reshape(-1, 3)
    alpha = arr[:, :, 3].reshape(-1)

    # Nearest palette color for every pixel (vectorized distance).
    diffs = rgb[:, None, :] - palette[None, :, :]
    dist2 = (diffs ** 2).sum(axis=2)
    nearest = palette[np.argmin(dist2, axis=1)]

    if alpha_threshold is not None:
        alpha = np.where(alpha >= alpha_threshold, 255, 0)

    out = np.concatenate([nearest, alpha[:, None]], axis=1).astype(np.uint8)
    out = out.reshape(h, w, 4)
    return Image.fromarray(out, "RGBA")


def resize_grid(img: Image.Image, cols: int, rows: int,
                 target_w: int, target_h: int,
                 resample=Image.BOX) -> Image.Image:
    """Resize every cell in a grid independently to a new cell size, keeping
    the same rows x cols layout. Useful for reformatting frames drawn at one
    canvas size (e.g. 32x32) onto a new standard (e.g. 16x32).

    Default resample is BOX, not NEAREST: nearest-neighbor on a DOWNSCALE
    just drops pixel columns/rows outright, which can delete thin 1px
    details (an outline, a glasses rim) entirely depending on which column
    survives. BOX averages instead, so thin details survive as slightly
    softened lines rather than vanishing — and a subsequent palette-lock
    pass snaps everything back to crisp, flat pixel-art color anyway.
    """
    arr = np.array(img.convert("RGBA"))
    cells, cw, ch = split_grid(arr, cols, rows)
    out = Image.new("RGBA", (target_w * cols, target_h * rows), (0, 0, 0, 0))
    for r in range(rows):
        for c in range(cols):
            cell_img = Image.fromarray(cells[r][c], "RGBA")
            resized = cell_img.resize((target_w, target_h), resample)
            out.paste(resized, (c * target_w, r * target_h))
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cmd_extract_palette(args):
    img = Image.open(args.input)
    hexes = extract_palette(img, max_colors=args.max_colors)
    Path(args.out).write_text(json.dumps(hexes, indent=2))
    print(f"Extracted {len(hexes)} colors -> {args.out}")
    print(hexes)


def cmd_align(args):
    img = Image.open(args.input)
    result = align_sheet(img, args.cols, args.rows, anchor=args.anchor,
                          alpha_threshold=args.alpha_threshold, margin=args.margin)
    result.save(args.out)
    print(f"Saved aligned sheet -> {args.out}")


def cmd_palette(args):
    img = Image.open(args.input)
    hexes = json.loads(Path(args.palette).read_text())
    result = lock_palette(img, hexes,
                           alpha_threshold=None if args.keep_alpha else 128)
    result.save(args.out)
    print(f"Saved palette-locked sheet -> {args.out}")


def cmd_process(args):
    img = Image.open(args.input)
    print("Step 1: aligning frames...")
    aligned = align_sheet(img, args.cols, args.rows, anchor=args.anchor,
                           alpha_threshold=args.alpha_threshold, margin=args.margin)
    if args.palette:
        print("Step 2: locking palette...")
        hexes = json.loads(Path(args.palette).read_text())
        aligned = lock_palette(aligned, hexes,
                                alpha_threshold=None if args.keep_alpha else 128)
    aligned.save(args.out)
    print(f"Saved final sheet -> {args.out}")


def cmd_resize(args):
    img = Image.open(args.input)
    result = resize_grid(img, args.cols, args.rows, args.target_width, args.target_height)
    result.save(args.out)
    print(f"Saved resized sheet -> {args.out} ({result.size[0]}x{result.size[1]}, "
          f"{args.cols}x{args.rows} grid of {args.target_width}x{args.target_height} cells)")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    ep = sub.add_parser("extract-palette", help="Pull a palette from an existing sprite")
    ep.add_argument("--input", required=True)
    ep.add_argument("--out", required=True)
    ep.add_argument("--max-colors", type=int, default=24, dest="max_colors")
    ep.set_defaults(func=cmd_extract_palette)

    al = sub.add_parser("align", help="Grid-align frames by content anchor")
    al.add_argument("--input", required=True)
    al.add_argument("--out", required=True)
    al.add_argument("--cols", type=int, required=True)
    al.add_argument("--rows", type=int, required=True)
    al.add_argument("--anchor", default="bottom-center",
                     choices=["bottom-center", "top-center", "center"])
    al.add_argument("--alpha-threshold", type=int, default=10, dest="alpha_threshold")
    al.add_argument("--margin", type=int, default=2)
    al.set_defaults(func=cmd_align)

    pl = sub.add_parser("palette", help="Snap image to a locked palette")
    pl.add_argument("--input", required=True)
    pl.add_argument("--out", required=True)
    pl.add_argument("--palette", required=True, help="JSON file: list of hex colors")
    pl.add_argument("--keep-alpha", action="store_true", dest="keep_alpha")
    pl.set_defaults(func=cmd_palette)

    pr = sub.add_parser("process", help="Align + palette-lock in one pass")
    pr.add_argument("--input", required=True)
    pr.add_argument("--out", required=True)
    pr.add_argument("--cols", type=int, required=True)
    pr.add_argument("--rows", type=int, required=True)
    pr.add_argument("--anchor", default="bottom-center",
                     choices=["bottom-center", "top-center", "center"])
    pr.add_argument("--alpha-threshold", type=int, default=10, dest="alpha_threshold")
    pr.add_argument("--margin", type=int, default=2)
    pr.add_argument("--palette", default=None, help="JSON file: list of hex colors (optional)")
    pr.add_argument("--keep-alpha", action="store_true", dest="keep_alpha")
    pr.set_defaults(func=cmd_process)

    rs = sub.add_parser("resize", help="Reformat frames from one cell size to another")
    rs.add_argument("--input", required=True)
    rs.add_argument("--out", required=True)
    rs.add_argument("--cols", type=int, required=True)
    rs.add_argument("--rows", type=int, required=True)
    rs.add_argument("--target-width", type=int, required=True, dest="target_width")
    rs.add_argument("--target-height", type=int, required=True, dest="target_height")
    rs.set_defaults(func=cmd_resize)

    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
