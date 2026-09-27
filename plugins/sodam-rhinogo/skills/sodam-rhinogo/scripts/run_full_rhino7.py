# -*- coding: utf-8 -*-
"""Run Rhino 7 generation and an independent read-only live audit."""
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
build_script = os.path.join(root, "assets", "parametric-pavilion-rhino7.py")
audit_script = os.path.join(root, "scripts", "audit_architectural_model_rhino7.py")
build_scope = {"__name__": "__main__", "__file__": build_script}
execfile(build_script, build_scope)
audit_scope = {"__name__": "__main__", "__file__": audit_script}
execfile(audit_script, audit_scope)
if not audit_scope["report"]["overall_pass"]:
    raise AssertionError("Rhino 7 live audit failed")
