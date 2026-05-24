# Prioritized Requirement Backlog: `agy-console` v1

Date: 2026-05-24  
Prioritization Method: MoSCoW  
Status: Approved for implementation

## Must Have

### AGY-M01: Stable REPL loop
Priority: Must  
Description: Console starts reliably, accepts command input continuously, and exits only on `exit/quit` or terminal interrupt.  
Acceptance Criteria:
- Startup prints banner or a non-fatal warning if banner rendering fails.
- Unexpected prompt/dispatch exceptions do not terminate session.
- `exit` and `quit` terminate cleanly with user-facing confirmation.

### AGY-M02: Run workflow execution command
Priority: Must  
Description: `run <prompt>` executes `MasterWorkflow` via adapter using selected runtime settings.  
Acceptance Criteria:
- Empty `run` input shows usage guidance.
- Valid prompt triggers workflow execution and final output display.
- Runtime failures are surfaced as concise, user-facing errors without REPL crash.

### AGY-M03: Runtime configuration commands
Priority: Must  
Description: Support `model`, `effort`, and `agent` commands with validation and state updates.  
Acceptance Criteria:
- Valid values update state and print confirmation.
- Invalid values return actionable error messages with expected usage.
- Configuration state is used by subsequent `run` commands.

### AGY-M04: Run history persistence and inspection
Priority: Must  
Description: Persist successful and failed run records and provide list/detail retrieval.  
Acceptance Criteria:
- Every `run` attempt creates a history entry with status and timestamps.
- `history` lists prior sessions in reverse chronological order.
- `history <index>` displays detailed record for a valid index.

### AGY-M05: Help and discoverability
Priority: Must  
Description: `help` command provides complete, accurate command reference.  
Acceptance Criteria:
- Help text includes every supported command and examples.
- Usage guidance is shown on incorrect arg count for all commands.

## Should Have

### AGY-S01: Progress feedback during run
Priority: Should  
Description: Show phase/step progress messages when available from adapter callback.  
Acceptance Criteria:
- During long runs, operator sees progress lines without waiting for final output.
- Step counts are shown when both current and total are known.

### AGY-S02: Resilient bootstrap diagnostics
Priority: Should  
Description: Startup failures related to orchestrator import/bootstrap are explicit and actionable.  
Acceptance Criteria:
- Import/bootstrap failures include concise reason and fail fast.
- Message indicates the failing component class or path context when possible.

## Could Have

### AGY-C01: Export run record
Priority: Could  
Description: Add command to export selected history record to a markdown/text artifact.  
Acceptance Criteria:
- Operator can export by history index.
- Export includes prompt, configuration, status, and final output.

### AGY-C02: Command aliases
Priority: Could  
Description: Optional short aliases for common commands (for example `h` for `help`).  
Acceptance Criteria:
- Aliases map deterministically to existing commands.
- Help text documents alias behavior clearly.

## Won't Have (v1)

### AGY-W01: Web dashboard
Priority: Won't  
Rationale: Not needed for first release; terminal UX is the deliberate scope.

### AGY-W02: Shared remote history
Priority: Won't  
Rationale: Adds infra complexity without v1 adoption value.

### AGY-W03: Multi-agent orchestration graph view
Priority: Won't  
Rationale: Depends on upstream event model not available in current contract.

## Dependency and Sequencing Notes
- Build order should be Must requirements first (M01 to M05), then Should requirements.
- `AGY-M02` depends on adapter and bootstrap stability.
- `AGY-M04` depends on reliable run lifecycle hooks from `AGY-M02`.

