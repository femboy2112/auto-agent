import argparse
import asyncio
import logging

from agy_orchestrator.core.instance import AgyInstance
from agy_orchestrator.core.optimizer import DynamicEffortAllocator
from agy_orchestrator.execution.verifier import QualityVerifier
from agy_orchestrator.workflows.adversarial import AdversarialReview
from agy_orchestrator.workflows.tree_of_thought import TreeOfThought
from agy_orchestrator.workflows.master import MasterWorkflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

async def run_adversarial(args):
    allocator = DynamicEffortAllocator(initial_effort=args.effort, initial_model=args.model)
    config = allocator.get_current_config()
    
    generator = AgyInstance(prompt="", model=config["model"], effort=config["effort"])
    critic = AgyInstance(prompt="", model=config["model"], effort="high")
    
    verifier = None
    if args.test_cmd:
        verifier = QualityVerifier(test_commands=[args.test_cmd])
        
    workflow = AdversarialReview(generator, critic, verifier, max_iterations=args.max_iterations)
    result = await workflow.execute(args.prompt)
    print("\n--- Final Verified Output ---\n")
    print(result)

async def run_tot(args):
    allocator = DynamicEffortAllocator(initial_effort=args.effort, initial_model=args.model)
    config = allocator.get_current_config()
    
    branches = [
        AgyInstance(prompt=args.prompt, model=config["model"], effort=config["effort"])
        for _ in range(args.branches)
    ]
    evaluator = AgyInstance(prompt="", model=config["model"], effort="high")
    
    workflow = TreeOfThought(branches, evaluator)
    result = await workflow.execute()
    print("\n--- Best Selected Output ---\n")
    print(result)

async def run_master(args):
    allocator = DynamicEffortAllocator(initial_effort=args.effort, initial_model=args.model)
    config = allocator.get_current_config()
    
    verifier = None
    if args.test_cmd:
        verifier = QualityVerifier(test_commands=[args.test_cmd])
        
    workflow = MasterWorkflow(
        model=config["model"],
        effort=config["effort"],
        branches=args.branches,
        max_iterations=args.max_iterations,
        verifier=verifier
    )
    result = await workflow.execute(args.prompt)
    print("\n--- Final Verified Output ---\n")
    print(result)

def main():
    parser = argparse.ArgumentParser(description="Agy Orchestrator - Advanced Multi-Agent Wrapper")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Adversarial Subcommand
    adv_parser = subparsers.add_parser("adversarial", help="Run Adversarial Review workflow")
    adv_parser.add_argument("--prompt", type=str, required=True, help="The goal prompt")
    adv_parser.add_argument("--model", type=str, default="standard", help="Base model to use")
    adv_parser.add_argument("--effort", type=str, default="low", help="Initial effort level")
    adv_parser.add_argument("--test-cmd", type=str, help="Optional programmatic test command")
    adv_parser.add_argument("--max-iterations", type=int, default=5, help="Max loops")
    
    # Tree of Thought Subcommand
    tot_parser = subparsers.add_parser("tot", help="Run Tree-of-Thought workflow")
    tot_parser.add_argument("--prompt", type=str, required=True, help="The goal prompt")
    tot_parser.add_argument("--model", type=str, default="standard", help="Base model to use")
    tot_parser.add_argument("--effort", type=str, default="low", help="Initial effort level")
    tot_parser.add_argument("--branches", type=int, default=3, help="Number of ToT branches")
    
    # Master Subcommand
    master_parser = subparsers.add_parser("master", help="Run Master Orchestrator workflow")
    master_parser.add_argument("--prompt", type=str, required=True, help="The goal prompt")
    master_parser.add_argument("--model", type=str, default="standard", help="Base model to use")
    master_parser.add_argument("--effort", type=str, default="low", help="Initial effort level")
    master_parser.add_argument("--test-cmd", type=str, help="Optional programmatic test command")
    master_parser.add_argument("--branches", type=int, default=3, help="Number of ToT branches per task")
    master_parser.add_argument("--max-iterations", type=int, default=5, help="Max loops for adversarial refinement")
    
    args = parser.parse_args()
    
    if args.command == "adversarial":
        asyncio.run(run_adversarial(args))
    elif args.command == "tot":
        asyncio.run(run_tot(args))
    elif args.command == "master":
        asyncio.run(run_master(args))

if __name__ == "__main__":
    main()
