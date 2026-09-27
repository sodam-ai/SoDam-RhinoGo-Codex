# Rhino 7 implementation

The implementation is directly in `D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo`.
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
rebuilds.

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

- `upstream-source/`: original GitHub clone. No Rhino 7 edits.
- `.`: editable Rhino 7 source project and local marketplace root.
- `work/`: generated models and temporary test outputs, ignored by Git.
- The `sodam-rhinogo` plugin contains the installed skill; the old standalone link is a legacy route.

The original Rhino MCP transport is Rhino 8-oriented and has not been verified
with Rhino 7; use the tested local live launcher for Rhino 7 execution. Back up
the project and original clone off-drive. A Git branch alone does not protect
the project from folder removal.
