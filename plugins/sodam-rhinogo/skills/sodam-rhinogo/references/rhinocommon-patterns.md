# RhinoCommon architectural patterns

## Document access and ownership

Use the document explicitly injected by Rhino MCP:

```python
doc = __rhino_doc__
```

Avoid `RhinoDoc.ActiveDoc`, `scriptcontext.doc`, selection-dependent commands, and UI prompts. For idempotent generation, assign a project prefix to every generated object and delete only active objects with that prefix before rebuilding.

## Layers and semantic attributes

Create or find layers by full path. Build new `ObjectAttributes` for each object, assigning both `LayerIndex` and a stable unique `Name`. Keep physical and reference geometry on separate layers.

## Oriented members

Axis-aligned boxes are appropriate only for axis-aligned members. For a sloped or rotated member:

1. define a local plane whose longitudinal axis follows the member vector;
2. construct the section intervals around or below the controlling datum;
3. create a box or swept profile in that plane;
4. verify its endpoints and actual intersection with adjacent members.

If the roof envelope has a strict maximum Z, do not centre a deep rafter on the roof datum; place its thickness below that datum.

## Counts and summaries

Compute the final summary from objects successfully added to the document, not from intended loop counts. Emit JSON only after all geometry is added. Redraw once at the end.

## Geometry validation

- `Brep.IsValid` is not equivalent to `Brep.IsSolid`; check both where required.
- For extrusions, check closed/solid status after creation or convert to Brep for a consistent audit.
- A bounding-box overlap is not proof that members touch.
- A line through an opening is not proof that the full clear volume is unobstructed.
- Duplicate geometry detection should include location as well as dimensions, otherwise repeated modular members will create false positives.

## Units and tolerance

Set or verify document units before geometry creation. Use the document absolute tolerance for intersections. Record the tolerance in the metrics so another reviewer can reproduce borderline results.
