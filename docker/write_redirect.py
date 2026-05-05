#!/usr/bin/env python3
"""Write a simple ``index.html`` redirect into a built HTML view.

Each Sphinx view has a different master_doc (``index_complete.html``,
``views/index_party_prep.html``, ...). Browsers open ``index.html`` by
default, so we drop a tiny redirect file at the build root that points to
the active view's master_doc. This keeps the URL of the entry page
predictable across views.
"""
from __future__ import annotations

import sys
from pathlib import Path

# View → relative master_doc html path (must match conf.py).
MASTER_DOC = {
    "complete":   "index_complete.html",
    "overview":   "index_overview.html",
    "detail":     "index_detail.html",
    "party_prep": "views/index_party_prep.html",
    "back_yard":  "views/index_back_yard.html",
    "schema":     "views/index_schema.html",
    "schedule":   "views/index_schedule.html",
}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: write_redirect.py <view> <build_dir>", file=sys.stderr)
        return 2
    view, build_dir = argv[1], Path(argv[2])
    target = MASTER_DOC.get(view)
    if not target:
        print(f"unknown view: {view}", file=sys.stderr)
        return 2
    redirect = (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        f"    <meta http-equiv=\"refresh\" content=\"0; url={target}\">\n"
        f"    <link rel=\"canonical\" href=\"{target}\">\n"
        f"    <title>Redirecting to {target}</title>\n"
        "  </head>\n"
        f"  <body>Redirecting to <a href=\"{target}\">{target}</a>.</body>\n"
        "</html>\n"
    )
    (build_dir / "index.html").write_text(redirect, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
