"""Simple in-memory history for `run` commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal

VALID_HISTORY_STATUSES = ("success", "failed")


@dataclass
class HistoryEntry:
    timestamp: datetime
    started_at: datetime
    ended_at: datetime
    status: Literal["success", "failed"]
    duration_seconds: float
    prompt: str
    model: str
    effort: str
    agent: str
    result_preview: str
    final_output: str
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_HISTORY_STATUSES:
            allowed = ", ".join(VALID_HISTORY_STATUSES)
            raise ValueError(f"Status must be one of: {allowed}")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")

    @property
    def agent_name(self) -> str:
        """Backward-compatible alias for older call sites."""
        return self.agent


@dataclass
class HistoryStore:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, entry: HistoryEntry) -> None:
        self.entries.append(entry)

    def all(self) -> List[HistoryEntry]:
        return list(self.entries)
