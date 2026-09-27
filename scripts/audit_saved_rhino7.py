#!/usr/bin/env python3
"""Independently reopen and audit a saved Rhino 7 pavilion archive."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import rhino3dm as r


def audit(model_path: Path) -> dict:
    model = r.File3dm.Read(str(model_path))
    if model is None:
        raise ValueError(f"Cannot read 3DM: {model_path}")
    build_path = model_path.with_suffix(".build.json")
    build = json.loads(build_path.read_text(encoding="utf-8"))
    params = build["parameters"]
    n, louvers = params["frame_count"], params["louver_count_per_side"]
    expected = {"Columns": 2*n, "Beams": n+3, "Rafters": 2*n,
                "Louvers": 2*louvers, "Reference": n+2}
    layers = {str(layer.Id): layer for layer in model.Layers}
    def layer_path(index: int) -> str:
        layer = model.Layers[index]
        parts = [layer.Name]
        while str(layer.ParentLayerId) in layers:
            layer = layers[str(layer.ParentLayerId)]
            parts.append(layer.Name)
        return "::".join(reversed(parts))

    objects = list(model.Objects)
    names = [obj.Attributes.Name or "" for obj in objects]
    counts = Counter(layer_path(obj.Attributes.LayerIndex) for obj in objects)
    short_counts = {key.removeprefix("PAVILION::"): counts.get("PAVILION::"+key, 0)
                    for key in expected}
    physical = [obj for obj in objects if layer_path(obj.Attributes.LayerIndex) != "PAVILION::Reference"]
    reference = [obj for obj in objects if layer_path(obj.Attributes.LayerIndex) == "PAVILION::Reference"]
    invalid = [obj.Attributes.Name for obj in objects if not obj.Geometry.IsValid]
    open_solids = [obj.Attributes.Name for obj in physical if not getattr(obj.Geometry, "IsSolid", False)]
    bounds = [obj.Geometry.GetBoundingBox() for obj in physical]
    bbox = {"min": [min(getattr(b.Min, axis) for b in bounds) for axis in "XYZ"],
            "max": [max(getattr(b.Max, axis) for b in bounds) for axis in "XYZ"]}
    fingerprints = defaultdict(list)
    for obj in physical:
        b = obj.Geometry.GetBoundingBox()
        fingerprint = (type(obj.Geometry).__name__,
                       *(round(getattr(point, axis), 6) for point in (b.Min, b.Max) for axis in "XYZ"))
        fingerprints[fingerprint].append(obj.Attributes.Name)
    duplicate_geometry = [group for group in fingerprints.values() if len(group) > 1]
    axes = []
    for obj in reference:
        if (obj.Attributes.Name or "").startswith("PAV_ref_frame_axis_"):
            b = obj.Geometry.GetBoundingBox()
            axes.append(b.Min.X)
    axes.sort()
    expected_axes = [params["length"]*i/(n-1) for i in range(n)]
    def near(left, right):
        return abs(left-right) <= 0.01
    checks = {
        "archive_70": r.File3dm.ReadArchiveVersion(str(model_path)) == 70,
        "millimeters": model.Settings.ModelUnitSystem == r.UnitSystem.Millimeters,
        "unique_owned_names": len(names) == len(set(names)) and all(name.startswith("PAV_") for name in names),
        "layer_counts": short_counts == expected and set(counts) == {"PAVILION::"+key for key in expected},
        "geometry_valid": not invalid,
        "physical_closed": not open_solids,
        "duplicate_geometry_zero": not duplicate_geometry,
        "frame_axes": len(axes) == n and all(near(a,b) for a,b in zip(axes, expected_axes)),
        "envelope": all(near(a,b) for a,b in zip(bbox["min"], [0,0,0])) and
                    all(near(a,b) for a,b in zip(bbox["max"],
                        [params["length"], params["width"], params["ridge_height"]])),
        "build_count_agrees": len(objects) == build["total_objects"],
    }
    return {"model": str(model_path), "object_count": len(objects),
            "physical_count": len(physical), "reference_count": len(reference),
            "layer_counts": dict(sorted(counts.items())), "bbox_physical": bbox,
            "frame_axes_x": axes, "invalid": invalid, "open_solids": open_solids,
            "duplicate_geometry": duplicate_geometry, "checks": checks,
            "overall_pass": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    args = parser.parse_args()
    report_path = args.model.with_suffix(".saved-audit.json")
    if report_path.exists():
        raise FileExistsError(f"Preserving existing audit: {report_path}")
    report = audit(args.model)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "overall_pass": report["overall_pass"],
                      "objects": report["object_count"], "checks": report["checks"]}))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
