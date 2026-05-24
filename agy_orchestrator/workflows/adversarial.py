import logging
from typing import Optional
from agy_orchestrator.core.agent import AgentInstance
from agy_orchestrator.execution.verifier import QualityVerifier

logger = logging.getLogger(__name__)

class AdversarialReview:
    """
    Executes a continuous loop where a Generator produces output,
    and a Critic reviews it against specifications. The loop 
    continues until the Critic explicitly approves the output.
    """
    def __init__(
        self,
        generator_instance: AgentInstance,
        critic_instance: AgentInstance,
        verifier: Optional[QualityVerifier] = None,
        max_iterations: int = 5
    ):
        self.generator = generator_instance
        self.critic = critic_instance
        self.verifier = verifier
        self.max_iterations = max_iterations
        
    async def execute(self, initial_prompt: str) -> str:
        current_prompt = initial_prompt
        last_output = ""
        
        for iteration in range(self.max_iterations):
            logger.info(f"Adversarial Review Iteration {iteration+1}/{self.max_iterations}")
            
            self.generator.prompt = current_prompt
            last_output = await self.generator.run_async()
            
            # Programmatic Verification Gate
            if self.verifier:
                success, error_msg = await self.verifier.verify(working_directory=".")
                if not success:
                    logger.info("Programmatic verification failed. Sending back to generator.")
                    current_prompt = (
                        f"{initial_prompt}\n\nYour last output failed verification with the following error:\n"
                        f"{error_msg}\nPlease fix the issues and output the corrected version."
                    )
                    continue
                    
            # LLM Critic Gate
            critic_prompt = (
                f"Please review the following output against the original requirement.\n"
                f"Original Requirement:\n{initial_prompt}\n\n"
                f"Generated Output:\n{last_output}\n\n"
                f"CRITICAL REVIEW INSTRUCTIONS:\n"
                f"1. CORRECTNESS: Look for any mismatched variable names or uniforms across files (e.g. C++ vs GLSL).\n"
                f"2. EXCELLENCE: If it generates visuals, ensure they are incredibly high-quality, dynamic, volumetric, and cinematic. It MUST be reference-grade quality (e.g. if rendering a black hole, it must accurately simulate the Interstellar Gargantua effect with full gravitational lensing, warped accretion disk visible over/under the event horizon, and extreme relativistic Doppler beaming). Do not accept flat or basic visuals.\n"
                f"3. CONVERGENCE: If the output is already stunning, highly performant, and meets all requirements without bugs, you MUST reply exactly with 'APPROVED'. Do not get stuck in an endless loop of minor aesthetic nitpicks. Reward excellence.\n"
                f"If it meets all requirements perfectly with NO bugs and STUNNING visual fidelity, reply exactly with 'APPROVED'. "
                f"If not, provide specific, actionable changes needed."
            )
            self.critic.prompt = critic_prompt
            critic_feedback = await self.critic.run_async()
            
            if "APPROVED" in critic_feedback.strip().upper():
                logger.info("Critic approved the output.")
                return last_output
                
            logger.info("Critic requested changes. Iterating...")
            current_prompt = (
                f"{initial_prompt}\n\n"
                f"Your last output:\n{last_output}\n\n"
                f"Critic Feedback:\n{critic_feedback}\n\n"
                f"Please carefully update the output based on this feedback."
            )
            
        logger.warning(f"Max iterations ({self.max_iterations}) reached without Critic approval.")
        return last_output
