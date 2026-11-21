"""Generated road paint + small ground decals, 1960s style.

Pre-1971 Pennsylvania roads: white dashed centre lines, crosswalks as two parallel white
lines (no zebra blocks), white stop bars. Paint is slightly worn (a few pixels dropped).
"""
from PIL import Image

import terrain as TR

T = 16
W = TR.PAINT_W
W2 = TR.PAINT_W2


def _blank():
    return Image.new("RGBA", (T, T))


def _worn(img, x, y, salt):
    """Drop a few pixels of paint for a worn look."""
    px = img.load()
    for i in range(3):
        xx = int(TR.rnd(x, y, salt + i) * T)
        yy = int(TR.rnd(x, y, salt + 10 + i) * T)
        if px[xx, yy][3]:
            px[xx, yy] = W2
    return img


def centre_dash_h(x, y, upper):
    """Dashed line between two rows of a horizontal road. upper=True -> this tile is the row above the line."""
    img = _blank()
    if x % 2 == 0:  # 16px dash, 16px gap
        yy = 15 if upper else 0
        for xx in range(2, 14):
            img.putpixel((xx, yy), W)
    return _worn(img, x, y, 1)


def centre_dash_v(x, y, left):
    img = _blank()
    if y % 2 == 0:
        xx = 15 if left else 0
        for yy in range(2, 14):
            img.putpixel((xx, yy), W)
    return _worn(img, x, y, 2)


def cross_lines_h(x, y, edge):
    """Crosswalk across a vertical road: pedestrians walk east-west through a band of rows.
    edge='top' draws the top line, 'bottom' the bottom line."""
    img = _blank()
    yy = (2, 3) if edge == "top" else (12, 13)
    for xx in range(16):
        for y2 in yy:
            img.putpixel((xx, y2), W)
    return _worn(img, x, y, 3)


def cross_lines_v(x, y, edge):
    """Crosswalk across a horizontal road: lines run north-south. edge='left'|'right'."""
    img = _blank()
    xs = (2, 3) if edge == "left" else (12, 13)
    for yy in range(16):
        for x2 in xs:
            img.putpixel((x2, yy), W)
    return _worn(img, x, y, 4)


def stop_bar_h(x, y):
    """Stop bar across a vertical-road lane (a horizontal bar)."""
    img = _blank()
    for xx in range(16):
        for yy in (6, 7, 8):
            img.putpixel((xx, yy), W)
    return _worn(img, x, y, 5)


def stop_bar_v(x, y):
    img = _blank()
    for yy in range(16):
        for xx in (6, 7, 8):
            img.putpixel((xx, yy), W)
    return _worn(img, x, y, 6)


def parking_tick_v(x, y):
    """Short line marking parking stall boundary on a horizontal road's curb lane (vertical tick)."""
    img = _blank()
    for yy in range(4, 16):
        img.putpixel((0, yy), W)
    return _worn(img, x, y, 7)


def track_rail(x, y):
    return _blank()


# ---------------------------------------------------------------- road painting helpers on a Level
def paint_road_h(L, x0, x1, y0, y1, centre=True, skip=()):
    """Horizontal road occupying rows y0..y1 (asphalt only). Draws a dashed centre line."""
    if not centre:
        return
    n = y1 - y0 + 1
    mid = y0 + n // 2  # line between mid-1 and mid
    for x in range(x0, x1 + 1):
        if any(a <= x <= b for a, b in skip):
            continue
        L.put("Decals", x, mid - 1, centre_dash_h(x, mid - 1, True))
        L.put("Decals", x, mid, centre_dash_h(x, mid, False))


def paint_road_v(L, x0, x1, y0, y1, centre=True, skip=()):
    if not centre:
        return
    n = x1 - x0 + 1
    mid = x0 + n // 2
    for y in range(y0, y1 + 1):
        if any(a <= y <= b for a, b in skip):
            continue
        L.put("Decals", mid - 1, y, centre_dash_v(mid - 1, y, True))
        L.put("Decals", mid, y, centre_dash_v(mid, y, False))


def crosswalk_across_v_road(L, x0, x1, y_top, y_bot):
    """Two lines spanning a vertical road (cols x0..x1) bounding rows y_top..y_bot."""
    for x in range(x0, x1 + 1):
        L.put("Decals", x, y_top, cross_lines_h(x, y_top, "top"))
        L.put("Decals", x, y_bot, cross_lines_h(x, y_bot, "bottom"))


def crosswalk_across_h_road(L, y0, y1, x_left, x_right):
    for y in range(y0, y1 + 1):
        L.put("Decals", x_left, y, cross_lines_v(x_left, y, "left"))
        L.put("Decals", x_right, y, cross_lines_v(x_right, y, "right"))
