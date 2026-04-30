"""CLI for ``needs-to-jsonld``."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import NeedsToJsonLD


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="needs-to-jsonld",
        description="Convert sphinx-needs needs.json into a JSON-LD document.",
    )
    p.add_argument("needs_json", type=Path, help="Path to needs.json.")
    p.add_argument("-s", "--schema", type=Path, required=True,
                   help="LinkML schema (its `prefixes` are reused as @context).")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="Output JSON-LD file.")
    args = p.parse_args(argv)

    if not args.needs_json.is_file():
        print(f"error: needs.json not found: {args.needs_json}", file=sys.stderr)
        return 2
    if not args.schema.is_file():
        print(f"error: schema not found: {args.schema}", file=sys.stderr)
        return 2

    n = NeedsToJsonLD(args.schema).convert(args.needs_json, args.output)
    print(f"  exported {n} need(s) → {args.output}")
    return 0
