"""LinkML data → MyST markdown converter for sphinx-needs.

The converter reads YAML data files from a directory, validates each entry
against the LinkML schema, and emits one ``.md`` file per data file containing
sphinx-needs MyST directives.

Example output for one ``UserStory``::

    ```{story} Keep the back-yard lawn freshly cut
    :id: US_MOW_LAWN
    :area: back_yard
    :tags: mowing;weekly
    :status: accepted

    As a **homeowner** I want my back-yard lawn mowed weekly...
    ```
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from linkml_runtime.utils.schemaview import SchemaView


# Maps LinkML class names to the sphinx-needs directive name.
# Keep in sync with `needs_types` in docs/public/conf.py.
_DIRECTIVE_FOR_CLASS = {
    "UserStory":               "story",
    "UseCase":                 "uc",
    "FunctionalRequirement":   "freq",
    "NonFunctionalRequirement": "nfreq",
    "Test":                    "test",
    "Risk":                    "risk",
    "Decision":                "decision",
    "GlossaryTerm":            "glossary_term",
}

# Display titles for the generated .md files.
_PAGE_TITLE = {
    "UserStory":                "User Stories",
    "UseCase":                  "Use Cases",
    "FunctionalRequirement":    "Functional Requirements",
    "NonFunctionalRequirement": "Non-Functional Requirements",
    "Test":                     "Tests",
    "Risk":                     "Risks",
    "Decision":                 "Decisions",
    "GlossaryTerm":             "Glossary",
}

# LinkML classes for which the generator emits a level-2 markdown heading
# (`## ID — TITLE`) in front of each need block. The heading puts the item
# into the PDF table of contents as a sub-entry of the page title.
_PER_ITEM_HEADING_CLASSES = {"UserStory", "UseCase"}

# Fields that are part of the directive *option block* (``:foo: value`` lines).
# Order matters for human readability and for stable diffs.
_OPTION_SLOTS_ORDER = [
    "id",
    "status",
    "tags",
    "area",
    "start_date",
    "duration",
    "completion",
    "implements",
    "verifies",
    "derives",
    "links",
]

# Lists are rendered semicolon-separated in sphinx-needs option lines.
_LIST_OPTION_SLOTS = {"tags", "implements", "verifies", "derives", "links"}


@dataclass
class _Item:
    """One concrete data row, paired with its LinkML class name."""
    cls: str
    data: dict[str, Any]


class NeedsFromLinkML:
    """High-level converter."""

    def __init__(self, schema_path: Path) -> None:
        self.schema_path = Path(schema_path)
        self._sv = SchemaView(str(self.schema_path))
        # Build directive lookup once.
        self._directive = dict(_DIRECTIVE_FOR_CLASS)
        # Permissible-value sets per enum (used to coerce enum objects to strings).
        self._enum_values: dict[str, set[str]] = {
            name: set(self._sv.get_enum(name).permissible_values or {})
            for name in self._sv.all_enums()
        }

    # ------------------------------------------------------------------ public
    def convert_directory(self, data_dir: Path, out_dir: Path) -> list[Path]:
        """Walk ``data_dir`` for ``*.yaml`` and emit one ``.md`` per file.

        The output filename is derived from the YAML filename (e.g.
        ``stories.yaml`` → ``stories.md``).
        """
        data_dir = Path(data_dir)
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        for yaml_path in sorted(data_dir.glob("*.yaml")):
            items = self._load_items(yaml_path)
            if not items:
                continue
            md_path = out_dir / (yaml_path.stem + ".md")
            self._write_markdown(md_path, items, source=yaml_path.name)
            written.append(md_path)
        return written

    # ------------------------------------------------------------------ loaders
    def _load_items(self, yaml_path: Path) -> list[_Item]:
        with yaml_path.open(encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}

        items: list[_Item] = []
        for top_key, rows in doc.items():
            if not isinstance(rows, list):
                continue
            cls_name = self._resolve_class_for_collection(top_key)
            for row in rows:
                items.append(_Item(cls=cls_name, data=row))
        return items

    # Top-level YAML keys → LinkML class names.
    # Plural / snake_case forms used in data files map to the canonical class.
    _COLLECTION_ALIASES = {
        "stories":                    "UserStory",
        "user_stories":               "UserStory",
        "use_cases":                  "UseCase",
        "usecases":                   "UseCase",
        "functional_requirements":    "FunctionalRequirement",
        "freqs":                      "FunctionalRequirement",
        "non_functional_requirements": "NonFunctionalRequirement",
        "nfreqs":                     "NonFunctionalRequirement",
        "tests":                      "Test",
        "risks":                      "Risk",
        "decisions":                  "Decision",
        "glossary":                   "GlossaryTerm",
        "glossary_terms":             "GlossaryTerm",
    }

    def _resolve_class_for_collection(self, key: str) -> str:
        """Map a top-level YAML key (e.g. ``stories``) to a LinkML class name.

        Falls back to direct CamelCase lookup if ``key`` is itself a class.
        """
        cls = self._COLLECTION_ALIASES.get(key)
        if cls is None and key in self._sv.all_classes():
            cls = key
        if cls is None:
            raise ValueError(
                f"YAML key '{key}' is not a known data collection. "
                f"Known aliases: {sorted(self._COLLECTION_ALIASES)}; "
                f"known classes: {sorted(self._sv.all_classes())}"
            )
        return cls

    # ------------------------------------------------------------------ emitters
    def _write_markdown(self, path: Path, items: Iterable[_Item], source: str) -> None:
        items = list(items)
        # Use the first class as the page title; mixed-class files are unusual
        # in this template, but supported.
        first_cls = items[0].cls
        title = _PAGE_TITLE.get(first_cls, first_cls)

        lines: list[str] = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"<!-- AUTO-GENERATED from `{source}`. Do not edit by hand. -->")
        lines.append("<!-- Re-run `make generate` after editing the source YAML. -->")
        lines.append("")

        for item in items:
            lines.extend(self._render_item(item))
            lines.append("")

        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _render_item(self, item: _Item) -> list[str]:
        directive = self._directive.get(item.cls)
        if directive is None:
            raise ValueError(
                f"No sphinx-needs directive mapped for LinkML class '{item.cls}'."
            )
        d = item.data
        title = d.get("title", "")
        item_id = d.get("id", "")
        body = (d.get("description") or "").strip()

        out: list[str] = []
        # For user stories and use cases, emit a level-2 markdown heading
        # before the need block so each item shows up in the PDF table of
        # contents as a sub-entry of the page title. Format: `## ID — TITLE`.
        # Functional and non-functional requirements are kept without a
        # per-item heading on purpose — they are written by hand in
        # `reqs/functional.md` and `reqs/nonfunctional.md`, where headings
        # can be added directly when needed.
        if item.cls in _PER_ITEM_HEADING_CLASSES and item_id and title:
              out.append(f"## {item_id} — {title}")
              out.append("")
        out.append(f"```{{{directive}}} {title}")
        for slot in _OPTION_SLOTS_ORDER:
            if slot not in d or d[slot] in (None, "", []):
                continue
            value = d[slot]
            if slot in _LIST_OPTION_SLOTS and isinstance(value, list):
                rendered = ";".join(self._stringify(v) for v in value)
            else:
                rendered = self._stringify(value)
            out.append(f":{slot}: {rendered}")
        out.append("")
        if body:
            out.append(body)
        out.append("```")
        return out

    def _stringify(self, value: Any) -> str:
        """Render scalars and enum values as strings.

        LinkML loads enum values as ``PermissibleValue`` instances; we
        accept both raw strings (loaded with ``yaml.safe_load``) and
        objects exposing ``.text`` or ``.code``.
        """
        if hasattr(value, "text") and value.text is not None:
            return str(value.text)
        if hasattr(value, "code") and value.code is not None:
            return str(value.code)
        return str(value)
