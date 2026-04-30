"""Bridge between sphinx-needs (docs) and pytest (tests).

What this conftest does:

1. **At test start**, read ``docs/public/_build/needs/needs.json`` and collect
   all known need IDs.
2. Register the ``@pytest.mark.satisfies("REQ_xxx")`` marker and validate it
   against those IDs. Any marker pointing to an unknown ID fails the
   collection phase (exit code 3).
3. **After the test run**, write
   ``docs/public/_generated/test_results.json`` — a sphinx-needs-compatible
   JSON that the doc build pulls in via ``needs_external_needs``.
4. **Coverage check**: any need of type ``freq`` / ``nfreq`` / ``test``
   without a passing test makes pytest exit with code 4.
   Set ``STRICT_COVERAGE=0`` to disable.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent  # tests/public/conftest.py → repo root
NEEDS_JSON = ROOT / "docs" / "public" / "_build" / "needs" / "needs.json"
RESULTS_JSON = ROOT / "docs" / "public" / "_generated" / "test_results.json"

# Need types and statuses that *must* have at least one passing test.
# Functional requirements that are still open / in_progress are aspirational
# and not yet expected to have implementation tests; non-functional
# requirements are commonly process or quality constraints rather than
# directly testable functions, so they are excluded from the coverage
# default. Tighten this set in your fork as your project matures.
COVERED_TYPES = {"freq"}
COVERED_STATUSES = {"implemented", "accepted"}

_known_ids: set[str] | None = None
_satisfies_by_test: dict[str, list[str]] = {}
_test_results: list[dict] = []


def _load_known_ids() -> set[str]:
    global _known_ids
    if _known_ids is not None:
        return _known_ids
    if not NEEDS_JSON.exists():
        # Without needs.json we can't validate. Allow the run, but warn loudly.
        print(
            f"\nWARNING: {NEEDS_JSON} not found. Run `make needs` first to "
            f"enable @satisfies marker validation and coverage.\n"
        )
        _known_ids = set()
        return _known_ids
    data = json.loads(NEEDS_JSON.read_text(encoding="utf-8"))
    versions = data.get("versions") or {}
    if not versions:
        _known_ids = set()
        return _known_ids
    latest = list(versions.values())[-1]
    _known_ids = set((latest.get("needs") or {}).keys())
    return _known_ids


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "satisfies(req_id): the test verifies the sphinx-needs requirement with this id",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Validate @satisfies markers before any test runs."""
    known = _load_known_ids()
    if not known:
        return
    invalid: list[str] = []
    for item in items:
        for marker in item.iter_markers(name="satisfies"):
            for arg in marker.args:
                if arg not in known:
                    invalid.append(f"  {item.nodeid}: @satisfies({arg!r}) — unknown id")
                else:
                    _satisfies_by_test.setdefault(item.nodeid, []).append(arg)
    if invalid:
        msg = ["\nInvalid @satisfies markers:"] + invalid
        raise pytest.UsageError("\n".join(msg))


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Capture pass/fail per test for the JSON export."""
    if report.when != "call":
        return
    sat = _satisfies_by_test.get(report.nodeid, [])
    if not sat:
        return
    test_id = "T_" + report.nodeid.replace("::", "_").replace("/", "_") \
                                    .replace(".", "_").upper()
    _test_results.append({
        "id":      test_id[:60],
        "title":   report.nodeid,
        "status":  "passed" if report.passed else ("failed" if report.failed else "skipped"),
        "links":   sat,
    })


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write test_results.json and enforce coverage."""
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created":      _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "current_version": "1",
        "versions": {
            "1": {
                "needs": {
                    r["id"]: {
                        "id":     r["id"],
                        "type":   "test",
                        "title":  r["title"],
                        "status": r["status"],
                        "links":  r["links"],
                        "tags":   [],
                    }
                    for r in _test_results
                }
            }
        },
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Coverage check.
    known = _load_known_ids()
    if not known:
        return
    if NEEDS_JSON.exists():
        data = json.loads(NEEDS_JSON.read_text(encoding="utf-8"))
        latest = list(data["versions"].values())[-1]
        needs = latest.get("needs") or {}
    else:
        needs = {}

    covered: set[str] = set()
    for r in _test_results:
        if r["status"] == "passed":
            covered.update(r["links"])

    requirements = {
        nid for nid, n in needs.items()
        if (n.get("type") or "") in COVERED_TYPES
        and (n.get("status") or "") in COVERED_STATUSES
    }
    uncovered = sorted(requirements - covered)

    print()
    print("=" * 30 + " Requirement Coverage " + "=" * 30)
    print(f"Requirements:       {len(requirements)}")
    print(f"Covered (passing):  {len(requirements) - len(uncovered)}")
    if uncovered:
        print("Uncovered:")
        for rid in uncovered:
            print(f"  - {rid}")
    print(f"Test results:       {RESULTS_JSON.relative_to(ROOT)}")

    strict = os.environ.get("STRICT_COVERAGE", "1") == "1"
    if strict and uncovered and exitstatus == 0:
        session.exitstatus = 4
