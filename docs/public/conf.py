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
- ``view_schedule``       — Gantt timeline of use cases and requirements

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
# Language switch (DOCS_LANG environment variable)
# -----------------------------------------------------------------------------
# DOCS_LANG=en (default)  → English UI strings, English Gantt labels
# DOCS_LANG=de            → German Sphinx UI strings (TOC headings, search,
#                           "Chapter" → "Kapitel", ...), German Gantt labels
#                           ("May 2026" → "Mai 2026", "Mo Tu We" → "Mo Di Mi"),
#                           and German need-type titles ("Use Case" →
#                           "Anwendungsfall" etc.).
#
# Demo content (user stories, requirements, tests) stays in English regardless
# of DOCS_LANG — that's a deliberate choice so the gardening example remains
# consistent.  When you fork the template for a real German project, you'd
# rewrite the content in your data files and toggle DOCS_LANG=de to align the
# rendering.
_SUPPORTED_LANGS = {"en", "de"}
_DOCS_LANG = os.environ.get("DOCS_LANG", "en").lower()
if _DOCS_LANG not in _SUPPORTED_LANGS:
    raise RuntimeError(
        f"DOCS_LANG={_DOCS_LANG!r} is not supported. "
        f"Set it to one of: {sorted(_SUPPORTED_LANGS)}."
    )
language = _DOCS_LANG

# Per-need-type titles. The directive name and prefix do NOT change — only
# the human-readable title that appears in tables, headings and badges.
# Add a row here when you introduce a new need type.
_NEED_TYPE_TITLES = {
    "en": {
        "story":         "User Story",
        "uc":            "Use Case",
        "freq":          "Functional Requirement",
        "nfreq":         "Non-Functional Requirement",
        "test":          "Test",
        "risk":          "Risk",
        "decision":      "Decision",
        "glossary_term": "Glossary Term",
        "cls":           "LinkML Class",
    },
    "de": {
        "story":         "User Story",                # eingebürgertes Fachwort
        "uc":            "Anwendungsfall",
        "freq":          "Funktionale Anforderung",
        "nfreq":         "Nicht-funktionale Anforderung",
        "test":          "Test",
        "risk":          "Risiko",
        "decision":      "Entscheidung",
        "glossary_term": "Glossarbegriff",
        "cls":           "LinkML-Klasse",
    },
}


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
                 "party_prep", "back_yard", "schema", "schedule"):
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
    "schedule":   "views/index_schedule",
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
    # Allow line wrapping inside long inline-code spans (e.g. need IDs like
    # ``T_MOWING_WARM_AND_DRY_IS_OK``) so they don't run past column edges
    # in PDF tables.
    "sphinxsetup": "verbatimwrapslines=true",
}

