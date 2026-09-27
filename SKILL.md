---
name: rhino-architectural-modeling
description: Plan, generate, inspect, and regression-test conceptual architectural models for Rhino 7 using offline rhino3dm archives, with the upstream RhinoCommon/MCP workflow retained for compatible live environments. Use for deterministic .3dm generation, model QA, and parameter-change tests.
---

# Rhino Architectural Modeling

Build Rhino architectural models from an explicit model contract, then verify the geometry independently from the generation script. Prefer reproducible evidence—saved `.3dm` versions, live document measurements, model metrics, and view captures—over self-reported success.

## Rhino 7 route

For Rhino 7 on Windows, first read [RHINO7_README.md](RHINO7_README.md). Use `scripts/first_run.ps1` for an offline conceptual pavilion, or `scripts/generate_rhino7_model.py` with a complete parameter JSON for a new variant. Reopen the saved `.3dm` with `scripts/inspect_rhino7_model.py`; compare audit JSONs with the upstream `scripts/compare_model_metrics.py`. The offline route does not require Rhino MCP or a Rhino license. It writes a Rhino 7 archive, not a live Rhino document. Open the result in Rhino 7 separately to inspect its appearance.

The workflow below is the upstream live RhinoCommon/MCP route. Do not run its Rhino 8 example or claim live Rhino 7 compatibility without verifying the connected Rhino version and the exact MCP operations.

## Choose the workflow

- For a new parametric concept model, follow the full workflow below.
- For an existing `.3dm`, begin at **Audit the live model** and do not rebuild unless asked.
- For a quick geometry edit, preserve the same naming, layer, ownership, and validation rules even if a full change test is unnecessary.
- For coordinated work with one or more agents, read [references/multi-agent-roles.md](references/multi-agent-roles.md) and assign roles from available capabilities rather than product names.
- When the environment specifically provides Codex, OpenCode, and Hermes, the optional tested mapping in [references/agent-profile-codex-opencode-hermes.md](references/agent-profile-codex-opencode-hermes.md) may be used.
- For Rhino MCP execution, read [references/rhino-mcp-workflow.md](references/rhino-mcp-workflow.md).
- For geometry construction patterns or QA criteria, read the corresponding reference only when needed.

## 1. Establish the model contract

Before writing geometry, state:

- units, tolerance, world-axis convention, and origin;
- baseline parameters and derived dimensions;
- physical envelope and reference datums;
- required layers, semantic object names, expected counts, and allowed geometry types;
- clearance volumes, connection/contact requirements, and acceptance tolerances;
- the parameter-only change test and which metrics must change or remain fixed;
- output paths for scripts, `.3dm` versions, metrics, captures, and the final report.

Use [assets/model-brief-template.md](assets/model-brief-template.md) as the starting point. Resolve ambiguous conventions early—for example, whether a stated frame envelope describes member centre-lines, outside faces, or both.

## 2. Select the construction method

Prefer a deterministic RhinoCommon Python script when exact regeneration, semantic naming, or change testing matters. Use Grasshopper when the deliverable is an editable visual definition. Use manual Rhino commands only for small exploratory edits or when the user explicitly wants interactive modelling.

For RhinoCommon scripts:

- use the document injected by the execution environment, such as `__rhino_doc__`;
- do not depend on `RhinoDoc.ActiveDoc`, `scriptcontext.doc`, selection state, dialogs, or the active viewport;
- keep user inputs in one clearly marked parameter block;
- make rebuilds idempotent by deleting only objects owned by a unique semantic prefix;
- create or reuse a stable layer hierarchy and give every object a unique semantic name;
- generate physical members as valid closed solids unless the contract explicitly permits surfaces or curves;
- redraw once at the end and emit one machine-readable JSON summary.

See [references/rhinocommon-patterns.md](references/rhinocommon-patterns.md). A tested example is available at [assets/parametric-pavilion-example.py](assets/parametric-pavilion-example.py).

## 3. Build a baseline version

1. Confirm the target Rhino slot/document before every operation. Never rely on an implicit active slot when multiple documents may be running.
2. Static-check the generator for document access, idempotency, units, naming, layers, and parameter isolation.
3. Run it in a dedicated document or slot.
4. Inspect the live context and object census after the build.
5. Save the baseline `.3dm` under a versioned name; never overwrite the only known-good model.
6. Record the script revision or checksum used to create it.

Treat the saved artifact, the on-disk generator, and live document state as three separate evidence sources. If their counts or timestamps disagree, investigate instead of reconciling them by assumption.

## 4. Audit the live model

Do not accept the generator's own summary as the only QA evidence. Recompute at least:

- active object count and counts by layer/type/semantic class;
- duplicate and missing names;
- invalid, open, or non-solid physical members;
- overall physical and scene bounding boxes;
- frame/station spacing and parameter-derived locations;
- required contacts or intersections;
- clear openings and obstruction volumes;
- louver/member orientations;
- duplicate geometry and unexpected objects.

Use [scripts/audit_architectural_model.py](scripts/audit_architectural_model.py) as a read-only Rhino MCP audit scaffold, adapting only its configuration block. Apply the detailed rules in [references/geometry-qa.md](references/geometry-qa.md).

Use bounding boxes for broad envelopes, not as proof of physical contact or clearance. Verify critical relationships with geometry operations such as Brep/Brep intersection, closest-point distance, containment, or collision against a guarded volume.

## 5. Run a parameter-only change test

Change multiple independent parameter classes—for example one dimension, one count, one height, one angle, and one offset—without editing construction logic. Rebuild, re-audit, and save a second `.3dm`.

Compare metric files with:

```bash
python3 scripts/compare_model_metrics.py baseline.json changed.json \
  --expect-change bbox.max \
  --expect-change frame_spacing \
  --expect-same bbox.min
```

Fail the change test if geometry code had to be edited, required changes did not propagate, invariants moved unexpectedly, or a second identical rebuild changes the metrics.

## 6. Review visually and close out

- Capture a shaded perspective and orthogonal views that expose entrances, facade rhythm, roof geometry, and likely collision zones.
- Check capture metadata such as visible-object count and scene bounding box; a non-empty image alone is weak evidence.
- Use rendered views only when material, lighting, or presentation quality is part of acceptance.
- Ask an independent reviewer to inspect artifacts and live state read-only when the risk warrants it.
- Write the final result from current artifacts, not from earlier implementation notes.

Start the review with [assets/qa-report-template.md](assets/qa-report-template.md). Report blockers separately from residual risks. State which claims were measured live, inferred from source, or only inspected visually.

## Safety and scope limits

- Maintain one writer for each Rhino document and one owner for each output file.
- Review agents must not mutate the master Rhino slot.
- Never erase unrelated document objects; ownership must be established by prefix, layer, or explicit object IDs.
- Preserve a versioned known-good `.3dm` before risky changes.
- Do not claim structural adequacy, code compliance, waterproofing, fabrication readiness, or constructability without the appropriate engineering inputs and review.
