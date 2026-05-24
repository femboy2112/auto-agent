from typing import Optional, List
from agy_orchestrator.core.agent import AgentInstance

class ClaudeAgent(AgentInstance):
    @classmethod
    async def get_available_models(cls) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]

    @classmethod
    async def get_model_usage(cls, model: str) -> float:
        import asyncio
        try:
            process = await asyncio.create_subprocess_exec(
                "claude", "--usage", model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                # In a real environment, parse usage from stdout.
                pass
        except Exception:
            pass
        return 100.0

    def build_command(self, piped_input: Optional[str] = None) -> List[str]:
        full_prompt = self.prompt
        if piped_input:
            full_prompt += f"\n\n[Context]:\n{piped_input}"
            
        cmd = ["claude", "-p", full_prompt]
        
        if self.model:
            cmd.extend(["--model", self.model])
            
        for k, v in self.additional_flags.items():
            cmd.extend([f"--{k}", str(v)])
        return cmd
