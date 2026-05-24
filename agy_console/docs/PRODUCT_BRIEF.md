# Product Brief: agy-console

Version: 1.0
Date: 2026-05-24
Status: Signed Off (Step 1 Baseline)

## Product Summary

`agy-console` is a terminal-first REPL that lets operators execute `MasterWorkflow` through a predictable command interface, tune runtime settings (`model`, `effort`, `agent`), observe execution progress, and inspect session history.

## Why This Product Exists

Current workflow execution via ad hoc scripts is brittle and inconsistent for repeated operator use. A focused console reduces setup friction and standardizes invocation, making iterative workflow execution faster and safer.

## Target Users

- Developers and operators running orchestrated workflow tasks locally.
- Maintainers who need repeatable repro steps for runtime issues.

## Goals

- Provide a stable command interface for local workflow operations.
- Surface run progress and completion/failure outcomes clearly.
- Enforce valid runtime settings to prevent invalid runs.
- Retain run history for session-level traceability.

## Success Metrics

- Time from process launch to first successful `run` <= 5 minutes for a prepared developer machine.
- 100% validation of `model`, `effort`, and `agent` values before run start.
- 95% of failed runs produce a concise, user-visible error summary.
- 90% of run completions include clear success/failure status and elapsed time.

## Scope (This Phase)

Included:
- REPL lifecycle and command dispatch.
- Runtime config state and validation.
- Orchestrator integration adapter and progress event normalization.
- UI rendering for both rich and plain fallback environments.
- Session in-memory history and detail inspection.

Excluded:
- Persistent history storage.
- Remote execution and distributed workers.
- Auth/authz, tenancy, and shared state.

## Risks and Mitigations

- Risk: orchestrator log format changes break progress mapping.
  - Mitigation: treat progress mapping as best-effort; preserve final run result path as source of truth.
- Risk: startup failures due to package path/dependency drift.
  - Mitigation: explicit bootstrap diagnostics and immediate fatal startup error messaging.
- Risk: command misuse reduces trust.
  - Mitigation: strict argument count checks and clear usage hints.

## Dependencies

- Local Python runtime compatible with `agy_console` and `agy_orchestrator`.
- Sibling repository layout with importable `agy_orchestrator` package.

## Sign-Off

Approved scope:
- Product: Approved
- Engineering: Approved
- Delivery: Approved

Sign-off date: 2026-05-24
Sign-off note: This brief is approved as the authoritative Step 1 baseline for immediate implementation and backlog execution.

