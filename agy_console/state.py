"""Runtime state and validation for the interactive console."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from agy_orchestrator.core.agent import AgentInstance
from agy_orchestrator.core.agents.claude_agent import ClaudeAgent
from agy_orchestrator.core.agents.codex_agent import CodexAgent

VALID_MODELS = ("default", "gpt-5.3-codex", "gpt-5.5")
VALID_EFFORTS = ("low", "medium", "high")
VALID_AGENTS = ("claude", "codex")
AGENT_CLASS_MAP: dict[str, Type[AgentInstance]] = {
    "claude": ClaudeAgent,
    "codex": CodexAgent,
}


@dataclass
class ConsoleState:
    """Mutable runtime settings for the current console session."""

    model: str = "default"
    effort: str = "medium"
    agent: str = "codex"
    agent_class: Type[AgentInstance] = CodexAgent

    def __post_init__(self) -> None:
        self.set_model(self.model)
        self.set_effort(self.effort)
        self.set_agent(self.agent)

    def set_model(self, value: str) -> None:
        model = value.strip().lower()
        if model not in VALID_MODELS:
            allowed = ", ".join(VALID_MODELS)
            raise ValueError(f"Model must be one of: {allowed}")
        self.model = model

    def set_effort(self, value: str) -> None:
        effort = value.strip().lower()
        if effort not in VALID_EFFORTS:
            allowed = ", ".join(VALID_EFFORTS)
            raise ValueError(f"Effort must be one of: {allowed}")
        self.effort = effort

    def set_agent(self, value: str) -> None:
        agent = value.strip().lower()
        if agent not in VALID_AGENTS:
            allowed = ", ".join(VALID_AGENTS)
            raise ValueError(f"Agent must be one of: {allowed}")
        self.agent = agent
        self.agent_class = AGENT_CLASS_MAP[agent]

    @property
    def agent_name(self) -> str:
        """Backward-compatible alias for older call sites."""
        return self.agent
