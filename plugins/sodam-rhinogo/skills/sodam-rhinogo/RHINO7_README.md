# Rhino 7 implementation

The installed plugin uses the directory containing this README as its implementation root. The editable source lives in the SoDam-RhinoGo project.
The clean original is retained only as a reference in `upstream-source/` at
commit `9faa760402a422262ae7f23cf53cd61a7334bf7f`. The working branch is
`rhino7-rebuild`. Preserve both during future cleanup.

## Live Rhino 7 workflow

`assets/parametric-pavilion-rhino7.py` ports the full upstream pavilion geometry,
semantic names, layer hierarchy, and parameters to Rhino 7 IronPython.
`scripts/run_full_rhino7.py` generates and saves a Rhino 7 `.3dm`, then runs an
independent live-document audit. `scripts/launch_rhino7_live.ps1` opens Rhino 7,
waits for that audit, and independently reopens the saved archive for another audit.

From this exact root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\launch_rhino7_live.ps1 -OutputFile .\work\pavilion-new-r7.3dm
```

The output parent directory must exist. Use a new output name for every version;
the launcher refuses to overwrite an existing model. It writes `.build.json`,
`.audit.json`, and `.saved-audit.json` beside the model.

Pass `-ParametersFile path\to\parameters.json` for a parameter-only variation.
The example is `work/pavilion-variant.parameters.json`. Use
`scripts/compare_model_metrics.py` on the baseline and variant audits. The
scratch-document `scripts/test_live_idempotence_rhino7.py` checks same-parameter
rebuilds. Set `RHINO7_IDEMPOTENCE_REPORT` to a new JSON path before running it
again; the previous report is preserved.

Inputs are checked before Rhino starts. The live model permits at most 2,000
objects and dimensions up to 10,000,000 mm; frames must have room for their
sections, the entrance must clear the columns, and the eaves must exceed beam
depth. Angles are limited to one full rotation. The offline model uses the
same object and coordinate safety limits. Use a fresh base name: existing
`.3dm`, `.build.json`, `.audit.json`, and `.saved-audit.json` files are preserved.

## Optional offline route

- `scripts/generate_rhino7_model.py` builds a parametric conceptual pavilion
  offline with `rhino3dm` and writes a Rhino 7 archive (`ReadArchiveVersion=70`).
- `scripts/inspect_rhino7_model.py` reopens that saved file and checks object
  counts, semantic names and layers, valid closed solids, units, and envelope.
- The original `scripts/compare_model_metrics.py` can compare the audit JSONs
  from baseline and changed models.
- This is a smaller quick model. Use the live route above for full geometry.

## Offline first use (PowerShell)

Run these commands from this project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\first_run.ps1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`first_run.ps1` refuses to use a nonempty output directory. Use `-OutputDir`
with a new directory for each run. The model and JSON reports are saved there.
Open the `.3dm` in Rhino 7 for visual inspection; archive readability alone
does not prove viewport appearance. This is conceptual geometry, not structural
or construction documentation.

## Paths and preservation

- The editable project keeps `upstream-source/` as a separate original GitHub clone. No Rhino 7 edits.
- `.`: installed SoDam-RhinoGo skill bundle and Rhino 7 scripts.
- `work/`: generated models and temporary test outputs, ignored by Git.
- The Codex plugin contains this skill; it does not require the legacy standalone skill link.

The original Rhino MCP transport is Rhino 8-oriented and has not been verified
with Rhino 7; use the tested local live launcher for Rhino 7 execution. Back up
the project and original clone off-drive. A Git branch alone does not protect
the project from folder removal.

## License and external materials

SoDam AI Studio's Rhino 7 and Codex plugin contributions use Apache License,
Version 2.0 (`LICENSE`; Copyright 2026 SoDam AI Studio). Original upstream
material retains MIT (`LICENSE-MIT`; Copyright (c) 2026 Rhino Architectural
Modeling contributors). See `../../NOTICE.md` for provenance and separate Rhino and
dependency terms. Carry applicable notices when redistributing; mark changes.
Commercial code use is allowed under those terms, while Rhino, customer assets,
and AI-assisted outputs require separate rights checks. No warranty is provided;
seek legal or specialist review before public release or customer delivery.
