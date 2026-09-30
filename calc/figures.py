"""Generates the SVG figures used in the documentation (standard library only).

    python calc/figures.py
"""
import os

import antenna as a

MM = 1e-3
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "images")
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, GRID = "#222", "#666", "#ddd"
COPPER, BLUE, ACCENT = "#b87333", "#2f6fb0", "#c0392b"


def svg(w, h, body):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' {FONT}>"
            f"<rect width='{w}' height='{h}' fill='white'/>{body}</svg>")


def text(x, y, s, size=13, anchor="start", color=INK, weight="normal"):
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' fill='{color}' font-weight='{weight}'>{s}</text>"


def dim_h(x1, x2, y, label):
    return (f"<line x1='{x1:.1f}' y1='{y:.1f}' x2='{x2:.1f}' y2='{y:.1f}' stroke='{MUTED}' marker-start='url(#a)' marker-end='url(#a)'/>"
            + text((x1 + x2) / 2, y - 5, label, 12, "middle", MUTED))


def dim_v(x, y1, y2, label):
    return (f"<line x1='{x:.1f}' y1='{y1:.1f}' x2='{x:.1f}' y2='{y2:.1f}' stroke='{MUTED}' marker-start='url(#a)' marker-end='url(#a)'/>"
            + f"<text x='{x - 6:.1f}' y='{(y1 + y2) / 2:.1f}' font-size='12' fill='{MUTED}' text-anchor='middle' "
              f"transform='rotate(-90 {x - 6:.1f} {(y1 + y2) / 2:.1f})'>{label}</text>")


ARROW = ("<defs><marker id='a' viewBox='0 0 10 10' refX='5' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
         f"<path d='M0,2 L5,5 L0,8' fill='none' stroke='{MUTED}' stroke-width='1.5'/></marker></defs>")


def geometry():
    s, ox, oy = 7.0, 380, 270                       # px per mm, card centre
    X = lambda x: ox + s * x
    Y = lambda y: oy + s * y
    b = [ARROW]
    b.append(f"<rect x='{X(-42.8)}' y='{Y(-26.99)}' width='{85.6 * s}' height='{53.98 * s}' rx='{3.18 * s}' fill='#1d1d1d'/>")
    pts = a.card_spiral(4, 80 * MM, 48 * MM, 1.0 * MM, 0.5 * MM)
    poly = " ".join(f"{X(x / MM):.1f},{Y(y / MM):.1f}" for x, y in pts)
    b.append(f"<polyline points='{poly}' fill='none' stroke='{COPPER}' stroke-width='{1.0 * s}' stroke-linecap='round'/>")
    b.append(f"<line x1='{X(-39.5)}' y1='{Y(23.5)}' x2='{X(-31)}' y2='{Y(15)}' stroke='#5aa0e6' stroke-width='2.5' stroke-dasharray='5 4'/>")
    b.append(f"<line x1='{X(-31)}' y1='{Y(15)}' x2='{X(-31)}' y2='{Y(11)}' stroke='#5aa0e6' stroke-width='2.5' stroke-dasharray='5 4'/>")
    b.append(f"<rect x='{X(-22.75)}' y='{Y(11)}' width='{1.5 * s}' height='{2 * s}' fill='#aaa'/>")
    b.append(text(X(-20), Y(12.8), "NTAG213F", 12, "start", "#ddd"))
    b.append(text(X(0), Y(-2), "Free inner area 69 × 37 mm", 15, "middle", "#eee"))
    b.append(text(X(0), Y(3), "(no copper pour inside the loop)", 12, "middle", "#bbb"))
    b.append(text(X(-29), Y(16.8), "back-side bridge", 11, "start", "#9cc7f0"))
    b.append(dim_h(X(-42.8), X(42.8), Y(-26.99) - 45, "card 85.6 mm (ISO/IEC 7810 ID-1)"))
    b.append(dim_h(X(-40), X(40), Y(-26.99) - 18, "antenna outline 80 mm"))
    b.append(dim_v(X(-42.8) - 42, Y(-26.99), Y(26.99), "53.98 mm"))
    b.append(dim_v(X(-42.8) - 16, Y(-24), Y(24), "48 mm"))
    b.append(text(X(42.8) + 14, Y(-20), "4 turns", 13, "start", INK, "bold"))
    b.append(text(X(42.8) + 14, Y(-15), "trace 1.0 mm", 13))
    b.append(text(X(42.8) + 14, Y(-10.5), "gap 0.5 mm", 13))
    b.append(text(X(42.8) + 14, Y(-6), "1 oz copper", 13))
    b.append(text(X(42.8) + 14, Y(2), "L ≈ 2.24 µH", 13, "start", COPPER, "bold"))
    b.append(text(X(42.8) + 14, Y(6.5), "C_par ≈ 2.5 pF", 13))
    b.append(text(X(42.8) + 14, Y(11), "f0 ≈ 14.7 MHz", 13, "start", ACCENT, "bold"))
    b.append(text(X(42.8) + 14, Y(15.5), "(with 50 pF chip)", 12, "start", MUTED))
    return svg(820, 500, "".join(b))


