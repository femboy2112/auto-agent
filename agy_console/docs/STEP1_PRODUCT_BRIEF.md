# Product Brief: `agy-console` v1

Version: 1.0  
Date: 2026-05-24  
Status: Signed Off

## Problem Statement
Running orchestrator workflows programmatically requires setup and repeated boilerplate. Users need a lightweight terminal interface with stable commands, visible progress, and reliable run history.

## Product Vision
`agy-console` is a focused, local-first REPL for executing orchestrator workflows with minimal friction and predictable operator experience.

## Target Users
- Developers and operators running `agy_orchestrator` workflows locally.
- Team members validating prompts and configurations across repeated runs.

## v1 Scope
- Command-driven REPL with commands: `run`, `model`, `effort`, `agent`, `history`, `clear`, `help`, `exit`.
- Integration adapter for `MasterWorkflow` execution and progress reporting.
- Persistent local history with list/detail views.
- Error-resilient runtime loop with clear user-facing diagnostics.

## Business Goals
- Decrease workflow invocation friction and onboarding time.
- Raise execution reliability and reproducibility.
- Establish a maintainable base for future orchestration enhancements.

## Success Criteria (Release Gate)
- A first-time user can execute a successful run within 10 minutes.
- No uncaught exceptions terminate the REPL during normal/invalid command usage tests.
- History list/detail functionality validated against successful and failed run scenarios.
- All v1 Must-have requirements completed and accepted.

## Constraints
- Must remain compatible with current `agy_orchestrator` structure.
- No dependency on cloud APIs for core functionality.
- Keep architecture modular and testable in current Python codebase layout.

## Key Assumptions
- Operators are terminal-native users.
- Orchestrator upstream will remain importable from local workspace.
- Current workflow output contract remains final string return.

## Non-Goals
- GUI/web interface.
- Multi-user remote operation and shared state.
- Enterprise auth, tenancy, or cloud-backed history.

## Dependencies
- Local availability of `agy_orchestrator`.
- Python runtime and console terminal capabilities.

## Signed-Off By
- Product Owner: Accepted (2026-05-24)
- Engineering Lead: Accepted (2026-05-24)
- Delivery Lead: Accepted (2026-05-24)

