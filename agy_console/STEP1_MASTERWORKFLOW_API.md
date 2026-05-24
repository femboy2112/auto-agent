# Step 1: `agy_orchestrator` Programmatic API Notes for `MasterWorkflow`

This document records the exact imports, signatures, and integration points needed to drive `MasterWorkflow` from `agy-console`.

## 1. Import paths

Use these import paths from `agy_orchestrator`:

- `from agy_orchestrator.workflows.master import MasterWorkflow`
- `from agy_orchestrator.core.profile import UserProfile`
- `from agy_orchestrator.core.optimizer import UsageAwareAllocator`
- `from agy_orchestrator.core.agents.agy_agent import AgyAgent`
- `from agy_orchestrator.core.agents.claude_agent import ClaudeAgent`
- `from agy_orchestrator.core.agents.codex_agent import CodexAgent`
- Optional verifier: `from agy_orchestrator.execution.verifier import QualityVerifier`

## 2. MasterWorkflow constructor + execution signature

Source: `../agy_orchestrator/workflows/master.py`

```python
class MasterWorkflow:
    def __init__(
        self,
        model: str,
        effort: str,
        branches: int = 3,
        max_iterations: int = 5,
        verifier: Optional[QualityVerifier] = None,
        agent_class=AgyAgent,
    )

    async def execute(self, initial_prompt: str) -> str
```

- `execute(...)` returns a `str` called `project_context`.
- That return string is what CLI currently prints as `--- Final Verified Output ---`.

## 3. How prompt/model/effort/agent are passed

### Prompt

- User prompt is passed to `await workflow.execute(prompt)` as `initial_prompt: str`.

### Agent backend (`agent <claude|codex|agy>`)

- Map agent name to class:
  - `claude` -> `ClaudeAgent`
  - `codex` -> `CodexAgent`
  - default/fallback -> `AgyAgent`
- Pass selected class into `MasterWorkflow(..., agent_class=<SelectedClass>)`.

### Model + effort

There are two supported patterns:

1. Direct/static:
   - Pass UI-selected values directly into `MasterWorkflow(model=..., effort=...)`.

2. Allocated (matches orchestrator CLI behavior):
   - Build `profile = UserProfile(...)`
   - `allocator = UsageAwareAllocator(profile, agent_class, agent_name, initial_model)`
   - `config = await allocator.get_current_config()`
   - Use:
     - `model=config["model"]`
     - `effort=config["effort"]`

The orchestrator CLI uses pattern #2.

## 4. Execution-step exposure (events/callbacks/iterator)

`MasterWorkflow` currently does **not** expose a structured step stream API:

- No callbacks in constructor.
- No event emitter.
- No async iterator/yielded step objects.
- `execute(...)` returns only the final `project_context` string at end.

How progress is exposed now:

- Internal `logger.info(...)` lines for phase-level milestones, e.g.:
  - planning start
  - `--- Executing Step i/n ---`
  - `Phase A: Tree of Thought Exploration`
  - `Phase B: Adversarial Review Refinement`
  - completion

For console streaming/progress in `agy-console` Step 2+, practical options are:

- Capture/display logging output in real time.
- Wrap workflow call with your own spinner/progress around major async stages.
- If needed later, extend `MasterWorkflow` to add callback hooks.

## 5. Final verified output field to read

For `MasterWorkflow`, the final read target is the return value of:

```python
result: str = await workflow.execute(prompt)
```

- This `result` is the accumulated `project_context` string.
- It includes original goal plus per-step summaries appended by the workflow.
- There is no separate object field like `result.verified_output`; use the returned string directly.

## 6. Minimal programmatic call pattern

```python
import asyncio
from agy_orchestrator.workflows.master import MasterWorkflow
from agy_orchestrator.core.profile import UserProfile
from agy_orchestrator.core.optimizer import UsageAwareAllocator
from agy_orchestrator.core.agents.claude_agent import ClaudeAgent

async def run(prompt: str, agent_name: str = "claude", model: str = "standard") -> str:
    agent_class = ClaudeAgent  # map from agent_name
    profile = UserProfile()
    config = await UsageAwareAllocator(profile, agent_class, agent_name, model).get_current_config()

    workflow = MasterWorkflow(
        model=config["model"],
        effort=config["effort"],
        branches=3,
        max_iterations=5,
        verifier=None,
        agent_class=agent_class,
    )
    return await workflow.execute(prompt)

# final_output = asyncio.run(run("Build X"))
```

## 7. Notes relevant to console command design

- `model <name>` should update the base model passed into allocator/workflow.
- `effort <level>` can be honored by bypassing allocator effort or by overriding `config["effort"]` before workflow init.
- `agent <claude|codex>` should switch the class used in `agent_class=...`.
- `run <prompt>` should be async-aware (`asyncio.run(...)` in sync REPL).
