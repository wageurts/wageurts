#!/usr/bin/env python3
"""Render the laid-out page to SVG — the preview that matches the slide."""
from __future__ import annotations

import pathlib
from xml.sax.saxutils import escape

import layout

FONT = "Segoe UI, Calibri, Helvetica, Arial, sans-serif"
NOTCH = layout.NOTCH


def _text(sh: dict) -> str:
    lines = sh["lines"]
    block = sum(ln["size"] * 1.28 for ln in lines)
    y = sh["y"] + (sh["h"] - block) / 2 if sh["valign"] == "m" else sh["y"]
    anchor = {"l": "start", "c": "middle", "r": "end"}[sh["align"]]
    x = {"l": sh["x"], "c": sh["x"] + sh["w"] / 2, "r": sh["x"] + sh["w"]}[sh["align"]]
    out = []
    for ln in lines:
        y += ln["size"] * 1.28
        out.append(
            f'<text x="{x:.1f}" y="{y - ln["size"] * 0.3:.1f}" font-size="{ln["size"]}" '
            f'font-weight="{"600" if ln["bold"] else "400"}" fill="{ln["color"]}" '
            f'text-anchor="{anchor}">{escape(ln["t"])}</text>')
    return "\n".join(out)


def _chevron_points(sh: dict) -> str:
    x, y, w, h = sh["x"], sh["y"], sh["w"], sh["h"]
    return " ".join(f"{px:.1f},{py:.1f}" for px, py in [
        (x, y), (x + w - NOTCH, y), (x + w, y + h / 2), (x + w - NOTCH, y + h),
        (x, y + h), (x + NOTCH, y + h / 2)])


def render(page: layout.Page) -> str:
    body = [f'<rect width="{layout.W}" height="{layout.H}" fill="#FFFFFF"/>']
    for sh in page.shapes:
        if sh["kind"] == "rect":
            dash = ' stroke-dasharray="3 2"' if sh["dash"] else ""
            stroke = (f' stroke="{sh["stroke"]}" stroke-width="0.8"{dash}'
                      if sh["stroke"] else "")
            body.append(
                f'<rect x="{sh["x"]:.1f}" y="{sh["y"]:.1f}" width="{sh["w"]:.1f}" '
                f'height="{sh["h"]:.1f}" rx="{sh["radius"]}" fill="{sh["fill"]}"{stroke}/>')
        elif sh["kind"] == "chevron":
            body.append(f'<polygon points="{_chevron_points(sh)}" fill="{sh["fill"]}" '
                        f'stroke="#DEE2E6" stroke-width="0.8"/>')
            body.append(_text({**sh, "x": sh["x"] + NOTCH + 8, "w": sh["w"] - NOTCH * 2 - 8,
                               "align": "l", "valign": "m"}))
        else:
            body.append(_text(sh))
    inner = "\n".join(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {layout.W:.0f} '
            f'{layout.H:.0f}" width="{layout.W:.0f}" height="{layout.H:.0f}" '
            f'font-family="{FONT}">\n{inner}\n</svg>\n')


def write(page: layout.Page, path: pathlib.Path) -> pathlib.Path:
    path.write_text(render(page), encoding="utf-8")
    return path
