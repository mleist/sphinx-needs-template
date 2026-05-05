# Getting Started

This guide walks through the whole template end to end. By the time you
finish you'll have built every output, added one new artefact of every
important kind, and run the test-coverage check that ties tests to
requirements.

The guide assumes Docker. If you'd rather install the toolchain natively,
the `Makefile` works the same way — see `README.md` for the bare-metal
instructions.

## 1. Prerequisites

You need exactly two things:

- **Docker** with the `compose` plugin (`docker compose version` should
  print a version ≥ 2.20).
- A clone of this repository.

Everything else — Python, Sphinx, sphinx-needs, LinkML, LaTeX, PlantUML,
Graphviz — lives inside the container image and never touches your host.

## 2. The first build

```bash
docker compose build
docker compose run --rm builder make all
```

Allow a few minutes for the first build (LaTeX is the slowest part to
install). The second time around, both commands return in seconds.

When `make all` finishes you should see:

- `Covered (passing): 3` — three functional requirements are tied to
  passing tests.
- `6 passed in 0.0Xs` — pytest's report.
- Six lines of `build succeeded.` — one per Sphinx view.

```{note}
**Concept — what just happened?** `make all` is the orchestrator for
five distinct stages, each defined as its own Make target:

1. `validate`  — every YAML file in `linkml/public/data/` is checked
   against `linkml/public/schema/needs.yaml`.
2. `generate`  — `needs-from-linkml` and `schema-to-needs` produce the
   files in `docs/public/reqs_gen/`.
3. `needs`     — Sphinx writes `needs.json`, the canonical "all needs"
   serialisation.
4. `test`      — pytest validates `@satisfies(...)` markers against
   `needs.json` and writes test results back as needs.
5. `html`      — Sphinx builds all six HTML views, ingesting the test
   results from stage 4.

Each stage depends on the previous one, so a single change ripples
through automatically.
```

## 3. Open the views

The build produced seven independent HTML sites under
`docs/public/_build/html-*/`. Open any `index.html` in a browser:

| View         | Purpose                                                      |
| ------------ | ------------------------------------------------------------ |
| `complete`   | Everything — every need type, every entry, every cross-link. |
| `overview`   | Stakeholder-friendly: stories, use cases, decisions, glossary. |
| `detail`     | Implementation-focused: requirements, tests, coverage, risks. |
| `party_prep` | Cross-cutting filter: every artefact tagged `party_prep`.    |
| `back_yard`  | Filtered by `area: back_yard`.                               |
| `schema`     | Reference of every LinkML class.                             |
| `schedule`   | Time-based view: Gantt charts of use cases and requirements. |

```{tip}
The same source tree produces all seven views by passing different
`-t view_<name>` flags to `sphinx-build`. The active tag selects a
different `master_doc` and a different `exclude_patterns` set in
`conf.py`, but every page text and every need lives only once on disk.
```

PDF reports are also available — run `make pdf` to build them; outputs
land in `docs/public/_build/pdf-*/`.

## 4. Read the LinkML schema

The schema is the single source of truth for what a need looks like.
Open `linkml/public/schema/needs.yaml`.

Three things to notice:

1. **The abstract `Need` class** defines the slots every need has:
   `id`, `title`, `description`, `tags`, `status`, `links`.
2. **Subclasses** like `UserStory`, `UseCase`, `FunctionalRequirement`
   add type-specific slots. `UserStory.area` is required and constrained
   to the values in `AreaEnum` — that's what makes the gardening
   filtering reliable.
3. **The `Container` class** is a technical helper. It declares the
   tree-root needed by `linkml-validate`, but it carries
   `annotations: hidden_in_docs: true` so it never shows up in the
   rendered class reference. If you add your own helper classes,
   re-use that annotation.

## 5. Add your own user story

Open `linkml/public/data/stories.yaml` and append a new entry:

```yaml
  - id: US_WATER_VEGGIES
    title: Water the vegetable bed in the morning
    area: vegetable_bed
    tags: [planting, daily]
    status: open
    description: |-
      As a **hobby gardener** I want to water the vegetable bed before 9 am
      so the soil absorbs water before the heat of the day.
```

Now rebuild — only the YAML pipeline needs to run:

```bash
docker compose run --rm builder make generate
docker compose run --rm builder make html-overview
```

Open `docs/public/_build/html-overview/reqs_gen/stories.html`. Your new
story is in the table, with the right `area` chip and tags.

