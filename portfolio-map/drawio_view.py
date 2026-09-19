#!/usr/bin/env python3
"""Render the laid-out page to a .drawio file — same shapes, editable by hand."""
from __future__ import annotations

import pathlib
from xml.sax.saxutils import escape

import layout


def _html_label(lines) -> str:
    parts = []
    for ln in lines:
        style = (f'font-size:{ln["size"]}px;color:{ln["color"]};'
                 f'font-weight:{"600" if ln["bold"] else "400"};')
        parts.append(f'<div style="{style}">{escape(ln["t"])}</div>')
    return "".join(parts)


def render(page: layout.Page) -> str:
    cells, nid = [], 1

    def add(value: str, style: str, x, y, w, h) -> None:
        nonlocal nid
        nid += 1
        cells.append(
            f'        <mxCell id="n{nid}" value="{value}" style="{style}" vertex="1" '
            f'parent="1"><mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
            f'height="{h:.0f}" as="geometry"/></mxCell>')

    for sh in page.shapes:
        if sh["kind"] == "rect":
            style = (f'rounded={1 if sh["radius"] else 0};whiteSpace=wrap;html=1;'
                     f'fillColor={sh["fill"]};'
                     f'strokeColor={sh["stroke"] or "none"};'
                     f'{"dashed=1;" if sh["dash"] else ""}')
            add("", style, sh["x"], sh["y"], sh["w"], sh["h"])
        elif sh["kind"] == "chevron":
            style = (f'shape=step;perimeter=stepPerimeter;whiteSpace=wrap;html=1;'
                     f'fixedSize=1;size={layout.NOTCH:.0f};fillColor={sh["fill"]};'
                     f'strokeColor=#DEE2E6;align=left;spacingLeft=16;'
                     f'verticalAlign=middle;')
            add(_html_label(sh["lines"]), style, sh["x"], sh["y"], sh["w"], sh["h"])
        else:
            align = {"l": "left", "c": "center", "r": "right"}[sh["align"]]
            style = (f'text;html=1;strokeColor=none;fillColor=none;align={align};'
                     f'verticalAlign={"middle" if sh["valign"] == "m" else "top"};'
                     f'whiteSpace=wrap;')
            add(_html_label(sh["lines"]), style, sh["x"], sh["y"], sh["w"], sh["h"])

    body = "\n".join(cells)
    return ('<mxfile host="render.py">\n'
            '  <diagram name="Portfolio overview">\n'
            f'    <mxGraphModel dx="{layout.W:.0f}" dy="{layout.H:.0f}" grid="1" '
            f'gridSize="10" page="1" pageWidth="{layout.W:.0f}" '
            f'pageHeight="{layout.H:.0f}" math="0" shadow="0">\n'
            '      <root>\n        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
            f'{body}\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


def write(page: layout.Page, path: pathlib.Path) -> pathlib.Path:
    path.write_text(render(page), encoding="utf-8")
    return path
