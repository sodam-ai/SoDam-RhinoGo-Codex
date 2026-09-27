# Rhino MCP workflow

## Slot discipline

List available Rhino slots first and pass the intended slot explicitly on every call. Record which slot is the master. Never assume the last active Rhino window is the correct document.

Use a dedicated scratch slot for destructive experiments. A review session should use read-only operations where possible and should not change selection, camera, geometry, or document state unless its scope explicitly includes those actions.

## Recommended sequence

1. List slots and inspect document context.
2. Run a static check on the generator.
3. Execute the generator with the injected document handle.
4. Re-read context and list the live object census.
5. Run a separate read-only audit script.
6. Save a versioned `.3dm`.
7. Capture shaded views and record image metadata.
8. Repeat the identical build for idempotency.
9. Apply parameter overrides only, rebuild, audit, and save the change-test version.

## Interpretation cautions

- A save response may describe the serialization operation rather than the current active census. Confirm counts with current context/list operations.
- Static source review cannot establish runtime geometry validity.
- A successful command response does not prove the intended object was built.
- Keep absolute paths out of agent handoffs when a repository-relative path works; non-ASCII volumes and shell quoting can make otherwise valid handoffs brittle.

## Failure handling

On script failure, capture the exact traceback and document state before retrying. Do not keep layering partial geometry into the same document. Fix the smallest issue, use the ownership prefix to clean only the failed build, and run again. Preserve the latest known-good `.3dm`.