```{note}
**Concept — generated vs hand-written content.** The files under
`docs/public/reqs_gen/` are auto-generated from LinkML. They are
committed to git on purpose so the repository renders correctly on
GitHub without anyone running `make generate` first, but they are
**never** edited by hand. The hand-written counterparts under
`docs/public/reqs/` (functional requirements, risks, decisions,
glossary) are edited as plain MyST.
```

## 6. Add your own functional requirement

Open `docs/public/reqs/functional.md` and append a `freq` directive:

````markdown
```{freq} Watering schedule helper
:id: FR_WATERING_SCHEDULE
:status: open
:tags: planting
:derives: US_WATER_VEGGIES

The system SHOULD compute the next watering time based on the most
recent watering and a configurable interval (default: 24 hours).
```
````

The `:derives:` value points to the user story you added in step 5,
which gives you bidirectional traceability automatically: visit the
story page after rebuilding, and it now lists this requirement under
"derived by".

## 7. Add a passing test

Open `tests/public/test_garden_helper.py` and append:

```python
@pytest.mark.satisfies("FR_WATERING_SCHEDULE")
def test_watering_schedule_placeholder():
    # Replace with a real test once you've implemented the helper.
    assert True
```

Run the full chain again:

```bash
docker compose run --rm builder make all
```

The output now reads `7 passed`. The coverage line still says 3 of 3
implemented requirements are covered — your new requirement has
`status: open`, so the coverage check correctly ignores it. As soon as
you flip the status to `implemented`, the requirement enters the
covered set and the test starts to count.

```{warning}
If you mistype the requirement id in `@pytest.mark.satisfies(...)`,
pytest fails fast at collection time:

> Invalid @satisfies markers:
>   tests/public/test_garden_helper.py::test_watering_schedule_placeholder:
>   @satisfies('FR_WAYERING_SCHEDULE') — unknown id

This is the bridge between the docs and the tests doing its job.
```

## 8. Export to ReqIF and JSON-LD

ReqIF is the lingua franca for exchanging requirements with classic RM
tools (DOORS Next, Polarion, ...). JSON-LD is the same data with a
proper semantic-web `@context`.

```bash
docker compose run --rm builder make reqif-export
docker compose run --rm builder make jsonld-export
```

Outputs land in `docs/public/_generated/`:

- `garden.reqif` — ~58 KB XML, round-trips cleanly through
  `reqif-bridge import`.
- `garden.jsonld` — ~15 KB JSON, with prefixes pulled directly from the
  LinkML schema's `prefixes:` section.

To re-import a customer-supplied ReqIF file as a JSON working set:

```bash
docker compose run --rm builder \
    reqif-bridge import reqif/private/customer.reqif -o /tmp/needs.json
```

## 9. Read the schedule

Open `docs/public/_build/html-schedule/index.html` (or, in any other
view, the `Schedule` page in the table of contents). You'll see two
Gantt charts — one for use cases, one for functional requirements — and
a flat status table sorted by start date.

Each bar is a need; its left edge is `start_date`, its width is
`duration` in days, and the darker shading inside it is `completion`
percent. Edit those fields in `linkml/public/data/usecases.yaml` or in
`docs/public/reqs/functional.md`, rebuild, and the chart updates.

```{note}
**Concept — `{needgantt}` vs `{needtable}`.** `{needtable}` is the
default rendering for any list of needs (rows + columns). `{needgantt}`
adds a calendar dimension. Both pull from the same field set and the
same filters; switching from one to the other only changes how the
result is drawn, not what it contains.
```

The dedicated `schedule` view (`html-schedule/index.html`) lifts the
schedule page to a master_doc, with two summary tables underneath the
Gantt chart that list every use case and every requirement that has a
`start_date` set. Reach for that view when you want a single
deliverable for status meetings.

## 10. Put your own content under `*/private/`

Every important folder has a public/private split. The `public/`
contents come with the template under BSD-3 and stay updateable. The
`private/` contents are yours, ignored by git, and never overwritten by
a `git pull` of the upstream template.

Useful private folders:

| Folder              | What lives there                                                     |
| ------------------- | -------------------------------------------------------------------- |
| `docs/private/`     | Internal notes, runbooks, decisions you don't publish.              |
| `linkml/private/`   | Private data files validated against the same schema.               |
| `src/private/`      | Internal helper scripts and modules.                                |
| `tests/private/`    | Tests for private code; pytest picks them up automatically.         |
| `pictures/private/` | Photos, screenshots, internal diagrams.                             |
| `reqif/private/`    | ReqIF exchange artefacts with customers / suppliers.                |

