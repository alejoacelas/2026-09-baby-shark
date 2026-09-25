"""The cast, drawn freehand (sharks) or with the ellipse tool (Steve, because he's easier)."""

import numpy as np

# side-view shark facing right, nose at +100
BODY = [(100, 0), (82, -15), (50, -26), (10, -29), (-30, -24), (-62, -12), (-80, -6), (-104, -36),
        (-94, -2), (-106, 32), (-80, 7), (-60, 13), (-25, 23), (20, 25), (60, 19), (88, 8)]
DORSAL = [(18, -26), (-2, -64), (-30, -24)]
PECTORAL = [(28, 21), (8, 46), (-6, 22)]
COLORS = {"baby": "yellow", "mommy": "pink", "daddy": "blue", "grandma": "lav", "grandpa": "lgray"}
SCALES = {"baby": 0.55, "mommy": 0.95, "daddy": 1.2, "grandma": 0.95, "grandpa": 1.0}


def make_T(cx, cy, s, flip, rot):
    a = np.deg2rad(rot)
    ca, sa = np.cos(a), np.sin(a)

    def T(x, y):
        x = -x if flip else x
        return (cx + s * (x * ca - y * sa), cy + s * (x * sa + y * ca))
    return T


def shark(c, who, cx, cy, s=None, flip=False, rot=0, legs=False, mood="smile", props=True, fill=True):
    """Draw a family member; returns the transform so callers can hang things off it."""
    rng = c.rng
    s = s if s is not None else SCALES[who]
    T = make_T(cx, cy, s, flip, rot)
    j = lambda pts, k=6: [T(x + rng.normal(0, k), y + rng.normal(0, k)) for x, y in pts]
    w = max(3.5, 6 * s ** 0.5)
    c.stroke(j(BODY), w, smooth=True, closed=True, wob=0.9)
    fins = [j(DORSAL), j(PECTORAL)]
    for f in fins:
        c.stroke(f, w, wob=0.8)
    if legs:
        for lx in (-45, -15, 20, 50):
            ph = rng.uniform(-18, 18)
            c.stroke([T(lx, 20), T(lx + ph, 52), T(lx + ph + 12, 54)], w * 0.8)
    if fill:
        area = int((210 * s) * (60 * s) * 1.3)
        for p in [(0, 0), (50, -4), (-45, 0), (80, 2), (-92, -18), (-94, 18)]:
            c.fill(T(*p), COLORS[who], max_px=area)
        for f in fins:
            c.fill(np.mean(f, axis=0), COLORS[who], max_px=int(area * 0.15))
    # face
    ex, ey = T(62, -8)
    er = max(3, 5 * s) * (1.6 if who == "baby" else 1)
    if who == "baby":
        c.ellipse((ex - er * 1.6, ey - er * 1.6, ex + er * 1.6, ey + er * 1.6), w=2, fill="white")
    c.brush(np.array([[ex, ey]]), er * 1.5)
    if mood == "smile":
        c.stroke([T(94, 8), T(82, 13), T(68, 10)], w * 0.7)
    elif mood == "flat":
        c.stroke([T(94, 9), T(68, 10)], w * 0.7)
    elif mood == "scared":
        mx, my = T(82, 12)
        c.ellipse((mx - 6 * s, my - 5 * s, mx + 6 * s, my + 7 * s), w=3, fill="black")
    for gx in (36, 26):
        c.stroke([T(gx, -9), T(gx - 4, 0), T(gx, 9)], w * 0.6)
    if props:
        PROPS[who](c, T, s)
    return T


def _mommy(c, T, s):
    # lipstick, lashes, handbag
    c.stroke([T(95, 8), T(82, 13), T(68, 10)], 5 * s ** 0.5, "red")
    for dx in (-4, 2, 8):
        c.stroke([T(60 + dx, -13), T(58 + dx * 1.5, -22)], 3)
    bx, by = T(10, 38)
    c.rect((bx - 26 * s, by, bx + 26 * s, by + 34 * s), w=3, fill="purple")
    c.stroke([(bx - 14 * s, by), (bx, by - 22 * s), (bx + 14 * s, by)], 3, smooth=True)


def _daddy(c, T, s):
    # sunglasses, mustache
    ex, ey = T(62, -8)
    r = 11 * s
    c.ellipse((ex - r * 1.3, ey - r, ex + r * 1.1, ey + r * 0.9), w=3, fill="black")
    c.stroke([T(50, -9), T(20, -14)], 3)
    mx, my = T(84, 5)
    for k in range(3):
        c.stroke([(mx - 12 * s, my + k * 2), (mx, my - 4 * s + k * 2), (mx + 12 * s, my + k * 2)], 5 * s, smooth=True)


def _grandma(c, T, s):
    # glasses and a bun
    ex, ey = T(62, -8)
    r = 10 * s
    c.ellipse((ex - r, ey - r, ex + r, ey + r), w=3)
    c.stroke([T(52, -8), T(40, -12)], 2)
    bx, by = T(20, -40)
    c.ellipse((bx - 16 * s, by - 16 * s, bx + 16 * s, by + 14 * s), w=3, fill="lgray")


