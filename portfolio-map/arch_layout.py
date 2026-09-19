#!/usr/bin/env python3
"""The architecture view: nested building blocks, responsibilities on the side.

Same model, same primitives, same three renderers as the grid overview — this
page just answers a different question: not "who is responsible for what" but
"what sits on top of what, and what talks to what".

    +------------------------------------------+  +----------------+
    |  Software Engineering  (uses both)       |  | Responsibilities|
    |     |uses            |uses               |  |  per block,     |
    |  +--------+      +--------+   +--------+ |  |  one line per   |
    |  |Platform| <--> | AI SDLC|   | Observ.| |  |  contribution   |
    |  +--------+      +--------+   |  rail  | |  |                 |
    |  |        Cloud Landingzone            | |  |                 |
    |  |        Security (governs)           | |  |                 |
    +------------------------------------------+  +----------------+
"""
from __future__ import annotations

from layout import (BAND, HAIRLINE, INK, MARGIN, MUTED, PAPER, Page, W, H,
                    run, tint, wrap)

RAIL_W = 292.0          # the responsibilities panel on the right
OBS_W = 78.0            # the observability rail inside the drawing
GAP = 12.0
COL_GAP = 56.0          # room for the "integrates with" arrow and its label


def _block(p: Page, x, y, w, h, color, title, note, *, title_size=11,
           note_size=7.5, solid=True):
    """A labelled container: strong fill for bands, soft fill for containers."""
    fill = color if solid else tint(color, 0.93)
    p.rect(x, y, w, h, fill=fill, stroke=color if not solid else None, radius=5)
    lines = [run(title, title_size, True, PAPER if solid else color)]
    if note:
        for piece in wrap(note, note_size, w - 20):
            lines.append(run(piece, note_size, False,
                             tint(color, 0.80) if solid else INK))
    p.text(x + 10, y + 7, w - 20, h - 14, lines)
    return lines


