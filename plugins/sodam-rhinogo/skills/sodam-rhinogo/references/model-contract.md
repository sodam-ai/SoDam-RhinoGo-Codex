# Model contract checklist

Use this checklist to turn an architectural description into an executable and testable geometry contract.

## Coordinate and dimensional conventions

- State units and absolute/model tolerances.
- Define X, Y, and Z meanings and the origin.
- Distinguish grid axes, centre-lines, outside faces, clear dimensions, and design envelopes.
- State which datum controls sloped-member top, bottom, or centre-line elevation.
- Define whether end stations sit on the overall envelope or are inset by half a member width.

## Parameter schema

For every input, record name, type, unit, baseline value, valid range, and dependencies. Keep primary inputs separate from derived values. Typical groups are:

- overall length, width, and height;
- grid or frame counts and spacing;
- section width/depth;
- roof rise, ridge height, and slope;
- facade module count, angle, depth, and offset;
- opening width, height, centre, and guarded clearance depth.

## Object schema

Define the required layer path, semantic class, naming pattern, geometry type, expected count formula, and whether each object is physical or reference-only. Reference curves must never silently satisfy solid-count checks.

Example naming patterns:

- `BLDG_COL_F03_L`
- `BLDG_RAFTER_F03_R`
- `BLDG_LOUVER_FRONT_L_07`
- `BLDG_REF_FRAME_AXIS_03`

## Acceptance schema

Separate exact checks, tolerance checks, and visual checks. Include:

- expected counts and formulae;
- allowable envelope bounds;
- valid/closed solid requirements;
- anchor and spacing deviation tolerance;
- clear-opening guarded volume;
- required member contacts;
- duplicate-name and duplicate-geometry policy;
- idempotent rebuild requirement;
- baseline/change-test metrics that must remain fixed or change.

## Provenance

For each saved model record the generator path, revision or checksum, parameter override set, Rhino version, timestamp, and metrics file. Do not let an earlier implementation report override newer source or live evidence.
