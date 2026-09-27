# -*- coding: utf-8 -*-
"""Rhino 7 IronPython 2.7 live version of the upstream pavilion example."""
import Rhino
import Rhino.Geometry as rg
import Rhino.DocObjects as rdo
import System.Drawing
import math
import json

import scriptcontext as sc
import os
from sodam_rhinogo_parameters import load_parameters
doc = sc.doc  # document owned by this Rhino script

# ── Parameters ─────────────────────────────────────────────────
PARAMS = load_parameters(os.environ.get("RHINO7_PARAMS_JSON", ""))
p = PARAMS
output_3dm = os.environ.get("RHINO7_OUTPUT_3DM", "")
if output_3dm:
    outputs = [output_3dm] + [os.path.splitext(output_3dm)[0] + suffix
                              for suffix in (".build.json", ".audit.json", ".saved-audit.json")]
    for candidate in outputs:
        if os.path.exists(candidate):
            raise IOError("Preserving existing output: " + candidate)

# ── Derived ────────────────────────────────────────────────────
frame_spacing = p["length"] / (p["frame_count"] - 1)
mid_y = p["width"] / 2.0
ent_half = p["entrance_width"] / 2.0
ent_start_y = mid_y + p["entrance_offset"] - ent_half
ent_end_y = mid_y + p["entrance_offset"] + ent_half
cw = p["column_section"][0]
cd = p["column_section"][1]
bw = p["beam_section"][0]
bd = p["beam_section"][1]
rafter_dy = mid_y        # horizontal run from outer eave edge to ridge centre
rafter_dz = p["ridge_height"] - p["eave_height"]  # vertical rise
rafter_len = math.sqrt(rafter_dy**2 + rafter_dz**2)
rafter_vec_L = rg.Vector3d(0, rafter_dy, rafter_dz)
rafter_vec_L.Unitize()
rafter_vec_R = rg.Vector3d(0, -rafter_dy, rafter_dz)
rafter_vec_R.Unitize()
louver_angle_rad = math.radians(p["louver_angle_deg"])

# ── Colours ────────────────────────────────────────────────────
COL = {
    "Columns":  System.Drawing.Color.FromArgb(139, 90, 43),
    "Beams":    System.Drawing.Color.FromArgb(160, 120, 60),
    "Rafters":  System.Drawing.Color.FromArgb(180, 140, 80),
    "Louvers":  System.Drawing.Color.FromArgb(200, 170, 120),
    "Reference": System.Drawing.Color.FromArgb(100, 100, 100),
}

# ── Helpers ────────────────────────────────────────────────────

def _layer(path):
    parent_id = System.Guid.Empty
    parts = path.split("::")
    for depth, name in enumerate(parts):
        full_path = "::".join(parts[:depth + 1])
        idx = doc.Layers.FindByFullPath(full_path, True)
        if idx < 0:
            layer = rdo.Layer()
            layer.Name = name
            layer.Color = COL.get(name, System.Drawing.Color.Black)
            layer.ParentLayerId = parent_id
            idx = doc.Layers.Add(layer)
            if idx < 0:
                raise RuntimeError("Cannot add layer: " + full_path)
        parent_id = doc.Layers[idx].Id
    return idx

def _attrs(layer_idx, name):
    oa = rdo.ObjectAttributes()
    oa.LayerIndex = layer_idx
    oa.Name = name
    return oa

def _add_brep(brep, layer_idx, name):
    return doc.Objects.AddBrep(brep, _attrs(layer_idx, name))

def _add_extrusion(ext, layer_idx, name):
    return doc.Objects.AddExtrusion(ext, _attrs(layer_idx, name))

def _is_closed_solid(obj_id):
    rh_obj = doc.Objects.Find(obj_id)
    if rh_obj is None:
        return False
    geo = rh_obj.Geometry
    if geo is None:
        return False
    b = geo if isinstance(geo, rg.Brep) else None
    if b is None:
        try:
            b = geo.ToBrep()
        except Exception:
            return False
    return b.IsValid and b.IsSolid

def _box_brep(x0, y0, z0, x1, y1, z1):
    bb = rg.BoundingBox(rg.Point3d(x0, y0, z0), rg.Point3d(x1, y1, z1))
    return rg.Brep.CreateFromBox(bb)

def _frame_x_bounds(frame_index, section):
    """Keep end-frame solids inside the 0..length design envelope."""
    fx = frame_index * frame_spacing
    if frame_index == 0:
        return fx, 0.0, float(section)
    if frame_index == p["frame_count"] - 1:
        return fx, float(p["length"] - section), float(p["length"])
    return fx, fx - section / 2.0, fx + section / 2.0

