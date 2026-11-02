"""Build a polished, self-contained Class 10 Light chapter PDF.

Outputs:
  study-notes/light-reflection-refraction/class10-light-reflection-refraction-ncert-notes.pdf
  study-notes/light-reflection-refraction/class10-light-reflection-refraction-ncert-notes.md
  study-notes/light-reflection-refraction/download.html
"""

from __future__ import annotations

import hashlib
import html
import os
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from light_notes_content_1 import BLOCKS as PART_1  # noqa: E402
from light_notes_content_2 import BLOCKS as PART_2  # noqa: E402
from light_notes_content_3 import BLOCKS as PART_3  # noqa: E402
from light_notes_diagrams import DIAGRAMS, W as DESIGN_W  # noqa: E402
import light_notes_diagrams as dg  # noqa: E402

CONTENT = PART_1 + PART_2 + PART_3
OUT_DIR = ROOT / "study-notes" / "light-reflection-refraction"
PDF_PATH = OUT_DIR / "class10-light-reflection-refraction-ncert-notes.pdf"
MD_PATH = OUT_DIR / "class10-light-reflection-refraction-ncert-notes.md"
HTML_PATH = OUT_DIR / "download.html"

PAGE_W, PAGE_H = A4
MARGIN = 45
CONTENT_W = PAGE_W - 2 * MARGIN

NAVY = colors.HexColor("#17324D")
INK = colors.HexColor("#243746")
TEAL = colors.HexColor("#008CA0")
GREEN = colors.HexColor("#238B57")
ORANGE = colors.HexColor("#D9800E")
RED = colors.HexColor("#C94A3D")
PURPLE = colors.HexColor("#7652A8")
GREY = colors.HexColor("#6F7D88")
LIGHT_BLUE = colors.HexColor("#EAF6FA")
LIGHT_GREEN = colors.HexColor("#ECF7F0")
LIGHT_YELLOW = colors.HexColor("#FFF7E2")
LIGHT_GREY = colors.HexColor("#F3F6F8")
RULE = colors.HexColor("#DCE5EA")
WHITE = colors.white

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono", str(FONT_DIR / "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono-Bold", str(FONT_DIR / "DejaVuSansMono-Bold.ttf")))
pdfmetrics.registerFontFamily(
    "DejaVu",
    normal="DejaVu",
    bold="DejaVu-Bold",
    italic="DejaVu",
    boldItalic="DejaVu-Bold",
)


def inline_markup(value: str) -> str:
    """Convert a small, safe Markdown subset to ReportLab paragraph markup."""
    s = html.escape(value, quote=False)
    s = re.sub(
        r"`([^`]+)`",
        r'<font face="DejaVuMono" color="#007681" size="8.6">\1</font>',
        s,
    )
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    return s


