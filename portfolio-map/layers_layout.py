#!/usr/bin/env python3
"""The layered view: division layer, portfolio layer, responsibility layer.

Three bands, each answering one question and each with its own colour key:

    1  DIVISION LAYER       who we are          colour = division
    2  PORTFOLIO LAYER      what we offer       colour = the division that builds it
    3  RESPONSIBILITY LAYER who does what       colour = the role

Keeping one colour meaning per band is what lets three dimensions share a page
without the reader having to hold a legend in their head.
"""
from __future__ import annotations

import icons
from layout import (BAND, HAIRLINE, INK, MARGIN, MUTED, PAPER, Page, W, H,
                    run, tint, wrap)

GAP = 10.0
LABEL_COL = 118.0


def _band_label(p: Page, x, y, number, title, note):
    p.text(x, y, 420, 12,
           [run(f"{number}  ·  {title}", 8.5, True, MUTED)])
    p.text(x + 220, y, 300, 12, [run(note, 8, False, "#ADB5BD")])


def _pill(p: Page, x, y, text, color, size=7.0):
    w = len(text) * size * 0.52 + 14
    p.rect(x, y, w, size + 8, fill=tint(color, 0.86), radius=(size + 8) / 2)
    p.text(x + 7, y, w - 14, size + 8, [run(text, size, False, color)], valign="m")
    return w


