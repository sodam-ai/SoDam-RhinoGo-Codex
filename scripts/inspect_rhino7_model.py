#!/usr/bin/env python3
"""Independently inspect the saved Rhino 7 pavilion archive."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import rhino3dm as r


def inspect(path: Path) -> dict:
    model = r.File3dm.Read(str(path))
    if model is None:
        raise ValueError(f"Cannot read 3DM: {path}")
    objects = list(model.Objects)
    layers = {layer.Index: layer.Name for layer in model.Layers}
    names = [obj.Attributes.Name for obj in objects]
    counts = Counter(layers.get(obj.Attributes.LayerIndex, "<missing>") for obj in objects)
    invalid = [obj.Attributes.Name for obj in objects if not obj.Geometry.IsValid]
    open_members = [obj.Attributes.Name for obj in objects if not getattr(obj.Geometry, "IsSolid", False)]
    bounds = [obj.Geometry.GetBoundingBox() for obj in objects]
    if not bounds:
        raise ValueError("Empty model")
    bbox = {
        "min": [min(getattr(b.Min, axis) for b in bounds) for axis in "XYZ"],
        "max": [max(getattr(b.Max, axis) for b in bounds) for axis in "XYZ"],
    }
    expected = {"Foundations", "Columns", "Beams", "RoofSlats"}
    issues = []
    archive = r.File3dm.ReadArchiveVersion(str(path))
    if archive != 70:
        issues.append(f"archive version {archive}, expected 70")
    if model.Settings.ModelUnitSystem != r.UnitSystem.Millimeters:
        issues.append("units are not millimeters")
    if set(counts) != expected:
        issues.append(f"unexpected layers: {sorted(set(counts) ^ expected)}")
    if len(names) != len(set(names)) or any(not name for name in names):
        issues.append("missing or duplicate object names")
    if any(not name.startswith("R7_") for name in names):
        issues.append("unexpected object ownership prefix")
    if invalid:
        issues.append(f"invalid geometry: {invalid}")
    if open_members:
        issues.append(f"open/non-solid geometry: {open_members}")
    if counts["Foundations"] != counts["Columns"] or counts["Columns"] != 2 * counts["Beams"]:
        issues.append("frame assembly counts disagree")
    if bbox["min"][2] >= 0 or bbox["max"][2] <= 2000:
        issues.append("implausible vertical envelope")
    return {
        "archive_version": archive,
        "units": str(model.Settings.ModelUnitSystem),
        "object_count": len(objects),
        "counts": dict(sorted(counts.items())),
        "bbox": bbox,
        "invalid": invalid,
        "open_members": open_members,
        "issues": issues,
        "overall_pass": not issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    args = parser.parse_args()
    report_path = args.model.with_suffix(".audit.json")
    if report_path.exists():
        raise FileExistsError(f"Preserving existing audit: {report_path}")
    report = inspect(args.model)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"model": str(args.model), "report": str(report_path), **report}))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
