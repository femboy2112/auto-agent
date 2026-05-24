# Prioritized Requirement Backlog

Date: 2026-05-24
Source: Step 1 discovery workshop

Priority legend:
- P0 = must-have for baseline usability and trust
- P1 = high-value enhancements after P0 acceptance
- P2 = nice-to-have improvements

## P0 Requirements

### RQ-001 Command Surface and Help
Priority: P0
Requirement:
- System SHALL provide `run`, `model`, `effort`, `agent`, `history`, `clear`, `help`, and `exit` commands.
Acceptance criteria:
- Unknown commands return a deterministic error message with a help hint.
- `help` prints command list and usage examples.

### RQ-002 Runtime State Validation
Priority: P0
Requirement:
- System SHALL validate `model`, `effort`, and `agent` inputs before accepting state changes.
Acceptance criteria:
- Invalid values are rejected with allowed options in response.
- Valid values update active session state.

### RQ-003 Workflow Execution
Priority: P0
Requirement:
- System SHALL execute `MasterWorkflow` with active run configuration and prompt.
Acceptance criteria:
- `run <prompt>` invokes workflow and returns final output to user.
- Run success/failure status and elapsed time are displayed.

### RQ-004 Progress Visibility
Priority: P0
Requirement:
- System SHALL surface normalized progress events during workflow execution when available.
Acceptance criteria:
- Planning, step execution, phase updates, and completion are visible when emitted by orchestrator logs.
- Progress callback failures do not crash execution.

### RQ-005 Robust Startup Diagnostics
Priority: P0
Requirement:
- System SHALL fail fast with actionable startup errors if `agy_orchestrator` import/bootstrap fails.
Acceptance criteria:
- Missing sibling package path returns explicit expected location.
- Import failures include root exception type and message.

### RQ-006 Session History
Priority: P0
Requirement:
- System SHALL record run session entries (success and failure) for in-process history review.
Acceptance criteria:
- `history` lists indexed runs with summary metadata.
- `history <index>` shows full run detail including final output and failure error text when relevant.

## P1 Requirements

### RQ-101 Persisted History
Priority: P1
Requirement:
- System SHOULD optionally persist history across process restarts.
Acceptance criteria:
- History storage backend can be configured and loaded on startup.
- Corrupt history files do not crash startup and instead degrade gracefully.

### RQ-102 Configurable Model Catalog
Priority: P1
Requirement:
- System SHOULD allow model list configuration without code edits.
Acceptance criteria:
- Model values can be loaded from config/env.
- Invalid configured values are rejected at startup with clear diagnostics.

### RQ-103 Structured Progress Contract
Priority: P1
Requirement:
- Adapter SHOULD support a future structured progress interface independent of log parsing.
Acceptance criteria:
- Adapter code path can consume callback/event stream when orchestrator provides it.
- Existing log-based fallback remains operational.

## P2 Requirements

### RQ-201 Batch or Scripted Command Mode
Priority: P2
Requirement:
- System MAY support non-interactive command execution for automation use.
Acceptance criteria:
- Users can run one command with args without entering interactive loop.
- Exit codes follow success/failure outcomes.

### RQ-202 Theming and Output Formatting Controls
Priority: P2
Requirement:
- System MAY expose rendering preferences for terminals.
Acceptance criteria:
- Users can force rich/plain mode explicitly.
- Output remains readable without ANSI support.

### RQ-203 Export Run Transcript
Priority: P2
Requirement:
- System MAY export a run transcript for audit/debug handoff.
Acceptance criteria:
- Users can save selected run output and metadata to file.
- Export operation reports destination path and errors clearly.

## Backlog Ordering Rationale

- P0 items directly protect baseline usability, correctness, and operator trust.
- P1 items improve maintainability and operational continuity.
- P2 items improve ergonomics and integration depth but are not required for baseline value delivery.

