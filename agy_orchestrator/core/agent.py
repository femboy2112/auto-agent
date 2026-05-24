import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class AgentInstance(ABC):
    """
    Abstract base class representing a single execution of an AI agent CLI.
    """
    def __init__(
        self,
        prompt: str,
        model: Optional[str] = None,
        additional_flags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.prompt = prompt
        self.model = model
        self.additional_flags = additional_flags or {}
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        self.stdout = ""
        self.stderr = ""
        self.returncode: Optional[int] = None
        self.max_retries = 3

    @classmethod
    @abstractmethod
    async def get_available_models(cls) -> List[str]:
        """
        Dynamically query the CLI for available models.
        """
        pass

    @classmethod
    @abstractmethod
    async def get_model_usage(cls, model: str) -> float:
        """
        Dynamically query the CLI for remaining usage percentage of a model.
        Returns a float between 0.0 and 100.0.
        """
        pass

    @abstractmethod
    def build_command(self, piped_input: Optional[str] = None) -> List[str]:
        """
        Build the command line arguments for the agent CLI execution.
        """
        pass

    def filter_stderr(self, stderr: str) -> str:
        """
        Filter out expected network errors or verbosely piped logs.
        Can be overridden by subclasses.
        """
        return stderr

    async def run_async(self, piped_input: Optional[str] = None) -> str:
        """Executes the instance asynchronously with exponential backoff for network smoothing."""
        cmd = self.build_command(piped_input)
        
        logger.info(f"Executing agent command")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout_bytes, stderr_bytes = await process.communicate()
                
                self.stdout = stdout_bytes.decode()
                raw_stderr = stderr_bytes.decode()
                self.stderr = self.filter_stderr(raw_stderr)
                self.returncode = process.returncode
                
                if self.returncode == 0:
                    return self.stdout
                
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed with code {self.returncode}:\n{self.stderr}")
                
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{self.max_retries} encountered an exception: {e}")
                self.stderr = str(e)
            
            if attempt < self.max_retries:
                backoff_time = 2 ** attempt
                logger.info(f"Retrying in {backoff_time} seconds...")
                await asyncio.sleep(backoff_time)
                
        logger.error(f"All {self.max_retries} attempts failed.")
        raise RuntimeError(f"AgentInstance failed after {self.max_retries} attempts: {self.stderr}")

    def run(self, piped_input: Optional[str] = None) -> str:
        """Synchronous wrapper for run_async."""
        return asyncio.run(self.run_async(piped_input))
