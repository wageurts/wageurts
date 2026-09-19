# Portfolio map — three pages, one model

Three pages, all generated from [`model.yaml`](model.yaml) by `python render.py`:

1. **Layers** (`layers.svg`, slide 1) — three stacked bands, each with its own
   colour key: the **division layer** (who we are, with expertise pills),
   the **portfolio layer** (what we offer, with the parts of each proposition) and
   the **responsibility layer** (roles as rows × propositions as columns, division
   badges in the cells). Icons carry the identity of each card.
2. **Architecture** (`architecture.svg`, slide 2) — the building blocks the way an
   engineer sketches them: software engineering on top using both the platform and
   the AI SDLC, the two containers with their parts, the landing zone underneath,
   observability as a rail beside it and security as a band across the bottom. The
   **responsibilities are written on the side**, one line per contribution.
3. **Overview grid** (`portfolio-overview.svg`, slide 3) — propositions as rows,
   divisions as columns, a coloured chip per contribution, and a supply-chain strip
   along the bottom.

Same facts, three questions: *what the layers are*, *what sits on what*, and
*who is responsible for what*.

## One colour meaning per band

Three dimensions on one page only works if the reader never has to ask what a
colour means twice. Each band states its own key in the header:

| Band | Colour means | Shape |
|---|---|---|
| Division layer | the division | card per division, expertise as pills |
| Portfolio layer | the division that **owns** it (`owner:` in the model) | card per proposition, parts listed |
| Responsibility layer | the **role** | role per row, proposition per column, division badge per contribution |

Icons are drawn from rectangles and ellipses (`icons.py`), never from a symbol
font or an image — so they arrive in PowerPoint and draw.io as editable shapes and
cannot break on a machine that lacks a font. Add one by writing a function in
`icons.py` and naming it in `icon:` on a division or proposition.

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
| `out/portfolio-map.pptx` | All three pages as slides. Native shapes. |
| `out/layers.svg` / `.drawio` | The three-layer page. |
| `out/architecture.svg` / `.drawio` | The building-block picture, responsibilities beside it. |
| `out/portfolio-overview.svg` / `.drawio` | The propositions × divisions grid. |
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

## The architecture page

Its shape lives under `architecture:` in the model — which propositions are the
two containers and what parts they hold, which one is the foundation, which one is
the rail, and the link labels (`uses`, `integrates with`, `deploys on`). The
responsibilities panel is generated from the same `contributions:` list as the
grid, so the two pages can never disagree, and it automatically drops to a smaller
type size (and finally to headings only) if you add more than fits.

Guardrails sit inside the AI SDLC rather than inside Platform Engineering, because
DA&E builds them along with the agents, flows and MCP integration. Move the string
between the two `parts:` lists if you would rather show them on the platform side.

## Open question

Contributions marked `assumed: true` are my inference, not something you stated —
they draw with a dashed border and an "(assumed)" tag so they are obvious in a
review. The AI SDLC row is as you described it; Platform Engineering,
Observability and Cloud Landingzone are first drafts. Confirm them, correct them,
or delete the line.