def _grandpa(c, T, s):
    # bushy eyebrow and a cane
    c.stroke([T(52, -18), T(62, -22), T(74, -17)], 6 * s, "gray")
    x, y = T(15, 22)
    c.stroke([(x, y), (x + 4 * s, y + 70 * s)], 5, "brown")
    c.stroke([(x, y), (x - 6 * s, y - 12 * s), (x - 18 * s, y - 8 * s), (x - 18 * s, y + 2 * s)], 5, "brown", smooth=True)


PROPS = {"baby": lambda c, T, s: None, "mommy": _mommy, "daddy": _daddy, "grandma": _grandma, "grandpa": _grandpa}


def dentures(c, x, y, s=1.0):
    c.ellipse((x - 22 * s, y - 10 * s, x + 22 * s, y + 10 * s), w=3, fill="pink")
    c.rect((x - 16 * s, y - 5 * s, x + 16 * s, y + 5 * s), w=2, fill="white")
    for k in range(-12, 16, 7):
        c.line((x + k * s, y - 5 * s), (x + k * s, y + 5 * s), w=2)


def steve(c, cx, cy, s=1.0, flip=False, mood="flat"):
    """Steve: an orange ellipse with a freehand tail. Not a shark."""
    d = -1 if flip else 1
    rx, ry = 34 * s, 20 * s
    c.stroke([(cx - d * rx * 0.9, cy), (cx - d * rx * 1.8, cy - ry * 1.1), (cx - d * rx * 1.7, cy + ry * 1.1),
              (cx - d * rx * 0.9, cy + 2)], max(3, 4 * s ** 0.5), wob=0.6)
    c.fill((cx - d * rx * 1.45, cy), "orange", max_px=int(rx * ry * 3))
    c.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), w=max(2, 3 * s ** 0.5), fill="orange")
    ex = cx + d * rx * 0.45
    c.brush(np.array([[ex, cy - ry * 0.25]]), max(3, 5 * s))
    if mood == "flat":
        c.stroke([(cx + d * rx * 0.55, cy + ry * 0.35), (cx + d * rx * 0.9, cy + ry * 0.35)], max(2, 3 * s ** 0.5))
    elif mood == "sad":
        c.stroke([(cx + d * rx * 0.5, cy + ry * 0.5), (cx + d * rx * 0.7, cy + ry * 0.3), (cx + d * rx * 0.9, cy + ry * 0.5)], 3)
    elif mood == "o":
        c.ellipse((cx + d * rx * 0.62 - 5 * s, cy + ry * 0.2, cx + d * rx * 0.62 + 5 * s, cy + ry * 0.2 + 10 * s), w=2)


def steves_mom_eye(c, cx, cy, s=1.0):
    """The part of Steve's mom that fits on screen."""
    c.ellipse((cx - 95 * s, cy - 60 * s, cx + 95 * s, cy + 60 * s), w=5, fill="white")
    c.ellipse((cx - 30 * s, cy - 32 * s, cx + 36 * s, cy + 34 * s), w=0, outline=None, fill="black")
    for k in range(5):
        a = np.deg2rad(200 + k * 35)
        x0, y0 = cx + 95 * s * np.cos(a) * 0.97, cy + 60 * s * np.sin(a) * 0.97
        c.stroke([(x0, y0), (x0 + 30 * s * np.cos(a), y0 + 40 * s * np.sin(a))], 6)


def stick(c, x, y, s=1.0, arm="out"):
    """Stick figure like the reference narrator. (x, y) is the top of the head."""
    c.stroke([(x - 20 * s, y + 20 * s), (x - 18 * s, y + 2 * s), (x + 2 * s, y - 4 * s), (x + 22 * s, y + 6 * s),
              (x + 20 * s, y + 38 * s), (x - 2 * s, y + 44 * s), (x - 20 * s, y + 30 * s)], 5, smooth=True, closed=True)
    c.brush(np.array([[x - 6 * s, y + 18 * s]]), 5)
    c.brush(np.array([[x + 6 * s, y + 16 * s]]), 5)
    c.stroke([(x - 6 * s, y + 30 * s), (x + 8 * s, y + 29 * s)], 4)
    c.stroke([(x, y + 44 * s), (x + 2 * s, y + 140 * s)], 5)
    c.stroke([(x + 2 * s, y + 140 * s), (x - 18 * s, y + 210 * s)], 5)
    c.stroke([(x + 2 * s, y + 140 * s), (x + 22 * s, y + 208 * s)], 5)
    if arm == "out":
        c.stroke([(x - 45 * s, y + 90 * s), (x + 50 * s, y + 80 * s)], 5)
    else:  # typing
        c.stroke([(x, y + 80 * s), (x + 45 * s, y + 100 * s), (x + 80 * s, y + 92 * s)], 5)