class Chart:
    def __init__(self, w, h, xr, yr, left=70, right=30, top=30, bottom=55):
        self.w, self.h, self.xr, self.yr = w, h, xr, yr
        self.l, self.r, self.t, self.b = left, w - right, top, h - bottom
        self.body = []

    def X(self, v):
        return self.l + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.r - self.l)

    def Y(self, v):
        return self.b - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.b - self.t)

    def axes(self, xticks, yticks, xlabel, ylabel, fmt_x="{:g}", fmt_y="{:g}"):
        for v in yticks:
            self.body.append(f"<line x1='{self.l}' x2='{self.r}' y1='{self.Y(v):.1f}' y2='{self.Y(v):.1f}' stroke='{GRID}'/>")
            self.body.append(text(self.l - 8, self.Y(v) + 4, fmt_y.format(v), 12, "end", MUTED))
        for v in xticks:
            self.body.append(text(self.X(v), self.b + 18, fmt_x.format(v), 12, "middle", MUTED))
        self.body.append(f"<line x1='{self.l}' x2='{self.r}' y1='{self.b}' y2='{self.b}' stroke='{MUTED}'/>")
        self.body.append(text((self.l + self.r) / 2, self.h - 12, xlabel, 13, "middle"))
        self.body.append(f"<text x='18' y='{(self.t + self.b) / 2:.1f}' font-size='13' fill='{INK}' text-anchor='middle' "
                         f"transform='rotate(-90 18 {(self.t + self.b) / 2:.1f})'>{ylabel}</text>")

    def line(self, pts, color, width=2.5, dash=None):
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        extra = f" stroke-dasharray='{dash}'" if dash else ""
        self.body.append(f"<polyline points='{d}' fill='none' stroke='{color}' stroke-width='{width}'{extra}/>")

    def band(self, lower, upper, color):
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in lower + upper[::-1])
        self.body.append(f"<polygon points='{d}' fill='{color}' opacity='0.18'/>")

    def dot(self, x, y, color, r=4):
        self.body.append(f"<circle cx='{self.X(x):.1f}' cy='{self.Y(y):.1f}' r='{r}' fill='{color}'/>")

    def render(self):
        return svg(self.w, self.h, "".join(self.body))


def tuning():
    pts = a.card_spiral()
    L = a.inductance_greenhouse(pts, 1.0 * MM)
    c0 = a.C_CHIP + a.interturn_capacitance(pts, 4, 1.0 * MM, 0.5 * MM) + 0.5e-12
    ch = Chart(760, 420, (0, 20), (12.4, 15.6))
    ch.axes(range(0, 21, 2), [12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5], "Tuning capacitance C1 + C2 [pF]",
            "Resonance frequency [MHz]", fmt_y="{:.1f}")
    xs = [i / 10 for i in range(0, 201)]
    f = lambda l, c: a.resonance(l, c) / 1e6
    ch.band([(x, f(L * 1.05, c0 * 1.05 + x * 1e-12)) for x in xs], [(x, f(L * 0.95, c0 * 0.95 + x * 1e-12)) for x in xs], BLUE)
    ch.line([(x, f(L, c0 + x * 1e-12)) for x in xs], BLUE)
    ch.line([(0, 13.56), (20, 13.56)], ACCENT, 1.8, "6 4")
    ch.body.append(text(ch.X(19.6), ch.Y(13.56) - 7, "13.56 MHz carrier", 12, "end", ACCENT))
    for c in (0, 3.3, 6.8, 10, 15):
        ch.dot(c, f(L, c0 + c * 1e-12), BLUE)
    ch.body.append(text(ch.X(19.6), ch.Y(15.35), "nominal: L = 2.24 µH, C = 52.5 pF + C_tune", 12, "end", BLUE))
    ch.body.append(text(ch.X(19.6), ch.Y(15.12), "band: ±5 % on L and on C (worst cases)", 12, "end", MUTED))
    return ch.render()


def turns():
    ch = Chart(760, 400, (1.8, 6.2), (0, 5))
    ch.axes([2, 3, 4, 5, 6], [0, 1, 2, 3, 4, 5], "Number of turns N (80 × 48 mm outline, 1.0 mm trace, 0.5 mm gap)",
            "Inductance [µH]")
    lo, hi = a.capacitance_for(a.C_CHIP + 3e-12, 15.0e6), a.capacitance_for(a.C_CHIP + 3e-12, 13.56e6)
    ch.band([(1.8, lo * 1e6), (6.2, lo * 1e6)], [(1.8, hi * 1e6), (6.2, hi * 1e6)], ACCENT)
    ch.body.append(text(ch.X(1.9), ch.Y(hi * 1e6) - 6, "target: f0 between 13.56 and 15 MHz", 12, "start", ACCENT))
    gh, em = [], []
    for n in range(2, 7):
        pts = a.card_spiral(n)
        gh.append((n, a.inductance_greenhouse(pts, 1.0 * MM) * 1e6))
        em.append((n, a.inductance_empirical(80 * MM, 48 * MM, n, 1.0 * MM, 0.5 * MM) * 1e6))
    ch.line(gh, COPPER)
    ch.line(em, BLUE, 2, "5 4")
    for n, v in gh:
        ch.dot(n, v, COPPER)
    ch.body.append(text(ch.X(2.1), ch.Y(4.6), "Greenhouse (segment sum)", 12, "start", COPPER))
    ch.body.append(text(ch.X(2.1), ch.Y(4.2), "ST AN2972 empirical formula", 12, "start", BLUE))
    return ch.render()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("antenna_geometry.svg", geometry), ("tuning_curve.svg", tuning), ("inductance_vs_turns.svg", turns)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("written", name)
