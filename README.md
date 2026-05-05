# sphinx-needs-template

[![build](https://github.com/mleist/sphinx-needs-template/actions/workflows/build.yml/badge.svg)](https://github.com/mleist/sphinx-needs-template/actions/workflows/build.yml)

A small, opinionated template for traceable requirements engineering with
**Sphinx**, **sphinx-needs**, **LinkML**, **ReqIF**, **JSON-LD** and
**pytest**.

The included demo describes a tiny home-garden project (lawn mowing, planting
beds, hosting a small garden party) — it is meant to be deleted and replaced
with your own content. The structure stays.

> Licensed under [BSD-3-Clause](LICENSE).

📖 **New here?** The
[Getting Started guide](docs/public/getting_started.md) walks you
through every moving part of the template — first build, seven views,
LinkML schema, adding your own user story / requirement / test, ReqIF
and JSON-LD exports, the public/private layout, switching to German
output, and adding private theme assets — in about 20 minutes.

## What this template gives you

- **One LinkML schema** as the single source of truth for need types
  (User Story, Use Case, Functional / Non-Functional Requirement, Test, Risk,
  Decision, Glossary Term).
- **`needs-from-linkml`** — converts validated YAML data into MyST markdown
  for sphinx-needs.
- **`schema-to-needs`** — renders the LinkML classes themselves as
  `cls`-typed needs so the data model shows up in the docs.
- **`reqif-bridge`** — minimal ReqIF import / export for exchange with
  classic RM tools.
- **`needs-to-jsonld`** — exports `needs.json` as a JSON-LD document whose
  `@context` reuses the LinkML prefixes.
- **pytest ↔ sphinx-needs bridge** — `@pytest.mark.satisfies("FR_xxx")`
  validates against `needs.json` at collection time, and the test results
  flow back into the docs as `test`-typed needs.
- **Six HTML/PDF views** from one source tree (`complete`, `overview`,
  `detail`, `party_prep`, `back_yard`, `schema`).
- **Single-service docker-compose** so `docker compose run --rm builder
  make all` builds everything with no host-side toolchain.

## Quick start

### With Docker (recommended)

```bash
docker compose build
docker compose run --rm builder make all
```

Outputs land in `docs/public/_build/`.

### Without Docker

```bash
pip install -e ".[dev]"
sudo apt install plantuml texlive-latex-recommended texlive-fonts-recommended latexmk
make all
```

### Common targets

```bash
make help                  # list everything
make generate              # rebuild reqs_gen/ from LinkML
make test                  # pytest with @satisfies validation + coverage
make html                  # all six HTML views
make pdf                   # all six PDF views
make html-overview         # just the stakeholder view
make reqif-export          # needs.json → ReqIF
make jsonld-export         # needs.json → JSON-LD
make clean
```

## Repository layout

The repo splits every important area into a `public/` folder (shipped with
the template, BSD-3) and a `private/` folder (yours, ignored by git).

```
sphinx-needs-template/
├── docs/
│   ├── public/
│   │   ├── conf.py                  Sphinx config (multi-view)
│   │   ├── index_complete.md        master_doc for view "complete"
│   │   ├── index_overview.md        master_doc for view "overview"
│   │   ├── index_detail.md          master_doc for view "detail"
│   │   ├── views/
│   │   │   ├── index_party_prep.md  cross-cutting tag filter
│   │   │   ├── index_back_yard.md   filtered by area
│   │   │   └── index_schema.md      class reference
│   │   ├── reqs/                    hand-written needs (FRs, NFRs, ...)
│   │   ├── reqs_gen/                AUTO-GENERATED — committed
│   │   └── _indices.md              compact tables of contents
│   └── private/                     your private docs (git-ignored)
│
├── linkml/
│   ├── public/
│   │   ├── schema/needs.yaml        single source of truth
│   │   └── data/                    YAML data → reqs_gen/*.md
│   └── private/                     your private LinkML (git-ignored)
│
├── src/
│   ├── public/                      converters + garden_helper module
│   │   ├── needs_from_linkml/
│   │   ├── schema_to_needs/
│   │   ├── reqif_bridge/
│   │   ├── needs_to_jsonld/
│   │   └── garden_helper/
│   └── private/                     your private code (git-ignored)
│
├── tests/
│   ├── public/                      conftest.py + tests for garden_helper
│   └── private/                     your private tests (git-ignored)
│
├── pictures/
│   ├── public/                      diagrams shipped with the template
│   └── private/                     your private images (git-ignored)
│
├── reqif/
│   ├── public/                      sample ReqIF (round-trippable)
│   └── private/                     your private ReqIF (git-ignored)
│
├── docker/Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── .github/workflows/build.yml      CI: generate → test → build all views
```

The decision to **commit `reqs_gen/`** is deliberate: it lets the repo render
correctly on GitHub without anyone running `make generate` first, and it
makes diffs in pull requests visible (you can see how a schema change
affects the rendered needs). The CI rebuilds it on every push and the
diff stays clean.

## How the pieces fit together

```
linkml/public/schema/needs.yaml ─┐
                                 ├─► needs-from-linkml ─► docs/public/reqs_gen/*.md
linkml/public/data/*.yaml ───────┘
                                                                  │
                                 ─► schema-to-needs ──► docs/public/reqs_gen/classes.md
                                                                  │
docs/public/reqs/*.md (hand-written) ─────────────────────────────┤
                                                                  ▼
                                                   sphinx-build -b needs
                                                                  │
                                                                  ▼
                                                docs/public/_build/needs/needs.json
                                                                  │
                  ┌───────────────────────────────────────────────┤
                  │                              │                │
                  ▼                              ▼                ▼
           pytest @satisfies            reqif-bridge       needs-to-jsonld
                  │                              │                │
                  ▼                              ▼                ▼
   docs/public/_generated/test_results.json   garden.reqif    garden.jsonld
                  │
                  ▼
   sphinx-build -b html (six views, with test results pulled in via
                         needs_external_needs)
```

## Replacing the demo with your own content

1. Edit `linkml/public/schema/needs.yaml` — add or remove need types and
   slots; the `area` enum is what you'd most likely change first.
2. Edit `linkml/public/data/*.yaml` — replace the gardening stories and
   use cases.
3. Edit `docs/public/reqs/*.md` — hand-written FRs, NFRs, risks,
   decisions, glossary.
4. Edit `src/public/garden_helper/` — rename the module to match your
   domain and update the tests in `tests/public/`.
5. Run `make generate && make test && make html`.

If you just want to layer your own content on top of the demo without
touching the public files, drop it under `*/private/`.

## Acknowledgements

Built on top of:

- [Sphinx](https://www.sphinx-doc.org/) — documentation generator
- [sphinx-needs](https://sphinx-needs.readthedocs.io/) — requirements
  engineering directives
- [MyST-Parser](https://myst-parser.readthedocs.io/) — Markdown extensions
  for Sphinx
- [LinkML](https://linkml.io/) — schema language and validation
- [pytest](https://docs.pytest.org/) — test runner
