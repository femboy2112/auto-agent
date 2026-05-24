import logging
import json
from typing import Optional, List

from agy_orchestrator.core.instance import AgyInstance
from agy_orchestrator.execution.verifier import QualityVerifier
from agy_orchestrator.workflows.adversarial import AdversarialReview
from agy_orchestrator.workflows.tree_of_thought import TreeOfThought

logger = logging.getLogger(__name__)

class MasterWorkflow:
    """
    Combines Tree of Thought and Adversarial Review to manage and execute 
    large, complex projects accurately.
    """
    def __init__(
        self,
        model: str,
        effort: str,
        branches: int = 3,
        max_iterations: int = 5,
        verifier: Optional[QualityVerifier] = None
    ):
        self.model = model
        self.effort = effort
        self.branches = branches
        self.max_iterations = max_iterations
        self.verifier = verifier

    async def execute(self, initial_prompt: str) -> str:
        logger.info("Starting Master Workflow Planning Phase...")
        
        # 1. Planner Phase
        planner_prompt = (
            f"You are the Lead Architect. Break down the following complex project into a logical sequence of implementation steps.\n"
            f"Output ONLY a valid JSON list of strings, where each string is a detailed prompt for a single step.\n"
            f"Example: [\"Step 1: Setup project structure and core utilities...\", \"Step 2: Implement UI component X...\"]\n\n"
            f"Project Request:\n{initial_prompt}"
        )
        
        planner = AgyInstance(prompt=planner_prompt, model=self.model, effort="high")
        plan_output = await planner.run_async()
        
        # Extract JSON list from plan_output
        tasks: List[str] = []
        try:
            start = plan_output.find('[')
            end = plan_output.rfind(']') + 1
            if start != -1 and end != 0:
                tasks = json.loads(plan_output[start:end])
            else:
                raise ValueError("No JSON array found.")
        except Exception as e:
            logger.warning(f"Failed to parse Planner output as JSON: {e}. Defaulting to a single step.")
            tasks = [initial_prompt]
            
        logger.info(f"Project broken down into {len(tasks)} steps.")
        
        project_context = f"Original Goal: {initial_prompt}\n\n=== Accumulated Implementation ===\n"
        
        # 2. Execution Loop
        for i, task in enumerate(tasks):
            logger.info(f"--- Executing Step {i+1}/{len(tasks)} ---")
            logger.info(f"Task description: {task[:100]}...")
            
            step_prompt = (
                f"You are implementing Step {i+1} of a larger project.\n\n"
                f"Project Context (What has been built so far):\n{project_context}\n\n"
                f"Current Task to implement NOW:\n{task}"
            )
            
            # Phase A: Tree of Thought (Exploration)
            logger.info("Phase A: Tree of Thought Exploration")
            tot_branches = [
                AgyInstance(prompt=step_prompt, model=self.model, effort=self.effort)
                for _ in range(self.branches)
            ]
            tot_evaluator = AgyInstance(prompt="", model=self.model, effort="high")
            tot = TreeOfThought(tot_branches, tot_evaluator)
            best_tot_output = await tot.execute()
            
            # Phase B: Adversarial Review (Refinement)
            logger.info("Phase B: Adversarial Review Refinement")
            adv_generator = AgyInstance(prompt=step_prompt, model=self.model, effort=self.effort)
            
            adv_prompt = (
                f"{step_prompt}\n\n"
                f"Please refine, finalize, and perfect the following draft implementation. Ensure it meets the highest standards and resolves any bugs:\n"
                f"{best_tot_output}"
            )
            
            adv_critic = AgyInstance(prompt="", model=self.model, effort="high")
            
            adv = AdversarialReview(
                generator_instance=adv_generator,
                critic_instance=adv_critic,
                verifier=self.verifier,
                max_iterations=self.max_iterations
            )
            
            final_step_output = await adv.execute(adv_prompt)
            
            logger.info(f"Step {i+1} Completed. Appending to Project Context.")
            project_context += f"\n--- Step {i+1} Output ---\n{final_step_output}\n"
            
        logger.info("Master Workflow Complete!")
        return project_context
