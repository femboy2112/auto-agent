"""Adapter around agy_orchestrator's MasterWorkflow with streaming progress capture."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Type

from agy_orchestrator.core.agent import AgentInstance
from agy_orchestrator.workflows.master import MasterWorkflow

LOGGER = logging.getLogger(__name__)


@dataclass
class ProgressRecord:
    """Normalized execution event emitted during workflow execution."""

    timestamp: datetime
    phase: str
    message: str
    step_index: int | None = None
    total_steps: int | None = None


@dataclass
class RunResult:
    """Structured workflow result with streaming events and final output."""

    steps: list[ProgressRecord] = field(default_factory=list)
    final_output: str = ""


@dataclass
class RunConfig:
    """Inputs required to run one orchestrator workflow invocation."""

    prompt: str
    model: str
    effort: str
    agent_class: Type[AgentInstance]
    on_progress: Callable[[ProgressRecord], None] | None = None


class _ProgressCaptureHandler(logging.Handler):
    """Maps orchestrator log records into normalized progress events."""
    _STEP_PATTERN = re.compile(r"--- Executing Step (\d+)/(\d+) ---")

    def __init__(self, sink: Callable[[ProgressRecord], None]) -> None:
        super().__init__()
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        try:
            event = self._normalize(record)
            if event is None:
                return
            self._sink(event)
        except Exception:
            # Never let logging capture break orchestrator execution.
            return

    def _normalize(self, record: logging.LogRecord) -> ProgressRecord | None:
        """Convert known workflow log signatures into UI-facing progress phases."""
        message = record.getMessage()
        timestamp = datetime.fromtimestamp(record.created)
        step_match = self._STEP_PATTERN.search(message)
        if step_match:
            return ProgressRecord(
                timestamp=timestamp,
                phase="step",
                message=message,
                step_index=int(step_match.group(1)),
                total_steps=int(step_match.group(2)),
            )
        if message.startswith("Phase A:"):
            return ProgressRecord(timestamp=timestamp, phase="tot", message=message)
        if message.startswith("Phase B:"):
            return ProgressRecord(timestamp=timestamp, phase="adversarial", message=message)
        if message.startswith("Starting Master Workflow"):
            return ProgressRecord(timestamp=timestamp, phase="planning", message=message)
        if message.startswith("Project broken down into"):
            return ProgressRecord(timestamp=timestamp, phase="planning", message=message)
        if "Completed. Summarizing for project context." in message:
            return ProgressRecord(timestamp=timestamp, phase="summary", message=message)
        if message.startswith("Master Workflow Complete"):
            return ProgressRecord(timestamp=timestamp, phase="complete", message=message)
        if record.levelno >= logging.ERROR:
            return ProgressRecord(timestamp=timestamp, phase="error", message=message)
        if record.levelno >= logging.WARNING:
            return ProgressRecord(timestamp=timestamp, phase="warning", message=message)
        return None


class OrchestratorAdapter:
    """Run MasterWorkflow with explicit config and normalized progress events."""

    async def run_async(self, config: RunConfig) -> RunResult:
        """Execute MasterWorkflow asynchronously and collect streamed progress."""
        result = RunResult()

        def sink(event: ProgressRecord) -> None:
            result.steps.append(event)
            if config.on_progress is not None:
                try:
                    config.on_progress(event)
                except Exception:
                    # UI callbacks must not break workflow execution.
                    LOGGER.debug("Progress callback failed; continuing run.", exc_info=True)
                    return

        handler = _ProgressCaptureHandler(sink)
        handler.setLevel(logging.INFO)

        root_logger = logging.getLogger("agy_orchestrator")
        old_level = root_logger.level
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        try:
            LOGGER.debug(
                "Creating MasterWorkflow(model=%s, effort=%s, agent_class=%s)",
                config.model,
                config.effort,
                config.agent_class.__name__,
            )
            workflow = MasterWorkflow(
                model=config.model,
                effort=config.effort,
                agent_class=config.agent_class,
            )
            result.final_output = await workflow.execute(config.prompt)
            return result
        finally:
            LOGGER.debug("Detaching progress capture handler.")
            root_logger.removeHandler(handler)
            root_logger.setLevel(old_level)

    def run(self, config: RunConfig) -> RunResult:
        """Synchronous wrapper for environments that call from a plain REPL loop."""
        return asyncio.run(self.run_async(config))
