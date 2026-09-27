#!/usr/bin/env python3
"""Compare two Rhino model metric JSON files and assert selected paths.

This script has no Rhino dependency. A path uses dot-separated dictionary keys
and integer list indexes, for example ``bbox.max.2``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


MISSING = object()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def values_equal(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)
    return left == right


def walk_diff(left: Any, right: Any, path: str, tolerance: float) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else str(key)
            if key not in left:
                changes.append({"path": child, "kind": "added", "after": right[key]})
            elif key not in right:
                changes.append({"path": child, "kind": "removed", "before": left[key]})
            else:
                changes.extend(walk_diff(left[key], right[key], child, tolerance))
        return changes
    if isinstance(left, list) and isinstance(right, list):
        for index in range(max(len(left), len(right))):
            child = f"{path}.{index}" if path else str(index)
            if index >= len(left):
                changes.append({"path": child, "kind": "added", "after": right[index]})
            elif index >= len(right):
                changes.append({"path": child, "kind": "removed", "before": left[index]})
            else:
                changes.extend(walk_diff(left[index], right[index], child, tolerance))
        return changes
    if not values_equal(left, right, tolerance):
        changes.append({"path": path or "$", "kind": "changed", "before": left, "after": right})
    return changes


def lookup(value: Any, path: str) -> Any:
    current = value
    for token in path.split(".") if path else []:
        if isinstance(current, dict):
            current = current.get(token, MISSING)
        elif isinstance(current, list) and token.isdigit():
            index = int(token)
            current = current[index] if index < len(current) else MISSING
        else:
            return MISSING
        if current is MISSING:
            return MISSING
    return current


def expectation_result(
    baseline: Any,
    changed: Any,
    path: str,
    should_change: bool,
    tolerance: float,
) -> dict[str, Any]:
    before = lookup(baseline, path)
    after = lookup(changed, path)
    exists = before is not MISSING and after is not MISSING
    observed_change = exists and not values_equal(before, after, tolerance)
    passed = exists and observed_change == should_change
    result: dict[str, Any] = {
        "path": path,
        "expectation": "change" if should_change else "same",
        "passed": passed,
    }
    if not exists:
        result["error"] = "path missing in one or both files"
    else:
        result["before"] = before
        result["after"] = after
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("changed", type=Path)
    parser.add_argument("--expect-change", action="append", default=[], metavar="PATH")
    parser.add_argument("--expect-same", action="append", default=[], metavar="PATH")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--output", type=Path, help="also write the JSON report to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline = load_json(args.baseline)
    changed = load_json(args.changed)
    diffs = walk_diff(baseline, changed, "", args.tolerance)
    expectations = [
        expectation_result(baseline, changed, path, True, args.tolerance)
        for path in args.expect_change
    ] + [
        expectation_result(baseline, changed, path, False, args.tolerance)
        for path in args.expect_same
    ]
    report = {
        "baseline": str(args.baseline),
        "changed": str(args.changed),
        "difference_count": len(diffs),
        "differences": diffs,
        "expectations": expectations,
        "expectations_pass": all(item["passed"] for item in expectations),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["expectations_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
