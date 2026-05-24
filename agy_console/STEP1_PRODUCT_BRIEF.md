# Step 1 Product Brief: `agy-console`

## Document Control

- Version: 1.0
- Date: 2026-05-24
- Status: Signed Off
- Related: `STEP1_MASTERWORKFLOW_API.md`

## Product Summary

`agy-console` is a terminal REPL that lets users run `agy_orchestrator`'s `MasterWorkflow` with explicit control of prompt, model, effort, and backend agent, while preserving run history and readable progress feedback.

## Problem Statement

Current orchestrator capabilities are strong but not accessible enough for fast interactive iteration. Users need a stable command-driven console with strong guardrails around invalid input, startup failures, and run-time errors.

## Business Goals

1. Reduce time from idea to first workflow run.
2. Increase successful run completion rate in normal operator usage.
3. Standardize runtime configuration (model/effort/agent) to reduce manual mistakes.
4. Create a dependable baseline UX for later automation and richer progress streaming.

## Success Metrics

1. Time-to-first-successful-run: <= 3 minutes for first-time local setup.
2. Run completion rate: >= 90% successful runs for valid prompts in smoke tests.
3. Command misuse recovery: 100% of invalid command inputs return actionable error text without terminating the session.
4. Session reliability: 0 unhandled exceptions during scripted command regression tests.
5. Operator feedback quality: progress and final output visible for 100% of successful `run` operations.

## In Scope (Step 1 Baseline)

1. Command surface: `run`, `model`, `effort`, `agent`, `history`, `clear`, `help`, `exit`.
2. Runtime state management for selected model/effort/agent.
3. MasterWorkflow execution adapter with final output handling.
4. User-facing error handling for startup, parse, dispatch, and run-time failures.
5. Local run history capture for later inspection.
6. Basic progress display based on available workflow progress callbacks/log mapping.

## Out of Scope for This Stage

1. Multi-user auth, remote tenancy, and RBAC.
2. Web UI and non-terminal interaction surfaces.
3. Distributed execution scheduling.
4. Deep observability platform integration.
5. Modifying `agy_orchestrator` internals beyond interface-safe integration.

## Constraints

1. `MasterWorkflow.execute(...)` currently returns final output only; no native structured event stream.
2. Runtime depends on local importability of sibling `agy_orchestrator`.
3. Must run in standard local terminal environments with graceful handling of TTY limitations.
4. Product should preserve thin-wrapper architecture rather than introducing heavy abstraction layers.

## Assumptions

1. Primary users are technical operators comfortable with CLI workflows.
2. Local Python environment can install and run required dependencies.
3. `agy_orchestrator` API seams documented in `STEP1_MASTERWORKFLOW_API.md` remain stable for this phase.
4. Progress fidelity can be incrementally improved in later phases without breaking command contracts.

## Stakeholders

1. Project Sponsor: Product Owner (Leah)
2. Primary Users: Local operator/developer users of `agy_orchestrator`
3. Engineering: `agy-console` maintainers
4. Upstream Dependency Owner: `agy_orchestrator` maintainers
5. QA/Validation: Engineering owners responsible for smoke and regression verification

## Non-Goals

1. Replacing orchestration logic owned by `agy_orchestrator`.
2. Building a generic workflow engine inside `agy-console`.
3. Solving cloud deployment, billing, or enterprise governance in this phase.
4. Implementing advanced UX features before core reliability metrics are met.

## Risks and Mitigations

1. Risk: Upstream API changes in `agy_orchestrator`.
Mitigation: Keep adapter boundary narrow, document import/signature assumptions, and add contract checks.
2. Risk: Ambiguous progress visibility.
Mitigation: Standardize current callback/log mapping and keep future event-stream extension path explicit.
3. Risk: Session-breaking edge-case exceptions.
Mitigation: Defensive exception handling at startup, REPL loop, command dispatch, and run wrapper layers.

## Sign-Off Record

1. Product Scope and Goals: Approved, 2026-05-24, Product Owner (Leah)
2. Technical Feasibility and Constraints: Approved, 2026-05-24, Engineering
3. Delivery Baseline and Backlog Priorities: Approved, 2026-05-24, Product + Engineering

