from typing import Optional, List
from agy_orchestrator.core.agent import AgentInstance

class CodexAgent(AgentInstance):
    @classmethod
    async def get_available_models(cls) -> List[str]:
        return ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-5.3-codex", "gpt-5.3-codex-spark", "gpt-5.2"]

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
            
        cmd = ["codex", "exec"]
        
        if self.model and self.model != "standard":
            cmd.extend(["--model", self.model])
        elif self.model == "standard":
            cmd.extend(["--model", "gpt-5.3-codex"])
            
        if hasattr(self, "effort"):
            cmd.extend(["--effort", self.effort])
            
        for k, v in self.additional_flags.items():
            cmd.extend([f"--{k}", str(v)])
            
        cmd.append(full_prompt)
        return cmd
