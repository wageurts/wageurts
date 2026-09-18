#!/usr/bin/env python3
"""Build the PowerPoint deck from the model, using native editable shapes.

Deliberately *not* a picture of a diagram: every box is a real PowerPoint
shape and every arrow is a real connector, glued to the shapes it joins. A
colleague can drag a box in PowerPoint and the arrows follow. When the model
changes, regenerate the deck rather than nudging shapes by hand.
"""
from __future__ import annotations

import math
import pathlib

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
INK = RGBColor(0x21, 0x25, 0x29)
MUTED = RGBColor(0x86, 0x8E, 0x96)
LINE = RGBColor(0x49, 0x50, 0x57)
BAND = RGBColor(0xF1, 0xF3, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


def tint(hexstr: str, amount: float = 0.82) -> RGBColor:
    """Mix a colour towards white — used for matrix cell fills."""
    c = rgb(hexstr)
    return RGBColor(*(round(v + (255 - v) * amount) for v in (c[0], c[1], c[2])))


def _text(frame, text: str, size: int, color: RGBColor, bold: bool = False,
          align=PP_ALIGN.CENTER) -> None:
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = frame.paragraphs[0]
    p.alignment = align
    for n, line in enumerate(text.split("\n")):
        run = (p if n == 0 else frame.add_paragraph()).add_run()
        run.text = line
        run.font.size = Pt(size if n == 0 else max(size - 3, 8))
        run.font.bold = bold and n == 0
        run.font.color.rgb = color if n == 0 else MUTED
        if n:
            frame.paragraphs[n].alignment = align


def add_box(slide, x, y, w, h, text, fill, *, font=12, color=WHITE,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE, bold=True, outline=LINE):
    box = slide.shapes.add_shape(shape, x, y, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = fill
    if outline is None:
        box.line.fill.background()
    else:
        box.line.color.rgb = outline
        box.line.width = Pt(0.75)
    box.shadow.inherit = False
    _text(box.text_frame, text, font, color, bold=bold)
    return box


def add_label(slide, x, y, w, h, text, size=11, color=INK, bold=False,
              align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    _text(tb.text_frame, text, size, color, bold=bold, align=align)
    return tb


def blank(prs, title: str, subtitle: str = "") -> "Slide":
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_label(slide, Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.5),
              title, size=24, bold=True)
    if subtitle:
        add_label(slide, Inches(0.5), Inches(0.78), Inches(12.3), Inches(0.35),
                  subtitle, size=12, color=MUTED)
    return slide


# --------------------------------------------------------------------- slides
def slide_title(prs, m) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_label(slide, Inches(0.9), Inches(2.4), Inches(11.5), Inches(1.0),
              m.meta.get("title", "Portfolio map"), size=34, bold=True)
    add_label(slide, Inches(0.9), Inches(3.4), Inches(11.5), Inches(0.5),
              m.meta.get("subtitle", ""), size=16, color=MUTED)
    add_label(slide, Inches(0.9), Inches(4.1), Inches(11.5), Inches(0.4),
              f'v{m.meta.get("version", "0.1")} · {m.meta.get("updated", "")} · '
              f'generated from model.yaml — do not edit shapes by hand',
              size=11, color=MUTED)
    x = Inches(0.9)
    for d in m.divisions:
        add_box(slide, x, Inches(5.0), Inches(2.2), Inches(0.7),
                f'{d["name"]}\n{d.get("long_name", "")}', rgb(d["color"]), font=12)
        x += Inches(2.35)


def slide_capability_map(prs, m) -> None:
    slide = blank(prs, "1 — What exists",
                  "Boxes are portfolio items. Colour = the division that builds it. "
                  "Cross-cutting concerns are a rail, not a box with eight arrows.")
    top, bottom = Inches(1.35), Inches(7.1)
    lanes = len(m.layers)
    lane_h = (bottom - top - Emu(int(Inches(0.12)) * (lanes - 1))) // lanes
    label_w, rail_w = Inches(1.6), Inches(1.15)
    area_x = Inches(0.5) + label_w + Inches(0.1)
    area_w = Inches(12.8) - label_w - rail_w - Inches(0.3)

    y = top
    for layer in m.layers:
        band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), y,
                                      label_w + Inches(0.1) + area_w, lane_h)
        band.fill.solid()
        band.fill.fore_color.rgb = BAND
        band.line.fill.background()
        band.shadow.inherit = False
        _text(band.text_frame, "", 10, INK)
        add_label(slide, Inches(0.6), y + Inches(0.1), label_w - Inches(0.1),
                  lane_h - Inches(0.2),
                  f'{layer["name"]}\n{layer.get("hint", "")}', size=12, bold=True)

        items = m.items_in(layer["id"])
        if items:
            gap = Inches(0.18)
            w = (area_w - gap * (len(items) - 1)) // len(items)
            bx = area_x
            for item in items:
                owner = m.owner(item["id"])
                add_box(slide, bx, y + Inches(0.22), w, lane_h - Inches(0.44),
                        item["name"] + (f"\n{owner}" if owner else ""),
                        rgb(m.color(item["id"])), font=12)
                bx += w + gap
        y += lane_h + Inches(0.12)

    rail_x = Inches(0.5) + label_w + Inches(0.1) + area_w + Inches(0.15)
    for n, item in enumerate(m.crosscutting):
        box = add_box(slide, rail_x + Inches(n * 1.25), top, rail_w,
                      y - top - Inches(0.12),
                      item["name"], rgb(m.color(item["id"])), font=12)
        box.text_frame.paragraphs[0].runs[0].font.size = Pt(13)


