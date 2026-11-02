#!/usr/bin/env python3
"""Convert a Markdown notes file into a nicely formatted PDF using ReportLab.

Supports: headings (#, ##, ###), paragraphs with **bold** / *italic*, bullet
lists (incl. one level of nesting), pipe tables, fenced code blocks (rendered
as boxed monospace lines), horizontal rules and blockquotes (rendered as
indented note lines).

Usage:  python3 scripts/make_notes_pdf.py <input.md> <output.pdf>
"""
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, Preformatted, KeepTogether, HRFlowable,
)

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DVS", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVS-Bold", FONT_DIR + "DejaVuSans-Bold.ttf"))
# No oblique faces installed; fall back to regular/bold for italic styles.
pdfmetrics.registerFont(TTFont("DVS-Italic", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVS-BoldItalic", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVMono", FONT_DIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DVMono-Bold", FONT_DIR + "DejaVuSansMono-Bold.ttf"))
pdfmetrics.registerFontFamily("DVS", normal="DVS", bold="DVS-Bold",
                              italic="DVS-Italic", boldItalic="DVS-BoldItalic")

# ---------------------------------------------------------------- styles
INK = colors.HexColor("#1a2332")
ACCENT = colors.HexColor("#0b5ed7")      # headings
ACCENT2 = colors.HexColor("#e8f0fe")     # heading band
NOTE_BG = colors.HexColor("#fff8e1")
NOTE_BD = colors.HexColor("#e6b800")
CODE_BG = colors.HexColor("#f1f4f9")
CODE_BD = colors.HexColor("#b9c6d8")
TBL_HEAD = colors.HexColor("#0b5ed7")
TBL_ROW = colors.HexColor("#eef3fb")
TBL_GRID = colors.HexColor("#b9c6d8")

S = {
    "title": ParagraphStyle("title", fontName="DVS-Bold", fontSize=20, leading=26,
                            textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4),
    "subtitle": ParagraphStyle("subtitle", fontName="DVS-Italic", fontSize=11.5,
                               leading=15, textColor=colors.HexColor("#4a5568"),
                               alignment=TA_CENTER, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="DVS-Bold", fontSize=15, leading=19,
                         textColor=colors.white, backColor=ACCENT, borderPadding=(4, 6, 5, 6),
                         spaceBefore=14, spaceAfter=8, leftIndent=0),
    "h2": ParagraphStyle("h2", fontName="DVS-Bold", fontSize=12.5, leading=16,
                         textColor=ACCENT, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="DVS-Bold", fontSize=11, leading=14,
                         textColor=INK, spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="DVS", fontSize=10, leading=14.5,
                           textColor=INK, spaceAfter=6, alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="DVS", fontSize=10, leading=14.5,
                             textColor=INK, spaceAfter=3, leftIndent=14, bulletIndent=4),
    "bullet2": ParagraphStyle("bullet2", fontName="DVS", fontSize=9.5, leading=13.5,
                              textColor=INK, spaceAfter=2, leftIndent=28, bulletIndent=18),
    "note": ParagraphStyle("note", fontName="DVS-Italic", fontSize=9.5, leading=13.5,
                           textColor=colors.HexColor("#6b5300"), leftIndent=10,
                           rightIndent=6, spaceAfter=6, backColor=NOTE_BG,
                           borderColor=NOTE_BD, borderWidth=0.8, borderPadding=(5, 7, 5, 7)),
    "code": ParagraphStyle("code", fontName="DVMono", fontSize=8.8, leading=12.5,
                           textColor=INK),
    "cell": ParagraphStyle("cell", fontName="DVS", fontSize=9, leading=12, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="DVS-Bold", fontSize=9, leading=12,
                            textColor=colors.white),
}


def inline(text):
    """Convert **bold** and *italic* markdown to reportlab XML tags."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # bold first, then italic (order matters)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    return text


def make_table(rows):
    data = []
    for i, row in enumerate(rows):
        style = S["cellb"] if i == 0 else S["cell"]
        data.append([Paragraph(inline(c.strip()), style) for c in row])
    n_cols = len(rows[0])
    widths = [A4[0] - 30 * mm - 8 * mm]  # fallback
    usable = A4[0] - 30 * mm
    widths = [usable / n_cols] * n_cols
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TBL_HEAD),
        ("GRID", (0, 0), (-1, -1), 0.6, TBL_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            style.append(("BACKGROUND", (0, r), (-1, r), TBL_ROW))
    t.setStyle(TableStyle(style))
    return t


def convert(md_text):
    story = []
    lines = md_text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code block
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            box = Table([[Preformatted("\n".join(code_lines), S["code"])]],
                        colWidths=[A4[0] - 30 * mm])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.8, CODE_BD),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 3))
            story.append(box)
            story.append(Spacer(1, 6))
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c3cede"),
                                    spaceBefore=4, spaceAfter=8))
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = inline(m.group(2).strip())
            if level == 1:
                story.append(Paragraph(text, S["h1"]))
            elif level == 2:
                story.append(Paragraph(text, S["h2"]))
            else:
                story.append(Paragraph(text, S["h3"]))
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                row = [c for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            # drop separator row (---)
            rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in r)]
            story.append(Spacer(1, 3))
            story.append(make_table(rows))
            story.append(Spacer(1, 8))
            continue

        # blockquote / note
        if stripped.startswith(">"):
            note_text = inline(stripped.lstrip(">").strip())
            story.append(Paragraph("Note: " + note_text, S["note"]))
            i += 1
            continue

        # bullets (with one nesting level) and numbered lists
        m = re.match(r"^(\s*)(?:-|\d+\.)\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            style = S["bullet2"] if indent >= 2 else S["bullet"]
            bullet = "•" if indent < 2 else "–"
            story.append(Paragraph(inline(m.group(2).strip()), style, bulletText=bullet))
            i += 1
            continue

        # blank line
        if not stripped:
            i += 1
            continue

        # normal paragraph (join wrapped lines until blank/other block)
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(("#", "|", ">", "-", "```")) \
                and not re.match(r"^\s*\d+\.\s", lines[i]) \
                and not re.fullmatch(r"-{3,}|\*{3,}", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        text = inline(" ".join(para))
        if text.startswith("Class 10 Chemistry"):
            story.append(Paragraph(text, S["title"]))
        elif text.startswith("Simple & Detailed"):
            story.append(Paragraph(text, S["subtitle"]))
        else:
            story.append(Paragraph(text, S["body"]))
    return story


# ---------------------------------------------------------------- page deco
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # header
    canvas.setFont("DVS-Bold", 8.5)
    canvas.setFillColor(colors.HexColor("#5a6b82"))
    canvas.drawString(15 * mm, h - 11 * mm, "Class 10 Chemistry  •  Chapter 3: Metals and Non-Metals")
    canvas.drawRightString(w - 15 * mm, h - 11 * mm, "NCERT Simple Notes")
    canvas.setStrokeColor(colors.HexColor("#c3cede"))
    canvas.setLineWidth(0.7)
    canvas.line(15 * mm, h - 13 * mm, w - 15 * mm, h - 13 * mm)
    # footer
    canvas.line(15 * mm, 13 * mm, w - 15 * mm, 13 * mm)
    canvas.setFont("DVS", 8.5)
    canvas.drawString(15 * mm, 9 * mm, "Prepared for exam revision")
    canvas.drawRightString(w - 15 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        md = f.read()

    doc = BaseDocTemplate(dst, pagesize=A4,
                          leftMargin=15 * mm, rightMargin=15 * mm,
                          topMargin=18 * mm, bottomMargin=18 * mm,
                          title="Class 10 Chemistry Ch 3 - Metals and Non-Metals Notes",
                          author="Study Notes")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=on_page)])

    story = convert(md)
    doc.build(story)
    print(f"✅ PDF created: {dst}")


if __name__ == "__main__":
    main()