Each of those folders has its own `README.md` with a short snippet
showing how to wire it up.

## 11. Switch to German output

Set `DOCS_LANG=de` to flip the build to German:

```bash
docker compose run --rm -e DOCS_LANG=de builder make all
```

What this changes:

- Sphinx UI strings: "Contents" → "Inhalt", "Search" → "Suche", chapter
  headings ("CHAPTER" → "KAPITEL"), navigation buttons.
- Need-type titles: "Use Case" → "Anwendungsfall", "Functional
  Requirement" → "Funktionale Anforderung", "Risk" → "Risiko" etc.
- Gantt-chart locale: month names ("May" → "Mai") and weekday
  abbreviations ("Mo Tu We" → "Mo Di Mi"). This is forwarded to
  PlantUML's in-script `language` directive.

What this does *not* change: the demo content (user stories,
requirements) stays in English. When you fork the template for a real
German project you'll be writing German content anyway, and `DOCS_LANG`
aligns the rendering around it.

```{note}
Only `en` (default) and `de` are supported out of the box. Adding more
languages is a one-liner: extend the `_NEED_TYPE_TITLES` dict and the
`_SUPPORTED_LANGS` set in `docs/public/conf.py`.
```

## 12. Brand the output (private theme overrides)

Without forking the template, you can layer private theme assets on top
of the public defaults. Drop any of these four files into
`docs/private/` — each is optional, each is git-ignored:

| File                              | Purpose                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------- |
| `static/`                         | CSS, fonts, logos. Auto-added to `html_static_path`.                          |
| `latex_preamble.tex`              | Appended to `latex_elements["preamble"]` — corp colours, custom title page.   |
| `plantuml_preamble.iuml`          | Skin parameters loaded into every PlantUML diagram via `-config`.             |
| `conf_overrides.py`               | Free-form Python; export `def update(globals_: dict) -> None`.                |

Concrete example — switch to the Furo HTML theme without touching the
public source:

```python
# docs/private/conf_overrides.py
def update(globals_: dict) -> None:
    globals_["html_theme"] = "furo"
    globals_["html_logo"] = "_static/my_logo.png"
```

Then place `my_logo.png` under `docs/private/static/` and rebuild. The
public template is unchanged; pulling upstream updates won't conflict
with your branding.

See `docs/private/README.md` for the full reference.

## 13. What to change next

Now that you've seen every moving part, here's what to customise to
make the template your own.

**The domain model.** Edit the `area` enum in
`linkml/public/schema/needs.yaml` to match your domain. Add or remove
need types in the same file. After every schema change, run
`make generate && make all`.

**Project metadata.** In `pyproject.toml`, replace the placeholder
`Homepage`, `Documentation` and `Issues` URLs with your own repo. Update
the `LICENSE` if you keep BSD-3 as-is, change the copyright line to
your name or organisation.

**The CI workflow.** `.github/workflows/build.yml` already runs
`make generate`, `make needs`, `make test`, `make html`,
`make reqif-export` and `make jsonld-export` on every push. The first
push to GitHub will tell you whether anything in your environment
differs from the container.

**The demo content.** When you're ready to delete the gardening
example, the safe order is:

1. `linkml/public/data/*.yaml` — replace stories and use cases.
2. `docs/public/reqs/*.md` — replace functional, non-functional, risks,
   decisions, glossary.
3. `src/public/garden_helper/` — rename to your domain module and
   update the tests in `tests/public/`.
4. `pictures/public/garden_layout.svg` — replace with your own.
5. The view files under `docs/public/views/` — adjust the filters to
   what your project actually needs.

**Adding a new view.** The mapping is in four places: the `VIEWS`
list in the `Makefile`, the `_master_doc_for` dict and
`_active_view()` tuple in `docs/public/conf.py`, the
`MASTER_DOC` dict in `docker/write_redirect.py`, and one new
master_doc file under `docs/public/views/`. Follow the pattern of
`index_party_prep.md` for a tag-based filter, or `index_back_yard.md`
for an area-based filter, or `index_schedule.md` for a time-based
view.

---

That's the whole tour. The `Makefile`'s `help` target lists every other
target you might need:

```bash
docker compose run --rm builder make help
```