styles = {
    "Body": ParagraphStyle(
        "Body", fontName="DejaVu", fontSize=9.1, leading=13.2,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=5,
        allowWidows=0, allowOrphans=0,
    ),
    "Bullet": ParagraphStyle(
        "Bullet", fontName="DejaVu", fontSize=8.9, leading=12.6,
        alignment=TA_LEFT, textColor=INK, leftIndent=15, bulletIndent=3,
        spaceAfter=2.5, allowWidows=0, allowOrphans=0,
    ),
    "Number": ParagraphStyle(
        "Number", fontName="DejaVu", fontSize=8.9, leading=12.7,
        alignment=TA_JUSTIFY, textColor=INK, leftIndent=20, bulletIndent=2,
        spaceAfter=3, allowWidows=0, allowOrphans=0,
    ),
    "H1": ParagraphStyle(
        "H1", fontName="DejaVu-Bold", fontSize=15, leading=19,
        textColor=NAVY, spaceBefore=11, spaceAfter=7, keepWithNext=1,
    ),
    "H2": ParagraphStyle(
        "H2", fontName="DejaVu-Bold", fontSize=11.5, leading=15,
        textColor=TEAL, spaceBefore=9, spaceAfter=5, keepWithNext=1,
    ),
    "H3": ParagraphStyle(
        "H3", fontName="DejaVu-Bold", fontSize=9.7, leading=13,
        textColor=PURPLE, spaceBefore=7, spaceAfter=3, keepWithNext=1,
    ),
    "CoverHeading": ParagraphStyle(
        "CoverHeading", fontName="DejaVu-Bold", fontSize=20, leading=25,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "TOCIntro": ParagraphStyle(
        "TOCIntro", fontName="DejaVu", fontSize=9, leading=13.2,
        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8,
    ),
    "Caption": ParagraphStyle(
        "Caption", fontName="DejaVu", fontSize=7.6, leading=10.5,
        textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8,
    ),
    "TableTitle": ParagraphStyle(
        "TableTitle", fontName="DejaVu-Bold", fontSize=8.2, leading=11,
        textColor=TEAL, alignment=TA_CENTER, spaceBefore=5, spaceAfter=4,
        keepWithNext=1,
    ),
    "TableHeader": ParagraphStyle(
        "TableHeader", fontName="DejaVu-Bold", fontSize=8.0, leading=10.5,
        textColor=WHITE, alignment=TA_LEFT,
    ),
    "TableCell": ParagraphStyle(
        "TableCell", fontName="DejaVu", fontSize=8.0, leading=10.8,
        textColor=INK, alignment=TA_LEFT,
    ),
    "CalloutTitle": ParagraphStyle(
        "CalloutTitle", fontName="DejaVu-Bold", fontSize=9.0, leading=12,
        textColor=NAVY,
    ),
    "CalloutBody": ParagraphStyle(
        "CalloutBody", fontName="DejaVu", fontSize=8.7, leading=12.2,
        textColor=INK, alignment=TA_JUSTIFY,
    ),
    "Formula": ParagraphStyle(
        "Formula", fontName="DejaVuMono-Bold", fontSize=9.4, leading=14,
        textColor=NAVY, alignment=TA_CENTER,
    ),
    "FormulaLabel": ParagraphStyle(
        "FormulaLabel", fontName="DejaVu", fontSize=7.4, leading=10,
        textColor=GREY, alignment=TA_CENTER,
    ),
}


class VecDiagram(Flowable):
    """Wrap a vector drawing function as a scalable Platypus flowable."""

    def __init__(self, draw_func, design_height: int):
        super().__init__()
        self.draw_func = draw_func
        self.design_height = float(design_height)
        self.design_width = float(DESIGN_W)
        self.scale = 1.0
        self.width = self.design_width
        self.height = self.design_height

    def wrap(self, availWidth, availHeight):
        w = min(self.design_width, availWidth)
        self.scale = w / self.design_width
        self.width = w
        self.height = self.design_height * self.scale
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(self.scale, self.scale)
        self.draw_func(c, self.design_height)
        c.restoreState()


class HRFlowable(Flowable):
    def __init__(self, width=CONTENT_W):
        super().__init__()
        self.width = width
        self.height = 13

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(RULE)
        c.setLineWidth(0.7)
        c.line(0, 7, self.width, 7)
        c.setFillColor(TEAL)
        p = c.beginPath()
        x = self.width / 2
        p.moveTo(x, 11)
        p.lineTo(x + 4, 7)
        p.lineTo(x, 3)
        p.lineTo(x - 4, 7)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.restoreState()


def para(value, style="Body"):
    return Paragraph(inline_markup(value), styles[style])


def make_table(block):
    data = block["rows"]
    widths = block.get("widths")
    caption = block.get("caption")
    fs = float(block.get("font_size", 8.2))
    cell_style = ParagraphStyle(
        "TableCellDynamic", parent=styles["TableCell"], fontSize=fs, leading=fs + 2.7,
    )
    header_style = ParagraphStyle(
        "TableHeaderDynamic", parent=styles["TableHeader"], fontSize=fs, leading=fs + 2.7,
    )
    rows = [[Paragraph(inline_markup(str(x)), header_style) for x in block["headers"]]]
    rows += [[Paragraph(inline_markup(str(x)), cell_style) for x in row] for row in data]
    if widths:
        scale = CONTENT_W / float(sum(widths))
        col_widths = [w * scale for w in widths]
    else:
        col_widths = [CONTENT_W / len(block["headers"])] * len(block["headers"])
    tbl = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="CENTER", splitByRow=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, TEAL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    out = []
    if caption:
        out.append(Paragraph(inline_markup(caption), styles["TableTitle"]))
    out.append(tbl)
    out.append(Spacer(1, 8))
    return out


def make_callout(block):
    kind = block["kind"]
    if kind == "warn":
        bg, edge, accent = LIGHT_YELLOW, ORANGE, RED
    elif kind == "tip":
        bg, edge, accent = LIGHT_GREEN, GREEN, GREEN
    else:
        bg, edge, accent = LIGHT_BLUE, TEAL, TEAL
    title = block["title"] or ("Important" if kind == "key" else "Study tip")
    title_para = Paragraph(
        f'<font color="#{accent.hexval()[2:]}"><b>{inline_markup(title)}</b></font>',
        styles["CalloutTitle"],
    )
    body_para = Paragraph(inline_markup(block["text"]), styles["CalloutBody"])
    tbl = Table([[title_para], [body_para]], colWidths=[CONTENT_W], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, edge),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return [Spacer(1, 2), tbl, Spacer(1, 8)]


def make_formula(block):
    main = Paragraph(inline_markup(block["text"]), styles["Formula"])
    rows = [[main]]
    if block.get("label"):
        rows.append([Paragraph(inline_markup(block["label"]), styles["FormulaLabel"])])
    tbl = Table(rows, colWidths=[CONTENT_W], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.7, TEAL),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2 if len(rows) > 1 else 7),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 2), tbl, Spacer(1, 7)]


