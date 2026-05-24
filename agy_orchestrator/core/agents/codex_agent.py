from typing import Optional, List
from agy_orchestrator.core.agent import AgentInstance

class CodexAgent(AgentInstance):
    @classmethod
    async def get_available_models(cls) -> List[str]:
        return ["codex-cushman", "codex-davinci"]

    @classmethod
    async def get_model_usage(cls, model: str) -> float:
        import asyncio
        try:
            process = await asyncio.create_subprocess_exec(
                "codex", "--usage", model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                pass
        except Exception:
            pass
        return 100.0

    def filter_stderr(self, stderr: str) -> str:
        lines = stderr.splitlines()
        filtered = [l for l in lines if "network" not in l.lower() and "timeout" not in l.lower()]
        return "\n".join(filtered)

    def build_command(self, piped_input: Optional[str] = None) -> List[str]:
        full_prompt = self.prompt
        if piped_input:
            full_prompt += f"\n\n[Context]:\n{piped_input}"
            
        cmd = ["codex", "--prompt", full_prompt]
        if self.model:
            cmd.extend(["--model", self.model])
            
        for k, v in self.additional_flags.items():
            cmd.extend([f"--{k}", str(v)])
        return cmd
