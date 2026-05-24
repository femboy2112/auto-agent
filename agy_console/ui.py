"""UI rendering abstraction with rich-first and plain fallback backends."""

from __future__ import annotations

from datetime import datetime
import sys
from typing import ContextManager, Iterable, Protocol

from history_store import HistoryEntry

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    HAS_RICH = True
except Exception:  # pragma: no cover - optional dependency
    HAS_RICH = False


class Renderer(Protocol):
    def banner(self) -> None: ...
    def print_text(self, text: str) -> None: ...
    def print_error(self, text: str) -> None: ...
    def print_history(self, entries: Iterable[HistoryEntry]) -> None: ...
    def print_history_detail(self, index: int, entry: HistoryEntry) -> None: ...
    def print_progress_step(self, label: str, message: str) -> None: ...
    def print_run_success(self, elapsed_seconds: float) -> None: ...
    def print_run_failure(self, elapsed_seconds: float, error: str) -> None: ...
    def print_final_output(self, output: str) -> None: ...
    def prompt(self) -> str: ...
    def spinner_status(self, message: str) -> ContextManager[object]: ...


class RichRenderer:
    """Rich-powered renderer used when optional dependency is available."""
    def __init__(self) -> None:
        self._console = Console()

    def banner(self) -> None:
        self._console.print(Panel("[bold cyan]agy-console[/bold cyan] ready. Type [bold]help[/bold]."))

    def print_text(self, text: str) -> None:
        self._console.print(text)

    def print_error(self, text: str) -> None:
        self._console.print(f"[bold red]Error:[/bold red] {text}")

    def print_history(self, entries: Iterable[HistoryEntry]) -> None:
        items = list(entries)
        if not items:
            self.print_text("No history yet.")
            return

        table = Table(title="Run History", show_lines=False)
        table.add_column("Start", style="cyan")
        table.add_column("#", style="dim")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Agent")
        table.add_column("Model")
        table.add_column("Effort")
        table.add_column("Prompt", overflow="fold")
        table.add_column("Result Preview", overflow="fold")
        for idx, entry in enumerate(items, start=1):
            table.add_row(
                entry.started_at.strftime("%H:%M:%S"),
                str(idx),
                entry.status,
                f"{entry.duration_seconds:.2f}s",
                entry.agent,
                entry.model,
                entry.effort,
                entry.prompt,
                entry.result_preview,
            )
        self._console.print(table)

    def print_history_detail(self, index: int, entry: HistoryEntry) -> None:
        error_section = ""
        if entry.status == "failed" and entry.error_message:
            error_section = f"\n\nError:\n{entry.error_message}"
        body = (
            f"Index: {index}\n"
            f"Started: {entry.started_at.isoformat(timespec='seconds')}\n"
            f"Ended: {entry.ended_at.isoformat(timespec='seconds')}\n"
            f"Status: {entry.status}\n"
            f"Duration: {entry.duration_seconds:.2f}s\n"
            f"Agent: {entry.agent}\n"
            f"Model: {entry.model}\n"
            f"Effort: {entry.effort}\n"
            f"Prompt: {entry.prompt}\n\n"
            f"Final Output:\n{entry.final_output or '(empty output)'}"
            f"{error_section}"
        )
        self._console.print(Panel(body, title="History Detail", border_style="cyan"))

    def print_progress_step(self, label: str, message: str) -> None:
        marker, marker_style, label_style = _progress_styles(label)
        self._console.print(
            f"[{marker_style}]{marker}[/{marker_style}] "
            f"[{label_style}]{label}[/{label_style}] {message}"
        )

    def print_run_success(self, elapsed_seconds: float) -> None:
        self._console.print(f"[bold green]✓ Run complete[/bold green] [dim]({elapsed_seconds:.2f}s)[/dim]")

    def print_run_failure(self, elapsed_seconds: float, error: str) -> None:
        self._console.print(f"[bold red]✗ Run failed[/bold red] [dim]({elapsed_seconds:.2f}s)[/dim] {error}")

    def print_final_output(self, output: str) -> None:
        self._console.print(Panel(output or "(empty output)", title="Verified Output", border_style="green"))

    def prompt(self) -> str:
        return self._console.input("[bold cyan]agy[/bold cyan][dim]> [/dim]")

    def spinner_status(self, message: str) -> ContextManager[object]:
        return self._console.status(f"[cyan]{message}[/cyan]", spinner="dots")


