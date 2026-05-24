"""Top-level REPL application wiring."""

from __future__ import annotations

import logging

from commands import CommandHandler
from history_store import HistoryStore
from orchestrator_adapter import OrchestratorAdapter
from state import ConsoleState
from ui import UI


class ConsoleApp:
    """Coordinates UI, command dispatch, state, and orchestrator adapter."""

    def __init__(self) -> None:
        self.state = ConsoleState()
        self.ui = UI()
        self.adapter = OrchestratorAdapter()
        self.history = HistoryStore()
        self.commands = CommandHandler(
            state=self.state,
            ui=self.ui,
            adapter=self.adapter,
            history=self.history,
        )

    def run(self) -> None:
        """Run the interactive REPL loop until explicit exit or terminal interrupt."""
        logger = logging.getLogger(__name__)
        try:
            self.ui.banner()
        except Exception as exc:
            logger.debug("Banner rendering failed", exc_info=exc)
            print(f"Startup warning: could not render banner: {exc.__class__.__name__}: {exc}")

        while True:
            try:
                line = self.ui.prompt()
            except (EOFError, KeyboardInterrupt):
                logger.debug("Received terminal interrupt; exiting REPL loop.")
                self.ui.print_text("\nExiting agy-console.")
                break
            except Exception as exc:
                logger.debug("Prompt read failed", exc_info=exc)
                self.ui.print_error(
                    f"Input error: {exc.__class__.__name__}: {exc}. Session is still active."
                )
                continue

            try:
                result = self.commands.handle(line)
            except Exception as exc:
                logger.debug("Command dispatch raised unexpected exception", exc_info=exc)
                self.ui.print_error(
                    f"Dispatch error: {exc.__class__.__name__}: {exc}. Continuing session."
                )
                continue

            if result.should_exit:
                logger.debug("Exit requested by command handler.")
                self.ui.print_text("Exiting agy-console.")
                break
