"""Copy the pieces of LimeZu's Modern Interiors (16x16) that the depot interior uses into the project.

Run once (needs Pillow). The pack lives outside the repo; it is licensed for use in games but not for
redistribution, so keep the pack itself out of public repos.

    python Tools/world_builder/prepare_depot_assets.py [path/to/moderninteriors-win]

Writes:
    Assets/Interiors/Room_Builder_Floors_16x16.png   (floor tiles, unchanged)
    Assets/Interiors/Room_Builder_Walls_16x16.png    (wall tiles, unchanged)
    Assets/Interiors/depot/<name>.png                (furniture cropped from the Theme Sorter sheets)
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

PACK = Path(sys.argv[1] if len(sys.argv) > 1 else "F:/moderninteriors-win")
SRC = PACK / "1_Interiors" / "16x16"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets" / "Interiors"

GEN = SRC / "Theme_Sorter" / "1_Generic_16x16.png"
CONF = SRC / "Theme_Sorter" / "13_Conference_Hall_16x16.png"

# name: (sheet, x0, y0, x1, y1). Rough pixel regions on the sheet that contain exactly one object;
# each is trimmed to its opaque bounding box.
PROPS = {
    "bench_light": (GEN, 0, 250, 33, 268),
    "bench_dark": (GEN, 32, 250, 66, 268),
    "rug_red": (GEN, 147, 64, 208, 110),
    "rug_small": (GEN, 146, 168, 175, 190),
    "desk": (CONF, 139, 74, 197, 95),
    "chair_b": (CONF, 206, 96, 226, 114),
    "extinguisher": (CONF, 208, 114, 224, 134),
    "bin": (CONF, 226, 6, 240, 26),
    "painting_green": (GEN, 3, 216, 28, 232),
    "painting_sun": (GEN, 32, 216, 64, 232),
    "painting_coast": (GEN, 65, 216, 96, 232),
    "palm": (GEN, 210, 404, 240, 440),
    "tree": (GEN, 212, 452, 236, 490),
    "window_blue": (GEN, 114, 134, 142, 154),
    "crates": (GEN, 199, 946, 228, 976),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "depot").mkdir(exist_ok=True)
    sub = SRC / "Room_Builder_subfiles"
    shutil.copy(sub / "Room_Builder_Floors_16x16.png", OUT / "Room_Builder_Floors_16x16.png")
    shutil.copy(sub / "Room_Builder_Walls_16x16.png", OUT / "Room_Builder_Walls_16x16.png")
    cache = {}
    for name, (sheet, x0, y0, x1, y1) in PROPS.items():
        im = cache.setdefault(sheet, Image.open(sheet).convert("RGBA"))
        crop = im.crop((x0, y0, x1, y1))
        box = crop.getbbox()
        if box:
            crop = crop.crop(box)
        crop.save(OUT / "depot" / f"{name}.png")
        print(f"{name}: {crop.size[0]}x{crop.size[1]}")


if __name__ == "__main__":
    main()
