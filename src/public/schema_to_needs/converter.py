"""Render LinkML classes themselves as sphinx-needs items.

This produces a ``cls``-typed need per non-abstract class so that the data
model is also visible inside the requirements documentation, with bidirectional
links between ``story``/``uc``/``freq`` items and the class they belong to.
"""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView


def _slugify(name: str) -> str:
    """Convert a CamelCase class name to an upper-snake CLS_* id."""
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.upper())
    return "CLS_" + "".join(out)


class SchemaToNeeds:
    """Render LinkML classes as `cls`-typed sphinx-needs."""

    def __init__(self, schema_path: Path) -> None:
        self.schema_path = Path(schema_path)
        self._sv = SchemaView(str(self.schema_path))

    def render(self, output_md: Path) -> None:
        """Write a single markdown file with one ``cls`` per LinkML class."""
        output_md = Path(output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        lines.append("# Schema (Class Reference)")
        lines.append("")
        lines.append(
            "<!-- AUTO-GENERATED from the LinkML schema. Do not edit by hand. -->"
        )
        lines.append("<!-- Re-run `make generate` after editing the schema YAML. -->")
        lines.append("")
        lines.append(
            "Each class in the LinkML schema is rendered as a `cls`-typed need so it "
            "can be filtered, listed and back-linked from any need page."
        )
        lines.append("")

        for class_name in sorted(self._sv.all_classes()):
            cls = self._sv.get_class(class_name)
            if cls.abstract:
                continue
            # Honour `annotations: hidden_in_docs: true` — used to skip
            # technical helper classes like the tree-root `Container`.
            if self._is_hidden(cls):
                continue
            lines.extend(self._render_class(class_name, cls))
            lines.append("")

        output_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    @staticmethod
    def _is_hidden(cls) -> bool:
        annotations = getattr(cls, "annotations", None) or {}
        ann = annotations.get("hidden_in_docs") if hasattr(annotations, "get") else None
        if ann is None:
            return False
        # LinkML annotations may be raw values or wrapped in `Annotation` objects
        # exposing a `.value` attribute. Accept any truthy form.
        value = getattr(ann, "value", ann)
        return str(value).lower() in {"true", "1", "yes"}

    def _render_class(self, name: str, cls) -> list[str]:
        cls_id = _slugify(name)
        title = name
        # Direct parents only (skip the abstract `Need` from the inherits-list
        # because every concrete class inherits from it; tagging on it adds
        # no signal).
        parents = [p for p in self._sv.class_ancestors(name)[1:] if p != "Need"]
        # Slot inventory (induced – includes inherited slots).
        slots = self._sv.class_induced_slots(name)
        description = (cls.description or "").strip()

        out: list[str] = []
        out.append(f"```{{cls}} {title}")
        out.append(f":id: {cls_id}")
        if parents:
            out.append(":tags: " + ";".join(p.lower() for p in parents))
        out.append("")
        if description:
            out.append(description)
            out.append("")
        if slots:
            out.append("**Slots**")
            out.append("")
            for s in slots:
                req = " *(required)*" if s.required else ""
                rng = f" → `{s.range}`" if s.range else ""
                out.append(f"- `{s.name}`{rng}{req}")
            out.append("")
        if parents:
            out.append("**Inherits from:** " + ", ".join(parents) + " (transitively from `Need`)")
        else:
            out.append("**Inherits from:** `Need`")
        out.append("```")
        return out
