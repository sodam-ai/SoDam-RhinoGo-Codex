---
name: sodam-rhinogo
description: Build, inspect, and regression-test conceptual architectural .3dm models in Rhino 7 using the bundled RhinoCommon scripts and independent audits. Use when the user asks for Rhino 7 architectural modeling or checking an existing Rhino model.
---

# SoDam-RhinoGo

Use the Rhino 7 implementation bundled with this skill. The original Rhino 8 and MCP workflow in the historical README is reference material; the Rhino 7 workflow is in [RHINO7_README.md](RHINO7_README.md). Rhino MCP transport has not been verified in Rhino 7.

## First use on Windows

Resolve this SKILL.md's parent directory as the skill root. Use an absolute root path in shell commands. Check that `C:\Program Files\Rhino 7\System\Rhino.exe` is installed. In the skill root, create `.venv` with Python 3.12 if absent, then install `requirements.txt` into it. Do not alter an unrelated Python environment. For example:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Full Rhino 7 model

Establish units, dimensions, semantic names, layers, object counts, clearance rules, and an output path. Keep each known-good model. From the skill root, create a unique output directory or use an existing one, then run:

```powershell
.\scripts\launch_rhino7_live.ps1 -OutputFile .\work\unique-model-r7.3dm
```

The output parent must exist and the launcher refuses to overwrite a model. It starts Rhino 7, builds the full pavilion, runs an independent live-document audit, saves the Rhino 7 `.3dm`, and reopens it for a separate saved-file audit. Read the `.build.json`, `.audit.json`, and `.saved-audit.json` reports. Treat a successful launcher as evidence of this model run only.

For a parameter change, pass `-ParametersFile` with a JSON file, save to another unique `.3dm`, and compare audit metrics with `scripts/compare_model_metrics.py`. Re-run identical parameters in a scratch document with `scripts/test_live_idempotence_rhino7.py` when idempotence matters.

For a smaller offline smoke test, use `scripts/first_run.ps1 -OutputDir <new-empty-directory>` and `scripts/inspect_rhino7_model.py`. Offline archive checks do not establish viewport appearance.

## Safety and limits

Inspect an existing model before editing it. Do not delete unrelated document objects or overwrite the only known-good `.3dm`. Keep the original upstream source separate from this plugin. Rhino 7 modeling results are conceptual and do not establish structural or code compliance. When reporting, distinguish source checks, live Rhino audits, saved-file audits, and visual inspection.

Detailed modeling patterns and audit criteria are in `references/`; use `assets/model-brief-template.md` and `assets/qa-report-template.md` when useful.