def _sloped_member(frame_index, start, direction, depth, side):
    """Create a capped rectangular member whose top line follows direction."""
    fx, x0, x1 = _frame_x_bounds(frame_index, cw)
    x_axis = rg.Vector3d.XAxis
    if side == "L":
        y_axis = rg.Vector3d(0, direction.Z, -direction.Y)
        depth_interval = rg.Interval(0, depth)
    else:
        y_axis = rg.Vector3d(0, direction.Z, -direction.Y)
        depth_interval = rg.Interval(-depth, 0)
    y_axis.Unitize()
    plane = rg.Plane(start, x_axis, y_axis)
    box = rg.Box(
        plane,
        rg.Interval(x0 - fx, x1 - fx),
        depth_interval,
        rg.Interval(0, rafter_len),
    )
    return box.ToBrep()

# ── Idempotent delete ──────────────────────────────────────────
to_delete = []
for obj in doc.Objects:
    if obj.Name and obj.Name.startswith("PAV_"):
        to_delete.append(obj.Id)
if to_delete:
    doc.Objects.Delete(to_delete, True)

# ── Units and layers ───────────────────────────────────────────
doc.ModelUnitSystem = Rhino.UnitSystem.Millimeters
layer_cols = _layer("PAVILION::Columns")
layer_beams = _layer("PAVILION::Beams")
layer_rafters = _layer("PAVILION::Rafters")
layer_louvers = _layer("PAVILION::Louvers")
layer_ref = _layer("PAVILION::Reference")

# ── Counters ───────────────────────────────────────────────────
counts = {"Columns": 0, "Beams": 0, "Rafters": 0, "Louvers": 0, "Reference": 0}
semantic_counts = {"TieBeams": 0, "Longitudinal": 0}
ids = []

# ── Portal frames ──────────────────────────────────────────────

for i in range(p["frame_count"]):
    fx = i * frame_spacing
    _, col_x0, col_x1 = _frame_x_bounds(i, cw)
    _, beam_x0, beam_x1 = _frame_x_bounds(i, bw)

    # Left column
    col_brep = _box_brep(col_x0, 0, 0,
                         col_x1, cd, p["eave_height"])
    ids.append(_add_brep(col_brep, layer_cols, "PAV_col_L_{0:02d}".format(i)))
    counts["Columns"] += 1

    # Right column
    col_brep = _box_brep(col_x0, p["width"] - cd, 0,
                         col_x1, p["width"], p["eave_height"])
    ids.append(_add_brep(col_brep, layer_cols, "PAV_col_R_{0:02d}".format(i)))
    counts["Columns"] += 1

    # One overhead tie beam per frame; the entrance remains clear below it.
    beam_brep = _box_brep(beam_x0, 0, p["eave_height"] - bd,
                          beam_x1, p["width"], p["eave_height"])
    ids.append(_add_brep(beam_brep, layer_beams,
                         "PAV_tie_beam_{0:02d}".format(i)))
    counts["Beams"] += 1
    semantic_counts["TieBeams"] += 1

    # Left rafter — top line runs Y+ from eave to ridge.
    rafter = _sloped_member(
        i, rg.Point3d(fx, 0, p["eave_height"]), rafter_vec_L, bd, "L"
    )
    ids.append(_add_brep(rafter, layer_rafters, "PAV_rafter_L_{0:02d}".format(i)))
    counts["Rafters"] += 1

    # Right rafter — top line runs Y- from eave to ridge.
    rafter = _sloped_member(
        i, rg.Point3d(fx, p["width"], p["eave_height"]),
        rafter_vec_R, bd, "R"
    )
    ids.append(_add_brep(rafter, layer_rafters, "PAV_rafter_R_{0:02d}".format(i)))
    counts["Rafters"] += 1

# ── Longitudinal members: ridge ────────────────────────────────
ridge_brep = _box_brep(0, mid_y - bw / 2, p["ridge_height"] - bd,
                       p["length"], mid_y + bw / 2, p["ridge_height"])
ids.append(_add_brep(ridge_brep, layer_beams, "PAV_ridge_beam"))
counts["Beams"] += 1
semantic_counts["Longitudinal"] += 1

# ── Longitudinal members: eaves ────────────────────────────────
eave_brep = _box_brep(0, cd / 2 - bw / 2, p["eave_height"] - bd / 2,
                      p["length"], cd / 2 + bw / 2, p["eave_height"] + bd / 2)
ids.append(_add_brep(eave_brep, layer_beams, "PAV_eave_beam_L"))
counts["Beams"] += 1
semantic_counts["Longitudinal"] += 1

eave_brep = _box_brep(0, p["width"] - cd / 2 - bw / 2, p["eave_height"] - bd / 2,
                      p["length"], p["width"] - cd / 2 + bw / 2, p["eave_height"] + bd / 2)
ids.append(_add_brep(eave_brep, layer_beams, "PAV_eave_beam_R"))
counts["Beams"] += 1
semantic_counts["Longitudinal"] += 1

# ── Louvers ────────────────────────────────────────────────────
louvers_left_y_range = (0, ent_start_y)
louvers_right_y_range = (ent_end_y, p["width"])
louver_w = 150   # blade width mm
louver_t = 10    # blade thickness mm