def _cell(table, r, c, text, *, fill=None, color=INK, bold=False, size=10,
          align=PP_ALIGN.CENTER):
    cell = table.cell(r, c)
    cell.text = ""
    cell.margin_left = cell.margin_right = Inches(0.04)
    cell.margin_top = cell.margin_bottom = Inches(0.02)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    else:
        cell.fill.background()
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def slide_matrix(prs, m) -> None:
    slide = blank(prs, "2 — Who does what",
                  "The many-to-many part of the story lives here, not in arrows. "
                  "One row per item, one column per division, role codes in the cell.")
    items = m.matrix_items
    rows, cols = len(items) + 1, len(m.divisions) + 1
    left, top = Inches(0.5), Inches(1.3)
    width, height = Inches(9.4), Inches(0.32) * rows
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table
    table.columns[0].width = Inches(3.0)
    for c in range(1, cols):
        table.columns[c].width = Inches(1.28)

    _cell(table, 0, 0, "Portfolio item", fill=RGBColor(0x34, 0x3A, 0x40),
          color=WHITE, bold=True, align=PP_ALIGN.LEFT)
    for c, d in enumerate(m.divisions, start=1):
        _cell(table, 0, c, d["name"], fill=rgb(d["color"]), color=WHITE, bold=True)

    for r, item in enumerate(items, start=1):
        prefix = "    " if item.get("parent") else ""
        suffix = "  (cross-cutting)" if item.get("crosscutting") else ""
        _cell(table, r, 0, prefix + item["name"] + suffix, fill=WHITE,
              align=PP_ALIGN.LEFT, bold=not item.get("parent"))
        for c, d in enumerate(m.divisions, start=1):
            codes = [m.role[x]["code"] for x in m.roles_on(item["id"], d["id"])]
            _cell(table, r, c, " ".join(codes),
                  fill=tint(d["color"]) if codes else WHITE,
                  color=rgb(d["color"]) if codes else MUTED, bold=bool(codes))

    x = Inches(10.15)
    add_label(slide, x, Inches(1.25), Inches(2.9), Inches(0.3), "Role codes",
              size=12, bold=True)
    y = Inches(1.65)
    for role in m.roles:
        add_label(slide, x, y, Inches(2.9), Inches(0.55),
                  f'{role["code"]} — {role["label"]}\n{role["definition"]}', size=9)
        y += Inches(0.62)
    add_label(slide, x, y + Inches(0.1), Inches(2.9), Inches(0.9),
              "A cell with two codes is not a mistake: it is the point. "
              "Empty column = that division has no stake in that row.",
              size=9, color=MUTED)


