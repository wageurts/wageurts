#!/usr/bin/env python3
"""Render model.yaml into the one-page portfolio overview.

    python render.py            # regenerate everything into ./out
    python render.py --check    # validate the model only

Outputs (all from one layout, so they cannot drift apart)
    out/portfolio-map.pptx         three slides, native editable shapes
    out/layers.svg|.drawio         division / portfolio / responsibility layers
    out/architecture.svg|.drawio   the building blocks, responsibilities beside them
    out/portfolio-overview.svg|.drawio   the propositions x divisions grid
    out/contribution-matrix.csv    the same facts as a grid, for Excel
    out/contribution-matrix.md     the same facts, rendered in the repo
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import yaml

import arch_layout
import drawio_view
import layers_layout
import layout
import svg_view

HERE = pathlib.Path(__file__).parent
CONTRIBUTION_KEYS = {"proposition", "division", "expertise", "role", "what", "assumed"}


class Model:
    def __init__(self, raw: dict):
        self.meta = raw.get("meta", {})
        self.divisions = raw["divisions"]
        self.roles = raw["roles"]
        self.propositions = raw["propositions"]
        self.contributions = raw["contributions"]
        self.chain = raw.get("chain", [])
        self.architecture = raw.get("architecture", {})
        self.div = {d["id"]: d for d in self.divisions}
        self.role = {r["id"]: r for r in self.roles}
        self.prop = {p["id"]: p for p in self.propositions}

    def validate(self) -> list[str]:
        errs = []
        for n, c in enumerate(self.contributions, start=1):
            stray = set(c) - CONTRIBUTION_KEYS
            if stray:
                # Almost always an unquoted comma inside `what:` — YAML then
                # reads the rest of the sentence as another key.
                errs.append(f"contribution {n}: unexpected key(s) {sorted(stray)} "
                            f"— quote the text after `what:`")
                continue
            if c["proposition"] not in self.prop:
                errs.append(f"contribution {n}: unknown proposition {c['proposition']}")
            if c["division"] not in self.div:
                errs.append(f"contribution {n}: unknown division {c['division']}")
            elif c["expertise"] not in self.div[c["division"]]["expertise"]:
                errs.append(f"contribution {n}: {c['division']} has no expertise "
                            f"{c['expertise']!r}")
            if c["role"] not in self.role:
                errs.append(f"contribution {n}: unknown role {c['role']}")
        arch = self.architecture
        for slot in ("foundation", "rail"):
            if arch.get(slot, {}).get("proposition") not in self.prop and arch:
                errs.append(f"architecture.{slot}: unknown proposition")
        for prop in self.propositions:
            if prop.get("owner") and prop["owner"] not in self.div:
                errs.append(f"proposition {prop['id']}: unknown owner "
                            f"{prop['owner']}")
        for col in arch.get("columns", []):
            if col["proposition"] not in self.prop:
                errs.append(f"architecture.columns: unknown proposition "
                            f"{col['proposition']}")
        for slot in ("consumer", "band"):
            if arch and arch.get(slot, {}).get("division") not in self.div:
                errs.append(f"architecture.{slot}: unknown division")
        for n, step in enumerate(self.chain, start=1):
            stray = set(step) - {"division", "label"}
            if stray:
                errs.append(f"chain step {n}: unexpected key(s) {sorted(stray)} "
                            f"— quote the text after `label:`")
            elif step["division"] not in self.div:
                errs.append(f"chain step {n}: unknown division {step['division']}")
        return errs

    def owner_of(self, proposition: str) -> str | None:
        """The division that owns a proposition — its colour in the drawings.

        Explicit `owner:` wins; otherwise the first division that builds it.
        """
        stated = self.prop[proposition].get("owner")
        if stated:
            return stated
        for c in self.contributions:
            if c["proposition"] == proposition and c["role"] == "build":
                return c["division"]
        return None

    def contributions_for(self, proposition: str, division: str) -> list[dict]:
        return [c for c in self.contributions
                if c["proposition"] == proposition and c["division"] == division]


def matrix_csv(m: Model, path: pathlib.Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Proposition", "Division", "Expertise", "Role", "Contribution",
                    "Confirmed"])
        for p in m.propositions:
            for d in m.divisions:
                for c in m.contributions_for(p["id"], d["id"]):
                    w.writerow([p["name"], d["short"], c["expertise"],
                                m.role[c["role"]]["label"], c["what"],
                                "assumed" if c.get("assumed") else "yes"])


def matrix_markdown(m: Model) -> str:
    out = [f'# {m.meta.get("title", "Portfolio overview")}', "",
           "Generated by `render.py` — edit `model.yaml`.", "",
           "| Proposition | " + " | ".join(d["short"] for d in m.divisions) + " |",
           "|" + "|".join(["---"] * (len(m.divisions) + 1)) + "|"]
    for p in m.propositions:
        row = [p["name"]]
        for d in m.divisions:
            cell = [f'{m.role[c["role"]]["code"]} {c["expertise"]}: {c["what"]}'
                    + (" *(assumed)*" if c.get("assumed") else "")
                    for c in m.contributions_for(p["id"], d["id"])]
            row.append("<br>".join(cell) or "—")
        out.append("| " + " | ".join(row) + " |")
    out += ["", "## Roles", ""]
    out += [f'- **{r["code"]}** — {r["label"]}' for r in m.roles]
    out += ["", "## Divisions", ""]
    out += [f'- **{d["short"]}** {d["name"]} — {", ".join(d["expertise"])}'
            for d in m.divisions]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=str(HERE / "model.yaml"))
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--check", action="store_true", help="validate and stop")
    ap.add_argument("--no-pptx", action="store_true")
    args = ap.parse_args()

    m = Model(yaml.safe_load(pathlib.Path(args.model).read_text(encoding="utf-8")))
    errs = m.validate()
    for e in errs:
        print(f"error: {e}", file=sys.stderr)
    if errs:
        return 1
    assumed = sum(1 for c in m.contributions if c.get("assumed"))
    if args.check:
        print(f"model ok — {len(m.propositions)} propositions, {len(m.divisions)} "
              f"divisions, {len(m.contributions)} contributions ({assumed} assumed)")
        return 0

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    layers = layers_layout.build(m)
    overview, architecture = layout.build(m), arch_layout.build(m)
    written = [svg_view.write(layers, out / "layers.svg"),
               drawio_view.write(layers, out / "layers.drawio"),
               svg_view.write(architecture, out / "architecture.svg"),
               drawio_view.write(architecture, out / "architecture.drawio"),
               svg_view.write(overview, out / "portfolio-overview.svg"),
               drawio_view.write(overview, out / "portfolio-overview.drawio")]
    matrix_csv(m, out / "contribution-matrix.csv")
    (out / "contribution-matrix.md").write_text(matrix_markdown(m), encoding="utf-8")
    written += [out / "contribution-matrix.csv", out / "contribution-matrix.md"]
    if not args.no_pptx:
        import pptx_view
        written.append(pptx_view.build([layers, architecture, overview],
                                       out / "portfolio-map.pptx"))
    for w in written:
        print(f"wrote {w}")
    if assumed:
        print(f"note: {assumed} contributions are marked `assumed` — confirm or remove them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
