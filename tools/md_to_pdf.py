#!/usr/bin/env python3
"""Convert a Markdown study-notes file into a nicely typeset PDF.

Usage: python md_to_pdf.py input.md output.pdf

Handles: h1-h4, paragraphs, bold/italic/code inline, nested bullets,
numbered lists, GFM tables, fenced code blocks, blockquotes, hr.
Requires: reportlab, DejaVu fonts (glyph coverage for subscripts / arrows / box drawing).
"""

import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageTemplate, Paragraph, Preformatted, Spacer,
                                Table, TableStyle)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Body", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FONT_DIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold",
                              italic="Body", boldItalic="Body-Bold")

ACCENT = colors.HexColor("#0f6b52")        # deep green
ACCENT_DARK = colors.HexColor("#0a4a39")
ACCENT_LIGHT = colors.HexColor("#e6f2ee")
INK = colors.HexColor("#1d2530")
MUTED = colors.HexColor("#4d5866")
CODE_BG = colors.HexColor("#f4f6f8")
TABLE_HEAD = colors.HexColor("#0f6b52")
TABLE_ALT = colors.HexColor("#f3f8f6")
RULE = colors.HexColor("#c9d6d1")

PAGE_W, PAGE_H = A4
LM = RM = 17 * mm
TM = 16 * mm
BM = 18 * mm
FRAME_W = PAGE_W - LM - RM

# ---------------------------------------------------------------- styles
S = {}
S["h1"] = ParagraphStyle("h1", fontName="Body-Bold", fontSize=20, leading=25,
                         textColor=ACCENT_DARK, alignment=TA_CENTER,
                         spaceAfter=4)
S["sub"] = ParagraphStyle("sub", fontName="Body", fontSize=11, leading=15,
                          textColor=MUTED, alignment=TA_CENTER, spaceAfter=2)
S["h2"] = ParagraphStyle("h2", fontName="Body-Bold", fontSize=13.2, leading=17,
                         textColor=colors.white, backColor=ACCENT,
                         borderPadding=(5, 7, 6, 7), spaceBefore=13, spaceAfter=8,
                         keepWithNext=1)
S["h3"] = ParagraphStyle("h3", fontName="Body-Bold", fontSize=11.4, leading=15,
                         textColor=ACCENT_DARK, spaceBefore=10, spaceAfter=4.5,
                         keepWithNext=1)
S["h4"] = ParagraphStyle("h4", fontName="Body-Bold", fontSize=10.2, leading=13.5,
                         textColor=ACCENT, spaceBefore=8, spaceAfter=3.5,
                         keepWithNext=1)
S["body"] = ParagraphStyle("body", fontName="Body", fontSize=9.6, leading=13.9,
                           textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5.0)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], alignment=0,
                             spaceAfter=2.6, leading=13.6)
S["cell"] = ParagraphStyle("cell", fontName="Body", fontSize=8.7, leading=12,
                           textColor=INK)
S["cellh"] = ParagraphStyle("cellh", fontName="Body-Bold", fontSize=8.9, leading=12,
                            textColor=colors.white)
S["quote"] = ParagraphStyle("quote", fontName="Body", fontSize=9.4, leading=13.6,
                            textColor=colors.HexColor("#26403a"), alignment=TA_JUSTIFY)
S["code"] = ParagraphStyle("code", fontName="Mono", fontSize=8.3, leading=11.2,
                           textColor=colors.HexColor("#21313d"))

INLINE_CODE = re.compile(r"`([^`]+)`")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text):
    """Markdown inline markup -> reportlab mini-HTML."""
    text = esc(text)
    stash = []

    def keep(html):
        stash.append(html)
        return "\x00%d\x00" % (len(stash) - 1)

    text = INLINE_CODE.sub(
        lambda m: keep('<font face="Mono" size="8.4" color="#b0332b">%s</font>' % m.group(1)),
        text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", text)
    # keep common dash/space entities compact
    text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_table_delim(line):
    return bool(re.fullmatch(r"\s*\|?[\s:-]*-[\s|:-]*\|?\s*", line)) and "-" in line


# ---------------------------------------------------------------- blocks
def build_code(text):
    """Code block drawn as one table row per line so it can split across pages."""
    lines = text.split("\n")
    data = [[Preformatted(l, S["code"])] for l in lines]
    if not data:
        data = [[Preformatted("", S["code"])]]
    t = Table(data, colWidths=[FRAME_W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d7dee3")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (0, 0), 7),
        ("BOTTOMPADDING", (0, -1), (0, -1), 7),
    ]))
    return t


