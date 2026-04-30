"""Command-line interface for ``needs-from-linkml``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import NeedsFromLinkML


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="needs-from-linkml",
        description="Convert LinkML YAML data into MyST sphinx-needs markdown.",
    )
    p.add_argument("data_dir", type=Path,
                   help="Directory with one or more *.yaml data files.")
    p.add_argument("-s", "--schema", type=Path, required=True,
                   help="Path to the LinkML schema (.yaml).")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="Output directory for generated .md files.")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress non-error output.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.schema.is_file():
        print(f"error: schema not found: {args.schema}", file=sys.stderr)
        return 2
    if not args.data_dir.is_dir():
        print(f"error: data dir not found: {args.data_dir}", file=sys.stderr)
        return 2

    conv = NeedsFromLinkML(args.schema)
    written = conv.convert_directory(args.data_dir, args.output)

    if not args.quiet:
        for p in written:
            print(f"  wrote {p}")
        print(f"{len(written)} file(s) generated in {args.output}")
    return 0
