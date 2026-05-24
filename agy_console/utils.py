"""General utility helpers."""

from __future__ import annotations

import importlib
import os
import shlex
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import List, Tuple


class OrchestratorBootstrapError(RuntimeError):
    """Bootstrap failure while resolving/importing agy_orchestrator."""


class CommandParseError(ValueError):
    """Raised when REPL input cannot be parsed into command tokens."""


def ensure_orchestrator_on_path() -> Path:
    """Add parent directory to sys.path in an idempotent way."""

    current = Path(__file__).resolve().parent
    parent = current.parent
    if not parent.exists() or not parent.is_dir():
        raise OrchestratorBootstrapError(
            "Startup failed: parent directory is missing or invalid.\n"
            f"Checked: {parent}"
        )

    parent_str = str(parent)
    normalized_existing = {str(Path(p).resolve()) for p in sys.path if p}
    if str(parent.resolve()) not in normalized_existing:
        sys.path.insert(0, parent_str)
    return parent


def bootstrap_orchestrator_import() -> None:
    """Validate path + importability of `agy_orchestrator` before app startup."""

    parent = ensure_orchestrator_on_path()
    package_dir = parent / "agy_orchestrator"

    if not package_dir.exists() or not package_dir.is_dir():
        raise OrchestratorBootstrapError(
            "Startup failed: `agy_orchestrator` directory was not found in parent directory.\n"
            f"Expected: {package_dir}\n"
            "Ensure `agy_console` and `agy_orchestrator` are sibling directories."
        )

    if find_spec("agy_orchestrator") is None:
        raise OrchestratorBootstrapError(
            "Startup failed: Python could not resolve `agy_orchestrator` after sys.path update.\n"
            f"Added path: {parent}"
        )

    try:
        importlib.import_module("agy_orchestrator")
    except Exception as exc:
        raise OrchestratorBootstrapError(
            "Startup failed: could not import `agy_orchestrator` after adding parent to sys.path.\n"
            f"Parent added: {parent}\n"
            "Check Python environment/dependencies and verify `agy_orchestrator` is a valid package.\n"
            f"Underlying error: {exc.__class__.__name__}: {exc}"
        ) from exc


def parse_command(line: str) -> Tuple[str, List[str]]:
    """Parse command input into command name + args."""

    text = line.strip()
    if not text:
        return "", []
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        raise CommandParseError(f"Invalid command syntax: {exc}") from exc
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def clear_screen() -> bool:
    """Clear the terminal screen across platforms; returns True on success."""
    code = os.system("cls" if os.name == "nt" else "clear")
    if code == 0:
        return True

    # Fallback for restricted shells where clear/cls is unavailable.
    print("\033[2J\033[H", end="")
    return False
