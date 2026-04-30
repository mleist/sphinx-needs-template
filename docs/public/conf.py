"""Sphinx configuration for the sphinx-needs-template (gardening demo).

Multi-view strategy
-------------------
We build the same source tree multiple times with different Sphinx tags. Each
tag activates a different ``master_doc`` and excludes irrelevant pages, so a
single set of MyST files yields several role-specific HTML/PDF outputs.

Tags (set by the Makefile via ``-t view_<name>``):

- ``view_complete``       — everything
- ``view_overview``       — stakeholder-friendly: stories, use cases, decisions
- ``view_detail``         — implementation-focused: requirements, tests, risks
- ``view_party_prep``     — cross-cutting filter on tag/area for the party
- ``view_back_yard``      — only stories with ``area: back_yard``
- ``view_schema``         — generated class reference

Each view selects the matching index file as ``master_doc``. The default
(no tag) builds the ``complete`` view.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Project information
# -----------------------------------------------------------------------------
project   = "sphinx-needs-template"
author    = "sphinx-needs-template contributors"
copyright = "2026, sphinx-needs-template contributors"
release   = "0.1.0"

# -----------------------------------------------------------------------------
# Path setup — make src/public importable so any custom extensions or
# autodoc'ed modules can be resolved.
# -----------------------------------------------------------------------------
HERE     = Path(__file__).resolve().parent
REPO     = HERE.parent.parent
sys.path.insert(0, str(REPO / "src" / "public"))

# -----------------------------------------------------------------------------
# Extensions
# -----------------------------------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_needs",
    "sphinxcontrib.plantuml",
    # Converts SVG images to PDF on-the-fly when building LaTeX, so SVG
    # diagrams (e.g. pictures/public/garden_layout.svg) work in both HTML
    # and PDF outputs. Requires `rsvg-convert` (apt: librsvg2-bin).
    "sphinxcontrib.rsvgconverter",
]

source_suffix = {
    ".md":  "markdown",
    ".rst": "restructuredtext",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# -----------------------------------------------------------------------------
# View selection
# -----------------------------------------------------------------------------
# The ``tags`` global is provided by Sphinx during build.
def _active_view() -> str:
    for view in ("complete", "overview", "detail",
                 "party_prep", "back_yard", "schema"):
        if tags.has(f"view_{view}"):  # noqa: F821 — provided by Sphinx
            return view
    return "complete"


_VIEW = _active_view()

_master_doc_for = {
    "complete":   "index_complete",
    "overview":   "index_overview",
    "detail":     "index_detail",
    "party_prep": "views/index_party_prep",
    "back_yard":  "views/index_back_yard",
    "schema":     "views/index_schema",
}
master_doc = _master_doc_for[_VIEW]
root_doc   = master_doc

# Per-view excludes — keep loaded the files that may contain link targets,
# but hide them from the toctree of the active view.
_view_excludes = {
    "complete": [],
    "overview": [
        "reqs/functional.md",
        "reqs/nonfunctional.md",
        "tests/tests.md",
        "reqs/risks.md",
    ],
    "detail": [
        # Stories/use cases are loaded so derives:- and implements:-targets
        "reqs/decisions.md",
        "reqs/glossary.md",
    ],
    "party_prep": [],
    "back_yard":  [],
    "schema":     [],  # schema view shows everything but its master_doc only links the class ref
}
exclude_patterns = ["_build", "_generated", "Thumbs.db", ".DS_Store"]
exclude_patterns.extend(_view_excludes.get(_VIEW, []))

# -----------------------------------------------------------------------------
# HTML / PDF output
# -----------------------------------------------------------------------------
html_theme       = "sphinx_rtd_theme"
html_static_path = ["_static"]
# Replace underscores with hyphens in the title only — underscores are
# LaTeX special characters in non-math mode and would need escaping.
_view_label = _VIEW.replace("_", "-")
html_title       = f"sphinx-needs-template — {_view_label}"

latex_documents = [
    (master_doc, f"sphinx-needs-template-{_VIEW}.tex",
     html_title, author, "manual"),
]

# XeLaTeX handles arbitrary Unicode (em/en dashes, →, U+2212, ...) natively,
# unlike pdflatex which would need each character declared explicitly.
# Requires `texlive-xetex` in the build image (see docker/Dockerfile).
#
# We deliberately do NOT override `fontpkg` here. Sphinx's default xelatex
# fontpkg uses the LaTeX macro packages `tgtermes`/`tgheros`/`txtt`, which
# are loaded directly via TeX's font system and do not depend on fontconfig.
# Overriding with `\setmainfont{TeX Gyre Termes}` (fontspec) requires the
# font to be discoverable by family name — which only works after a
# `fc-cache` refresh in the build image and silently falls back to
# `nullfont` when it isn't, producing thousands of "no character in font
# nullfont" errors during the PDF build.
latex_engine = "xelatex"
latex_elements = {
    # Map the explicit Unicode minus sign U+2212 to a regular hyphen so it
    # renders even when an unusual code path emits it directly.
    "preamble": r"""
