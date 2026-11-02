"""Vector ray diagrams for the Class 10 Light notes PDF.

All diagrams are drawn directly with ReportLab so the PDF stays sharp,
searchable and small. Coordinates use a 500-point design width; the builder
scales each diagram to the available text width.
"""

from __future__ import annotations

import math

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

W = 500

NAVY = HexColor("#17324D")
INK = HexColor("#243746")
TEAL = HexColor("#008CA0")
BLUE = HexColor("#2864C4")
ORANGE = HexColor("#E28A17")
RED = HexColor("#D64B3C")
GREEN = HexColor("#238B57")
PURPLE = HexColor("#7652A8")
GREY = HexColor("#71808B")
LIGHT_BLUE = HexColor("#E8F6FA")
LIGHT_GREY = HexColor("#F2F5F7")
LIGHT_YELLOW = HexColor("#FFF7E2")
WHITE = HexColor("#FFFFFF")
PAPER = HexColor("#FBFCFD")


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------

def line(c, p1, p2, color=INK, width=1.0, dash=None):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    if dash:
        c.setDash(dash)
    c.line(p1[0], p1[1], p2[0], p2[1])
    c.restoreState()


def arrow_head(c, tip, angle, color, size=6.0):
    a = angle
    p = c.beginPath()
    p.moveTo(tip[0], tip[1])
    p.lineTo(
        tip[0] - size * math.cos(a - 0.48),
        tip[1] - size * math.sin(a - 0.48),
    )
    p.lineTo(
        tip[0] - size * math.cos(a + 0.48),
        tip[1] - size * math.sin(a + 0.48),
    )
    p.close()
    c.saveState()
    c.setFillColor(color)
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def arrow(c, p1, p2, color=RED, width=1.4, dash=None, head=6.0):
    line(c, p1, p2, color=color, width=width, dash=dash)
    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    arrow_head(c, p2, angle, color, head)


def vertical_arrow(c, x, base, height, color=ORANGE, width=1.8, dashed=False, head=5.5):
    end = base + height
    line(c, (x, base), (x, end), color=color, width=width, dash=[3, 3] if dashed else None)
    arrow_head(c, (x, end), math.pi / 2 if height >= 0 else -math.pi / 2, color, head)


def dot(c, x, y, r=2.2, color=NAVY):
    c.saveState()
    c.setFillColor(color)
    c.circle(x, y, r, stroke=0, fill=1)
    c.restoreState()


def text(c, x, y, s, size=8, color=INK, bold=False, align="left", bg=None):
    font = "DejaVu-Bold" if bold else "DejaVu"
    c.saveState()
    c.setFont(font, size)
    if bg:
        tw = pdfmetrics.stringWidth(s, font, size) + 7
        if align == "center":
            left = x - tw / 2
        elif align == "right":
            left = x - tw
        else:
            left = x - 3
        c.setFillColor(bg)
        c.roundRect(left, y - 2.5, tw, size + 5, 2, stroke=0, fill=1)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)
    c.restoreState()


def axis(c, y, x1=15, x2=485, label="principal axis", size=7.5):
    line(c, (x1, y), (x2, y), color=GREY, width=0.8)
    arrow_head(c, (x2, y), 0, GREY, 4.5)
    if label:
        text(c, x2 - 2, y - 11, label, size=size, color=GREY, align="right")


