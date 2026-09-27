#!/usr/bin/env python3
"""Create a deterministic conceptual pavilion as a Rhino 7 .3dm archive.

No Rhino process or license is needed. This is an offline companion to the
upstream RhinoCommon/MCP workflow, not a replacement for live Rhino editing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rhino3dm as r


DEFAULTS = {
    "length_mm": 12000.0,
    "width_mm": 8000.0,
    "frame_count": 6,
    "eave_height_mm": 3200.0,
    "column_size_mm": 220.0,
    "beam_depth_mm": 300.0,
    "roof_slat_count": 11,
    "roof_slat_width_mm": 100.0,
    "roof_slat_depth_mm": 80.0,
    "footing_size_mm": 500.0,
    "footing_depth_mm": 150.0,
}


def validate(p: dict) -> None:
    if set(p) != set(DEFAULTS):
        raise ValueError(f"Parameter keys must be exactly {sorted(DEFAULTS)}")
    if type(p["frame_count"]) is not int or p["frame_count"] < 2:
        raise ValueError("frame_count must be an integer >= 2")
    if type(p["roof_slat_count"]) is not int or p["roof_slat_count"] < 2:
        raise ValueError("roof_slat_count must be an integer >= 2")
    for key, value in p.items():
        if key.endswith("_mm") and (not isinstance(value, (int, float)) or value <= 0):
            raise ValueError(f"{key} must be positive")
    if p["column_size_mm"] >= p["width_mm"] / 2:
        raise ValueError("Columns leave no usable span")
    if p["roof_slat_width_mm"] >= p["length_mm"] / (p["roof_slat_count"] - 1):
        raise ValueError("Roof slats overlap")
    if p["eave_height_mm"] <= p["beam_depth_mm"] + 1000:
        raise ValueError("Insufficient clear height")


def build(p: dict) -> tuple[r.File3dm, dict]:
    validate(p)
    model = r.File3dm()
    model.Settings.ModelUnitSystem = r.UnitSystem.Millimeters
    model.Settings.ModelAbsoluteTolerance = 0.01
    layers = {}
    for name in ("Foundations", "Columns", "Beams", "RoofSlats"):
        layer = r.Layer()
        layer.Name = name
        layers[name] = model.Layers.Add(layer)

    names = []

    def add_box(layer: str, name: str, xyz0: tuple, xyz1: tuple) -> None:
        if not all(b > a for a, b in zip(xyz0, xyz1)):
            raise ValueError(f"Degenerate member: {name}")
        bbox = r.BoundingBox(r.Point3d(*xyz0), r.Point3d(*xyz1))
        brep = r.Brep.CreateFromBox(r.Box(bbox))
        if brep is None or not brep.IsSolid or not brep.IsValid:
            raise ValueError(f"Invalid solid: {name}")
        attr = r.ObjectAttributes()
        attr.Name = name
        attr.LayerIndex = layers[layer]
        model.Objects.AddBrep(brep, attr)
        names.append(name)

    L, W = p["length_mm"], p["width_mm"]
    n = p["frame_count"]
    c = p["column_size_mm"]
    z = p["eave_height_mm"]
    bd = p["beam_depth_mm"]
    fs, fd = p["footing_size_mm"], p["footing_depth_mm"]
    for i in range(n):
        x = L * i / (n - 1)
        for side, y in (("L", 0.0), ("R", W)):
            add_box("Foundations", f"R7_Footing_{i:02d}_{side}",
                    (x - fs / 2, y - fs / 2, -fd), (x + fs / 2, y + fs / 2, 0))
            add_box("Columns", f"R7_Column_{i:02d}_{side}",
                    (x - c / 2, y - c / 2, 0), (x + c / 2, y + c / 2, z))
        add_box("Beams", f"R7_Beam_{i:02d}",
                (x - c / 2, -c / 2, z - bd), (x + c / 2, W + c / 2, z))
    sn = p["roof_slat_count"]
    sw, sd = p["roof_slat_width_mm"], p["roof_slat_depth_mm"]
    for i in range(sn):
        x = L * i / (sn - 1)
        add_box("RoofSlats", f"R7_RoofSlat_{i:02d}",
                (x - sw / 2, -c / 2, z), (x + sw / 2, W + c / 2, z + sd))

    summary = {
        "archive_version": 70,
        "units": "Millimeters",
        "object_count": len(names),
        "counts": {"Foundations": n * 2, "Columns": n * 2,
                   "Beams": n, "RoofSlats": sn},
        "frame_spacing_mm": L / (n - 1),
        "parameters": p,
    }
    return model, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--parameters", type=Path)
    args = parser.parse_args()
    p = json.loads(args.parameters.read_text(encoding="utf-8")) if args.parameters else DEFAULTS.copy()
    model, summary = build(p)
    if args.output.exists():
        raise FileExistsError(f"Preserving existing file: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not model.Write(str(args.output), 7):
        raise RuntimeError("File3dm.Write failed")
    metrics = args.output.with_suffix(".build.json")
    metrics.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"model": str(args.output), "build_report": str(metrics), **summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
