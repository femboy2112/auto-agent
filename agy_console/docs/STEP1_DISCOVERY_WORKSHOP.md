# Step 1 Discovery Workshop Output

Date: 2026-05-24
Project: `agy-console`
Workshop Type: Scope and requirements discovery
Facilitator: Codex implementation agent

## 1. Problem Statement

Developers need a reliable interactive console to run `agy_orchestrator`'s `MasterWorkflow` with simple runtime control (`model`, `effort`, `agent`), visible progress, and session-level history, without directly writing ad hoc Python scripts each time.

## 2. Project Scope

In scope:
- Interactive REPL for workflow execution (`run`, `model`, `effort`, `agent`, `history`, `help`, `clear`, `exit`).
- Runtime setting validation and state management.
- Progress streaming from orchestrator logs into normalized UI events.
- Run result display and in-memory session history.
- Startup/import checks for sibling `agy_orchestrator` package.

Out of scope for current scope boundary:
- Multi-user collaboration and shared history stores.
- Web UI, remote API service, or daemonized orchestration layer.
- Persistent database-backed history.
- Plugin ecosystem and custom command scripting.

## 3. Business Goals

- Reduce time-to-first-successful workflow run for operators.
- Improve operator confidence through clear progress and error feedback.
- Standardize local workflow invocation semantics to reduce support/debug overhead.

## 4. Success Metrics

Primary metrics:
- First successful run setup time <= 5 minutes on a fresh environment with documented prerequisites.
- Command validation error messages returned in < 1 second.
- 95% of run attempts either complete successfully or return a concise actionable failure reason.

Secondary metrics:
- At least 90% of interactive runs have visible progress events before completion.
- At least 80% of workshop-defined P0 requirements accepted in first implementation pass.

## 5. Constraints

Technical constraints:
- `agy_console` and `agy_orchestrator` must remain sibling directories for bootstrapping.
- `MasterWorkflow` currently returns only final output string and does not expose callback API; progress depends on log capture.
- REPL runtime is synchronous at command entry (`run` wraps async execution via `asyncio.run`).

Delivery constraints:
- Keep implementation thin and additive over existing architecture.
- Preserve current command surface unless explicit migration path is provided.

## 6. Assumptions

- Operators run in local terminal sessions with Python environment configured for orchestrator dependencies.
- `agy_orchestrator` log format remains stable enough for current progress normalization.
- In-memory history is acceptable for Step 1 and early validation.

## 7. Stakeholders

- Primary users: local developers/operators running multi-step workflow tasks.
- Engineering owner: maintainers of `agy_console` and adjacent `agy_orchestrator` integration.
- Product owner: workflow operator lead responsible for task throughput and quality expectations.

## 8. Non-Goals

- Replacing `agy_orchestrator` internal planning/execution logic.
- Designing a generalized workflow engine.
- Implementing centralized observability infrastructure.

## 9. Key Decisions from Workshop

- Keep command set minimal and explicit.
- Treat robust failure messaging and startup diagnostics as P0 user experience requirements.
- Prioritize deterministic behavior and clear boundaries over feature breadth in this phase.

## 10. Outputs Produced

- Signed-off product brief: `docs/PRODUCT_BRIEF.md`
- Prioritized requirement backlog: `docs/REQUIREMENT_BACKLOG.md`

