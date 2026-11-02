"""Tiny helpers for the Class 10 Light notes content."""

from __future__ import annotations


def H1(text: str):
    return ("h1", {"text": text})


def H2(text: str):
    return ("h2", {"text": text})


def H3(text: str):
    return ("h3", {"text": text})


def P(text: str):
    return ("p", {"text": text})


def BULLETS(items):
    return ("bullets", {"items": list(items)})


def NUMBERS(items):
    return ("numbers", {"items": list(items)})


def CALLOUT(kind: str, title: str, text: str):
    return ("callout", {"kind": kind, "title": title, "text": text})


def FORMULA(text: str, label: str = ""):
    return ("formula", {"text": text, "label": label})


def TABLE(headers, rows, widths=None, caption="", font_size=8.2):
    return (
        "table",
        {
            "headers": list(headers),
            "rows": [list(row) for row in rows],
            "widths": widths,
            "caption": caption,
            "font_size": font_size,
        },
    )


def DIAGRAM(name: str, caption: str, height: int = 170):
    return ("diagram", {"name": name, "caption": caption, "height": height})


def SPACER(height: int = 8):
    return ("spacer", {"height": height})


def PAGEBREAK():
    return ("pagebreak", {})


def SECTION_BREAK():
    return ("sectionbreak", {})
