#!/usr/bin/env python3
"""Lay the one-page overview out once, in points, on a 960x540 canvas.

Every backend (PowerPoint, draw.io, SVG) draws the *same* list of shapes, so
the slide, the drawing and the preview image can never drift apart. Shapes are
plain dicts:

    {"kind": "rect",  x, y, w, h, fill, stroke, radius, dash}
    {"kind": "text",  x, y, w, h, lines, align, valign}
    {"kind": "chevron", x, y, w, h, fill, lines}

`lines` is a list of {"t": str, "size": pt, "bold": bool, "color": "#rrggbb"}.
Text is wrapped here rather than by the renderer, so all three outputs break
lines in the same places.
"""
from __future__ import annotations

W, H = 960.0, 540.0
MARGIN = 20.0
LABEL_W = 132.0
COL_GAP = 8.0
ROW_GAP = 6.0
HEADER_H = 44.0
CHAIN_H = 50.0
CHIP_GAP = 5.0
NOTCH = 11.0  # chevron point depth, shared by every backend

INK = "#212529"
MUTED = "#868E96"
PAPER = "#FFFFFF"
HAIRLINE = "#DEE2E6"
BAND = "#F8F9FA"


def wrap(text: str, size: float, width: float, bold: bool = False) -> list[str]:
    """Greedy wrap using an average glyph width — good enough, and identical
    for every backend, which is the point."""
    per_char = size * (0.53 if bold else 0.49)
    limit = max(int(width / per_char), 8)
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= limit or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def tint(hexstr: str, amount: float) -> str:
    c = hexstr.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    mix = lambda v: round(v + (255 - v) * amount)
    return f"#{mix(r):02X}{mix(g):02X}{mix(b):02X}"


class Page:
    def __init__(self, model):
        self.m = model
        self.shapes: list[dict] = []

    # -- primitives --------------------------------------------------------
    def rect(self, x, y, w, h, fill=PAPER, stroke=None, radius=0.0, dash=False):
        self.shapes.append({"kind": "rect", "x": x, "y": y, "w": w, "h": h,
                            "fill": fill, "stroke": stroke, "radius": radius,
                            "dash": dash})

    def text(self, x, y, w, h, lines, align="l", valign="t"):
        self.shapes.append({"kind": "text", "x": x, "y": y, "w": w, "h": h,
                            "lines": lines, "align": align, "valign": valign})

    def chevron(self, x, y, w, h, fill, lines):
        self.shapes.append({"kind": "chevron", "x": x, "y": y, "w": w, "h": h,
                            "fill": fill, "lines": lines})


def run(t, size, bold=False, color=INK):
    return {"t": t, "size": size, "bold": bold, "color": color}


def chip_lines(contribution, model, width):
    """The wrapped text of one contribution chip."""
    role = model.role[contribution["role"]]
    head = contribution["expertise"]
    if contribution.get("assumed"):
        head += "  (assumed)"
    lines = [run(head, 8.5, True, role["color"])]
    for n, piece in enumerate(wrap(contribution["what"], 7.5, width)):
        lines.append(run(piece, 7.5, False, INK if n == 0 else INK))
    return lines


def chip_height(lines) -> float:
    return 9.0 + sum(ln["size"] * 1.28 for ln in lines)