def mirror_arc(c, p, y, half_height, kind="concave", radius=300):
    """Draw a spherical mirror arc and small hatch marks on its back."""
    r = radius
    a = math.degrees(math.asin(min(0.94, half_height / r)))
    c.saveState()
    c.setStrokeColor(NAVY)
    c.setLineWidth(2.2)
    if kind == "concave":
        cx = p - r
        c.arc(cx - r, y - r, cx + r, y + r, -a, 2 * a)
        angles = [-a + 2 + i * (2 * a - 4) / 8 for i in range(9)]
        for deg in angles:
            th = math.radians(deg)
            px = cx + r * math.cos(th)
            py = y + r * math.sin(th)
            nx, ny = math.cos(th), math.sin(th)
            line(c, (px + 3 * nx, py + 3 * ny), (px + 10 * nx, py + 10 * ny), color=GREY, width=0.8)
    else:
        cx = p + r
        c.arc(cx - r, y - r, cx + r, y + r, 180 - a, 2 * a)
        angles = [180 - a + 2 + i * (2 * a - 4) / 8 for i in range(9)]
        for deg in angles:
            th = math.radians(deg)
            px = cx + r * math.cos(th)
            py = y + r * math.sin(th)
            nx, ny = math.cos(th), math.sin(th)
            line(c, (px - 3 * nx, py - 3 * ny), (px - 10 * nx, py - 10 * ny), color=GREY, width=0.8)
    c.restoreState()


def lens_shape(c, x, y, half_height, half_width, kind="convex"):
    p = c.beginPath()
    if kind == "convex":
        p.moveTo(x, y + half_height)
        p.curveTo(x - half_width, y + 0.62 * half_height,
                  x - half_width, y - 0.62 * half_height,
                  x, y - half_height)
        p.curveTo(x + half_width, y - 0.62 * half_height,
                  x + half_width, y + 0.62 * half_height,
                  x, y + half_height)
    else:
        p.moveTo(x - 0.72 * half_width, y + half_height)
        p.lineTo(x + 0.72 * half_width, y + half_height)
        p.curveTo(x + 0.18 * half_width, y + 0.62 * half_height,
                  x + 0.18 * half_width, y - 0.62 * half_height,
                  x + 0.72 * half_width, y - half_height)
        p.lineTo(x - 0.72 * half_width, y - half_height)
        p.curveTo(x - 0.18 * half_width, y - 0.62 * half_height,
                  x - 0.18 * half_width, y + 0.62 * half_height,
                  x - 0.72 * half_width, y + half_height)
    p.close()
    c.saveState()
    c.setFillColor(LIGHT_BLUE)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.4)
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def mark(c, x, y, label, label_y=None, color=NAVY, size=7.2):
    dot(c, x, y, 2.1, color=color)
    line(c, (x, y - 4), (x, y + 4), color=color, width=0.8)
    text(c, x, label_y if label_y is not None else y - 13, label, size=size, color=color, align="center", bg=WHITE)


def legend(c, x, y, color, number, caption):
    line(c, (x, y + 3), (x + 14, y + 3), color=color, width=1.8)
    text(c, x + 18, y, number + " " + caption, size=7.2, color=INK)


# ---------------------------------------------------------------------------
# Foundation diagrams
# ---------------------------------------------------------------------------

def reflection_plane(c, H):
    surf = 52
    O = (250, surf)
    c.setFillColor(LIGHT_GREY)
    c.rect(0, 0, W, surf, stroke=0, fill=1)
    line(c, (35, surf), (465, surf), color=NAVY, width=2.4)
    for x in range(45, 461, 18):
        line(c, (x, surf), (x - 7, surf - 10), color=GREY, width=0.7)
    line(c, (250, surf), (250, 150), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, (95, 145), O, color=RED, width=1.7)
    arrow(c, O, (405, 145), color=BLUE, width=1.7)
    c.saveState()
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.0)
    c.arc(215, 17, 285, 87, 30, 60)
    c.arc(215, 17, 285, 87, 90, 60)
    c.restoreState()
    text(c, 208, 103, "i", size=11, color=PURPLE, bold=True)
    text(c, 286, 103, "r", size=11, color=PURPLE, bold=True)
    text(c, 256, 139, "normal", size=7.5, color=GREY)
    text(c, 105, 137, "incident ray", size=7.5, color=RED)
    text(c, 340, 137, "reflected ray", size=7.5, color=BLUE)
    text(c, 250, 24, "smooth plane mirror", size=8, color=NAVY, bold=True, align="center")
    text(c, 250, 9, "i = r ; both angles are measured from the normal", size=7.5, color=GREY, align="center")