class PlainRenderer:
    """Stdlib-only renderer with optional ANSI styling on interactive terminals."""
    def __init__(self) -> None:
        self._use_ansi = sys.stdout.isatty()

    def banner(self) -> None:
        if self._use_ansi:
            print("\033[1;36magy-console\033[0m ready. Type \033[1mhelp\033[0m.")
            return
        print("agy-console ready. Type help.")

    def print_text(self, text: str) -> None:
        print(text)

    def print_error(self, text: str) -> None:
        if self._use_ansi:
            print(f"\033[31mERROR:\033[0m {text}")
            return
        print(f"ERROR: {text}")

    def print_history(self, entries: Iterable[HistoryEntry]) -> None:
        items = list(entries)
        if not items:
            self.print_text("No history yet.")
            return
        for idx, entry in enumerate(items, start=1):
            ts = entry.started_at.strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[{idx}] [{ts}] status={entry.status} duration={entry.duration_seconds:.2f}s "
                f"{entry.agent} {entry.model}/{entry.effort} :: {entry.prompt}"
            )
            print(f"  -> {entry.result_preview}")

    def print_history_detail(self, index: int, entry: HistoryEntry) -> None:
        print(f"History #{index}")
        print(f"  started : {entry.started_at.isoformat(timespec='seconds')}")
        print(f"  ended   : {entry.ended_at.isoformat(timespec='seconds')}")
        print(f"  status  : {entry.status}")
        print(f"  duration: {entry.duration_seconds:.2f}s")
        print(f"  agent   : {entry.agent}")
        print(f"  model   : {entry.model}")
        print(f"  effort  : {entry.effort}")
        print(f"  prompt  : {entry.prompt}")
        if entry.status == "failed" and entry.error_message:
            print(f"  error   : {entry.error_message}")
        print("  final output:")
        print(entry.final_output or "(empty output)")

    def print_progress_step(self, label: str, message: str) -> None:
        marker, _, _ = _progress_styles(label)
        print(f"{marker} [{label}] {message}")

    def print_run_success(self, elapsed_seconds: float) -> None:
        print(f"SUCCESS: run complete ({elapsed_seconds:.2f}s)")

    def print_run_failure(self, elapsed_seconds: float, error: str) -> None:
        print(f"FAILED: run failed ({elapsed_seconds:.2f}s): {error}")

    def print_final_output(self, output: str) -> None:
        print("=== VERIFIED OUTPUT ===")
        print(output or "(empty output)")
        print("=======================")

    def prompt(self) -> str:
        return input("agy> ")

    def spinner_status(self, message: str) -> ContextManager[object]:
        # Keep behavior explicit in non-rich mode: print once and keep execution moving.
        print(message)
        return _NoopContext()


class UI:
    """Backend-agnostic UI facade used by command/application layers."""
    def __init__(self, renderer: Renderer | None = None) -> None:
        self._renderer = renderer or _create_renderer()

    def banner(self) -> None:
        self._renderer.banner()

    def print_text(self, text: str) -> None:
        self._renderer.print_text(text)

    def print_error(self, text: str) -> None:
        self._renderer.print_error(text)

    def print_history(self, entries: Iterable[HistoryEntry]) -> None:
        self._renderer.print_history(entries)

    def print_history_detail(self, index: int, entry: HistoryEntry) -> None:
        self._renderer.print_history_detail(index, entry)

    def print_progress_step(self, label: str, message: str) -> None:
        self._renderer.print_progress_step(label, message)

    def print_run_success(self, elapsed_seconds: float) -> None:
        self._renderer.print_run_success(elapsed_seconds)

    def print_run_failure(self, elapsed_seconds: float, error: str) -> None:
        self._renderer.print_run_failure(elapsed_seconds, error)

    def print_final_output(self, output: str) -> None:
        self._renderer.print_final_output(output)

    def prompt(self) -> str:
        return self._renderer.prompt()

    def spinner_status(self, message: str) -> ContextManager[object]:
        return self._renderer.spinner_status(message)


def _create_renderer() -> Renderer:
    if HAS_RICH:
        return RichRenderer()
    return PlainRenderer()


def now() -> datetime:
    return datetime.now()


class _NoopContext:
    """No-op context manager used as spinner fallback when rich is unavailable."""

    def __enter__(self) -> _NoopContext:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def _progress_styles(label: str) -> tuple[str, str, str]:
    """Map progress phase labels to marker/icon and color styles."""
    lowered = label.lower()
    if "error" in lowered:
        return ("✗", "bold red", "red")
    if "warning" in lowered or "warn" in lowered:
        return ("!", "bold yellow", "yellow")
    if "success" in lowered or "complete" in lowered:
        return ("✓", "bold green", "green")
    return ("•", "dim", "cyan")
