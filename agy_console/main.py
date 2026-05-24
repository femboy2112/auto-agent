"""Entrypoint for agy-console."""

from __future__ import annotations

import sys

from utils import OrchestratorBootstrapError, bootstrap_orchestrator_import

# Ensure parent workspace (containing `agy_orchestrator`) is importable
# before importing modules that reference orchestrator classes.
try:
    bootstrap_orchestrator_import()
except OrchestratorBootstrapError as exc:
    print(str(exc), file=sys.stderr)
    raise SystemExit(1) from exc

from console_app import ConsoleApp


def main() -> None:
    try:
        app = ConsoleApp()
    except Exception as exc:
        print(
            f"Startup failed while initializing console components: "
            f"{exc.__class__.__name__}: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    try:
        app.run()
    except Exception as exc:
        print(
            f"Fatal runtime error: {exc.__class__.__name__}: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
