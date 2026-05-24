"""Command handling for the REPL."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

from history_store import HistoryEntry, HistoryStore
from orchestrator_adapter import OrchestratorAdapter, ProgressRecord, RunConfig
from state import ConsoleState
from ui import UI, now
from utils import CommandParseError, clear_screen, parse_command

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    should_exit: bool = False


@dataclass
class CommandContext:
    state: ConsoleState
    ui: UI
    history: HistoryStore
    orchestrator: OrchestratorAdapter


@dataclass
class ParsedCommand:
    command: str
    args: list[str]


@dataclass
class ParseError:
    """Represents a user-facing parse issue that should not break the REPL."""

    message: str


class CommandHandler:
    """Parses input and routes all supported console commands."""

    def __init__(
        self,
        *,
        state: ConsoleState,
        ui: UI,
        adapter: OrchestratorAdapter,
        history: HistoryStore,
    ) -> None:
        self._ctx = CommandContext(
            state=state,
            ui=ui,
            history=history,
            orchestrator=adapter,
        )

    def handle(self, line: str) -> CommandResult:
        """Handle one REPL input line and return loop control state."""
        try:
            parsed = _parse_repl_input(line)
            if isinstance(parsed, ParseError):
                self._ctx.ui.print_error(parsed.message)
                return CommandResult()

            if not parsed.command:
                return CommandResult()

            should_continue = handle_command(self._ctx, parsed.command, parsed.args)
            return CommandResult(should_exit=not should_continue)
        except Exception as exc:
            logger.exception("Unexpected command handler failure")
            self._ctx.ui.print_error(f"Command failed unexpectedly: {exc.__class__.__name__}: {exc}")
            return CommandResult()


def help_text() -> str:
    return """agy-console commands:
  run <prompt>
      Execute MasterWorkflow using current model/effort/agent settings.
      Example: run Build a robust async retry helper in Python.

  model <default|gpt-5.3-codex|gpt-5.5>
      Switch active model for future runs.
      Example: model gpt-5.5

  effort <low|medium|high>
      Set reasoning effort for future runs.
      Example: effort high

  agent <claude|codex>
      Switch backend agent class used by MasterWorkflow.
      Example: agent claude

  history <index?>
      Show prior run sessions. Optionally pass a 1-based index for details.
      Examples: history
                history 2

  clear
      Clear the terminal screen (cross-platform).

  help
      Show this command reference.

  exit
      Quit agy-console cleanly.
