"""Build terrain + selected districts and render a region preview (normal + collision debug).

    python run_region.py <district>[,<district>...] x0 y0 x1 y1 [out_prefix]
Renders <out_prefix>_view.png (2x) and <out_prefix>_debug.png (collision in red, chunk seams yellow).
Also prints prefab placement count and any prefab ids that failed to load.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_downtown as BD  # noqa: E402

names = sys.argv[1].split(",")
x0, y0, x1, y1 = map(int, sys.argv[2:6])
prefix = sys.argv[6] if len(sys.argv) > 6 else os.path.join(os.environ.get("WB_OUT", "."), "region")
L, lib = BD.build_base()
BD.run_districts(L, lib, only=names)
L.render(prefix + "_view.png", scale=2 if (x1 - x0) <= 48 else 1, region=(x0, y0, x1 + 1, y1 + 1))
L.render(prefix + "_debug.png", scale=2 if (x1 - x0) <= 48 else 1, debug=True, region=(x0, y0, x1 + 1, y1 + 1))
print("placed", len(L.placed), "->", prefix + "_view.png", prefix + "_debug.png")