def build(model) -> Page:
    p = Page(model)
    divs, props = model.divisions, model.propositions
    col_w = (W - 2 * MARGIN - LABEL_W - COL_GAP * len(divs)) / len(divs)
    chip_w = col_w - 16.0

    # ---- role legend, then the title in whatever width is left -----------
    used = {c["role"] for c in model.contributions}
    legend = [r for r in model.roles if r["id"] in used]
    legend_w = sum(len(r["label"]) * 4.4 + 26 for r in legend)
    lx = W - MARGIN
    for role in reversed(legend):
        tw = len(role["label"]) * 4.4 + 16
        lx -= tw + 10
        p.rect(lx, 22, 9, 9, fill=role["color"], radius=2)
        p.text(lx + 13, 20, tw, 13, [run(role["label"], 8, False, INK)], valign="m")

    title_w = W - 2 * MARGIN - legend_w - 20
    title_lines = wrap(model.meta["title"], 18, title_w, bold=True)
    p.text(MARGIN, 14, title_w, 24 * len(title_lines),
           [run(t, 18, True) for t in title_lines])
    subtitle_y = 14 + 23 * len(title_lines)
    p.text(MARGIN, subtitle_y, W - 2 * MARGIN, 16,
           [run(model.meta.get("subtitle", ""), 9.5, False, MUTED)])

    # ---- division headers -------------------------------------------------
    gx, gy = MARGIN, max(62.0, subtitle_y + 22)
    p.text(gx, gy + 12, LABEL_W, 20, [run("Propositions", 9, True, MUTED)])
    for i, d in enumerate(divs):
        x = gx + LABEL_W + COL_GAP + i * (col_w + COL_GAP)
        p.rect(x, gy, col_w, HEADER_H, fill=d["color"], radius=4)
        lines = [run(f'{d["name"]}  ({d["short"]})', 10.5, True, PAPER)]
        for piece in wrap(" · ".join(d["expertise"]), 7.5, col_w - 16):
            lines.append(run(piece, 7.5, False, tint(d["color"], 0.78)))
        p.text(x + 8, gy + 5, col_w - 16, HEADER_H - 8, lines)

    # ---- how tall does each row want to be? ------------------------------
    body_top = gy + HEADER_H + ROW_GAP
    body_bottom = H - MARGIN - CHAIN_H - 14
    cells: dict[tuple[str, str], list[list[dict]]] = {}
    wanted = []
    for prop in props:
        tallest = 0.0
        for d in divs:
            stack = [chip_lines(c, model, chip_w)
                     for c in model.contributions_for(prop["id"], d["id"])]
            cells[(prop["id"], d["id"])] = stack
            h = sum(chip_height(s) for s in stack) + CHIP_GAP * max(len(stack) - 1, 0)
            tallest = max(tallest, h)
        wanted.append(tallest + 12.0)

    available = body_bottom - body_top - ROW_GAP * (len(props) - 1)
    scale = min(1.0, available / sum(wanted))
    heights = [h * scale for h in wanted]
    slack = (available - sum(heights)) / len(props)
    heights = [h + slack for h in heights]

    # ---- rows -------------------------------------------------------------
    y = body_top
    for prop, row_h in zip(props, heights):
        p.rect(gx, y, LABEL_W, row_h, fill=BAND, stroke=HAIRLINE, radius=4)
        p.text(gx + 10, y + 8, LABEL_W - 20, row_h - 16,
               [run(prop["name"], 11.5, True)], valign="m")
        for i, d in enumerate(divs):
            x = gx + LABEL_W + COL_GAP + i * (col_w + COL_GAP)
            p.rect(x, y, col_w, row_h, fill=PAPER, stroke=HAIRLINE, radius=4)
            stacks = cells[(prop["id"], d["id"])]
            if not stacks:
                p.text(x, y, col_w, row_h, [run("no role", 8, False, "#CED4DA")],
                       align="c", valign="m")
            cy = y + 6
            for stack in stacks:
                ch = chip_height(stack)
                role_color = stack[0]["color"]
                assumed = "(assumed)" in stack[0]["t"]
                p.rect(x + 8, cy, chip_w, ch, fill=tint(role_color, 0.90),
                       stroke=tint(role_color, 0.55), radius=3, dash=assumed)
                p.rect(x + 8, cy, 3.5, ch, fill=role_color, radius=1)
                p.text(x + 8 + 9, cy + 4, chip_w - 16, ch - 8, stack)
                cy += ch + CHIP_GAP
        y += row_h + ROW_GAP

    # ---- the supply chain along the bottom -------------------------------
    cy = H - MARGIN - CHAIN_H
    p.text(gx, cy - 13, 300, 12,
           [run("How it fits together", 9, True, MUTED)])
    n = len(model.chain)
    step_w = (W - 2 * MARGIN) / n
    for i, step in enumerate(model.chain):
        d = model.div[step["division"]]
        lines = [run(d["short"], 9, True, d["color"])]
        for piece in wrap(step["label"], 8, step_w - 46):
            lines.append(run(piece, 8, False, INK))
        p.chevron(gx + i * step_w, cy, step_w - 4, CHAIN_H,
                  tint(d["color"], 0.88), lines)
    return p