def _build_louver_set(y0, y1, side_label, y_sign):
    span = y1 - y0
    for j in range(p["louver_count_per_side"]):
        ly = y0 + span * (j + 0.5) / p["louver_count_per_side"]
        depth_axis = rg.Vector3d(
            math.cos(louver_angle_rad),
            y_sign * math.sin(louver_angle_rad),
            0,
        )
        width_axis = rg.Vector3d(
            -y_sign * math.sin(louver_angle_rad),
            math.cos(louver_angle_rad),
            0,
        )
        # Shift inward so a centred blade thickness never crosses X=0.
        origin = rg.Point3d(abs(width_axis.X) * louver_t / 2.0, ly, 0)
        louver_plane = rg.Plane(origin, depth_axis, width_axis)
        box = rg.Box(
            louver_plane,
            rg.Interval(0, louver_w),
            rg.Interval(-louver_t / 2.0, louver_t / 2.0),
            rg.Interval(0, p["eave_height"]),
        )
        ids.append(_add_brep(box.ToBrep(), layer_louvers,
                             "PAV_louver_{0}_{1:02d}".format(side_label, j)))
        counts["Louvers"] += 1

_build_louver_set(louvers_left_y_range[0], louvers_left_y_range[1], "L", 1)
_build_louver_set(louvers_right_y_range[0], louvers_right_y_range[1], "R", -1)

# ── Reference geometry ─────────────────────────────────────────
# Footprint (rectangle)
footprint = rg.Rectangle3d(
    rg.Plane.WorldXY,
    rg.Interval(0, p["length"]),
    rg.Interval(0, p["width"]),
)
ids.append(doc.Objects.AddCurve(footprint.ToNurbsCurve(),
                                _attrs(layer_ref, "PAV_ref_footprint")))
counts["Reference"] += 1

# Portal-frame axes preserve the exact 0..length stations even though end
# members are shifted inward to keep physical geometry inside the envelope.
for i in range(p["frame_count"]):
    fx = i * frame_spacing
    axis = rg.LineCurve(rg.Point3d(fx, 0, 0),
                        rg.Point3d(fx, p["width"], 0))
    ids.append(doc.Objects.AddCurve(
        axis, _attrs(layer_ref, "PAV_ref_frame_axis_{0:02d}".format(i))
    ))
    counts["Reference"] += 1

# Entrance opening indicator
ent_line = rg.LineCurve(
    rg.Point3d(0, ent_start_y, p["eave_height"]),
    rg.Point3d(0, ent_end_y, p["eave_height"]),
)
ids.append(doc.Objects.AddCurve(ent_line,
                                _attrs(layer_ref, "PAV_ref_entrance")))
counts["Reference"] += 1

# ── Validation ─────────────────────────────────────────────────
solid_ok = 0
solid_bad = 0
for oid in ids:
    rh_obj = doc.Objects.Find(oid)
    if (rh_obj and rh_obj.Attributes.LayerIndex != layer_ref and
            hasattr(rh_obj, "Geometry") and rh_obj.Geometry is not None):
        geo = rh_obj.Geometry
        try:
            b = geo if isinstance(geo, rg.Brep) else geo.ToBrep()
        except Exception:
            solid_bad += 1
            continue
        if b.IsValid and b.IsSolid:
            solid_ok += 1
        else:
            solid_bad += 1

# ── Bounding box (physical objects only) ──────────────────────
all_bb = rg.BoundingBox.Unset
for oid in ids:
    obj = doc.Objects.Find(oid)
    if obj and obj.Geometry and obj.Attributes.LayerIndex != layer_ref:
        bb = obj.Geometry.GetBoundingBox(True)
        if bb.IsValid:
            all_bb = rg.BoundingBox.Union(all_bb, bb) if all_bb.IsValid else bb

# ── Redraw ─────────────────────────────────────────────────────
for view in doc.Views.GetViewList(True, False):
    view.ActiveViewport.ZoomBoundingBox(all_bb)
doc.Views.Redraw()

# ── Summary ────────────────────────────────────────────────────
summary = {
    "parameters": PARAMS,
    "object_counts": counts,
    "semantic_counts": semantic_counts,
    "total_objects": sum(counts.values()),
    "solid_validation": {"physical_ok": solid_ok, "physical_bad": solid_bad},
    "frame_axes_x": [i * frame_spacing for i in range(p["frame_count"])],
    "frame_spacing": frame_spacing,
    "entrance_y_range": [ent_start_y, ent_end_y],
    "bounding_box": {
        "min": [all_bb.Min.X, all_bb.Min.Y, all_bb.Min.Z],
        "max": [all_bb.Max.X, all_bb.Max.Y, all_bb.Max.Z],
    },
}
if output_3dm:
    output_dir = os.path.dirname(output_3dm)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    if not doc.SaveAs(output_3dm, 7):
        raise IOError("Rhino 7 SaveAs failed: " + output_3dm)
    report_path = os.path.splitext(output_3dm)[0] + ".build.json"
    with open(report_path, "w") as report_file:
        report_file.write(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
