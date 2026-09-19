# Portfolio overview — one page, one model

One diagram that carries all three dimensions at once: **propositions** (rows),
**divisions** (columns) and **responsibilities** (the coloured chips in the cells,
each naming the expertise that does the work). A supply-chain strip along the
bottom answers the fourth question — how the divisions need each other.

Everything is generated from [`model.yaml`](model.yaml) by `python render.py`.

## Why a grid and not a box-and-arrow drawing

Divisions × propositions is a many-to-many relation, and many-to-many drawn with
arrows is spaghetti: four propositions and three divisions would already need
eighteen crossing lines. A grid shows the same eighteen facts with no lines at
all, and it has room for *what* each division contributes — not just a RACI
letter.

Three rules keep the page readable:

* **Colour means one thing: the role.** Blue builds, green uses, orange governs,
  violet drives adoption. Divisions are already encoded by column, so they do not
  need a second colour dimension (the header bands are labels, not data).
* **Every chip names an expertise.** "C&D" is too coarse to act on; "Cloud
  Engineering — delivers the cloud platform the AI SDLC runs on" is a commitment.
  Validation enforces that the expertise actually belongs to that division.
* **An empty cell is a statement**, not an oversight: that division has no role in
  that proposition.

The AI SDLC row is the case that made this necessary: C&D contributes twice
(Cloud Engineering builds the platform it runs on, Software Engineering *uses* it
to build and maintain applications), DA&E builds the agents, guardrails, MCP
integration and flows, and S&TT drives adoption. Four different relationships to
one proposition, in one row, with no crossing arrows.

## Keeping it maintainable

The slide is an output; `model.yaml` is the source.

* One layout engine (`layout.py`) feeds all three renderers, so the PowerPoint,
  the draw.io drawing and the SVG preview cannot drift apart.
* `python render.py --check` refuses a model with an unknown division, an
  expertise that division does not have, or the classic YAML trap of an unquoted
  comma swallowing half a sentence.
* `git diff model.yaml` is the record of who decided what.
* Shapes in the `.pptx` are **native PowerPoint shapes**, so anyone can nudge them
  in the meeting — but nudges are disposable and the model is not. When the
  content changes, regenerate and replace the slide.

## Usage

```bash
pip install -r requirements.txt
python render.py --check    # validate
python render.py            # regenerate ./out
```

| Output | Use |
|---|---|
| `out/portfolio-overview.pptx` | The slide. One page, native shapes. |
| `out/portfolio-overview.drawio` | Open in draw.io / diagrams.net to edit by hand or export SVG/VSDX. |
| `out/portfolio-overview.svg` | Preview in a browser, a wiki or the repo. |
| `out/contribution-matrix.csv` | The same facts for Excel or a PowerPoint table. |
| `out/contribution-matrix.md` | The same facts, readable in the repo. |

## Editing

```yaml
contributions:
  - {proposition: ai-sdlc, division: DAE, expertise: AI,
     role: build, what: "Engineers who build agents, guardrails, MCP integration and flows"}
```

Always quote the text after `what:` and `label:` — an unquoted comma inside a
`{...}` entry silently turns the rest of the sentence into a new key. The
validator catches it, but quoting avoids the round trip.

Roles: `build` (B), `use` (U), `operate` (O), `govern` (G), `adopt` (A). The
legend only shows the roles actually used on the page.

## Open question

Contributions marked `assumed: true` are my inference, not something you stated —
they draw with a dashed border and an "(assumed)" tag so they are obvious in a
review. The AI SDLC row is as you described it; Platform Engineering,
Observability and Cloud Landingzone are first drafts. Confirm them, correct them,
or delete the line.
