#!/usr/bin/env python3
"""A tiny icon set drawn from rectangles and ellipses.

Deliberately not a font and not an image: every icon is made of the same
primitives as the rest of the page, so it survives the trip into PowerPoint and
draw.io as editable shapes, and it cannot break because a machine is missing a
symbol font.

    icons.draw(page, "cloud", x, y, size, "#0B7285")
"""
from __future__ import annotations

from layout import PAPER, tint


def _cloud(p, x, y, s, c):
    p.ellipse(x + s * .06, y + s * .42, s * .40, s * .40, c)
    p.ellipse(x + s * .28, y + s * .28, s * .48, s * .48, c)
    p.ellipse(x + s * .56, y + s * .44, s * .38, s * .38, c)
    p.rect(x + s * .12, y + s * .62, s * .76, s * .20, fill=c, radius=s * .10)


def _data(p, x, y, s, c):
    for n in range(3):
        top = y + s * (.18 + n * .24)
        p.rect(x + s * .14, top, s * .72, s * .20, fill=c, radius=s * .09)
        p.ellipse(x + s * .14, top - s * .07, s * .72, s * .16, c)


def _shield(p, x, y, s, c):
    p.rect(x + s * .18, y + s * .14, s * .64, s * .46, fill=c, radius=s * .06)
    p.ellipse(x + s * .18, y + s * .30, s * .64, s * .58, c)
    p.ellipse(x + s * .43, y + s * .38, s * .14, s * .14, PAPER)
    p.rect(x + s * .47, y + s * .46, s * .06, s * .16, fill=PAPER)


def _layers(p, x, y, s, c):
    for n, inset in enumerate((.10, .16, .22)):
        p.rect(x + s * inset, y + s * (.20 + n * .22), s * (1 - 2 * inset),
               s * .14, fill=c if n == 0 else tint(c, .35 * n), radius=s * .05)


def _agent(p, x, y, s, c):
    p.ellipse(x + s * .44, y + s * .08, s * .12, s * .12, c)
    p.rect(x + s * .49, y + s * .16, s * .02, s * .10, fill=c)
    p.rect(x + s * .16, y + s * .26, s * .68, s * .52, fill=c, radius=s * .14)
    p.ellipse(x + s * .30, y + s * .42, s * .13, s * .13, PAPER)
    p.ellipse(x + s * .57, y + s * .42, s * .13, s * .13, PAPER)
    p.rect(x + s * .34, y + s * .62, s * .32, s * .06, fill=PAPER, radius=s * .03)


def _eye(p, x, y, s, c):
    p.ellipse(x + s * .06, y + s * .26, s * .88, s * .48, c)
    p.ellipse(x + s * .30, y + s * .32, s * .40, s * .36, PAPER)
    p.ellipse(x + s * .38, y + s * .38, s * .24, s * .24, c)


def _grid(p, x, y, s, c):
    for row in (0, 1):
        for col in (0, 1):
            p.rect(x + s * (.16 + col * .38), y + s * (.16 + row * .38),
                   s * .30, s * .30, fill=c if row == col else tint(c, .45),
                   radius=s * .06)


GLYPHS = {"cloud": _cloud, "data": _data, "shield": _shield, "layers": _layers,
          "agent": _agent, "eye": _eye, "grid": _grid}


def draw(page, name: str, x: float, y: float, size: float, color: str,
         badge: bool = True) -> None:
    """Draw `name` in a size x size box, optionally on a tinted round badge."""
    if badge:
        page.ellipse(x, y, size, size, tint(color, 0.86))
        inset = size * 0.18
        x, y, size = x + inset, y + inset, size - 2 * inset
    GLYPHS.get(name, _grid)(page, x, y, size, color)