def build_quote(lines):
    paras = [Paragraph(inline(" ".join(lines)), S["quote"])]
    t = Table([[paras]], colWidths=[FRAME_W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def build_table(rows):
    header, body = rows[0], rows[1:]
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    header = rows[0]
    body = rows[1:]

    # column widths: at least the longest unbreakable word, rest by content weight
    CHAR = 4.9          # approx width of one 8.7pt char
    PAD = 13            # cell padding
    mins, weights = [], []
    for i in range(ncol):
        cells = [re.sub(r"[*`]", "", r[i]) for r in rows]
        longest_word = max((len(w) for c in cells for w in c.split()), default=4)
        mins.append(min(longest_word, 26) * CHAR + PAD)
        weights.append(max(8, sum(len(c) for c in cells) / len(cells)))

    if sum(mins) > FRAME_W:                       # squeeze proportionally
        k = FRAME_W / sum(mins)
        widths = [m * k for m in mins]
    else:
        spare = FRAME_W - sum(mins)
        total_w = sum(weights)
        widths = [m + spare * w / total_w for m, w in zip(mins, weights)]

    data = [[Paragraph(inline(c), S["cellh"]) for c in header]]
    for r in body:
        data.append([Paragraph(inline(c), S["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style))
    return t


def parse(md):
    lines = md.split("\n")
    flow = []
    i = 0
    seen_h1 = False
    first_h3_after_h1 = False
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i].rstrip())
                i += 1
            i += 1
            while buf and not buf[0].strip():
                buf.pop(0)
            while buf and not buf[-1].strip():
                buf.pop()
            block = build_code("\n".join(buf))
            flow.append(Spacer(1, 3))
            # keep the diagram on one page, together with its heading
            group = [block]
            k = len(flow) - 1
            while k >= 0 and isinstance(flow[k], Spacer):
                k -= 1
            if k >= 0 and isinstance(flow[k], Paragraph) and flow[k].style.name in (
                    "h2", "h3", "h4"):
                group.insert(0, flow.pop(k))
            flow.append(KeepTogether(group))
            flow.append(Spacer(1, 7))
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
            rule = Table([[""]], colWidths=[FRAME_W], rowHeights=[7])
            rule.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.8, RULE)]))
            flow.append(rule)
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            txt = m.group(2).strip()
            if level == 1:
                seen_h1 = True
                flow.append(Paragraph(inline(txt), S["h1"]))
            elif level == 3 and seen_h1 and not first_h3_after_h1:
                first_h3_after_h1 = True
                flow.append(Paragraph(inline(txt), S["sub"]))
            else:
                flow.append(Paragraph(inline(txt), S["h%d" % level]))
            i += 1
            continue

        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            flow.append(build_quote([b for b in buf if b]))
            flow.append(Spacer(1, 6))
            continue

        if "|" in s and i + 1 < len(lines) and is_table_delim(lines[i + 1]):
            rows = [split_row(s)]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            flow.append(build_table(rows))
            flow.append(Spacer(1, 8))
            continue

        if re.match(r"^\s*[-*+]\s+", line):
            while i < len(lines):
                l2 = lines[i]
                if not re.match(r"^\s*[-*+]\s+", l2):
                    break
                indent = len(l2) - len(l2.lstrip())
                level = indent // 2
                txt = re.sub(r"^\s*[-*+]\s+", "", l2)
                st = ParagraphStyle(
                    "b%d" % level, parent=S["bullet"],
                    leftIndent=13 + 12 * level, bulletIndent=3 + 12 * level)
                marker = "•" if level == 0 else ("–" if level == 1 else "·")
                flow.append(Paragraph(inline(txt), st, bulletText=marker))
                i += 1
            flow.append(Spacer(1, 3))
            continue

        if re.match(r"^\s*\d+[.)]\s+", line):
            while i < len(lines):
                l2 = lines[i]
                if not re.match(r"^\s*\d+[.)]\s+", l2):
                    break
                indent = len(l2) - len(l2.lstrip())
                level = indent // 2
                num = re.match(r"^\s*(\d+)[.)]", l2).group(1)
                txt = re.sub(r"^\s*\d+[.)]\s+", "", l2)
                st = ParagraphStyle(
                    "n%d" % level, parent=S["bullet"],
                    leftIndent=15 + 13 * level, bulletIndent=3 + 13 * level)
                flow.append(Paragraph(inline(txt), st, bulletText="%s." % num))
                i += 1
            flow.append(Spacer(1, 3))
            continue

        # paragraph
        buf = []
        while i < len(lines) and lines[i].strip():
            nxt = lines[i].strip()
            if (nxt.startswith(("#", ">", "```")) or re.match(r"^\s*[-*+]\s+", nxt)
                    or re.match(r"^\s*\d+[.)]\s+", nxt)
                    or re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", nxt)):
                break
            buf.append(nxt)
            i += 1
        if buf:
            flow.append(Paragraph(inline(" ".join(buf)), S["body"]))

    while flow and isinstance(flow[-1], Spacer):   # avoids a trailing blank page
        flow.pop()
    return flow


# ---------------------------------------------------------------- page furniture
def deco(canv, doc):
    canv.saveState()
    # top hairline
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.7)
    canv.line(LM, PAGE_H - TM + 6 * mm, PAGE_W - RM, PAGE_H - TM + 6 * mm)
    canv.setFont("Body", 7.6)
    canv.setFillColor(MUTED)
    canv.drawString(LM, PAGE_H - TM + 8.6 * mm, "Class 10 Biology  ·  Life Processes")
    canv.drawRightString(PAGE_W - RM, PAGE_H - TM + 8.6 * mm, "NCERT / CBSE Notes")
    # footer
    canv.line(LM, BM - 6 * mm, PAGE_W - RM, BM - 6 * mm)
    canv.setFont("Body", 8)
    canv.drawCentredString(PAGE_W / 2, BM - 11 * mm, "Page %d" % doc.page)
    canv.restoreState()


class NotesDoc(BaseDocTemplate):
    """Doc template that adds PDF bookmarks for headings."""

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name not in ("h1", "h2", "h3"):
            return
        text = re.sub(r"<[^>]+>", "", flowable.getPlainText())
        level = {"h1": 0, "h2": 0, "h3": 1}[name]
        key = "bm%d" % id(flowable)
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=(level == 0))


def main(src, out):
    md = open(src, encoding="utf-8").read()
    doc = NotesDoc(out, pagesize=A4,
                          leftMargin=LM, rightMargin=RM,
                          topMargin=TM, bottomMargin=BM,
                          title="Life Processes — Class 10 Notes",
                          author="Class 10 Biology Notes",
                          subject="Life Processes: NCERT/CBSE study notes")
    frame = Frame(LM, BM, FRAME_W, PAGE_H - TM - BM, id="body",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=deco)])
    doc.build(parse(md))
    return out


if __name__ == "__main__":
    print(main(sys.argv[1], sys.argv[2]))