# -----------------------------------------------------------------------------
# sphinx-needs configuration
# -----------------------------------------------------------------------------
needs_types = [
    {"directive": "story",          "title": _NEED_TYPE_TITLES[language]["story"],         "prefix": "US_",  "color": "#FFD8A8", "style": "node"},
    {"directive": "uc",             "title": _NEED_TYPE_TITLES[language]["uc"],            "prefix": "UC_",  "color": "#A8D8FF", "style": "node"},
    {"directive": "freq",           "title": _NEED_TYPE_TITLES[language]["freq"],          "prefix": "FR_",  "color": "#BFD8D2", "style": "node"},
    {"directive": "nfreq",          "title": _NEED_TYPE_TITLES[language]["nfreq"],         "prefix": "NFR_", "color": "#D2BFD8", "style": "node"},
    {"directive": "test",           "title": _NEED_TYPE_TITLES[language]["test"],          "prefix": "T_",   "color": "#D8D2BF", "style": "node"},
    {"directive": "risk",           "title": _NEED_TYPE_TITLES[language]["risk"],          "prefix": "RSK_", "color": "#FFB8B8", "style": "node"},
    {"directive": "decision",       "title": _NEED_TYPE_TITLES[language]["decision"],      "prefix": "DEC_", "color": "#B8FFB8", "style": "node"},
    {"directive": "glossary_term",  "title": _NEED_TYPE_TITLES[language]["glossary_term"], "prefix": "G_",   "color": "#E0E0E0", "style": "node"},
    {"directive": "cls",            "title": _NEED_TYPE_TITLES[language]["cls"],           "prefix": "CLS_", "color": "#C0E0FF", "style": "node"},
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
    "completion": {
        "description": "Completion percentage for Gantt rendering (0-100).",
        "schema": {"type": "integer", "minimum": 0, "maximum": 100},
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
    "complete", "detail", "party_prep", "back_yard", "schema", "schedule",
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
plantuml_latex_output_format = "svg_pdf"
# In LaTeX builds we want vector PDF embedding for sharp Gantt diagrams.
# `svg_pdf` makes sphinxcontrib-plantuml emit SVG and then convert it to PDF
# at build time using rsvg-convert (provided by `librsvg2-bin` in the image).
plantuml_latex_output_format = "svg_pdf"

# Build the PlantUML invocation. We use `-config <file>` to inject a small
# preamble file that PlantUML loads before every diagram. The preamble
# contains:
#   - a `language <code>` line for non-English locales (Gantt month names,
#     weekday abbreviations, ...)
#   - any user-supplied skin parameters from
#     `docs/private/plantuml_preamble.iuml`, if that file exists.
# This is the supported PlantUML mechanism for global per-document settings.
def _build_plantuml_preamble() -> str | None:
    """Write a temporary PlantUML preamble file and return its absolute path.

    Returns ``None`` if there is nothing to inject (English language and no
    private preamble file). The caller appends ``-config <path>`` to the
    `plantuml` command only when this returns a path.
    """
    lines: list[str] = []
    if language and language != "en":
        lines.append(f"language {language}")

    private_preamble = HERE.parent / "private" / "plantuml_preamble.iuml"
    if private_preamble.is_file():
        # PlantUML can `!include` other files; using that directive keeps the
        # preamble file authoritative and editable in place.
        lines.append(f"!include {private_preamble}")

    if not lines:
        return None

    out = HERE / "_generated" / "plantuml-preamble.iuml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out)

_plantuml_cmd = os.environ.get("PLANTUML_CMD", "plantuml")
_preamble = _build_plantuml_preamble()
plantuml = f"{_plantuml_cmd} -config {_preamble}" if _preamble else _plantuml_cmd

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

# -----------------------------------------------------------------------------
# Private theme overrides (Hybrid B+C — see docs/private/README.md)
#
# Each of the four hooks below is OPTIONAL. When a file is present under
# docs/private/, it is applied; when it is missing, the default behaviour
# stays intact. This lets a user maintain their own corporate / project
# theme outside the public template repository.
#
#   docs/private/static/                 → added to html_static_path
#   docs/private/latex_preamble.tex      → appended to latex_elements["preamble"]
#   docs/private/plantuml_preamble.iuml  → loaded by every PlantUML diagram
#                                           (handled above in _build_plantuml_preamble)
#   docs/private/conf_overrides.py       → free-form Python; exports
#                                           `update(globals_: dict) -> None`
# -----------------------------------------------------------------------------
_PRIVATE_DIR = HERE.parent / "private"

# 1. Static assets (CSS, fonts, logos) ---------------------------------------
_private_static = _PRIVATE_DIR / "static"
if _private_static.is_dir():
    # html_static_path entries are resolved relative to the source dir
    # (docs/public/), so we use a relative path string.
    html_static_path = list(html_static_path) + [str(_private_static.relative_to(HERE))]

# 2. LaTeX preamble snippet --------------------------------------------------
_private_latex_preamble = _PRIVATE_DIR / "latex_preamble.tex"
if _private_latex_preamble.is_file():
    extra = _private_latex_preamble.read_text(encoding="utf-8")
    latex_elements["preamble"] = (latex_elements.get("preamble", "") or "") + "\n" + extra

# 3. Free-form Python overrides ----------------------------------------------
# Imported via importlib (no exec()) so syntax errors surface with a useful
# traceback. The module must define `update(globals_: dict) -> None`.
_private_conf_overrides = _PRIVATE_DIR / "conf_overrides.py"
if _private_conf_overrides.is_file():
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("private_conf_overrides",
                                         _private_conf_overrides)
    if _spec is not None and _spec.loader is not None:
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        if hasattr(_mod, "update") and callable(_mod.update):
            _mod.update(globals())
        else:
            raise RuntimeError(
                f"{_private_conf_overrides} must define "
                "`def update(globals_: dict) -> None`."
            )

# -----------------------------------------------------------------------------
# Monkey-patch: fix doubled Gantt bars with sphinx-needs 8.x + PlantUML 1.2026+
#
# Background
# ~~~~~~~~~~
# sphinx-needs 8.0.0 (`sphinx_needs/directives/needgantt.py`) builds the
# PlantUML script for `{needgantt}` like this:
#
#   [Display title] as [NEED_ID] lasts N days        ← defines the task
#   [Display title] is 100% completed                ← style command
#   [Display title] is colored in #RRGGBB            ← style command
#
# In PlantUML 1.2026.x the gantt parser interprets a follow-up line that
# starts with `[Display title]` as a NEW task definition because the
# original task is registered under its alias `[NEED_ID]`. Each need ends
# up rendered TWICE: once with the bar (right-anchored title), once
# without a bar (left-anchored label) — the doubled-bar effect that
# shows up in the SVG.
#
# Older PlantUML versions (e.g. 1.2020 from Ubuntu apt) silently
# matched the title back to the existing alias and produced a single
# bar. The strict matching in 1.2026 surfaces the mismatch.
#
# Fix
# ~~~
# We wrap `process_needgantt` and post-process its emitted ``uml`` string:
# for every `[Display title] is colored in ...` and `[Display title] is
# N% completed` line we substitute the display title with the matching
# need ID, picking the mapping from the `as [ID]` part of the
# task-definition lines that appear earlier in the same script.
#
# When sphinx-needs upstream fixes the bug (writing the alias directly
# in style commands), the regex below will simply match nothing and the
# patch becomes a no-op — no future cleanup needed.
# -----------------------------------------------------------------------------
def _patch_needgantt_alias_styles() -> None:
    """Install the post-processing wrapper around process_needgantt.

    sphinx-needs dispatches `{needgantt}` rendering through a dictionary
    `sphinx_needs.needs.NODE_TYPES`, looked up at event-dispatch time
    rather than via a closure-captured reference. We replace the entry
    for `Needgantt` so the dispatcher picks up the wrapper without us
    having to disconnect/reconnect the Sphinx event handler.

    The wrapper performs three post-processing steps on the PlantUML
    script that sphinx-needs builds:

    1. **Project-start month fix** — corrects the off-by-one indexing
       into `MONTH_NAMES` in sphinx-needs 8.0.0 that turns April into
       "May", November into "December", and crashes on December. The
       fix only triggers when the buggy expression is detected in the
       installed `process_needgantt` source, so it self-disables when
       upstream lands a fix.

    2. **Style-line alias rewrite** — `[Title] is colored …` and
       `[Title] is N% completed` become `[ID] is colored …` etc.
       Reason: with sphinx-needs 8.x and PlantUML 1.2026.x, style
       commands keyed on the display title get parsed as new task
       definitions, which doubles every bar.

    3. **Per-task start date injection** — for every need that has a
       `start_date` field set, an extra line `[ID] starts the YYYY-MM-DD`
       is inserted right after the task definition. Reason: sphinx-needs
       8.x emits only `lasts N days` and never reads back the per-need
       `start_date`, so PlantUML places every bar at the project origin
       and chains them sequentially. Reading the field from `app.env`
       and injecting an explicit `starts the` line restores correct
       calendar placement.

    All three rewrites become no-ops the day sphinx-needs upstream
    fixes the underlying issues; the patch then leaves the script
    untouched.
    """
    import re
    from sphinx_needs import needs as _sn_needs
    from sphinx_needs.directives import needgantt as _ng
    from sphinx_needs.directives.needgantt import Needgantt

    _original = _ng.process_needgantt

    # Matches a task-definition line and captures (title, id).
    _DEFINE_RE = re.compile(r"^\[(.+?)\] as \[([^\]]+)\] lasts ", re.MULTILINE)

    # ---- sphinx-needs 8.0.0 month off-by-one bug detection ----------------
    # In sphinx-needs 8.0.0 (`needgantt.py` ~line 237) the project start
    # line is built with `MONTH_NAMES[int(start_date.strftime("%m"))]`,
    # but `MONTH_NAMES` is 0-indexed — so April (month 4) becomes "May",
    # December crashes with IndexError. We probe the source string of
    # `process_needgantt` for that exact buggy expression, so the fix
    # self-disables the day sphinx-needs lands a correct version.
    import inspect as _inspect
    from sphinx_needs.utils import MONTH_NAMES as _MONTH_NAMES
    try:
        _ng_src = _inspect.getsource(_original)
        _HAS_MONTH_BUG = (
            'MONTH_NAMES[int(start_date.strftime("%m"))]' in _ng_src
        )
    except (OSError, TypeError):
        _HAS_MONTH_BUG = False

    _PROJECT_START_RE = re.compile(
        r"^(Project starts the )(\d+)(th of )([A-Z][a-z]+)( \d{4})$",
        re.MULTILINE,
    )

    def _shift_month_back(buggy_name: str) -> str | None:
        """Return the month one position earlier in `MONTH_NAMES`, or
        `None` if the input is not a recognised name. The bug shifts
        every actual month forward by one, so January (the only name
        that cannot occur as a buggy output) is the only edge case
        we treat as "leave alone"."""
        try:
            idx = _MONTH_NAMES.index(buggy_name)
        except ValueError:
            return None
        if idx == 0:
            return None
        return _MONTH_NAMES[idx - 1]
    # ----------------------------------------------------------------------

    def _rewrite_uml(uml: str, start_dates: dict[str, str]) -> str:
        """Apply both style rewrite and start-date injection."""
        # Step 0 — fix the buggy `Project starts the …` line emitted by
        # sphinx-needs 8.0.0 (off-by-one into MONTH_NAMES). No-op when
        # the bug isn't present in the installed version.
        if _HAS_MONTH_BUG:
            def _fix_project(m: "re.Match[str]") -> str:
                prefix, day, mid, month, suffix = m.groups()
                corrected = _shift_month_back(month)
                if corrected is None:
                    return m.group(0)
                return f"{prefix}{day}{mid}{corrected}{suffix}"
            uml = _PROJECT_START_RE.sub(_fix_project, uml)

        title_to_id: dict[str, str] = {
            m.group(1): m.group(2) for m in _DEFINE_RE.finditer(uml)
        }
        if not title_to_id:
            return uml

        out: list[str] = []
        for line in uml.splitlines():
            stripped = line.strip()

            # Step 1 — task definition: keep as-is, but optionally insert
            # a `[ID] starts the YYYY-MM-DD` line right after it.
            def_match = _DEFINE_RE.match(stripped)
            if def_match:
                out.append(line)
                _, need_id = def_match.group(1), def_match.group(2)
                start_date = start_dates.get(need_id)
                if start_date:
                    indent = line[: len(line) - len(line.lstrip())]
                    out.append(f"{indent}[{need_id}] starts {start_date}")
                continue

            # Step 2 — style follow-up lines: rewrite [Title] → [ID].
            is_color_cmd = stripped.startswith("[") and " is colored " in stripped
            is_completion_cmd = (
                stripped.startswith("[")
                and " is " in stripped
                and "% completed" in stripped
            )
            if is_color_cmd or is_completion_cmd:
                m = re.match(r"^(\s*)\[(.+?)\](.*)$", line)
                if m:
                    indent, title, rest = m.group(1), m.group(2), m.group(3)
                    if title in title_to_id:
                        out.append(f"{indent}[{title_to_id[title]}]{rest}")
                        continue
            out.append(line)

        # Preserve a trailing newline if the original had one.
        return "\n".join(out) + ("\n" if uml.endswith("\n") else "")

    def _collect_start_dates(app) -> dict[str, str]:  # noqa: ANN001
        """Build a `need_id -> start_date` lookup from `app.env`.

        Each plotted bar's start date comes from the LinkML data files or
        from the hand-written `:start_date:` option on FR/NFR directives.
        sphinx-needs stores it as a plain field on the resolved need.
        """
        try:
            from sphinx_needs.data import SphinxNeedsData
        except ImportError:
            return {}
        try:
            needs = SphinxNeedsData(app.env).get_needs_view()
        except Exception:  # pragma: no cover — env not ready yet
            return {}
        out: dict[str, str] = {}
        for need_id, need in needs.items():
            sd = need.get("start_date")
            if sd:
                out[need_id] = str(sd)
        return out

    def _wrapped(app, doctree, fromdocname, found_nodes):  # noqa: ANN001
        result = _original(app, doctree, fromdocname, found_nodes)
        try:
            from sphinxcontrib.plantuml import plantuml as _puml_node
        except ImportError:
            return result
        start_dates = _collect_start_dates(app)
        for node in doctree.findall(_puml_node):
            uml = node.get("uml") or ""
            if "@startgantt" not in uml:
                continue
            node["uml"] = _rewrite_uml(uml, start_dates)
        return result

    # Replace both the function reference (so future imports see it) and
    # the dispatch table entry (so already-registered Sphinx handlers
    # pick up the new function).
    _ng.process_needgantt = _wrapped
    _sn_needs.NODE_TYPES[Needgantt] = _wrapped


# Install the patch at import time so it is in place before
# Sphinx fires `builder-inited` and any other lifecycle events.
_patch_needgantt_alias_styles()


def setup(app):  # noqa: ANN001 (Sphinx API)
    """Sphinx entry point. The monkey-patch is installed at module
    import time (above); this `setup()` exists so Sphinx recognises
    `conf.py` as an extension and can record the version metadata."""
    return {"version": release, "parallel_read_safe": True,
            "parallel_write_safe": True}
