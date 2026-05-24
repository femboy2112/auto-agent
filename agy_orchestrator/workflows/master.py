import logging
import json
from typing import Optional, List

from agy_orchestrator.core.agents.agy_agent import AgyAgent
from agy_orchestrator.core.agent import AgentInstance
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
        verifier: Optional[QualityVerifier] = None,
        agent_class=AgyAgent
    ):
        self.model = model
        self.effort = effort
        self.branches = branches
        self.max_iterations = max_iterations
        self.verifier = verifier
        self.agent_class = agent_class

    async def execute(self, initial_prompt: str) -> str:
        logger.info("Starting Master Workflow Planning Phase...")
        
        # 1. Planner Phase
        planner_prompt = (
            f"You are the Lead Architect. Break down the following complex project into a logical sequence of implementation steps.\n"
            f"Output ONLY a valid JSON list of strings, where each string is a detailed prompt for a single step.\n"
            f"Example: [\"Step 1: Setup project structure and core utilities...\", \"Step 2: Implement UI component X...\"]\n\n"
            f"Project Request:\n{initial_prompt}"
        )
        
        planner = self.agent_class(prompt=planner_prompt, model=self.model, effort="high")
        plan_output = await planner.run_async()

        # Capture session established by planner for reuse across all subsequent calls
        workflow_session_id = getattr(planner, "session_id", None)
        if workflow_session_id:
            logger.info("Workflow session established: %s", workflow_session_id)
        
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
            # ToT branches run fresh sessions — concurrent --fork-session on the same parent
            # causes race conditions. They're throwaway explorers anyway.
            tot_branches = [
                self.agent_class(prompt=step_prompt, model=self.model, effort=self.effort)
                for _ in range(self.branches)
            ]
            # Evaluator is sequential, can safely resume main session
            eval_kwargs = dict(model=self.model, effort="high")
            if workflow_session_id:
                eval_kwargs["session_id"] = workflow_session_id
            tot_evaluator = self.agent_class(prompt="", **eval_kwargs)
            tot = TreeOfThought(tot_branches, tot_evaluator)
            best_tot_output = await tot.execute()
            
            # Phase B: Adversarial Review (Refinement) — resume main workflow session
            logger.info("Phase B: Adversarial Review Refinement")
            gen_kwargs = dict(model=self.model, effort=self.effort)
            critic_kwargs = dict(model=self.model, effort="high")
            if workflow_session_id:
                try:
                    gen_kwargs["session_id"] = workflow_session_id
                    critic_kwargs["session_id"] = workflow_session_id
                except Exception:
                    pass
            adv_generator = self.agent_class(prompt=step_prompt, **gen_kwargs)

            adv_prompt = (
                f"{step_prompt}\n\n"
                f"Please refine, finalize, and perfect the following draft implementation. Ensure it meets the highest standards and resolves any bugs:\n"
                f"{best_tot_output}"
            )

            adv_critic = self.agent_class(prompt="", **critic_kwargs)
            
            adv = AdversarialReview(
                generator_instance=adv_generator,
                critic_instance=adv_critic,
                verifier=self.verifier,
                max_iterations=self.max_iterations
            )
            
            final_step_output = await adv.execute(adv_prompt)
            
            logger.info(f"Step {i+1} Completed. Summarizing for project context.")
            # Summarize the step output to keep project_context compact.
            # Passing full HTML/code outputs into every subsequent prompt balloons to 50KB+.
            summarize_kwargs = dict(model=self.model, effort="low")
            if workflow_session_id:
                try:
                    summarize_kwargs["session_id"] = workflow_session_id
                except Exception:
                    pass
            summarizer = self.agent_class(
                prompt=(
                    f"In 3-5 bullet points, summarize what was just implemented in Step {i+1}.\n"
                    f"Focus on: what files were created/modified, key design decisions, and any\n"
                    f"CSS classes, JS functions, or IDs that other steps should know about.\n"
                    f"Be concise. Do NOT reproduce the full code.\n\nStep output:\n{final_step_output[:8000]}"
                ),
                **summarize_kwargs
            )
            try:
                step_summary = await summarizer.run_async()
                # Update workflow session from summarizer if we don't have one yet
                if not workflow_session_id:
                    workflow_session_id = getattr(summarizer, "session_id", None)
            except Exception as e:
                logger.warning(f"Summarizer failed ({e}), falling back to task description.")
                step_summary = f"Completed: {task[:300]}"
            project_context += f"\n--- Step {i+1} Summary ---\n{step_summary}\n"
            
        logger.info("Master Workflow Complete!")
        return project_context
