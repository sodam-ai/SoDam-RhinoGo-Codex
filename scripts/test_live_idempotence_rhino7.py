# -*- coding: utf-8 -*-
"""Run the same Rhino 7 generator twice in one scratch document."""
import json
import os
import scriptcontext as sc

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
generator = os.path.join(root, "assets", "parametric-pavilion-rhino7.py")
report_path = os.path.join(root, "work", "pavilion-idempotence.json")
if os.path.exists(report_path):
    raise IOError("Preserving existing report: " + report_path)
os.environ["RHINO7_OUTPUT_3DM"] = ""
os.environ["RHINO7_PARAMS_JSON"] = ""

def snapshot():
    objects = [obj for obj in sc.doc.Objects if obj.Name and obj.Name.startswith("PAV_")]
    names = sorted(obj.Name for obj in objects)
    return {"count": len(objects), "names": names}

execfile(generator)
first = snapshot()
execfile(generator)
second = snapshot()
result = {"first_count": first["count"], "second_count": second["count"],
          "names_equal": first["names"] == second["names"],
          "pass": first["count"] == 67 and first == second}
with open(report_path, "w") as handle:
    handle.write(json.dumps(result, indent=2))
if not result["pass"]:
    raise AssertionError("Rhino 7 rebuild is not idempotent")
print(json.dumps(result, indent=2))