def blocks_to_story(blocks):
    story = []
    for kind, data in blocks:
        if kind == "h1":
            story.append(para(data["text"], "H1"))
        elif kind == "h2":
            story.append(para(data["text"], "H2"))
        elif kind == "h3":
            story.append(para(data["text"], "H3"))
        elif kind == "p":
            story.append(para(data["text"], "Body"))
        elif kind == "bullets":
            for item in data["items"]:
                story.append(Paragraph(inline_markup(item), styles["Bullet"], bulletText="•"))
            story.append(Spacer(1, 4))
        elif kind == "numbers":
            for i, item in enumerate(data["items"], 1):
                story.append(Paragraph(inline_markup(item), styles["Number"], bulletText=f"{i}."))
            story.append(Spacer(1, 4))
        elif kind == "callout":
            story.extend(make_callout(data))
        elif kind == "formula":
            story.extend(make_formula(data))
        elif kind == "table":
            story.extend(make_table(data))
        elif kind == "diagram":
            name = data["name"]
            if name not in DIAGRAMS:
                raise KeyError(f"Missing diagram function: {name}")
            d = VecDiagram(DIAGRAMS[name], int(data.get("height", 170)))
            caption = Paragraph(inline_markup(data["caption"]), styles["Caption"])
            story.append(KeepTogether([d, caption]))
            story.append(Spacer(1, 3))
        elif kind == "spacer":
            story.append(Spacer(1, data["height"]))
        elif kind == "pagebreak":
            story.append(PageBreak())
        elif kind == "sectionbreak":
            story.append(HRFlowable())
        else:
            raise ValueError(f"Unknown content block: {kind}")
    return story


# ---------------------------------------------------------------------------
# Page furniture
# ---------------------------------------------------------------------------

