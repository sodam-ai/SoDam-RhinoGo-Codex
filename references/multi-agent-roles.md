# Capability-driven collaboration for Rhino modelling

## Preserve the invariant: one document writer

Give exactly one active role ownership of each Rhino document or master slot. Other roles may prepare code, inspect artifacts, calculate expected values, or review live state read-only, but must not mutate that document concurrently.

Also assign one owner per output file. Avoid overlapping edits to generators, metrics, captures, and reports.

## Discover capabilities before assigning roles

Do not assume any agent product, provider, child-agent feature, or topology is available. Record:

- Rhino MCP and filesystem access;
- permission to mutate or only inspect a Rhino document;
- code generation and static-review ability;
- geometry and visual-review ability;
- child-agent or asynchronous-task support and whether lifecycle monitoring is reliable;
- context capacity, quota, latency, and current provider stability;
- which output files each participant can own.

Assign roles from this evidence. If a capability is unavailable, merge or serialize roles instead of pretending it exists.

## Use three logical roles

### Coordination and integration

- own the brief, model contract, acceptance rules, task boundaries, versions, and final evidence;
- designate the master Rhino writer and resolve conflicts between source, saved artifacts, live state, and reports;
- confirm the integration gate before close-out.

### Model implementation

- own the RhinoCommon generator or Grasshopper definition and its implementation notes;
- keep parameters isolated, generation idempotent, and objects semantically named;
- mutate the master slot only while explicitly holding writer ownership;
- return the exact source revision and machine-readable build summary.

### Independent verification

- define defect-sensitive QA before accepting implementation;
- review the exact generator, metrics, live object census, and captures;
- remain read-only on the master slot;
- separate blocking failures from residual risks and state the evidence type for each claim.

These are responsibilities, not necessarily three separate agents.

## Adapt to the available topology

### One agent

Run the roles serially: freeze the contract, implement and save, then start a distinct verification pass using live measurements rather than the build summary. Record that independence is procedural rather than interpersonal.

### Two agents

Let one participant coordinate and implement as the sole document writer. Give the other independent verification ownership and read-only access to the master slot.

### Three agents

Separate coordination/integration, implementation, and independent verification. This is the preferred topology when all three participants are reliable and have the required access.

### Four or more agents

Keep the three accountable role owners. Delegate only bounded check groups such as parameter calculations, code review, visual review, or report consistency. Child agents do not acquire document-write authority merely by delegation.

## Treat child agents as optional

Never make child-agent support a prerequisite. When available, give children one bounded question, explicit read/write boundaries, required evidence, and a return format. The parent role owner must monitor asynchronous work through completion, reconcile outputs, and remain accountable for the result.

If lifecycle monitoring is unavailable or unreliable, run the task directly or serialize it.

## Handoff contract

Every handoff should state:

- logical role and accountable owner;
- owned files and read-only boundaries;
- repository-relative source paths and the explicit Rhino slot/document;
- model conventions and acceptance rules;
- permitted tool actions;
- expected evidence and return format;
- timeout, quota, or fallback conditions.

## Capacity and fallback

Do not place a flaky, rate-limited, or poorly observed provider on the critical path. Give it small, independently verifiable tasks. Reassign or absorb missing optional work and report it honestly; never mark incomplete work as complete.

## Integration gate

Before closing, confirm:

- the generator on disk matches the source used for the saved model;
- the master slot had one known writer at a time;
- baseline and change-test metrics were measured, not merely predicted;
- reviewer findings are fixed or recorded as residual risks;
- child or auxiliary outputs were received and reconciled;
- the final report reflects current artifacts rather than stale handoff notes.
