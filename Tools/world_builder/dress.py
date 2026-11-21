"""Placement helpers shared by district builders."""
import random

T = 16

WALKABLE_GROUND = {"grass", "sidewalk", "road", "plaza", "plaza_grey", "cobble", "dirt", "track", "shoal"}


def ground_solid(L, x, y):
    """True if the baked ground cell at (x,y) is solid (water, wall, cliff rim)."""
    e = L.cells["Ground"].get((x, y))
    return bool(e and e[0][1])


def footprint(L, pid, x, y):
    """(object_cells, overhead_cells) a prefab would occupy at top-left (x,y)."""
    p = L.lib[pid]
    obj, ovh = [], []
    for ry in range(p.h):
        for rx in range(p.w):
            if p.tile_empty(rx, ry):
                continue
            (ovh if ry < p.overhead_rows else obj).append((x + rx, y + ry))
    return obj, ovh


def can_place(L, pid, x, y, kinds=None, pad=0, allow_overhead_overlap=True, reserved=None):
    """Prefab fits: in bounds, its object cells are free (Objects layer + pad ring), sit on walkable
    ground of an allowed kind, and avoid `reserved` cells (paths you want kept clear)."""
    obj, ovh = footprint(L, pid, x, y)
    for (cx, cy) in obj + ovh:
        if not L.inb(cx, cy):
            return False
    for (cx, cy) in obj:
        if ground_solid(L, cx, cy):
            return False
        if kinds and L.kind[cy][cx] not in kinds:
            return False
        if reserved and (cx, cy) in reserved:
            return False
        for dy in range(-pad, pad + 1):
            for dx in range(-pad, pad + 1):
                if (cx + dx, cy + dy) in L.cells["Objects"] or (cx + dx, cy + dy) in L.extra_solid:
                    return False
    if not allow_overhead_overlap:
        for c in ovh:
            if c in L.cells["Overhead"] or c in L.cells["Objects"]:
                return False
    return True


def try_place(L, pid, x, y, **kw):
    if can_place(L, pid, x, y, **kw):
        L.place(pid, x, y)
        return True
    return False


def scatter(L, pids, rect, count, seed=0, kinds=None, pad=1, tries=40, reserved=None, weights=None):
    """Randomly place up to `count` prefabs (chosen from pids) with their top-left inside rect
    (x0,y0,x1,y1 inclusive). Returns number placed."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = rect
    n = 0
    for _ in range(count):
        pid = rng.choices(pids, weights=weights)[0] if weights else rng.choice(pids)
        p = L.lib[pid]
        for _t in range(tries):
            x = rng.randint(x0, max(x0, x1 - p.w + 1))
            y = rng.randint(y0, max(y0, y1 - p.h + 1))
            if can_place(L, pid, x, y, kinds=kinds, pad=pad, reserved=reserved):
                L.place(pid, x, y)
                n += 1
                break
    return n


def place_b(L, pid, x, ybottom, **kw):
    """Place with bottom row at ybottom (uses can_place unless force=True)."""
    force = kw.pop("force", False)
    p = L.lib[pid]
    y = ybottom - p.h + 1
    if force or can_place(L, pid, x, y, **kw):
        L.place(pid, x, y)
        return True
    return False


def rect_cells(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def rect_outline(x0, y0, x1, y1, gaps=()):
    cells = set()
    for x in range(x0, x1 + 1):
        cells.add((x, y0))
        cells.add((x, y1))
    for y in range(y0, y1 + 1):
        cells.add((x0, y))
        cells.add((x1, y))
    for g in gaps:
        cells -= set(g)
    return cells