def cover_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # A soft optical-ray illustration in the lower half.
    c.setFillColor(colors.HexColor("#1E425F"))
    c.rect(0, 0, PAGE_W, 390, stroke=0, fill=1)
    focus = (500, 250)
    for i, yy in enumerate([130, 180, 230, 280, 330, 380]):
        col = colors.HexColor("#5FD1E0") if i % 2 == 0 else colors.HexColor("#FFC46B")
        c.setStrokeColor(col)
        c.setLineWidth(1.4)
        c.line(35, yy, 385, yy)
        c.line(385, yy, focus[0], focus[1])
        dg.arrow_head(c, (385, yy), 0, col, 5)
    dg.lens_shape(c, 385, 250, 165, 22, "convex")
    c.setFillColor(colors.HexColor("#FFC46B"))
    c.circle(focus[0], focus[1], 4.5, stroke=0, fill=1)
    c.setFont("DejaVu-Bold", 9)
    c.setFillColor(colors.HexColor("#8DDDE8"))
    c.drawString(52, 770, "CLASS 10 SCIENCE  •  NCERT / CBSE")
    c.drawRightString(PAGE_W - 52, 770, "COMPLETE CHAPTER NOTES")
    c.setStrokeColor(colors.HexColor("#8DDDE8"))
    c.setLineWidth(0.8)
    c.line(52, 758, PAGE_W - 52, 758)

    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 30)
    c.drawString(52, 690, "Light — Reflection")
    c.drawString(52, 650, "& Refraction")
    c.setFont("DejaVu", 14)
    c.setFillColor(colors.HexColor("#CFE9F1"))
    c.drawString(54, 616, "Complete notes in simple English")
    c.setFont("DejaVu-Bold", 9.5)
    c.setFillColor(colors.HexColor("#FFC46B"))
    c.drawString(54, 585, "CHAPTER 9 IN THE CURRENT NCERT BOOK  ·  CHAPTER 10 IN SOME OLDER EDITIONS")

    features = [
        "Easy explanations", "Ray diagrams", "Formula sheet", "Solved numericals",
        "Practical work", "Practice + answers", "10-minute revision",
    ]
    x, y = 52, 535
    c.setFont("DejaVu", 8.5)
    for feat in features:
        w = pdfmetrics.stringWidth(feat, "DejaVu", 8.5) + 18
        if x + w > PAGE_W - 52:
            x = 52
            y -= 30
        c.setFillColor(colors.HexColor("#24506F"))
        c.roundRect(x, y, w, 22, 8, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.drawString(x + 9, y + 7, feat)
        x += w + 8

    c.setFont("DejaVu", 9)
    c.setFillColor(colors.HexColor("#CFE9F1"))
    c.drawString(52, 55, "Original study guide • NCERT/CBSE aligned")
    c.drawRightString(PAGE_W - 52, 55, "A4 • searchable • clickable contents")
    c.restoreState()


def later_pages(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 27, PAGE_W, 27, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 7.8)
    c.drawString(MARGIN, PAGE_H - 18, "CLASS 10 SCIENCE  •  LIGHT — REFLECTION & REFRACTION")
    c.setFont("DejaVu", 7.8)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 18, "NCERT / CBSE NOTES")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.line(MARGIN, 36, PAGE_W - MARGIN, 36)
    c.setFillColor(GREY)
    c.setFont("DejaVu", 7.5)
    c.drawString(MARGIN, 23, "Original notes • simple English • exam-focused")
    c.drawRightString(PAGE_W - MARGIN, 23, f"Page {c.getPageNumber()}")
    c.restoreState()


class NotesDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outline_seq = 0

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name not in ("H1", "H2"):
            return
        level = 0 if name == "H1" else 1
        title = flowable.getPlainText()
        # A deterministic key is essential: multiBuild compares TOC entries
        # between passes, and changing keys would never converge.
        key = "section-" + hashlib.md5(f"{level}:{title}".encode("utf-8")).hexdigest()[:12]
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(title, key, level=level, closed=False)
        # Keep the printed contents to one clean page of main sections.
        # Subsections remain available in the PDF bookmark/outlines panel.
        if level == 0:
            self.notify("TOCEntry", (level, title, self.page, key))


# ---------------------------------------------------------------------------
# Markdown and download page
# ---------------------------------------------------------------------------

def md_cell(value):
    return str(value).replace("|", "\\|")