"""


def _parse_repl_input(line: str) -> ParsedCommand | ParseError:
    """Normalize one raw input line into parsed command tokens."""
    stripped = line.strip()
    if not stripped:
        return ParsedCommand(command="", args=[])

    try:
        cmd, args = parse_command(stripped)
    except CommandParseError as exc:
        return ParseError(f"Malformed command: {exc}. Hint: close all quotes, then retry.")

    return ParsedCommand(command=cmd, args=args)


def _usage(command: str) -> str:
    usage_map = {
        "run": "Usage: run <prompt>",
        "model": "Usage: model <default|gpt-5.3-codex|gpt-5.5>",
        "effort": "Usage: effort <low|medium|high>",
        "agent": "Usage: agent <claude|codex>",
        "history": "Usage: history OR history <index>",
        "clear": "Usage: clear",
        "help": "Usage: help",
        "exit": "Usage: exit",
    }
    return usage_map.get(command, "Type 'help' for usage.")


def _require_arg_count(
    command: str,
    args: Sequence[str],
    *,
    minimum: int,
    maximum: int | None = None,
) -> str | None:
    if len(args) < minimum:
        return _usage(command)
    if maximum is not None and len(args) > maximum:
        return _usage(command)
    return None


def handle_command(ctx: CommandContext, cmd: str, args: list[str]) -> bool:
    if cmd == "help":
        err = _require_arg_count("help", args, minimum=0, maximum=0)
        if err:
            ctx.ui.print_error(err)
        else:
            ctx.ui.print_text(help_text())
        return True
    if cmd == "clear":
        err = _require_arg_count("clear", args, minimum=0, maximum=0)
        if err:
            ctx.ui.print_error(err)
        else:
            if not clear_screen():
                ctx.ui.print_text("Screen redraw fallback applied (clear command unavailable).")
        return True
    if cmd == "history":
        _handle_history(ctx, args)
        return True
    if cmd == "model":
        return _handle_model(ctx, args)
    if cmd == "effort":
        return _handle_effort(ctx, args)
    if cmd == "agent":
        return _handle_agent(ctx, args)
    if cmd == "run":
        return _handle_run(ctx, args)
    if cmd in {"exit", "quit"}:
        err = _require_arg_count("exit", args, minimum=0, maximum=0)
        if err:
            ctx.ui.print_error(err)
            return True
        ctx.ui.print_text("Shutting down agy-console.")
        return False

    ctx.ui.print_error(f"Unknown command: {cmd}. Type 'help'.")
    return True


def _handle_model(ctx: CommandContext, args: list[str]) -> bool:
    err = _require_arg_count("model", args, minimum=1, maximum=1)
    if err:
        ctx.ui.print_error(err)
        return True
    try:
        ctx.state.set_model(args[0])
    except ValueError as exc:
        ctx.ui.print_error(f"{exc}. {_usage('model')}")
        return True
    ctx.ui.print_text(f"Model set to: {ctx.state.model}")
    return True


def _handle_effort(ctx: CommandContext, args: list[str]) -> bool:
    err = _require_arg_count("effort", args, minimum=1, maximum=1)
    if err:
        ctx.ui.print_error(err)
        return True
    try:
        ctx.state.set_effort(args[0])
    except ValueError as exc:
        ctx.ui.print_error(f"{exc}. {_usage('effort')}")
        return True
    ctx.ui.print_text(f"Effort set to: {ctx.state.effort}")
    return True


def _handle_agent(ctx: CommandContext, args: list[str]) -> bool:
    err = _require_arg_count("agent", args, minimum=1, maximum=1)
    if err:
        ctx.ui.print_error(err)
        return True
    try:
        ctx.state.set_agent(args[0])
    except ValueError as exc:
        ctx.ui.print_error(f"{exc}. {_usage('agent')}")
        return True
    ctx.ui.print_text(f"Agent set to: {ctx.state.agent}")
    return True


def _handle_run(ctx: CommandContext, args: list[str]) -> bool:
    """Execute a workflow run and persist success/failure history."""
    err = _require_arg_count("run", args, minimum=1)
    if err:
        ctx.ui.print_error(err)
        return True

    prompt = " ".join(args)
    model = ctx.state.model
    effort = ctx.state.effort
    agent = ctx.state.agent
    agent_class = ctx.state.agent_class

    def _print_progress(event: ProgressRecord) -> None:
        label = event.phase
        if event.step_index is not None and event.total_steps is not None:
            label = f"{label} {event.step_index}/{event.total_steps}"
        ctx.ui.print_progress_step(label, event.message)

    cfg = RunConfig(
        prompt=prompt,
        model=model,
        effort=effort,
        agent_class=agent_class,
        on_progress=_print_progress,
    )

    started_at = now()
    ended_at = started_at
    status = "success"
    error_message: str | None = None
    final_output = ""

    try:
        logger.debug("Run starting: model=%s effort=%s agent=%s", model, effort, agent)
        with ctx.ui.spinner_status("Running MasterWorkflow..."):
            run_result = ctx.orchestrator.run(cfg)
        final_output = run_result.final_output
        ended_at = now()
        elapsed = max((ended_at - started_at).total_seconds(), 0.0)
        ctx.ui.print_run_success(elapsed)
        ctx.ui.print_final_output(final_output)
    except Exception as exc:
        logger.exception("Run failed")
        status = "failed"
        error_message = f"{exc.__class__.__name__}: {exc}"
        concise = error_message.splitlines()[0].strip()
        final_output = f"Run failed: {concise}"
        ended_at = now()
        elapsed = max((ended_at - started_at).total_seconds(), 0.0)
        ctx.ui.print_run_failure(elapsed, final_output)

    try:
        duration_seconds = max((ended_at - started_at).total_seconds(), 0.0)
        preview = final_output.strip().replace("\n", " ")[:120]
        ctx.history.add(
            HistoryEntry(
                started_at=started_at,
                timestamp=started_at,
                ended_at=ended_at,
                status=status,
                duration_seconds=duration_seconds,
                prompt=prompt,
                model=model,
                effort=effort,
                agent=agent,
                result_preview=preview,
                final_output=final_output,
                error_message=error_message,
            )
        )
        logger.debug("History recorded: status=%s duration=%.3fs", status, duration_seconds)
    except Exception as exc:
        logger.exception("History save failed")
        ctx.ui.print_error(
            f"History save failed ({exc.__class__.__name__}): {exc}. "
            "Run output was shown but not recorded."
        )
    return True


def _handle_history(ctx: CommandContext, args: list[str]) -> None:
    err = _require_arg_count("history", args, minimum=0, maximum=1)
    if err:
        ctx.ui.print_error(err)
        return

    entries = ctx.history.all()
    if not args:
        ctx.ui.print_history(entries)
        return

    try:
        index = int(args[0])
    except ValueError:
        ctx.ui.print_error(f"history index must be an integer. {_usage('history')}")
        return

    if index < 1 or index > len(entries):
        ctx.ui.print_error(f"history index out of range (1-{len(entries)}).")
        return

    entry = entries[index - 1]
    ctx.ui.print_history_detail(index, entry)