\usepackage{newunicodechar}
\newunicodechar{−}{-}
""",
}

# -----------------------------------------------------------------------------
# sphinx-needs configuration
# -----------------------------------------------------------------------------
needs_types = [
    {"directive": "story",          "title": "User Story",                  "prefix": "US_",  "color": "#FFD8A8", "style": "node"},
    {"directive": "uc",             "title": "Use Case",                    "prefix": "UC_",  "color": "#A8D8FF", "style": "node"},
    {"directive": "freq",           "title": "Functional Requirement",      "prefix": "FR_",  "color": "#BFD8D2", "style": "node"},
    {"directive": "nfreq",          "title": "Non-Functional Requirement",  "prefix": "NFR_", "color": "#D2BFD8", "style": "node"},
    {"directive": "test",           "title": "Test",                        "prefix": "T_",   "color": "#D8D2BF", "style": "node"},
    {"directive": "risk",           "title": "Risk",                        "prefix": "RSK_", "color": "#FFB8B8", "style": "node"},
    {"directive": "decision",       "title": "Decision",                    "prefix": "DEC_", "color": "#B8FFB8", "style": "node"},
    {"directive": "glossary_term",  "title": "Glossary Term",               "prefix": "G_",   "color": "#E0E0E0", "style": "node"},
    {"directive": "cls",            "title": "LinkML Class",                "prefix": "CLS_", "color": "#C0E0FF", "style": "node"},
]

# Custom fields (sphinx-needs 5+ replaces the deprecated needs_extra_options
# and needs_statuses with one unified `needs_fields` dict).
# - status uses an enum to constrain the lifecycle values.
# - duration is an integer for needgantt rendering.
# - start_date is a string in ISO date format.
needs_fields = {
    "area": {
        "description": "Garden area a user story applies to.",
        "schema": {
            "type": "string",
            "enum": ["front_yard", "back_yard", "vegetable_bed",
                     "flower_bed", "patio"],
        },
    },
    "start_date": {
        "description": "ISO start date for Gantt rendering.",
        "schema": {"type": "string", "format": "date"},
    },
    "duration": {
        "description": "Duration in days (Gantt).",
        "schema": {"type": "integer", "minimum": 0},
    },
    "status": {
        "description": "Lifecycle status of a need.",
        "schema": {
            "type": "string",
            "enum": [
                # Authoring statuses (mirror the LinkML schema's StatusEnum).
                "open", "in_progress", "implemented", "accepted", "rejected",
                # Test-result statuses pushed in via needs_external_needs.
                "passed", "failed", "skipped",
            ],
        },
    },
}

# Replaces the deprecated needs_extra_links list.
needs_links = {
    "implements": {"incoming": "implemented by", "outgoing": "implements"},
    "verifies":   {"incoming": "verified by",    "outgoing": "verifies"},
    "derives":    {"incoming": "derived by",     "outgoing": "derives from"},
}

# -----------------------------------------------------------------------------
# External test results (per-view).
#
# The pytest run writes ``test_results.json`` with one external need per test,
# linking back to the FR/NFR it verifies. Loading those needs only makes sense
# in views whose toctree actually contains the FR pages — otherwise every link
# resolves to a missing target. Views like ``overview`` deliberately exclude
# requirements; we therefore omit external needs there to avoid bogus warnings
# rather than suppressing them after the fact.
# -----------------------------------------------------------------------------
_results_json = HERE / "_generated" / "test_results.json"
_views_with_test_results = {
    "complete", "detail", "party_prep", "back_yard", "schema",
}
if _results_json.exists() and _VIEW in _views_with_test_results:
    needs_external_needs = [
        {
            "base_url":  "../tests/",
            "json_path": str(_results_json),
            "id_prefix": "",
            "css_class": "external_link",
        }
    ]
else:
    needs_external_needs = []

# -----------------------------------------------------------------------------
# PlantUML — discoverable on PATH inside the docker image and on most CIs.
# -----------------------------------------------------------------------------
plantuml_output_format = "svg"
plantuml = os.environ.get("PLANTUML_CMD", "plantuml")

# -----------------------------------------------------------------------------
# Suppress harmless warnings.
# - toc.not_included: each view loads only its own master_doc, so the index
#   files of other views are correctly listed as 'not included'.
# - toc.excluded: same root cause for explicit exclude_patterns.
# -----------------------------------------------------------------------------
suppress_warnings = [
    "toc.not_included",
    "toc.excluded",
    "toc.not_readable",
]
