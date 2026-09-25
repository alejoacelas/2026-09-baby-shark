"""A fake MS Paint: mouse-jittered brush, shape tools, pixel bucket fill, spray can.

Every Canvas owns a seeded RNG, so a drawing comes out the same on every run.
"""

import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

W, H = 960, 540
SS = 3  # supersampling for anti-aliased strokes (the grey edge pixels stop the bucket)

# Windows 7 Paint default swatches
PAL = {
    "black": (0, 0, 0), "white": (255, 255, 255), "gray": (127, 127, 127),
    "lgray": (195, 195, 195), "dkred": (136, 0, 21), "red": (237, 28, 36),
    "orange": (255, 127, 39), "yellow": (255, 242, 0), "green": (34, 177, 76),
    "lime": (181, 230, 29), "turq": (153, 217, 234), "aqua": (0, 162, 232),
    "blue": (63, 72, 204), "purple": (163, 73, 164), "lav": (200, 191, 231),
    "pink": (255, 174, 201), "brown": (185, 122, 87), "sand": (239, 228, 176),
    "gold": (255, 201, 14), "dkbrown": (120, 67, 21), "winblue": (0, 84, 227),
    "wingray": (236, 233, 216),
}
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"


def col(c):
    return PAL[c] if isinstance(c, str) else tuple(c)


def catmull(P, n=8):
    P = np.asarray(P, float)
    if len(P) < 3:
        return P
    ext = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return np.array(out)