def build(model) -> Page:
    arch = model.architecture
    p = Page(model)
    divs = model.div

    # ---- title and the division legend ----------------------------------
    legend_w = sum(len(d["short"]) * 5.2 + 26 for d in model.divisions)
    lx = W - MARGIN
    for d in reversed(model.divisions):
        tw = len(d["short"]) * 5.2 + 16
        lx -= tw + 10
        p.rect(lx, 22, 9, 9, fill=d["color"], radius=2)
        p.text(lx + 13, 20, tw, 13, [run(d["short"], 8, False, INK)], valign="m")

    title_w = W - 2 * MARGIN - legend_w - 20
    title_lines = wrap(arch.get("title", "How it fits together"), 18, title_w, True)
    p.text(MARGIN, 14, title_w, 24 * len(title_lines),
           [run(t, 18, True) for t in title_lines])
    sub_y = 14 + 23 * len(title_lines)
    p.text(MARGIN, sub_y, W - RAIL_W - 2 * MARGIN, 16,
           [run(arch.get("subtitle", ""), 9, False, MUTED)])

    # ---- the drawing ------------------------------------------------------
    top = max(64.0, sub_y + 22)
    main_w = W - 2 * MARGIN - RAIL_W - GAP
    stack_w = main_w - OBS_W - GAP

    consumer = arch["consumer"]
    c_color = divs[consumer["division"]]["color"]
    _block(p, MARGIN, top, stack_w, 46, c_color, consumer["label"], consumer["note"])

    # "uses" arrows, one per column
    cols = arch["columns"]
    widths = [stack_w * 0.56 - COL_GAP / 2, stack_w * 0.44 - COL_GAP / 2]
    arrow_y = top + 46 + 6
    col_y = arrow_y + 30
    col_h = 224.0
    xs, x = [], MARGIN
    for w in widths:
        xs.append(x)
        x += w + COL_GAP
    for cx, cw in zip(xs, widths):
        p.arrow(cx + cw / 2 - 9, arrow_y, 18, 24, "down", tint(c_color, 0.55))
        p.text(cx + cw / 2 + 12, arrow_y + 5, 60, 14,
               [run(arch["links"]["uses"], 7.5, False, MUTED)], valign="m")

    # the two containers, with their parts inside
    for (col, cx, cw) in zip(cols, xs, widths):
        prop = model.prop[col["proposition"]]
        owner = model.owner_of(prop["id"])
        color = divs[owner]["color"] if owner else INK
        _block(p, cx, col_y, cw, col_h, color, prop["name"], None,
               title_size=12, solid=False)
        parts = col["parts"]
        ncols = 2 if cw > 240 else 1
        rows = -(-len(parts) // ncols)
        pw = (cw - 20 - (ncols - 1) * 8) / ncols
        ph = min(58.0, (col_h - 34 - 10 - (rows - 1) * 8) / rows)
        block_h = rows * ph + (rows - 1) * 8
        first_y = col_y + 34 + (col_h - 44 - block_h) / 2
        for i, part in enumerate(parts):
            px = cx + 10 + (i % ncols) * (pw + 8)
            py = first_y + (i // ncols) * (ph + 8)
            p.rect(px, py, pw, ph, fill=PAPER, stroke=tint(color, 0.45), radius=3)
            p.text(px + 8, py, pw - 16, ph,
                   [run(t, 8, False, INK) for t in wrap(part, 8, pw - 16)],
                   valign="m")

    # "integrates with" between the two containers
    gap_x = xs[0] + widths[0]
    p.arrow(gap_x + 10, col_y + col_h / 2 - 11, COL_GAP - 20, 22, "leftright",
            tint(INK, 0.72))
    p.text(gap_x, col_y + col_h / 2 + 14, COL_GAP, 22,
           [run(t, 7, False, MUTED)
            for t in wrap(arch["links"]["integrates"], 7, COL_GAP - 4)],
           align="c")

    # foundation band
    found = arch["foundation"]
    f_prop = model.prop[found["proposition"]]
    f_owner = model.owner_of(f_prop["id"])
    f_color = divs[f_owner]["color"] if f_owner else INK
    f_y = col_y + col_h + 26
    p.arrow(MARGIN + stack_w / 2 - 9, f_y - 24, 18, 20, "down", tint(f_color, 0.55))
    p.text(MARGIN + stack_w / 2 + 12, f_y - 21, 70, 14,
           [run(arch["links"]["deploys"], 7.5, False, MUTED)], valign="m")
    _block(p, MARGIN, f_y, stack_w, 44, f_color, f_prop["name"], found["note"])

    # observability rail beside the stack, spanning every layer
    rail = arch["rail"]
    r_prop = model.prop[rail["proposition"]]
    r_owner = model.owner_of(r_prop["id"])
    r_color = divs[r_owner]["color"] if r_owner else INK
    rail_x = MARGIN + stack_w + GAP
    p.rect(rail_x, top, OBS_W, f_y + 44 - top, fill=tint(r_color, 0.92),
           stroke=r_color, radius=5)
    lines = [run(r_prop["name"], 9.5, True, r_color)]
    for piece in wrap(rail["note"], 7, OBS_W - 16):
        lines.append(run(piece, 7, False, INK))
    p.text(rail_x + 8, top + 8, OBS_W - 16, 120, lines)

    # security band underneath everything
    band = arch["band"]
    b_color = divs[band["division"]]["color"]
    b_y = f_y + 44 + 10
    p.rect(MARGIN, b_y, main_w, 40, fill=tint(b_color, 0.92), stroke=b_color,
           radius=5, dash=True)
    p.text(MARGIN + 12, b_y + 6, main_w - 24, 28,
           [run(band["label"], 9.5, True, b_color)]
           + [run(t, 7.5, False, INK) for t in wrap(band["note"], 7.5, main_w - 24)])

    # ---- responsibilities, written on the side ---------------------------
    rx = W - MARGIN - RAIL_W
    bottom = H - MARGIN
    p.rect(rx, top, RAIL_W, bottom - top, fill=BAND, stroke=HAIRLINE, radius=5)
    p.text(rx + 12, top + 8, RAIL_W - 24, 14,
           [run("Responsibilities", 10, True, INK)])
    p.text(rx + 12, top + 22, RAIL_W - 24, 12,
           [run("who builds it, who uses it, who governs it", 7.5, False, MUTED)])

    _responsibilities(p, model, rx, top + 36, bottom - 10, RAIL_W)
    return p


# The panel is drawn at the first setting whose blocks still fit the page:
# full description, clipped description, smaller type, and finally headings only.
DETAIL_STEPS = [("full", 7.0, 4.0), ("short", 7.0, 3.0), ("short", 6.5, 1.5),
                ("head", 7.5, 5.0)]


def _entry_lines(model, c, width, detail: str, size: float):
    """One responsibility, at the level of detail that still fits the panel."""
    role, d = model.role[c["role"]], model.div[c["division"]]
    head = f'{d["short"]} · {c["expertise"]} — {role["label"].lower()}'
    lines = [run(t, size, True, role["color"]) for t in wrap(head, size, width, True)]
    what = c["what"] + (" (assumed)" if c.get("assumed") else "")
    if detail == "full":
        lines += [run(t, size, False, MUTED) for t in wrap(what, size, width)]
    elif detail == "short":
        pieces = wrap(what, size, width)
        lines.append(run(pieces[0] + ("…" if len(pieces) > 1 else ""),
                         size, False, MUTED))
    return lines


def _responsibilities(p: Page, model, rx, y0, y_max, panel_w) -> None:
    text_w = panel_w - 44
    for detail, size, gap in DETAIL_STEPS:
        y, blocks = y0, []
        for prop in model.propositions:
            blocks.append(("head", prop["name"], y))
            y += 13
            for c in [c for d in model.divisions
                      for c in model.contributions_for(prop["id"], d["id"])]:
                lines = _entry_lines(model, c, text_w, detail, size)
                h = sum(ln["size"] * 1.3 for ln in lines)
                blocks.append((c, lines, y, h))
                y += h + gap
            y += gap + 1
        if y <= y_max or detail == "head":
            break
    for block in blocks:
        if block[0] == "head":
            _, name, by = block
            p.text(rx + 12, by, panel_w - 24, 12, [run(name, 8.5, True, INK)])
        else:
            c, lines, by, h = block
            color = model.role[c["role"]]["color"]
            p.rect(rx + 14, by + 1, 2.5, h - 2, fill=color, radius=1)
            p.text(rx + 22, by, text_w, h, lines)