def _sites(a, b) -> tuple[int, int]:
    """Pick sensible connection points (0 top, 1 left, 2 bottom, 3 right)."""
    dx = (b.left + b.width // 2) - (a.left + a.width // 2)
    dy = (b.top + b.height // 2) - (a.top + a.height // 2)
    if abs(dx) >= abs(dy):
        return (3, 1) if dx > 0 else (1, 3)
    return (2, 0) if dy > 0 else (0, 2)


def slide_value_flow(prs, m) -> None:
    slide = blank(prs, "3 — How the divisions need each other",
                  "One arrow per handoff, each labelled with a verb. Keep this under "
                  "eight arrows; anything more belongs in the matrix.")

    cx, cy = Inches(6.35), Inches(4.35)
    rx, ry = Inches(4.3), Inches(2.3)
    bw, bh = Inches(2.3), Inches(0.95)
    shapes = {}
    n = len(m.divisions)
    for i, d in enumerate(m.divisions):
        angle = -math.pi / 2 + i * 2 * math.pi / n
        x = int(cx + rx * math.cos(angle) - bw / 2)
        y = int(cy + ry * math.sin(angle) - bh / 2)
        shapes[d["id"]] = add_box(slide, Emu(x), Emu(y), bw, bh,
                                  f'{d["name"]}\n{d.get("long_name", "")}',
                                  rgb(d["color"]), font=13)

    for h in m.handoffs:
        a, b = shapes[h["from"]], shapes[h["to"]]
        sa, sb = _sites(a, b)
        conn = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, a.left, a.top, b.left, b.top)
        conn.begin_connect(a, sa)
        conn.end_connect(b, sb)
        conn.line.color.rgb = rgb(m.div[h["from"]]["color"])
        conn.line.width = Pt(1.75)
        mx = (a.left + a.width // 2 + b.left + b.width // 2) // 2
        my = (a.top + a.height // 2 + b.top + b.height // 2) // 2
        add_label(slide, Emu(mx - int(Inches(0.95))), Emu(my - int(Inches(0.16))),
                  Inches(1.9), Inches(0.32), h["label"], size=9,
                  color=rgb(m.div[h["from"]]["color"]), align=PP_ALIGN.CENTER)


def slide_howto(prs, m) -> None:
    slide = blank(prs, "How to keep this slide deck true",
                  "The deck is an output. The model is the source.")
    steps = [
        ("1. Change the model", "Edit portfolio-map/model.yaml — one line per item, "
         "responsibility, dependency or handoff. No shape fiddling."),
        ("2. Regenerate", "`make all` (or `python render.py`) rewrites the Mermaid, "
         "draw.io, CSV and PowerPoint outputs from that one file."),
        ("3. Re-paste, don't redraw", "Replace slides 2–4 wholesale. Shapes stay "
         "native PowerPoint objects, so anyone can still nudge them — but nudges "
         "are disposable, the model is not."),
        ("4. Review cadence", "Walk the matrix in the portfolio review; a disputed "
         "cell is a real governance question, and the diff on model.yaml is the "
         "record of the decision."),
    ]
    y = Inches(1.5)
    for head, body in steps:
        add_box(slide, Inches(0.5), y, Inches(2.6), Inches(0.9), head,
                rgb("#343A40"), font=13)
        add_label(slide, Inches(3.3), y, Inches(9.4), Inches(0.9), body, size=12)
        y += Inches(1.1)
    add_label(slide, Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.8),
              "Rule of thumb: structure (what exists) → layered picture; "
              "responsibility (who) → matrix; dependency (who needs who) → flow. "
              "Mixing the three is what makes these diagrams unreadable and unmaintainable.",
              size=12, color=MUTED)


def build_deck(model, path: pathlib.Path) -> pathlib.Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    slide_title(prs, model)
    slide_capability_map(prs, model)
    slide_matrix(prs, model)
    slide_value_flow(prs, model)
    slide_howto(prs, model)
    prs.save(str(path))
    return path
