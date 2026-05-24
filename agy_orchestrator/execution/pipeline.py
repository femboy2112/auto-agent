import asyncio
from typing import List, Optional
from agy_orchestrator.core.agent import AgentInstance

class LinearPipeline:
    """
    Executes a sequence of AgentInstances, piping the stdout of one 
    into the stdin (as additional prompt context) of the next.
    """
    def __init__(self, instances: List[AgentInstance]):
        self.instances = instances
        
    async def execute(self, initial_input: Optional[str] = None) -> str:
        current_input = initial_input
        for idx, instance in enumerate(self.instances):
            current_input = await instance.run_async(piped_input=current_input)
        return current_input

class ParallelSwarm:
    """
    Executes multiple AgentInstances concurrently. Useful for exploring 
    multiple paths (like in Tree of Thought) or handling chunked tasks.
    """
    def __init__(self, instances: List[AgentInstance]):
        self.instances = instances
        
    async def execute(self, common_input: Optional[str] = None) -> List[str]:
        tasks = [
            asyncio.create_task(instance.run_async(piped_input=common_input))
            for instance in self.instances
        ]
        results = await asyncio.gather(*tasks)
        return list(results)
