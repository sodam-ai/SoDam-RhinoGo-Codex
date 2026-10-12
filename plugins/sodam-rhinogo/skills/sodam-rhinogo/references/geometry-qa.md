# Geometry QA for architectural concept models

## Evidence hierarchy

Use several evidence sources:

1. live measurements from the current Rhino document;
2. saved `.3dm` existence and reopen checks;
3. static review of the exact generator on disk;
4. viewport captures and their metadata;
5. implementation reports.

Implementation reports are lowest because they often describe an earlier revision. A generator's own JSON is useful but is not independent verification.

## Required checks

### Inventory

- Count all active objects and objects by layer and geometry type.
- Confirm every owned object has one unique semantic name.
- Detect objects on wrong or missing layers.
- Distinguish physical solids from reference curves/surfaces.

### Shape validity

- Require physical Breps or extrusions to be valid and closed/solid.
- Detect degenerate dimensions, zero-length axes, and empty geometry.
- Detect exact duplicates using type, location-aware bounding box, and volume/length fingerprints; confirm suspected duplicates geometrically before deleting anything.

### Dimensional intent

- Measure the physical bounding box separately from the full scene bounding box.
- Recompute station positions and spacing from geometry.
- Measure offsets from reference axes, not only from neighbouring members.
- Check angle vectors for louvers and sloped members.

### Contact and clearance

- Use Brep/Brep intersection or distance for ridge, beam, and column connections.
- Test an opening with a guarded 3D clearance volume that extends through the occupied depth.
- Ignore permitted boundary contact while rejecting penetration into the clear interior.

### Parametric behaviour

- Rebuild twice with the same inputs and compare metrics.
- Change independent input classes without changing construction code.
- Confirm expected deltas and invariants explicitly.

## Defect sensitivity set

A serious QA plan should be able to detect at least:

- a small global or single-member offset;
- a wrong layer or missing name;
- an open or invalid solid;
- duplicate geometry;
- unequal frame spacing;
- an incorrect clear opening;
- a sloped member that nearly reaches but does not contact its support;
- a parameter value that changes in JSON but not in geometry.

## Visual review

Capture at least one perspective and the relevant elevations/sections. Confirm the view contains all expected visible objects and a plausible scene bounding box. Pixel review detects composition and obvious gaps, but it cannot replace measured geometry checks.