def sign_convention(c, H):
    y = 82
    axis(c, y, 20, 480, label="direction of incident light →")
    line(c, (250, 25), (250, 145), color=GREY, width=0.8, dash=[3, 3])
    lens_shape(c, 250, y, 52, 10, "convex")
    text(c, 250, 145, "P for a mirror / O for a lens", size=8.5, color=NAVY, bold=True, align="center")
    text(c, 115, 118, "+ heights", size=8.5, color=GREEN, bold=True, align="center")
    text(c, 385, 118, "+ heights", size=8.5, color=GREEN, bold=True, align="center")
    text(c, 115, 43, "− heights", size=8.5, color=RED, bold=True, align="center")
    text(c, 385, 43, "− heights", size=8.5, color=RED, bold=True, align="center")
    text(c, 105, y + 6, "− distances", size=9, color=RED, bold=True, align="center", bg=WHITE)
    text(c, 395, y + 6, "+ distances", size=9, color=GREEN, bold=True, align="center", bg=WHITE)
    vertical_arrow(c, 120, y, 26, color=ORANGE, width=1.6)
    text(c, 120, 113, "object", size=7.2, color=ORANGE, align="center")
    vertical_arrow(c, 380, y, -26, color=GREEN, width=1.6)
    text(c, 380, 43, "inverted image", size=7.2, color=GREEN, align="center")
    text(c, 250, 10, "Origin at P/O · right and above are positive · left and below are negative", size=7.6, color=NAVY, align="center")


# ---------------------------------------------------------------------------
# Mirror diagrams
# ---------------------------------------------------------------------------

def mirror_concave_focus(c, H):
    y = 82
    P, R, f = 390, 300, 150
    C, F = P - R, P - f
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    axis(c, y)
    mirror_arc(c, P, y, 46, "concave", R)
    mark(c, C, y, "C", 62)
    mark(c, F, y, "F", 62)
    mark(c, P, y, "P", 62)
    for yy in (116, 101, 63, 48):
        arrow(c, (35, yy), (P - 2, yy), color=RED, width=1.15, head=5)
        arrow(c, (P - 2, yy), (F, y), color=BLUE, width=1.15, head=5)
        arrow(c, (F, y), (F - 45, y + (yy - y) * -0.3), color=BLUE, width=1.0, head=4.5)
    line(c, (C, 36), (P, 36), color=PURPLE, width=1.1)
    arrow_head(c, (C, 36), math.pi, PURPLE, 5)
    arrow_head(c, (P, 36), 0, PURPLE, 5)
    text(c, (C + P) / 2, 24, "R = 2f", size=8, color=PURPLE, align="center")
    line(c, (F, 48), (P, 48), color=GREEN, width=1.1)
    arrow_head(c, (F, 48), math.pi, GREEN, 5)
    arrow_head(c, (P, 48), 0, GREEN, 5)
    text(c, (F + P) / 2, 39, "f", size=8, color=GREEN, align="center", bg=WHITE)
    text(c, 38, 132, "parallel rays", size=8, color=RED, bold=True)
    text(c, 250, 145, "CONCAVE MIRROR · real focus", size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 8, "Rays parallel to the principal axis meet at F after reflection.", size=7.5, color=GREY, align="center")


def mirror_convex_focus(c, H):
    y = 82
    P, R, f = 120, 300, 150
    C, F = P + R, P + f
    axis(c, y)
    mirror_arc(c, P, y, 46, "convex", R)
    mark(c, P, y, "P", 62)
    mark(c, F, y, "F", 62)
    mark(c, C, y, "C", 62)
    for yy in (116, 101, 63, 48):
        arrow(c, (20, yy), (P + 2, yy), color=RED, width=1.15, head=5)
        slope = -(yy - y) / f
        x_end = 20
        y_end = yy + slope * (x_end - P)
        arrow(c, (P + 2, yy), (x_end, y_end), color=BLUE, width=1.15, head=5)
        line(c, (P + 2, yy), (F, y), color=GREY, width=0.9, dash=[3, 3])
    text(c, 20, 132, "parallel rays", size=8, color=RED, bold=True)
    text(c, 250, 145, "CONVEX MIRROR · virtual focus", size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 24, "dashed extensions appear to start at F behind the mirror", size=7.5, color=GREY, align="center")
    text(c, 250, 9, "The mirror spreads parallel rays, so its focus is virtual.", size=7.5, color=GREY, align="center")