def build(model) -> Page:
    p = Page(model)

    # ---- title and the role key ------------------------------------------
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
    for n, line in enumerate(wrap("Divisions, portfolio and responsibilities",
                                  18, title_w, True)):
        p.text(MARGIN, 14 + n * 23, title_w, 24, [run(line, 18, True)])
    p.text(MARGIN, 38, W - 2 * MARGIN, 16,
           [run("Three layers, one colour meaning per layer", 9.5, False, MUTED)])

    top = 62.0
    full_w = W - 2 * MARGIN

    # ---- layer 1 · divisions ---------------------------------------------
    _band_label(p, MARGIN, top, "1", "DIVISION LAYER", "who we are · colour = division")
    y = top + 14
    card_w = (full_w - 2 * GAP) / 3

    def pill_rows(division):
        """How many rows the expertise pills wrap into."""
        rows, px = 1, 12.0
        for e in division["expertise"]:
            pw = len(e) * 3.64 + 14
            if px + pw > card_w - 10:
                rows, px = rows + 1, 12.0
            px += pw + 5
        return rows

    band1_h = 54 + max(pill_rows(d) for d in model.divisions) * 17 + 6
    for i, d in enumerate(model.divisions):
        x = MARGIN + i * (card_w + GAP)
        p.rect(x, y, card_w, band1_h, fill=tint(d["color"], 0.94),
               stroke=d["color"], radius=6)
        p.rect(x, y, card_w, 4, fill=d["color"], radius=2)
        icons.draw(p, d.get("icon", "grid"), x + 12, y + 16, 34, d["color"])
        p.text(x + 56, y + 14, card_w - 68, 16,
               [run(d["name"], 11, True, d["color"])])
        p.text(x + 56, y + 30, card_w - 68, 12,
               [run(d["short"], 8, False, MUTED)])
        px, py = x + 12, y + 52
        for expertise in d["expertise"]:
            pw = len(expertise) * 3.64 + 14
            if px + pw > x + card_w - 10:
                px, py = x + 12, py + 17
            _pill(p, px, py, expertise, d["color"])
            px += pw + 5

    # ---- layer 2 · portfolio ---------------------------------------------
    y += band1_h + 12
    _band_label(p, MARGIN, y, "2", "PORTFOLIO LAYER",
                "what we offer · colour = who owns it")
    y += 14
    card_w = (full_w - 3 * GAP) / 4
    band2_h = 50 + max(len(p_.get("parts", [])) for p_ in model.propositions) * 15 + 6
    for i, prop in enumerate(model.propositions):
        owner = model.owner_of(prop["id"])
        color = model.div[owner]["color"] if owner else INK
        x = MARGIN + i * (card_w + GAP)
        p.rect(x, y, card_w, band2_h, fill=PAPER, stroke=color, radius=6)
        p.rect(x, y, card_w, 4, fill=color, radius=2)
        icons.draw(p, prop.get("icon", "grid"), x + 10, y + 14, 30, color)
        p.text(x + 48, y + 13, card_w - 58, 14,
               [run(prop["name"], 10.5, True, color)])
        if owner:
            p.text(x + 48, y + 28, card_w - 58, 11,
                   [run(f'built by {model.div[owner]["short"]}', 7, False, MUTED)])
        py = y + 50
        for part in prop.get("parts", []):
            p.rect(x + 10, py, card_w - 20, 13, fill=tint(color, 0.93), radius=3)
            p.text(x + 16, py, card_w - 32, 13,
                   [run(part, 7, False, INK)], valign="m")
            py += 15

    # ---- layer 3 · responsibilities --------------------------------------
    y += band2_h + 12
    _band_label(p, MARGIN, y, "3", "RESPONSIBILITY LAYER",
                "who does what · colour = role")
    y += 14
    p.rect(MARGIN, y, full_w, H - MARGIN - y, fill=BAND, stroke=HAIRLINE, radius=6)
    col_w = (full_w - LABEL_COL - 5 * 8) / 4
    hy = y + 6
    for i, prop in enumerate(model.propositions):
        owner = model.owner_of(prop["id"])
        color = model.div[owner]["color"] if owner else INK
        x = MARGIN + LABEL_COL + 8 + i * (col_w + 8)
        p.rect(x, hy, col_w, 18, fill=color, radius=3)
        p.text(x + 8, hy, col_w - 16, 18,
               [run(prop["name"], 8.5, True, PAPER)], valign="m")

    rows = [r for r in model.roles if r["id"] in used]
    rows_bottom = H - MARGIN - 8          # keep the band's own edge visible
    row_h = (rows_bottom - (hy + 24) - (len(rows) - 1) * 5) / len(rows)
    ry = hy + 24
    for role in rows:
        p.rect(MARGIN + 8, ry, LABEL_COL - 8, row_h, fill=tint(role["color"], 0.90),
               radius=4)
        p.rect(MARGIN + 8, ry, 4, row_h, fill=role["color"], radius=2)
        p.text(MARGIN + 20, ry, LABEL_COL - 28, row_h,
               [run(role["label"], 8.5, True, role["color"]),
                run(role["definition"].split(";")[0], 6.5, False, MUTED)],
               valign="m")
        for i, prop in enumerate(model.propositions):
            x = MARGIN + LABEL_COL + 8 + i * (col_w + 8)
            p.rect(x, ry, col_w, row_h, fill=PAPER, stroke=HAIRLINE, radius=4)
            entries = [c for c in model.contributions
                       if c["proposition"] == prop["id"] and c["role"] == role["id"]]
            if not entries:
                p.text(x, ry, col_w, row_h,
                       [run("–", 9, False, "#CED4DA")], align="c", valign="m")
                continue
            eh = min(17.0, (row_h - 8) / len(entries))
            ey = ry + (row_h - (eh * len(entries) + 3 * (len(entries) - 1))) / 2
            for c in entries:
                d = model.div[c["division"]]
                p.rect(x + 6, ey, col_w - 12, eh, fill=tint(d["color"], 0.90),
                       radius=3, dash=bool(c.get("assumed")))
                p.rect(x + 6, ey, 3, eh, fill=d["color"], radius=1)
                label = f'{d["short"]} · {c["expertise"]}'
                p.text(x + 14, ey, col_w - 22, eh,
                       [run(label, 7, True, d["color"])], valign="m")
                ey += eh + 3
        ry += row_h + 5
    return p
