#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
CLI Runner (Root Directory Entry Point)

This script provides a convenient entry point to run the Roman Senate simulation
from the project root directory without having to navigate to the scripts folder.
Simply run: python run_senate.py [commands...]
"""

import os
import sys
import subprocess

def main():
    """
    Forward all arguments to the scripts/run_senate.py script.
    This ensures the user can run the simulation from the project root directory.
    """
    # Get the absolute path to the scripts/run_senate.py file
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'scripts',
        'run_senate.py'
    )
    
    # Ensure the script exists
    if not os.path.exists(script_path):
        print(f"Error: Could not find {script_path}")
        print("Make sure you are running this from the project root directory.")
        sys.exit(1)
    
    # Forward all command line arguments to the script
    args = [sys.executable, script_path] + sys.argv[1:]
    
    # Execute the script with all arguments
    print(f"Starting Roman Senate Simulation...")
    try:
        result = subprocess.run(args)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(130)  # 130 is the standard exit code for SIGINT
    except Exception as e:
        print(f"Error running simulation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()