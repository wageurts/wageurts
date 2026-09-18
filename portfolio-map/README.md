# Portfolio, responsibility & dependency map

A way to draw "the AI SDLC is a Platform Engineering portfolio item, DAE builds the
agents and guardrails, CD uses and operates it, S&TT drives adoption, software
engineering acts as PO of the agents and the flow, and observability is everywhere"
— without ending up with a slide nobody dares to touch.

## The idea in one line

**One model, three views.** Everything lives in [`model.yaml`](model.yaml); the
diagrams, the matrix and the PowerPoint deck are generated from it and are
disposable.

## Why three views and not one picture

The three things you are trying to show answer different questions, and each one
wants a different shape. Forcing them into a single chart is what makes these
diagrams unreadable and then unmaintainable.

| Question | View | Shape | Rule |
|---|---|---|---|
| What exists? | Capability map | Layers, boxes nested by portfolio item | Colour = the division that **builds** it. One colour per division, never per item type. |
| Who does what? | Responsibility matrix | Grid: rows = items, columns = divisions | Every many-to-many relation goes here. A cell with two role codes is the point, not a mistake. |
| Who needs whom? | Value flow | One arrow per handoff, labelled with a verb | Hard cap of ~8 arrows. More than that means it belongs in the matrix. |

Three conventions keep it honest:

* **Colour carries exactly one meaning: ownership** (who builds and maintains).
  Use, adoption, governance and PO-ship are *roles*, and roles live in the matrix,
  not in more colours.
* **Cross-cutting things get a rail, not arrows.** Observability touches every
  layer; drawn as a box with nine arrows it destroys the diagram, drawn as a band
  down the side it reads in one second. Its owner (CD) still shows in the matrix.
* **Arrows mean dependency, and they are labelled with a verb** — "provides models
  to", "plug into", "drives adoption of". An unlabelled arrow is a disagreement
  waiting to happen.

The hard case in your setup — the AI SDLC built by DAE, used by CD, adopted via
S&TT, with software engineering as PO — is exactly what the matrix is for. In the
capability map the AI SDLC is one purple (DAE) box; the row for it in the matrix
carries `G` for PE, `B` for DAE, `U` for CD and `A` for S&TT. Nothing is lost and
no arrow is drawn.

## Maintainability: why a text model instead of drawing

The deck and the drawing are *outputs*. The model is the source, which means:

* a change is a one-line edit, not twenty minutes of nudging shapes;
* `git diff` on `model.yaml` is the record of who decided what, when;
* `python render.py --check` fails on a typo (unknown division, dangling
  dependency) before it reaches a slide;
* the same facts feed PowerPoint, draw.io, Mermaid and a CSV — no "which version is
  current?".

Shapes in the generated `.pptx` are **native PowerPoint shapes and connectors**, not
images. Anyone can drag a box in the meeting; the arrows stay glued. The rule is:
nudges are disposable, the model is not — when the content changes, regenerate and
replace the slide rather than patching it.

## Usage

```bash
pip install -r requirements.txt
python render.py --check    # validate the model
python render.py            # regenerate everything into ./out
# or: make check / make all
```

## Outputs

| File | What it is | How to use it |
|---|---|---|
| `out/portfolio-map.pptx` | 5-slide deck, native editable shapes | The meeting artefact. Regenerate, don't repaint. |
| `out/portfolio-map.drawio` | Ready-to-open draw.io / diagrams.net file | For whiteboard-style editing; exports to editable VSDX or SVG for PowerPoint. |
| `out/drawio-import.csv` | draw.io CSV import spec | In draw.io: *Extras → Insert → Advanced → CSV*. Auto-layout, so the picture survives model growth. |
| `out/capability-map.mmd` | Mermaid — what exists | Renders in GitHub, Confluence, Notion, most wikis. |
| `out/dependency-flow.mmd` | Mermaid — what needs what | Kept separate on purpose (see below). |
| `out/value-flow.mmd` | Mermaid — who needs whom | The division-level story. |
| `out/responsibility-matrix.md` / `.csv` | The RACI-style grid | Paste the CSV into Excel or PowerPoint; the `.md` renders in the repo. |

A note on Mermaid: it ignores a subgraph's `direction` as soon as an arrow crosses
a subgraph boundary, so the structure view carries no dependency arrows and the
dependencies get their own diagram. draw.io and PowerPoint place shapes explicitly,
so there both live on one page.

## Editing the model

```yaml
items:
  - id: evals                 # stable id, referenced everywhere else
    name: Evaluation harness
    layer: capability         # one of the layers listed at the top of the file
    parent: ai-sdlc           # optional: it is part of a bigger portfolio item

responsibilities:
  - {item: evals, division: DAE, role: build}
  - {item: evals, division: CD,  role: use}

dependencies:
  - {from: evals, to: sdlc-flow, label: gates}
```

Roles: `build` (B), `po` (P), `use` (U), `adopt` (A), `govern` (G), `operate` (O).
Six is already the practical maximum for a readable matrix — resist adding a
seventh; if a distinction only matters to one team, put it in the `note:` field.

The division long names in `model.yaml` are marked `TODO: confirm` — fill in the
official expansions of DAE, CD and S&TT.
