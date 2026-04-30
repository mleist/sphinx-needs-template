"""CLI for ``schema-to-needs``."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import SchemaToNeeds


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="schema-to-needs",
        description="Render LinkML classes as sphinx-needs `cls` items.",
    )
    p.add_argument("schema", type=Path, help="Path to the LinkML schema (.yaml).")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="Output markdown file.")
    args = p.parse_args(argv)

    if not args.schema.is_file():
        print(f"error: schema not found: {args.schema}", file=sys.stderr)
        return 2

    SchemaToNeeds(args.schema).render(args.output)
    print(f"  wrote {args.output}")
    return 0
