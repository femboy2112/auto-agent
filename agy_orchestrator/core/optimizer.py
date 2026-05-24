from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DynamicEffortAllocator:
    """
    Manages and scales the execution effort and model configuration 
    based on success or failure of previous steps, minimizing token usage.
    """
    
    EFFORT_LEVELS = ["low", "medium", "high", "max"]
    
    def __init__(self, initial_effort: str = "low", initial_model: str = "standard"):
        self.initial_effort = initial_effort
        if initial_effort in self.EFFORT_LEVELS:
            self.current_effort_index = self.EFFORT_LEVELS.index(initial_effort)
        else:
            self.current_effort_index = 0
            
        self.base_model = initial_model
        
    def get_current_config(self) -> Dict[str, Any]:
        """Returns the active configuration dictionary."""
        return {
            "effort": self.EFFORT_LEVELS[self.current_effort_index],
            "model": self.base_model
        }
        
    def escalate(self) -> bool:
        """
        Escalates to a higher effort tier.
        Returns True if escalated, False if already at max effort.
        """
        if self.current_effort_index < len(self.EFFORT_LEVELS) - 1:
            self.current_effort_index += 1
            logger.info(f"Escalated effort to: {self.EFFORT_LEVELS[self.current_effort_index]}")
            return True
        logger.warning("Already at max effort, cannot escalate further.")
        return False
        
    def reset(self):
        """Resets to the initial configured effort."""
        self.current_effort_index = self.EFFORT_LEVELS.index(self.initial_effort) if self.initial_effort in self.EFFORT_LEVELS else 0
        logger.info("Effort allocator reset.")
