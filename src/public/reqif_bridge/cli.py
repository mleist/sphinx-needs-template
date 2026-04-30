"""CLI for ``reqif-bridge``: import or export ReqIF."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .converter import import_reqif, export_reqif, needs_json_to_dicts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="reqif-bridge",
        description="Import or export ReqIF for sphinx-needs items.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_imp = sub.add_parser("import", help="ReqIF file → JSON list of need dicts")
    p_imp.add_argument("reqif", type=Path)
    p_imp.add_argument("-o", "--output", type=Path, required=True)

    p_exp = sub.add_parser("export", help="needs.json → ReqIF file")
    p_exp.add_argument("needs_json", type=Path)
    p_exp.add_argument("-o", "--output", type=Path, required=True)

    args = p.parse_args(argv)

    if args.cmd == "import":
        if not args.reqif.is_file():
            print(f"error: file not found: {args.reqif}", file=sys.stderr)
            return 2
        needs = import_reqif(args.reqif)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(needs, indent=2), encoding="utf-8")
        print(f"  imported {len(needs)} need(s) → {args.output}")
        return 0

    if args.cmd == "export":
        if not args.needs_json.is_file():
            print(f"error: file not found: {args.needs_json}", file=sys.stderr)
            return 2
        needs = needs_json_to_dicts(args.needs_json)
        export_reqif(needs, args.output)
        print(f"  exported {len(needs)} need(s) → {args.output}")
        return 0

    return 1
