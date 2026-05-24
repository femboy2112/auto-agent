import asyncio
import shlex
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class AgyInstance:
    """
    Represents a single execution of the agy CLI.
    """
    def __init__(
        self,
        prompt: str,
        model: Optional[str] = None,
        effort: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        additional_flags: Optional[Dict[str, str]] = None
    ):
        self.prompt = prompt
        self.model = model
        self.effort = effort
        self.input_files = input_files or []
        self.output_files = output_files or []
        self.additional_flags = additional_flags or {}
        
        self.stdout = ""
        self.stderr = ""
        self.returncode: Optional[int] = None

    def build_command(self) -> List[str]:
        # Inject model/effort requirements into the prompt since agy doesn't have native flags
        injected_prompt = f"System constraints: \n"
        if self.model:
            injected_prompt += f"- Use model architecture equivalent to: {self.model}\n"
        if self.effort:
            injected_prompt += f"- Effort level: {self.effort}\n"
        if self.input_files:
            injected_prompt += f"- Read these files: {', '.join(self.input_files)}\n"
        if self.output_files:
            injected_prompt += f"- Ensure these files are created: {', '.join(self.output_files)}\n"
        
        injected_prompt += f"- EXCELLENCE: If generating visual output (UI, shaders, graphics), ensure it is visually stunning, highly dynamic, volumetric, and cinematic (e.g. use ACES tonemapping, fbm noise, complex physical rendering). It MUST be reference-grade quality (e.g. if rendering a black hole, it must accurately simulate the Interstellar Gargantua effect with full gravitational lensing, warped accretion disk visible over/under the event horizon, and extreme relativistic Doppler beaming).\n"
        injected_prompt += f"- PERFORMANCE: If writing shaders or complex graphics, aggressively optimize to hit a locked 60fps. (e.g., Use adaptive raymarching steps, map 3D noise to 2D where possible to reduce hash lookups, and avoid redundant math in heavy loops).\n"
        injected_prompt += f"- CORRECTNESS: Double-check that all variable and uniform names match exactly between different files (e.g. C++ host code and GLSL shaders). Ensure it is not static.\n"
        injected_prompt += f"- NO SUDO: Do NOT use `sudo` under any circumstances (e.g. for package installation). This is a non-interactive environment and password prompts will cause a permanent hang. If dependencies are missing, install them in user space or gracefully fail.\n"
        
        injected_prompt += f"\n{self.prompt}"
        
        cmd = ["agy", "--print", injected_prompt, "--dangerously-skip-permissions"]
        
        for k, v in self.additional_flags.items():
            cmd.extend([f"--{k}", str(v)])
            
        return cmd

    async def run_async(self, piped_input: Optional[str] = None) -> str:
        """Executes the instance asynchronously."""
        cmd = self.build_command()
        
        if piped_input:
            cmd[-2] = f"{cmd[-2]}\n\n[Piped Context from previous step]:\n{piped_input}"
            
        logger.info(f"Executing agy command")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout_bytes, stderr_bytes = await process.communicate()
        
        self.stdout = stdout_bytes.decode()
        self.stderr = stderr_bytes.decode()
        self.returncode = process.returncode
        
        if self.returncode != 0:
            logger.error(f"Execution failed with return code {self.returncode}:\n{self.stderr}")
            raise RuntimeError(f"AgyInstance failed (code {self.returncode}): {self.stderr}")
            
        return self.stdout

    def run(self, piped_input: Optional[str] = None) -> str:
        """Synchronous wrapper for run_async."""
        return asyncio.run(self.run_async(piped_input))
