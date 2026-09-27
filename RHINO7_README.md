# Rhino 7 adaptation

This directory is the independent Rhino 7 work copy of
`leoyang1984/rhino-architectural-modeling` at commit `9faa760402a422262ae7f23cf53cd61a7334bf7f`.
The upstream source is stored beside it in `../upstream-source`; this working
copy uses branch `rhino7-rebuild` and a local `upstream-local` remote. Do not
delete this folder when cleaning the upstream source.

## What works

- `scripts/generate_rhino7_model.py` builds a parametric conceptual pavilion
  offline with `rhino3dm` and writes a Rhino 7 archive (`ReadArchiveVersion=70`).
- `scripts/inspect_rhino7_model.py` reopens that saved file and checks object
  counts, semantic names and layers, valid closed solids, units, and envelope.
- The original `scripts/compare_model_metrics.py` can compare the audit JSONs
  from baseline and changed models.
- The original RhinoCommon and MCP guidance remains available for a separately
  configured live Rhino environment. It has not been ported to Rhino 7 here.

## First use (PowerShell)

Run these commands from this work copy:

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

- `../upstream-source`: original GitHub clone. No Rhino 7 edits.
- `.`: editable Rhino 7 project and installed Codex skill target.
- `work/`: generated models and temporary test outputs, ignored by Git.
- The `rhino-architectural-modeling` skill link points here, never at upstream.

Back up both source and work copy independently. A Git branch alone does not
protect uncommitted files from folder removal.