def draw_mirror_case(c, H, u, f, title, result, virtual=False):
    y = 84
    P, h = 350, 25
    C, F = P - 2 * f, P - f
    axis(c, y, 15, 485, label="")
    mirror_arc(c, P, y, 50, "concave", 2 * f)
    for x, lab in ((C, "C"), (F, "F"), (P, "P")):
        mark(c, x, y, lab, y - 14, size=7)
    xo = P - u
    vertical_arrow(c, xo, y, h, color=ORANGE, width=1.8)
    text(c, xo, y + h + 7, "object", size=7, color=ORANGE, align="center")
    # Ray 1: parallel to axis, then through F.
    arrow(c, (xo, y + h), (P, y + h), color=RED, width=1.35, head=5)
    # Ray 2: through pole, reflected symmetrically.
    arrow(c, (xo, y + h), (P, y), color=PURPLE, width=1.35, head=5)
    t = u * f / (f - u)
    xi = P + t
    yi = h * t / u
    if not virtual:
        # Reflected rays meet in front of the mirror.
        left = max(18, xi - 28)
        y1 = y + h + (h / f) * (left - P)
        y2 = y + (h / u) * (left - P)
        arrow(c, (P, y + h), (left, y1), color=BLUE, width=1.35, head=5)
        arrow(c, (P, y), (left, y2), color=BLUE, width=1.35, head=5)
        vertical_arrow(c, xi, y, yi, color=GREEN, width=1.8)
        text(c, xi, y + yi - 14, "image", size=7, color=GREEN, align="center", bg=WHITE)
    else:
        # Solid reflected rays to the left, dashed backward extensions to the right.
        left = 245
        y1 = y + h + (h / f) * (left - P)
        y2 = y + (h / u) * (left - P)
        arrow(c, (P, y + h), (left, y1), color=BLUE, width=1.35, head=5)
        arrow(c, (P, y), (left, y2), color=BLUE, width=1.35, head=5)
        line(c, (P, y + h), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
        line(c, (P, y), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
        vertical_arrow(c, xi, y, yi, color=GREEN, width=1.7, dashed=True)
        text(c, xi, y + yi + 4, "virtual image", size=7, color=GREEN, align="center", bg=WHITE)
    text(c, 250, H - 14, title, size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 8, result, size=7.4, color=GREY, align="center")


def concave_beyond_c(c, H):
    draw_mirror_case(c, H, 150, 50, "OBJECT BEYOND C", "Real, inverted, diminished image between F and C", virtual=False)


def concave_between_c_f(c, H):
    draw_mirror_case(c, H, 70, 50, "OBJECT BETWEEN C AND F", "Real, inverted, enlarged image beyond C", virtual=False)


def concave_inside_f(c, H):
    draw_mirror_case(c, H, 30, 50, "OBJECT BETWEEN F AND P", "Virtual, erect, enlarged image behind the mirror", virtual=True)


def convex_mirror_case(c, H):
    y = 88
    P, f, u, h = 230, 70, 160, 20
    C, F = P + 2 * f, P + f
    xo = P - u
    axis(c, y, 15, 485, label="")
    mirror_arc(c, P, y, 48, "convex", 2 * f)
    for x, lab in ((P, "P"), (F, "F"), (C, "C")):
        mark(c, x, y, lab, y - 14, size=7)
    vertical_arrow(c, xo, y, 30, color=ORANGE, width=1.8)
    text(c, xo, y + 37, "object", size=7, color=ORANGE, align="center")
    # Ray parallel to axis, reflected as if from F.
    arrow(c, (xo, y + 30), (P, y + 30), color=RED, width=1.35, head=5)
    slope = -(30) / f
    left = 35
    y_end = y + 30 + slope * (left - P)
    arrow(c, (P, y + 30), (left, y_end), color=BLUE, width=1.35, head=5)
    # Ray to pole, reflected symmetrically.
    arrow(c, (xo, y + 30), (P, y), color=PURPLE, width=1.35, head=5)
    left2 = 35
    y2 = y + (30 / u) * (left2 - P)
    arrow(c, (P, y), (left2, y2), color=BLUE, width=1.35, head=5)
    # Virtual intersection behind mirror.
    t = u * f / (u + f)
    xi = P + t
    yi = h * f / (u + f)
    # Use h=30 for the actual object height.
    yi = 30 * f / (u + f)
    line(c, (P, y + 30), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
    line(c, (P, y), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
    vertical_arrow(c, xi, y, yi, color=GREEN, width=1.7, dashed=True)
    text(c, xi, y + yi + 8, "virtual image", size=7, color=GREEN, align="center", bg=WHITE)
    text(c, 250, H - 14, "CONVEX MIRROR · REAL OBJECT", size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 8, "Image is always virtual, erect and smaller, between P and F.", size=7.4, color=GREY, align="center")


# ---------------------------------------------------------------------------
# Refraction diagrams
# ---------------------------------------------------------------------------

def refraction_plane(c, H):
    yb = 92
    O = (250, yb)
    c.setFillColor(HexColor("#EDF8FC"))
    c.rect(0, yb, W, H - yb, stroke=0, fill=1)
    c.setFillColor(HexColor("#E7F3EC"))
    c.rect(0, 0, W, yb, stroke=0, fill=1)
    line(c, (20, yb), (480, yb), color=NAVY, width=1.8)
    line(c, (250, 15), (250, 175), color=GREY, width=0.9, dash=[3, 3])
    line(c, O, (400, 12), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, (95, 172), O, color=RED, width=1.8)
    arrow(c, O, (315, 12), color=BLUE, width=1.8)
    c.saveState()
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.0)
    c.arc(215, 57, 285, 127, 90, 61)
    c.arc(215, 57, 285, 127, -90, 37)
    c.restoreState()
    text(c, 205, 130, "i", size=11, color=PURPLE, bold=True)
    text(c, 267, 62, "r", size=11, color=PURPLE, bold=True)
    text(c, 255, 166, "normal", size=7.5, color=GREY)
    text(c, 30, 160, "Air (n1 ≈ 1)", size=8.5, color=NAVY, bold=True)
    text(c, 30, 25, "Glass (n2 > n1)", size=8.5, color=NAVY, bold=True)
    text(c, 340, 32, "towards normal", size=8, color=BLUE, bold=True)
    text(c, 350, 152, "dashed line = original path", size=7.4, color=GREY)
    text(c, 250, H - 14, "REFRACTION: AIR → GLASS", size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 5, "Speed decreases; r < i. Frequency stays unchanged.", size=7.4, color=GREY, align="center")


def glass_slab(c, H):
    top, bottom = 148, 62
    c.setFillColor(LIGHT_BLUE)
    c.rect(90, bottom, 320, top - bottom, stroke=1, fill=1)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.6)
    c.rect(90, bottom, 320, top - bottom, stroke=1, fill=0)
    A = (160, top)
    B = (265, bottom)
    incident_start = (35, 195)
    m = (A[1] - incident_start[1]) / (A[0] - incident_start[0])
    refracted_end = (385, B[1] + m * (385 - B[0]))
    arrow(c, incident_start, A, color=RED, width=1.7)
    arrow(c, A, B, color=BLUE, width=1.7)
    arrow(c, B, refracted_end, color=GREEN, width=1.7)
    # Straight continuation of incident ray.
    ext_end = (390, A[1] + m * (390 - A[0]))
    line(c, A, ext_end, color=GREY, width=0.9, dash=[3, 3])
    # Normals at entry and emergence.
    line(c, (160, 35), (160, 180), color=GREY, width=0.8, dash=[3, 3])
    line(c, (265, 30), (265, 175), color=GREY, width=0.8, dash=[3, 3])
    # Mark lateral shift with a double arrow.
    y_em = B[1] + m * (360 - B[0])
    y_ext = A[1] + m * (360 - A[0])
    line(c, (360, y_em), (360, y_ext), color=PURPLE, width=1.1)
    arrow_head(c, (360, y_em), -math.pi / 2, PURPLE, 5)
    arrow_head(c, (360, y_ext), math.pi / 2, PURPLE, 5)
    text(c, 366, (y_em + y_ext) / 2 - 3, "d", size=10, color=PURPLE, bold=True)
    text(c, 142, 160, "i", size=9, color=PURPLE, bold=True)
    text(c, 174, 112, "r", size=9, color=PURPLE, bold=True)
    text(c, 276, 50, "e", size=9, color=PURPLE, bold=True)
    text(c, 250, 172, "rectangular glass slab", size=8.5, color=NAVY, bold=True, align="center", bg=WHITE)
    text(c, 40, 35, "air", size=8, color=GREY)
    text(c, 425, 35, "air", size=8, color=GREY)
    text(c, 250, H - 12, "GLASS SLAB: i = e AND THE EMERGENT RAY IS PARALLEL", size=8.7, color=NAVY, bold=True, align="center")
    text(c, 250, 4, "d = lateral displacement (sideways shift)", size=7.3, color=GREY, align="center")


# ---------------------------------------------------------------------------
# Lens diagrams
# ---------------------------------------------------------------------------

def lens_terms(c, H):
    y = 90
    axis(c, y, 10, 490, label="")
    centers = [(135, "convex"), (365, "concave")]
    for x, kind in centers:
        f = 55
        pts = [(x - 2 * f, "2F1"), (x - f, "F1"), (x, "O"), (x + f, "F2"), (x + 2 * f, "2F2")]
        lens_shape(c, x, y, 48, 10, kind)
        for px, lab in pts:
            mark(c, px, y, lab, y - 14, size=6.8)
    # Convex convergence and concave divergence.
    arrow(c, (15, 126), (135, 126), color=RED, width=1.1, head=5)
    arrow(c, (135, 126), (190, y), color=BLUE, width=1.1, head=5)
    line(c, (135, 126), (80, y), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, (255, 126), (365, 126), color=RED, width=1.1, head=5)
    arrow(c, (365, 126), (475, 165), color=BLUE, width=1.1, head=5)
    line(c, (365, 126), (310, y), color=GREY, width=0.9, dash=[3, 3])
    text(c, 135, H - 18, "CONVEX / CONVERGING", size=8.8, color=NAVY, bold=True, align="center")
    text(c, 365, H - 18, "CONCAVE / DIVERGING", size=8.8, color=NAVY, bold=True, align="center")
    text(c, 135, 17, "f > 0 ; P > 0", size=7.6, color=GREEN, align="center")
    text(c, 365, 17, "f < 0 ; P < 0", size=7.6, color=RED, align="center")
    text(c, 250, 4, "F1/F2 are focal points; 2F1/2F2 are at twice the focal distance from O.", size=7.2, color=GREY, align="center")


def lens_ray_rules(c, H):
    y = 103
    axis(c, y, 10, 490, label="")
    # Left: convex lens, object at 2F1.
    L, f = 145, 60
    object_top = (25, 145)
    F1, F2, O = L - f, L + f, (L, y)
    lens_shape(c, L, y, 56, 9, "convex")
    for px, lab in ((L - 2 * f, "2F1"), (F1, "F1"), (L, "O"), (F2, "F2"), (L + 2 * f, "2F2")):
        mark(c, px, y, lab, y - 13, size=6.6)
    vertical_arrow(c, 25, y, 40, color=ORANGE, width=1.6)
    arrow(c, object_top, (L, 145), color=RED, width=1.3, head=5)
    arrow(c, (L, 145), (265, 61), color=RED, width=1.3, head=5)
    arrow(c, object_top, (L, 61), color=BLUE, width=1.3, head=5)
    arrow(c, (L, 61), (250, 61), color=BLUE, width=1.3, head=5)
    arrow(c, object_top, O, color=PURPLE, width=1.3, head=5)
    arrow(c, O, (250, 66), color=PURPLE, width=1.3, head=5)
    vertical_arrow(c, 265, y, -42, color=GREEN, width=1.6)
    text(c, 145, H - 17, "CONVEX LENS: THREE STANDARD RAYS", size=8.5, color=NAVY, bold=True, align="center")
    # Right: concave lens.
    L2, f2 = 355, 60
    object_top2 = (255, 145)
    F1b, F2b, Ob = L2 - f2, L2 + f2, (L2, y)
    lens_shape(c, L2, y, 56, 9, "concave")
    for px, lab in ((L2 - 2 * f2, "2F1"), (F1b, "F1"), (L2, "O"), (F2b, "F2"), (L2 + 2 * f2, "2F2")):
        mark(c, px, y, lab, y - 13, size=6.6)
    vertical_arrow(c, 255, y, 40, color=ORANGE, width=1.6)
    arrow(c, object_top2, (L2, 145), color=RED, width=1.3, head=5)
    arrow(c, (L2, 145), (430, 197.5), color=RED, width=1.3, head=5)
    line(c, (L2, 145), (F1b, y), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, object_top2, (L2, 118.75), color=BLUE, width=1.3, head=5)
    arrow(c, (L2, 118.75), (455, 118.75), color=BLUE, width=1.3, head=5)
    line(c, (L2, 118.75), (F2b, y), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, object_top2, Ob, color=PURPLE, width=1.3, head=5)
    arrow(c, Ob, (450, 63.1), color=PURPLE, width=1.3, head=5)
    line(c, (L2, 118.75), (318, 118.75), color=GREY, width=0.9, dash=[3, 3])
    vertical_arrow(c, 318, y, 15.75, color=GREEN, width=1.5, dashed=True)
    text(c, 355, H - 17, "CONCAVE LENS: THREE STANDARD RAYS", size=8.5, color=NAVY, bold=True, align="center")
    # Legend.
    legend(c, 18, 23, RED, "1", "parallel ray")
    legend(c, 145, 23, BLUE, "2", "focus ray")
    legend(c, 265, 23, PURPLE, "3", "optical-centre ray")
    legend(c, 405, 23, GREEN, "4", "image")
    text(c, 250, 6, "Dashed lines are backward extensions; use any two rays to locate an image.", size=7.1, color=GREY, align="center")


def draw_convex_case(c, y0, u, title, result, virtual=False):
    c.saveState()
    c.translate(0, y0)
    y = 66
    L, f, h = 230, 55, 20
    F1, F2 = L - f, L + f
    axis(c, y, 12, 488, label="")
    lens_shape(c, L, y, 57, 9, "convex")
    for px, lab in ((L - 2 * f, "2F1"), (F1, "F1"), (L, "O"), (F2, "F2"), (L + 2 * f, "2F2")):
        mark(c, px, y, lab, y - 13, size=6.5)
    xo = L - u
    vertical_arrow(c, xo, y, h, color=ORANGE, width=1.7)
    text(c, xo, y + h + 7, "object", size=6.8, color=ORANGE, align="center")
    t = f * u / (u - f)
    xi = L + t
    yi = -h * f / (u - f)
    if not virtual:
        arrow(c, (xo, y + h), (L, y + h), color=RED, width=1.25, head=5)
        arrow(c, (L, y + h), (xi, y + yi), color=BLUE, width=1.25, head=5)
        arrow(c, (xo, y + h), (L, y), color=PURPLE, width=1.25, head=5)
        arrow(c, (L, y), (xi, y + yi), color=PURPLE, width=1.25, head=5)
        vertical_arrow(c, xi, y, yi, color=GREEN, width=1.7)
        text(c, xi, y + yi - 13, "image", size=6.8, color=GREEN, align="center", bg=WHITE)
    else:
        arrow(c, (xo, y + h), (L, y + h), color=RED, width=1.25, head=5)
        arrow(c, (L, y + h), (400, y + h - (h / f) * 170), color=BLUE, width=1.25, head=5)
        arrow(c, (xo, y + h), (L, y), color=PURPLE, width=1.25, head=5)
        arrow(c, (L, y), (330, y - (h / u) * 100), color=PURPLE, width=1.25, head=5)
        line(c, (L, y + h), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
        line(c, (xo, y + h), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
        vertical_arrow(c, xi, y, yi, color=GREEN, width=1.6, dashed=True)
        text(c, xi, y + yi + 4, "virtual image", size=6.8, color=GREEN, align="center", bg=WHITE)
    text(c, 250, 126, title, size=8.3, color=NAVY, bold=True, align="center")
    text(c, 250, 4, result, size=7.0, color=GREY, align="center")
    c.restoreState()


def convex_lens_cases(c, H):
    draw_convex_case(c, 272, 160, "OBJECT BEYOND 2F1", "Real, inverted, diminished image between F2 and 2F2")
    line(c, (15, 272), (485, 272), color=HexColor("#DCE5EA"), width=0.7)
    draw_convex_case(c, 136, 80, "OBJECT BETWEEN F1 AND 2F1", "Real, inverted, enlarged image beyond 2F2")
    line(c, (15, 136), (485, 136), color=HexColor("#DCE5EA"), width=0.7)
    draw_convex_case(c, 0, 35, "OBJECT BETWEEN F1 AND O", "Virtual, erect, enlarged image on the object side", virtual=True)


def concave_lens_case(c, H):
    y = 90
    L, f, u, h = 300, 70, 200, 35
    F1, F2 = L - f, L + f
    xo = L - u
    axis(c, y, 12, 488, label="")
    lens_shape(c, L, y, 60, 11, "concave")
    for px, lab in ((F1, "F1"), (L, "O"), (F2, "F2")):
        mark(c, px, y, lab, y - 14, size=7)
    vertical_arrow(c, xo, y, h, color=ORANGE, width=1.8)
    text(c, xo, y + h + 7, "object", size=7, color=ORANGE, align="center")
    # Parallel ray and optical-centre ray.
    arrow(c, (xo, y + h), (L, y + h), color=RED, width=1.35, head=5)
    arrow(c, (L, y + h), (420, y + h + (h / f) * 120), color=BLUE, width=1.35, head=5)
    line(c, (L, y + h), (F1, y), color=GREY, width=0.9, dash=[3, 3])
    arrow(c, (xo, y + h), (L, y), color=PURPLE, width=1.35, head=5)
    arrow(c, (L, y), (450, y - (h / u) * 150), color=PURPLE, width=1.35, head=5)
    t = -u * f / (u + f)
    xi = L + t
    yi = h * f / (u + f)
    line(c, (L, y + h), (xi, y + yi), color=GREY, width=1.0, dash=[3, 3])
    vertical_arrow(c, xi, y, yi, color=GREEN, width=1.7, dashed=True)
    text(c, xi, y + yi + 8, "virtual image", size=7, color=GREEN, align="center", bg=WHITE)
    text(c, 250, H - 14, "CONCAVE LENS · REAL OBJECT", size=9, color=NAVY, bold=True, align="center")
    text(c, 250, 8, "Image is always virtual, erect and smaller, between O and F1.", size=7.4, color=GREY, align="center")


DIAGRAMS = {
    "reflection_plane": reflection_plane,
    "sign_convention": sign_convention,
    "mirror_concave_focus": mirror_concave_focus,
    "mirror_convex_focus": mirror_convex_focus,
    "concave_beyond_c": concave_beyond_c,
    "concave_between_c_f": concave_between_c_f,
    "concave_inside_f": concave_inside_f,
    "convex_mirror_case": convex_mirror_case,
    "refraction_plane": refraction_plane,
    "glass_slab": glass_slab,
    "lens_terms": lens_terms,
    "lens_ray_rules": lens_ray_rules,
    "convex_lens_cases": convex_lens_cases,
    "concave_lens_case": concave_lens_case,
}
