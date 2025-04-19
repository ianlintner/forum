#!/usr/bin/env python3
"""
Run Script for Agentic Game Framework Example Simulation.

This script provides a simple way to run the example simulation
from the command line.
"""

import argparse
import sys

from src.agentic_game_framework.examples.simple_simulation import run_simulation


def main():
    """Parse command line arguments and run the simulation."""
    parser = argparse.ArgumentParser(
        description="Run an example simulation using the Agentic Game Framework."
    )
    
    parser.add_argument(
        "--agents", 
        type=int, 
        default=5,
        help="Number of agents in the simulation (default: 5)"
    )
    
    parser.add_argument(
        "--steps", 
        type=int, 
        default=20,
        help="Number of simulation steps to run (default: 20)"
    )
    
    args = parser.parse_args()
    
    print("Agentic Game Framework - Example Simulation")
    print("===========================================")
    print(f"Running with {args.agents} agents for {args.steps} steps")
    print()
    
    try:
        run_simulation(num_agents=args.agents, max_steps=args.steps)
        return 0
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError running simulation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())