# Step 1 Prioritized Requirements Backlog: `agy-console`

## Prioritization Model

- `P0`: Required for initial usable release and success metrics.
- `P1`: Important next increments after `P0`.
- `P2`: Valuable enhancements after baseline reliability is stable.

## Backlog

| ID | Priority | Requirement | Type | Acceptance Criteria | Dependencies |
|---|---|---|---|---|---|
| R-001 | P0 | `run <prompt>` executes `MasterWorkflow` with current state and prints final output. | Functional | Valid prompt triggers workflow; successful runs display completion status and final output text. | `agy_orchestrator` import path and `MasterWorkflow.execute(...)` |
| R-002 | P0 | Console startup handles orchestrator import/bootstrap failures with actionable errors and clean exit. | Functional | Broken import path exits with non-zero code and clear error message naming the failing condition. | Bootstrap utility + environment setup |
| R-003 | P0 | `model`, `effort`, and `agent` commands enforce allowed values and preserve current state across runs. | Functional | Invalid values never crash session; valid values persist until changed; subsequent `run` uses selected values. | State model + command parser |
| R-004 | P0 | REPL loop remains alive after malformed input and non-fatal command errors. | Functional | Invalid syntax shows hint text and returns to prompt; no unhandled exception terminates session. | Parser + command dispatcher |
| R-005 | P0 | Run execution path captures status (`success`/`error`), timestamps, and output in history store. | Functional | `history` lists prior runs with metadata and supports detailed lookup by index. | History store + run wrapper |
| R-006 | P0 | Error handling covers startup, prompt read, dispatch, and run execution boundaries. | Non-Functional | Simulated failures produce user-facing messages and controlled continuation or exit behavior. | Console app control flow |
| R-007 | P1 | Progress display reports major run phases and step counters when available. | Functional | During `run`, users see phase messages without blocking final output presentation. | Adapter progress callback surface |
| R-008 | P1 | `help` and usage text remain accurate for all supported commands and examples. | Functional | Every supported command has a one-line usage and one example; unknown commands point users to help. | Command registry |
| R-009 | P1 | Screen-clear behavior is cross-platform with fallback notice when clear operation is unavailable. | Non-Functional | `clear` works where supported; otherwise prints non-fatal fallback message and continues REPL. | Utility layer |
| R-010 | P1 | Basic smoke tests validate happy path and core command validation behavior. | Non-Functional | CI/local test run covers startup, command parsing, and at least one successful `run` flow with controllable adapter. | Test harness and mocks |
| R-011 | P2 | Structured progress event schema prepared for future orchestrator callback/event-stream upgrades. | Functional | Internal interface supports event object evolution without breaking existing UI method signatures. | Upstream orchestrator evolution |
| R-012 | P2 | Optional session export to markdown/text for run audit sharing. | Functional | User can export selected history entries to a file with prompt/config/status/output summary. | History serialization |

## Release Sequence

1. Milestone M1 (Step 1 baseline): Deliver all `P0` requirements.
2. Milestone M2: Deliver `P1` usability and testing hardening.
3. Milestone M3: Deliver `P2` extensibility and audit enhancements.

## Traceability to Product Brief

- Scope, goals, constraints, assumptions, and non-goals are defined in `STEP1_PRODUCT_BRIEF.md`.
- This backlog is the approved execution order for Step 2 planning and implementation.

## Sign-Off Record

1. Backlog ordering (`P0`/`P1`/`P2`): Approved, 2026-05-24, Product Owner (Leah)
2. Feasibility of `P0` baseline: Approved, 2026-05-24, Engineering
3. Milestone sequencing (M1/M2/M3): Approved, 2026-05-24, Product + Engineering

