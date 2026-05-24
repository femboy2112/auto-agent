import logging
import asyncio
from typing import List, Tuple
from agy_orchestrator.core.instance import AgyInstance
from agy_orchestrator.execution.pipeline import ParallelSwarm

logger = logging.getLogger(__name__)

class TreeOfThought:
    """
    Implements a single-layer Tree-of-Thought (ToT) generation strategy.
    Generates multiple independent solution paths and uses an Evaluator
    instance to score and select the best path.
    """
    def __init__(self, branch_instances: List[AgyInstance], evaluator_instance: AgyInstance):
        self.branch_instances = branch_instances
        self.evaluator = evaluator_instance
        
    async def execute(self) -> str:
        logger.info(f"Generating {len(self.branch_instances)} ToT branches concurrently...")
        
        # Execute branches in parallel
        swarm = ParallelSwarm(self.branch_instances)
        outputs = await swarm.execute()
        
        logger.info("Evaluating generated branches...")
        scored_outputs: List[Tuple[int, str]] = []
        
        for idx, out in enumerate(outputs):
            self.evaluator.prompt = (
                f"Evaluate the following solution on a scale of 1-10 based on correctness, "
                f"efficiency, and adherence to best practices. "
                f"CRITICAL: If it involves visual graphics, score it highly ONLY if it is extremely high-fidelity, volumetric, and cinematic. It MUST be reference-grade quality (e.g. if rendering a black hole, it must accurately simulate the Interstellar Gargantua effect with full gravitational lensing, warped accretion disk visible over/under the event horizon, and extreme relativistic Doppler beaming).\n"
                f"CRITICAL: Penalize heavily (score < 5) if variable or uniform names do not match exactly across different files (e.g. C++ vs GLSL).\n"
                f"Reply ONLY with the integer score.\n\nSolution:\n{out}"
            )
            score_str = await self.evaluator.run_async()
            
            try:
                # Extract numeric score from string
                digits = ''.join(filter(str.isdigit, score_str))
                score = int(digits) if digits else 0
            except ValueError:
                score = 0
                
            logger.info(f"Branch {idx+1} evaluated with score: {score}")
            scored_outputs.append((score, out))
            
        # Select the branch with the highest score
        scored_outputs.sort(key=lambda x: x[0], reverse=True)
        best_score, best_output = scored_outputs[0]
        
        logger.info(f"Selected best branch with score {best_score}")
        return best_output
