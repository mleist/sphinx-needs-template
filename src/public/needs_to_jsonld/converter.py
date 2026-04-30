"""Export sphinx-needs ``needs.json`` as JSON-LD.

The LinkML schema provides the prefix table used in the JSON-LD ``@context``,
so identifiers stay aligned with the rest of the data model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from linkml_runtime.utils.schemaview import SchemaView


class NeedsToJsonLD:
    def __init__(self, schema_path: Path) -> None:
        self.schema_path = Path(schema_path)
        self._sv = SchemaView(str(self.schema_path))

    def convert(self, needs_json: Path, output_jsonld: Path) -> int:
        """Read ``needs.json`` and emit a JSON-LD document next to it.

        Returns the number of needs exported.
        """
        needs_json = Path(needs_json)
        output_jsonld = Path(output_jsonld)
        output_jsonld.parent.mkdir(parents=True, exist_ok=True)

        data = json.loads(needs_json.read_text(encoding="utf-8"))
        versions = data.get("versions") or {}
        if not versions:
            output_jsonld.write_text(json.dumps({"@graph": []}, indent=2),
                                     encoding="utf-8")
            return 0
        latest = list(versions.values())[-1]
        items = latest.get("needs") or {}

        context: dict[str, Any] = {}
        for prefix_name, prefix_obj in self._sv.schema.prefixes.items():
            # Prefix can be a string or a `Prefix` LinkML object with
            # `prefix_reference`. Coerce both shapes to string.
            uri = getattr(prefix_obj, "prefix_reference", None) or str(prefix_obj)
            if uri:
                context[prefix_name] = uri
        # Ensure a default vocabulary so bare keys are interpretable.
        context.setdefault("@vocab", "https://example.com/garden/")

        graph: list[dict[str, Any]] = []
        for need_id, need in items.items():
            graph.append({
                "@id":         f"garden:{need_id}",
                "@type":       need.get("type", "Need"),
                "title":       need.get("title", ""),
                "description": need.get("content") or need.get("description") or "",
                "status":      need.get("status", ""),
                "tags":        need.get("tags") or [],
                "links":       need.get("links") or [],
            })

        document = {"@context": context, "@graph": graph}
        output_jsonld.write_text(json.dumps(document, indent=2),
                                 encoding="utf-8")
        return len(graph)
