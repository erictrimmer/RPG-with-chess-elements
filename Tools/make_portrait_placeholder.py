#!/usr/bin/env python3
"""Makes the placeholder opponent portrait (96x96) until real art is drawn.
Output: Assets/UI/portrait_placeholder.png"""
import os
from PIL import Image, ImageDraw
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Assets", "UI")
os.makedirs(out, exist_ok=True)
S = 96
img = Image.new("RGBA", (S, S), (58, 62, 96, 255))
d = ImageDraw.Draw(img)
for y in range(0, S, 8):                      # soft stripes
    d.rectangle([0, y, S, y + 3], fill=(64, 68, 104, 255))
sil, edge = (36, 38, 60, 255), (22, 23, 38, 255)
d.ellipse([28, 14, 68, 54], fill=sil, outline=edge, width=2)           # head
d.rounded_rectangle([10, 58, 86, 120], radius=22, fill=sil, outline=edge, width=2)  # shoulders
Q = [  # pixel "?" glyph, 5x7
 "01110", "10001", "00001", "00110", "00100", "00000", "00100"]
for r, row in enumerate(Q):
    for c, v in enumerate(row):
        if v == "1":
            x, y = 38 + c * 4, 22 + r * 4
            d.rectangle([x, y, x + 3, y + 3], fill=(240, 196, 80, 255))
d.rectangle([0, 0, S - 1, S - 1], outline=edge, width=2)
img.save(os.path.join(out, "portrait_placeholder.png"))
print("ok")
