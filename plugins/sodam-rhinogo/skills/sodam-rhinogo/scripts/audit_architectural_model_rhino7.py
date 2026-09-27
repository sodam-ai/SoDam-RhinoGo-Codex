# -*- coding: utf-8 -*-
"""Read-only architectural model audit for Rhino 7 IronPython 2.7."""

import json
import os
import scriptcontext as sc
from collections import Counter, defaultdict

import Rhino
import Rhino.Geometry as rg


CONFIG = {
    # Empty means include every active object that has a name.
    "name_prefix": "PAV_",
    # Full layer paths expected to exist among audited objects.
    "required_layers": ["PAVILION::Columns", "PAVILION::Beams", "PAVILION::Rafters", "PAVILION::Louvers", "PAVILION::Reference"],
    # Geometry on these layers is reference-only and need not be solid.
    "reference_layers": ["PAVILION::Reference"],
    # Optional physical bounding-box limits: [x, y, z]. Use None to skip.
    "bbox_min": None,
    "bbox_max": None,
    "tolerance": None,  # None uses the document absolute tolerance.
}


doc = sc.doc
tolerance = CONFIG["tolerance"] or doc.ModelAbsoluteTolerance
prefix = CONFIG["name_prefix"]
reference_layers = set(CONFIG["reference_layers"])


def layer_path(rhino_object):
    layer = doc.Layers[rhino_object.Attributes.LayerIndex]
    return layer.FullPath if layer else "<missing>"


def point_values(point):
    return [round(point.X, 6), round(point.Y, 6), round(point.Z, 6)]


def geometry_volume(geometry):
    try:
        properties = rg.VolumeMassProperties.Compute(geometry)
        return properties.Volume if properties else None
    except Exception:
        return None


def geometry_length(geometry):
    try:
        return geometry.GetLength() if isinstance(geometry, rg.Curve) else None
    except Exception:
        return None


def closed_solid_status(geometry):
    if isinstance(geometry, rg.Brep):
        return geometry.IsValid and geometry.IsSolid
    if isinstance(geometry, rg.Extrusion):
        return geometry.IsValid and geometry.IsSolid
    return False


def fingerprint(geometry):
    bbox = geometry.GetBoundingBox(True)
    volume = geometry_volume(geometry)
    length = geometry_length(geometry)
    return (
        geometry.GetType().Name,
        tuple(point_values(bbox.Min)),
        tuple(point_values(bbox.Max)),
        None if volume is None else round(volume, 6),
        None if length is None else round(length, 6),
    )


objects = []
for candidate in doc.Objects.GetObjectList(Rhino.DocObjects.ObjectType.AnyObject):
    if candidate.IsDeleted:
        continue
    name = candidate.Attributes.Name or ""
    if not name or (prefix and not name.startswith(prefix)):
        continue
    objects.append(candidate)

names = [obj.Attributes.Name for obj in objects]
name_counts = Counter(names)
duplicate_names = sorted(name for name, count in name_counts.items() if count > 1)
layer_counts = Counter(layer_path(obj) for obj in objects)
type_counts = Counter(obj.Geometry.GetType().Name for obj in objects)
missing_layers = sorted(set(CONFIG["required_layers"]) - set(layer_counts))

invalid_or_open = []
physical_objects = []
reference_objects = []
for obj in objects:
    if layer_path(obj) in reference_layers:
        reference_objects.append(obj)
        continue
    physical_objects.append(obj)
    if not closed_solid_status(obj.Geometry):
        invalid_or_open.append(obj.Attributes.Name)

fingerprints = defaultdict(list)
for obj in objects:
    fingerprints[fingerprint(obj.Geometry)].append(obj.Attributes.Name)
duplicate_geometry_groups = [sorted(group) for group in fingerprints.values() if len(group) > 1]

physical_bbox = rg.BoundingBox.Empty
for obj in physical_objects:
    physical_bbox.Union(obj.Geometry.GetBoundingBox(True))

bbox = None
if physical_bbox.IsValid:
    bbox = {"min": point_values(physical_bbox.Min), "max": point_values(physical_bbox.Max)}


def bbox_within_contract(actual):
    if actual is None:
        return CONFIG["bbox_min"] is None and CONFIG["bbox_max"] is None
    lower = CONFIG["bbox_min"]
    upper = CONFIG["bbox_max"]
    if lower is not None:
        for actual_value, limit in zip(actual["min"], lower):
            if actual_value < limit - tolerance:
                return False
    if upper is not None:
        for actual_value, limit in zip(actual["max"], upper):
            if actual_value > limit + tolerance:
                return False
    return True


checks = {
    "objects_found": bool(objects),
    "duplicate_names_zero": not duplicate_names,
    "duplicate_geometry_zero": not duplicate_geometry_groups,
    "missing_required_layers_zero": not missing_layers,
    "physical_objects_closed_solids": not invalid_or_open,
    "physical_bbox_within_contract": bbox_within_contract(bbox),
}

report = {
    "document": doc.Name,
    "units": str(doc.ModelUnitSystem),
    "absolute_tolerance": doc.ModelAbsoluteTolerance,
    "config": CONFIG,
    "object_count": len(objects),
    "physical_object_count": len(physical_objects),
    "reference_object_count": len(reference_objects),
    "layer_counts": dict(sorted(layer_counts.items())),
    "geometry_type_counts": dict(sorted(type_counts.items())),
    "bbox_physical": bbox,
    "duplicate_names": duplicate_names,
    "duplicate_geometry_groups": duplicate_geometry_groups,
    "missing_required_layers": missing_layers,
    "invalid_or_open": sorted(invalid_or_open),
    "checks": checks,
    "overall_pass": all(checks.values()),
}

print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

output_3dm = os.environ.get("RHINO7_OUTPUT_3DM", "")
if output_3dm:
    report_path = os.path.splitext(output_3dm)[0] + ".audit.json"
    with open(report_path, "w") as report_file:
        report_file.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