# Handwriting: capitals as polylines on a 4-wide, 6-tall grid (y down).
_O = [(2, 0), (0.6, 0.8), (0, 3), (0.6, 5.2), (2, 6), (3.4, 5.2), (4, 3), (3.4, 0.8), (2, 0)]
FONT = {
    "A": [[(0, 6), (2, 0), (4, 6)], [(0.9, 3.8), (3.1, 3.8)]],
    "B": [[(0, 6), (0, 0), (3, 0), (4, 1.4), (3, 2.9), (0, 3)], [(3, 3), (4, 4.5), (3, 6), (0, 6)]],
    "C": [[(4, 0.6), (2.5, 0), (0.6, 0.9), (0, 3), (0.6, 5.1), (2.5, 6), (4, 5.4)]],
    "D": [[(0, 0), (0, 6), (2, 6), (3.6, 4.8), (4, 3), (3.6, 1.2), (2, 0), (0, 0)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "F": [[(4, 0), (0, 0), (0, 6)], [(0, 3), (3, 3)]],
    "G": [[(4, 0.6), (2.5, 0), (0.6, 0.9), (0, 3), (0.6, 5.1), (2.5, 6), (4, 5.2), (4, 3.4), (2.4, 3.4)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(2, 0), (2, 6)], [(0.6, 0), (3.4, 0)], [(0.6, 6), (3.4, 6)]],
    "J": [[(4, 0), (4, 4.5), (2.6, 6), (1.2, 6), (0, 4.6)]],
    "K": [[(0, 0), (0, 6)], [(4, 0), (0, 3.6)], [(1.3, 2.7), (4, 6)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "M": [[(0, 6), (0, 0), (2, 3.2), (4, 0), (4, 6)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "O": [_O],
    "P": [[(0, 6), (0, 0), (3, 0), (4, 1.5), (3, 3), (0, 3)]],
    "Q": [_O, [(2.5, 4.4), (4.4, 6.6)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1.5), (3, 3), (0, 3)], [(1.6, 3), (4, 6)]],
    "S": [[(4, 0.8), (3, 0), (1, 0), (0, 1.3), (1, 2.8), (3, 3.2), (4, 4.6), (3, 6), (1, 6), (0, 5.2)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "U": [[(0, 0), (0, 4.5), (1.4, 6), (2.6, 6), (4, 4.5), (4, 0)]],
    "V": [[(0, 0), (2, 6), (4, 0)]],
    "W": [[(0, 0), (1, 6), (2, 2.6), (3, 6), (4, 0)]],
    "X": [[(0, 0), (4, 6)], [(4, 0), (0, 6)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
    "Z": [[(0, 0), (4, 0), (0, 6), (4, 6)]],
    "0": [_O],
    "1": [[(1, 1.2), (2.2, 0), (2.2, 6)]],
    "2": [[(0, 1.2), (1.5, 0), (3.4, 0.4), (4, 1.8), (0, 6), (4, 6)]],
    "3": [[(0, 0.6), (3, 0), (4, 1.4), (2, 2.9), (4, 4.5), (3, 6), (0, 5.4)]],
    "4": [[(3, 6), (3, 0), (0, 4), (4, 4)]],
    "5": [[(4, 0), (0.6, 0), (0.2, 2.8), (3, 2.6), (4, 4.3), (3, 6), (0, 5.5)]],
    "6": [[(3.6, 0), (1, 1.4), (0, 4), (1, 6), (3, 6), (4, 4.5), (3, 3.1), (1, 3.1), (0, 4)]],
    "7": [[(0, 0), (4, 0), (1.5, 6)]],
    "8": [[(2, 3), (0.4, 1.5), (2, 0), (3.6, 1.5), (2, 3), (0, 4.5), (2, 6), (4, 4.5), (2, 3)]],
    "9": [[(4, 2.6), (2, 3.2), (0, 1.8), (1.5, 0), (3.5, 0.4), (4, 2.6), (3, 6)]],
    "!": [[(2, 0), (2, 4.2)], [(2, 5.7), (2.1, 5.9)]],
    "?": [[(0, 1), (1.5, 0), (3.5, 0.4), (4, 1.8), (2, 3.4), (2, 4.4)], [(2, 5.7), (2.1, 5.9)]],
    ".": [[(2, 5.7), (2.1, 5.9)]],
    ",": [[(2.2, 5.3), (1.6, 6.8)]],
    "'": [[(2, 0), (1.8, 1.6)]],
    '"': [[(1.2, 0), (1.1, 1.6)], [(2.8, 0), (2.7, 1.6)]],
    "-": [[(0.8, 3), (3.2, 3)]],
    ":": [[(2, 1.8), (2.1, 2)], [(2, 5.7), (2.1, 5.9)]],
    "(": [[(3, 0), (1.6, 1.8), (1.4, 4.2), (3, 6)]],
    ")": [[(1, 0), (2.4, 1.8), (2.6, 4.2), (1, 6)]],
    "/": [[(4, 0), (0, 6)]],
    "+": [[(0.5, 3), (3.5, 3)], [(2, 1.5), (2, 4.5)]],
    "=": [[(0.5, 2), (3.5, 2)], [(0.5, 4), (3.5, 4)]],
    "#": [[(1.3, 0.5), (1, 5.5)], [(3, 0.5), (2.7, 5.5)], [(0, 2), (4, 2)], [(0, 4), (4, 4)]],
    "*": [[(2, 1), (2, 5)], [(0.4, 2), (3.6, 4)], [(3.6, 2), (0.4, 4)]],
    "<": [[(4, 0.5), (0, 3), (4, 5.5)]],
    "3": [[(0, 0.6), (3, 0), (4, 1.4), (2, 2.9), (4, 4.5), (3, 6), (0, 5.4)]],
}


def seed_of(name):
    return zlib.crc32(name.encode())


class Canvas:
    def __init__(self, name, bg="white", img=None):
        self.name = name
        self.rng = np.random.default_rng(seed_of(name))
        self.img = img.copy() if img is not None else Image.new("RGB", (W, H), col(bg))

    def copy(self, name):
        return Canvas(name, img=self.img)

    # ---- mouse --------------------------------------------------------------
    def mouse(self, pts, wob=1.0, smooth=False, closed=False):
        """Turn intended control points into the shaky path a mouse would make."""
        rng = self.rng
        P = np.asarray(pts, float)
        if len(P) == 1:
            return P + rng.normal(0, 0.4 * wob, 2)
        if closed:
            P = np.vstack([P, P[:1]])
        if smooth and len(P) > 2:
            P = catmull(P)
        seg = np.hypot(*np.diff(P, axis=0).T)
        cum = np.r_[0, np.cumsum(seg)]
        tot = cum[-1]
        if tot < 1:
            return P[:1]
        n = max(3, int(tot / 1.5))
        s = np.linspace(0, tot, n)
        x, y = np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])
        dx, dy = np.gradient(x), np.gradient(y)
        L = np.hypot(dx, dy) + 1e-9
        nx, ny = -dy / L, dx / L
        amp = wob * (1.1 + min(tot, 700) / 170)
        off = np.zeros(n)
        for lo, hi, a in [(160, 320, 1.0), (50, 110, 0.45), (18, 32, 0.08)]:
            off += amp * a * np.sin(2 * np.pi * s / rng.uniform(lo, hi) + rng.uniform(0, 2 * np.pi))
        tr = np.convolve(rng.normal(0, 1, n + 4), np.ones(5) / 5, "valid")
        off += tr * 0.3 * wob
        if closed:  # pin the joint so the loop closes (and the bucket doesn't leak)
            ramp = np.clip(np.minimum(s, tot - s) / max(8, tot * 0.08), 0, 1)
            off *= ramp
        x, y = x + nx * off, y + ny * off
        # the hand overshoots or stops short at the ends
        tx0, ty0 = x[0] - x[1], y[0] - y[1]
        tx1, ty1 = x[-1] - x[-2], y[-1] - y[-2]
        l0, l1 = np.hypot(tx0, ty0) + 1e-9, np.hypot(tx1, ty1) + 1e-9
        e0 = rng.uniform(-1, 4) * wob
        e1 = rng.uniform(5, 12) * wob if closed else rng.uniform(-1, 5) * wob
        x = np.r_[x[0] + tx0 / l0 * e0, x, x[-1] + tx1 / l1 * e1]
        y = np.r_[y[0] + ty0 / l0 * e0, y, y[-1] + ty1 / l1 * e1]
        return np.c_[x, y]

    # ---- low-level mask drawing --------------------------------------------
    def _stamp(self, bbox, color, draw_fn):
        x0, y0, x1, y1 = [int(v) for v in bbox]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(W, x1), min(H, y1)
        if x1 <= x0 or y1 <= y0:
            return
        m = Image.new("L", ((x1 - x0) * SS, (y1 - y0) * SS), 0)
        draw_fn(ImageDraw.Draw(m), lambda x, y: ((x - x0) * SS, (y - y0) * SS))
        m = m.resize((x1 - x0, y1 - y0), Image.BOX).filter(ImageFilter.GaussianBlur(0.7))
        self.img.paste(Image.new("RGB", m.size, col(color)), (x0, y0), m)

    def brush(self, path, w=6, color="black"):
        path = np.asarray(path, float)
        pad = w + 3
        bb = (path[:, 0].min() - pad, path[:, 1].min() - pad, path[:, 0].max() + pad, path[:, 1].max() + pad)

        def fn(d, T):
            p = [T(x, y) for x, y in path]
            r = w * SS / 2
            if len(p) > 1:
                d.line(p, fill=255, width=int(w * SS), joint="curve")
            for q in (p[0], p[-1]):
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
        self._stamp(bb, color, fn)

    def stroke(self, pts, w=6, color="black", wob=1.0, smooth=False, closed=False):
        self.brush(self.mouse(pts, wob, smooth, closed), w, color)

    # ---- shape tools (perfect geometry) -------------------------------------
    def ellipse(self, box, outline="black", w=4, fill=None):
        x0, y0, x1, y1 = box

        def fn(d, T):
            a, b = T(x0, y0), T(x1, y1)
            d.ellipse([a, b], fill=255 if fill else None, outline=255, width=int(w * SS))
        if fill:
            self._stamp((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill,
                        lambda d, T: d.ellipse([T(x0 + w / 2, y0 + w / 2), T(x1 - w / 2, y1 - w / 2)], fill=255))
        if outline:
            self._stamp((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline,
                        lambda d, T: d.ellipse([T(x0, y0), T(x1, y1)], outline=255, width=int(w * SS)))

    def rect(self, box, outline="black", w=4, fill=None):
        d = ImageDraw.Draw(self.img)
        x0, y0, x1, y1 = [int(v) for v in box]
        if fill:
            d.rectangle([x0, y0, x1, y1], fill=col(fill))
        if outline:
            d.rectangle([x0, y0, x1, y1], outline=col(outline), width=w)

    def polygon(self, pts, outline="black", w=4, fill=None):
        P = np.asarray(pts, float)
        bb = (P[:, 0].min() - w, P[:, 1].min() - w, P[:, 0].max() + w, P[:, 1].max() + w)
        if fill:
            self._stamp(bb, fill, lambda d, T: d.polygon([T(x, y) for x, y in P], fill=255))
        if outline:
            self._stamp(bb, outline, lambda d, T: d.line([T(x, y) for x, y in np.vstack([P, P[:1]])],
                                                         fill=255, width=int(w * SS), joint="curve"))

    def line(self, p0, p1, w=4, color="black"):
        """Paint's straight line tool."""
        self._stamp((min(p0[0], p1[0]) - w, min(p0[1], p1[1]) - w, max(p0[0], p1[0]) + w, max(p0[1], p1[1]) + w),
                    color, lambda d, T: d.line([T(*p0), T(*p1)], fill=255, width=int(w * SS)))

    # ---- bucket -------------------------------------------------------------
    def fill(self, xy, color, max_px=None, only_if=None):
        """Real flood fill: exact colour match, 4-connected, like Paint's bucket."""
        a = np.asarray(self.img).copy()
        x, y = int(xy[0]), int(xy[1])
        if not (0 <= x < W and 0 <= y < H):
            return False
        target = a[y, x].copy()
        if only_if is not None and tuple(target) != col(only_if):
            return False
        if tuple(target) == col(color):
            return False
        lab, _ = ndimage.label(np.all(a == target, axis=2))
        reg = lab == lab[y, x]
        if max_px is not None and reg.sum() > max_px:
            return False
        a[reg] = col(color)
        self.img = Image.fromarray(a)
        return True

    # ---- spray can ----------------------------------------------------------
    def spray(self, pts, color, radius=18, density=25, step=4):
        rng = self.rng
        P = np.asarray(pts, float)
        if len(P) > 1:
            P = self.mouse(P, wob=1.5)
            seg = np.hypot(*np.diff(P, axis=0).T)
            cum = np.r_[0, np.cumsum(seg)]
            s = np.arange(0, cum[-1] + 1e-6, step)
            P = np.c_[np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])]
        a = np.asarray(self.img).copy()
        for cx, cy in P:
            r = radius * np.sqrt(rng.uniform(0, 1, density))
            t = rng.uniform(0, 2 * np.pi, density)
            xs = (cx + r * np.cos(t)).astype(int)
            ys = (cy + r * np.sin(t)).astype(int)
            ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
            a[ys[ok], xs[ok]] = col(color)
        self.img = Image.fromarray(a)

    # ---- eraser -------------------------------------------------------------
    def erase(self, pts, w=24, color="white"):
        """Paint's eraser is a square; a lazy drag leaves bits behind."""
        path = self.mouse(pts, wob=2.5)
        d = ImageDraw.Draw(self.img)
        for x, y in path[::2]:
            d.rectangle([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col(color))

    # ---- text ---------------------------------------------------------------
    def write(self, text, x, y, size=30, w=None, color="black", wob=None, slant=0.0):
        """Shaky handwritten capitals. Returns the x where the text ended."""
        rng = self.rng
        w = w or max(3, size / 8)
        wob = wob if wob is not None else 0.45 * (size / 30) ** 0.5
        s = size / 6
        top = y
        cx = x
        for ch in text.upper():
            if ch == "\n":
                top += size * 1.45
                cx = x + rng.normal(0, size * 0.1)
                continue
            if ch == " ":
                cx += s * 3.2
                continue
            sc = rng.uniform(0.8, 1.2)
            sx = sc * rng.uniform(0.8, 1.15)
            dy = rng.normal(0, size * 0.08)
            sl = slant + rng.normal(0, 0.1)
            for st in FONT.get(ch, []):
                st = [(px + rng.normal(0, 0.28), py + rng.normal(0, 0.28)) for px, py in st]
                pts = [(cx + px * s * sx + sl * (6 - py) * s, top + dy + (py * sc + (1 - sc) * 6) * s) for px, py in st]
                if len(st) == 2 and np.hypot(st[1][0] - st[0][0], st[1][1] - st[0][1]) < 0.5:  # a dot
                    self.brush(np.array(pts[:1]), w * 1.1, color)
                else:
                    self.stroke(pts, w, color, wob=wob)
            cx += (4 * sx + 1.6) * s + rng.normal(0, s * 0.45)
        return cx

    def type(self, text, x, y, size=20, color="black", font=FONT_PATH):
        f = ImageFont.truetype(font, size)
        ImageDraw.Draw(self.img).multiline_text((x, y), text, font=f, fill=col(color), spacing=4)

    # ---- composite helpers --------------------------------------------------
    def arrow(self, p0, p1, w=4, color="black", head=16, bend=0.15):
        rng = self.rng
        p0, p1 = np.array(p0, float), np.array(p1, float)
        v = p1 - p0
        n = np.array([-v[1], v[0]])
        mid = (p0 + p1) / 2 + n * rng.uniform(-bend, bend)
        self.stroke([p0, mid, p1], w, color, smooth=True)
        u = v / (np.linalg.norm(v) + 1e-9)
        for sgn in (1, -1):
            a = np.deg2rad(150 * sgn + rng.normal(0, 8))
            r = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]) @ u
            self.stroke([p1 + rng.normal(0, 1.5, 2), p1 + r * head * rng.uniform(0.8, 1.2)], w, color)

    def label(self, text, tx, ty, target, size=26, w=None, color="black"):
        """Handwritten label with an arrow pointing at `target`."""
        end = self.write(text, tx, ty, size, w, color)
        lines = text.split("\n")
        width = end - tx if len(lines) == 1 else max(len(l) for l in lines) * size * 0.9
        tgt = np.array(target, float)
        th = size * 1.45 * len(lines)
        # leave from whichever side of the text faces the target
        x0, x1, y0, y1 = tx - 6, tx + width + 6, ty - 8, ty + th
        cx, cy = np.clip(tgt[0], x0, x1), np.clip(tgt[1], y0, y1)
        if x0 < cx < x1 and y0 < cy < y1:
            cy = y1
        start = np.array([cx, cy])
        v = tgt - start
        L = np.linalg.norm(v)
        if L > 30:
            self.arrow(start + v / L * 10, tgt - v / L * 8, w=max(3, size / 9), color=color)

    def bubble(self, text, x, y, tail=None, size=24, shape=None, bg_fill="white"):
        """Speech bubble centred on (x, y). Freehand loop or Paint ellipse, whichever."""
        rng = self.rng
        lines = text.upper().split("\n")
        tw = max(len(l) for l in lines) * size * 0.88
        th = len(lines) * size * 1.45
        rx, ry = tw / 2 * 1.2 + 16, th / 2 * 1.25 + 14
        shape = shape or ("free" if rng.uniform() < 0.6 else "ellipse")
        if tail is not None:
            tail = np.array(tail, float)
            ang = np.arctan2(tail[1] - y, tail[0] - x)
            bx0 = np.array([x + rx * 0.85 * np.cos(ang - 0.25), y + ry * 0.85 * np.sin(ang - 0.25)])
            bx1 = np.array([x + rx * 0.85 * np.cos(ang + 0.25), y + ry * 0.85 * np.sin(ang + 0.25)])
        if shape == "ellipse":
            self.ellipse((x - rx, y - ry, x + rx, y + ry), w=3, fill=bg_fill)
        else:
            t = np.linspace(0, 2 * np.pi, 13)[:-1] + rng.uniform(0, 1)
            pts = [(x + rx * (1 + rng.normal(0, 0.05)) * np.cos(a), y + ry * (1 + rng.normal(0, 0.06)) * np.sin(a)) for a in t]
            self.stroke(pts, 4, smooth=True, closed=True, wob=0.8)
            if bg_fill:
                self.fill((x, y), bg_fill, max_px=int(4 * rx * ry))
                self.fill((x + rx * 0.5, y), bg_fill, max_px=int(4 * rx * ry))
        if tail is not None:
            self.stroke([bx0, tail], 4)
            self.stroke([bx1, tail], 4)
        ty = y - th / 2 + size * 0.2
        for l in lines:
            lw = len(l) * size * 0.85
            self.write(l, x - lw / 2, ty, size)
            ty += size * 1.45

    def paste_small(self, other, box):
        """Select all, copy, paste, drag the corner: nearest-neighbour shrink."""
        x0, y0, x1, y1 = [int(v) for v in box]
        self.img.paste(other.img.resize((x1 - x0, y1 - y0), Image.NEAREST), (x0, y0))

    def save(self, path):
        self.img.save(path)