def write_markdown():
    lines = [
        "# Class 10 Light — Reflection and Refraction",
        "",
        "**Complete NCERT/CBSE notes in simple English**  ",
        "Current NCERT: Chapter 9 · Some older editions: Chapter 10",
        "",
        "> The diagrams are included in the matching PDF. This Markdown file is a searchable, editable text version.",
        "",
    ]
    for kind, data in CONTENT:
        if kind == "h1":
            lines += ["", f"## {data['text']}", ""]
        elif kind == "h2":
            lines += ["", f"### {data['text']}", ""]
        elif kind == "h3":
            lines += ["", f"#### {data['text']}", ""]
        elif kind == "p":
            lines += [data["text"], ""]
        elif kind == "bullets":
            lines += [f"- {x}" for x in data["items"]] + [""]
        elif kind == "numbers":
            lines += [f"{i}. {x}" for i, x in enumerate(data["items"], 1)] + [""]
        elif kind == "callout":
            label = {"key": "Key point", "tip": "Study tip", "warn": "Warning"}.get(data["kind"], "Note")
            title = data["title"] or label
            lines += [f"> **{label}: {title}** — {data['text']}", ""]
        elif kind == "formula":
            lines += [f"> **Formula:** `{data['text']}`"]
            if data.get("label"):
                lines.append(f"> {data['label']}")
            lines.append("")
        elif kind == "table":
            if data.get("caption"):
                lines += [f"*{data['caption']}*", ""]
            headers = [md_cell(x) for x in data["headers"]]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in data["rows"]:
                lines.append("| " + " | ".join(md_cell(x) for x in row) + " |")
            lines.append("")
        elif kind == "diagram":
            lines += [f"> **[Diagram]** {data['caption']}", ""]
        elif kind in ("pagebreak", "sectionbreak"):
            lines += ["", "---", ""]
    MD_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_download_page():
    size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
    page_count = len(PdfReader(str(PDF_PATH)).pages)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Download — Class 10 Light Notes PDF</title>
  <style>
    :root {{ --navy:#17324d; --teal:#008ca0; --paper:#f7fafc; --ink:#243746; --line:#dce5ea; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Arial,Helvetica,sans-serif; background:var(--paper); color:var(--ink); }}
    header {{ background:var(--navy); color:white; padding:28px 20px; }}
    .wrap {{ max-width:980px; margin:0 auto; }}
    .eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#8ddde8; font-weight:700; }}
    h1 {{ margin:8px 0 6px; font-size:clamp(25px,4vw,38px); line-height:1.15; }}
    .sub {{ color:#d3e9f2; margin:0; font-size:16px; }}
    main {{ max-width:980px; margin:0 auto; padding:28px 20px 45px; }}
    .card {{ background:white; border:1px solid var(--line); border-radius:16px; box-shadow:0 10px 30px rgba(23,50,77,.08); padding:22px; }}
    .buttons {{ display:flex; flex-wrap:wrap; gap:12px; margin:18px 0 20px; }}
    a.button {{ display:inline-flex; align-items:center; justify-content:center; gap:8px; text-decoration:none; border-radius:10px; padding:13px 18px; font-weight:700; font-size:15px; }}
    .primary {{ background:var(--teal); color:white; }}
    .secondary {{ background:#eef6f8; color:var(--navy); border:1px solid #b9dce3; }}
    .primary:hover {{ background:#007689; }}
    .secondary:hover {{ background:#e2f1f5; }}
    .meta {{ display:flex; flex-wrap:wrap; gap:9px; margin:0 0 18px; padding:0; list-style:none; }}
    .meta li {{ background:#f1f6f8; border:1px solid var(--line); border-radius:999px; padding:7px 12px; font-size:13px; }}
    .tip {{ background:#fff7e2; border-left:4px solid #e28a17; padding:12px 14px; border-radius:8px; font-size:14px; line-height:1.5; }}
    iframe {{ width:100%; height:72vh; min-height:520px; border:1px solid var(--line); border-radius:12px; background:white; }}
    footer {{ text-align:center; color:#6f7d88; font-size:13px; padding:18px; }}
    @media (max-width:600px) {{ iframe {{ height:65vh; min-height:420px; }} a.button {{ width:100%; }} }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">Class 10 Science · NCERT / CBSE</div>
      <h1>Light — Reflection &amp; Refraction</h1>
      <p class="sub">Complete chapter notes in simple English</p>
    </div>
  </header>
  <main>
    <section class="card">
      <h2 style="margin-top:0;color:var(--navy);">Download your PDF</h2>
      <p>The file is a self-contained, searchable A4 PDF. Use the green button below to save it to your device.</p>
      <div class="buttons">
        <a class="button primary" href="./class10-light-reflection-refraction-ncert-notes.pdf" download>
          ⬇ Download PDF
        </a>
        <a class="button secondary" href="./class10-light-reflection-refraction-ncert-notes.pdf" target="_blank" rel="noopener">
          Open PDF in new tab
        </a>
        <a class="button secondary" href="./class10-light-reflection-refraction-ncert-notes.md" download>
          Download text version (.md)
        </a>
      </div>
      <ul class="meta">
        <li>{page_count} pages</li>
        <li>{size_mb:.2f} MB</li>
        <li>Searchable text</li>
        <li>Clickable contents</li>
        <li>Vector ray diagrams</li>
        <li>Solved numericals + answer key</li>
      </ul>
      <div class="tip"><strong>If the download does not start:</strong> right-click the green button and choose “Save link as…”, or open the PDF in a new tab and use your browser’s download icon.</div>
      <h3 style="margin:24px 0 10px;color:var(--navy);">Preview</h3>
      <iframe src="./class10-light-reflection-refraction-ncert-notes.pdf#view=FitH" title="PDF preview"></iframe>
    </section>
  </main>
  <footer>Original study notes · Not a copy of the NCERT textbook</footer>
</body>
</html>
"""
    HTML_PATH.write_text(html_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = NotesDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=48,
        bottomMargin=45,
        title="Class 10 Light — Reflection and Refraction | NCERT/CBSE Complete Notes",
        author="Arena.ai study notes",
        subject="CBSE Class 10 Science Chapter: Light — Reflection and Refraction",
        keywords="Class 10, CBSE, NCERT, Light, Reflection, Refraction, mirrors, lenses, ray diagrams, numericals",
        creator="ReportLab",
    )

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOCLevel0", fontName="DejaVu-Bold", fontSize=9.4, leading=17,
            textColor=NAVY, leftIndent=0, firstLineIndent=0, spaceBefore=3,
        ),
        ParagraphStyle(
            "TOCLevel1", fontName="DejaVu", fontSize=8.3, leading=13,
            textColor=INK, leftIndent=16, firstLineIndent=0,
        ),
    ]

    story = [
        Spacer(1, 1),
        PageBreak(),
        Paragraph("Contents", styles["CoverHeading"]),
        Paragraph(
            "Use the clickable entries below to jump to any of the 15 main sections. "
            "Open the PDF bookmarks panel for every subsection. Each section has simple explanations, "
            "tables, diagrams, formulas and exam-focused tips.",
            styles["TOCIntro"],
        ),
        toc,
        PageBreak(),
    ]
    story.extend(blocks_to_story(CONTENT))
    doc.multiBuild(story, onFirstPage=cover_page, onLaterPages=later_pages)

    reader = PdfReader(str(PDF_PATH))
    page_count = len(reader.pages)
    extracted = []
    short_pages = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        extracted.append(text)
        if len(text.strip()) < 80:
            short_pages.append((i, len(text.strip())))
    all_text = "\n".join(extracted)
    checks = [
        "Chapter roadmap", "Spherical mirrors", "Mirror formula", "Refraction of light",
        "Spherical lenses", "Power of a lens", "Answer key", "Final checklist",
    ]
    missing = [x for x in checks if x.lower() not in all_text.lower()]
    if missing:
        raise RuntimeError(f"PDF text validation missing headings: {missing}")
    if page_count < 20:
        raise RuntimeError(f"Unexpectedly short PDF: {page_count} pages")
    if short_pages:
        print(f"Warning: pages with very little extractable text: {short_pages}")
    print(f"Built PDF: {PDF_PATH}")
    print(f"Pages: {page_count}; size: {PDF_PATH.stat().st_size / 1024:.0f} KiB")
    print(f"Extracted characters: {len(all_text)}")
    return page_count


def main():
    page_count = build_pdf()
    write_markdown()
    write_download_page()
    print(f"Built Markdown: {MD_PATH}")
    print(f"Built download page: {HTML_PATH}")
    print(f"Total pages: {page_count}")


if __name__ == "__main__":
    main()
