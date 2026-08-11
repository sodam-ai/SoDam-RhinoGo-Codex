# Optional profile: Codex, OpenCode, and Hermes

Use this mapping only when these three agents are actually available and their current capabilities match the assignments below. The generic collaboration rules remain authoritative.

## Codex — coordination and integration

- own the model brief, acceptance contract, task breakdown, master Rhino slot, versioned saves, and final evidence;
- resolve conflicts between source, live state, and reports;
- run the final cross-source integration gate.

## OpenCode — model implementation

- own the RhinoCommon generator and implementation notes;
- perform static review and local corrections;
- return child-agent work to the implementation owner before integration;
- avoid mutating the master slot unless explicitly handed sole writer ownership.

## Hermes — independent verification

- own the test plan and independent review report;
- define defect-sensitive checks before implementation is accepted;
- review the generator, metrics, live census, and captures read-only;
- monitor asynchronous child work through completion and reconcile its evidence.

## Fallbacks

- If any agent is unavailable, merge its logical role into a reliable participant and serialize the affected phases.
- If child-agent support is missing, perform the assigned checks directly.
- If a provider becomes rate-limited or unstable, remove it from the critical path and preserve only bounded, independently verifiable optional tasks.
