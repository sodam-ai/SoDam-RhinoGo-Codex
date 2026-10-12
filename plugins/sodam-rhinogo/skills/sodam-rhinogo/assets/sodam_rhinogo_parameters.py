# -*- coding: utf-8 -*-
"""Shared Rhino 7 parameter defaults and validation for IronPython and CPython."""
import json
import math

DEFAULTS = {
    "length": 12000,          # mm, X axis
    "width": 8000,            # mm, Y axis
    "frame_count": 7,         # portal frames including both ends
    "eave_height": 3000,      # mm, Z of eave
    "ridge_height": 4500,     # mm, Z of ridge
    "column_section": (200, 200),   # (wx, wy) mm
    "beam_section": (200, 300),     # (wx, wy) mm — wy is vertical dim
    "louver_count_per_side": 10,
    "louver_angle_deg": 30,
    "entrance_width": 2400,   # mm clear opening
    "entrance_offset": 0,     # mm from facade centre along Y
}


MAX_MODEL_OBJECTS = 2000
MAX_COORDINATE_MM = 10000000  # 10 km, well beyond a pavilion


def validate_parameters(p):
    def finite_number(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        try:
            return not math.isnan(value) and not math.isinf(value)
        except (OverflowError, ValueError):
            return False

    if type(p["frame_count"]) is not int or p["frame_count"] < 2:
        raise ValueError("frame_count must be an integer >= 2")
    if type(p["louver_count_per_side"]) is not int or p["louver_count_per_side"] < 1:
        raise ValueError("louver_count_per_side must be an integer >= 1")
    if 6 * p["frame_count"] + 2 * p["louver_count_per_side"] + 5 > MAX_MODEL_OBJECTS:
        raise ValueError("model exceeds the 2000-object safety limit")
    for key in ("length", "width", "eave_height", "ridge_height", "entrance_width"):
        if not finite_number(p[key]) or not 0 < p[key] <= MAX_COORDINATE_MM:
            raise ValueError(key + " must be a finite positive number <= 10000000 mm")
    for key in ("column_section", "beam_section"):
        section = p[key]
        if (not isinstance(section, (list, tuple)) or len(section) != 2 or
                any(not finite_number(value) or not 0 < value <= MAX_COORDINATE_MM
                    for value in section)):
            raise ValueError(key + " must contain two finite positive dimensions")
    for key in ("louver_angle_deg", "entrance_offset"):
        if not finite_number(p[key]):
            raise ValueError(key + " must be a finite number")
    if abs(p["louver_angle_deg"]) > 360:
        raise ValueError("louver_angle_deg must be within one full rotation")
    if p["length"] / (p["frame_count"] - 1) <= 2 * max(p["column_section"][0], p["beam_section"][0]):
        raise ValueError("portal frames overlap along the length")
    if p["eave_height"] <= p["beam_section"][1]:
        raise ValueError("eaves must exceed beam depth")
    if p["ridge_height"] <= p["eave_height"]:
        raise ValueError("ridge must be above eaves")
    if abs(p["entrance_offset"]) + p["entrance_width"] / 2.0 >= (p["width"] / 2.0 - p["column_section"][1]):
        raise ValueError("entrance does not fit facade")


def load_parameters(path=""):
    params = DEFAULTS.copy()
    if path:
        with open(path, "r") as params_file:
            overrides = json.load(params_file)
        if not isinstance(overrides, dict) or set(overrides) - set(params):
            raise ValueError("Parameter JSON has unknown keys or is not an object")
        params.update(overrides)
    validate_parameters(params)
    return params
