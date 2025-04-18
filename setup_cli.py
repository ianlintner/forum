#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Setup Script for CLI commands

This script creates a convenient 'senate' command that can be run from anywhere.
"""

import os
import sys
import shutil
import subprocess

def main():
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the shell script that will be installed as 'senate' command
    script_content = f"""#!/bin/bash
# Roman Senate AI Game CLI Runner
python {os.path.join(project_dir, 'run_senate.py')} "$@"
"""
    
    # Write the script to a temporary file
    script_path = os.path.join(project_dir, 'senate_runner.sh')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    # Determine where to install it
    install_dir = os.path.expanduser('~/.local/bin')
    os.makedirs(install_dir, exist_ok=True)
    
    # Install the script
    dest_path = os.path.join(install_dir, 'senate')
    shutil.copy2(script_path, dest_path)
    
    # Clean up
    os.remove(script_path)
    
    print(f"\nSuccessfully installed 'senate' command to {install_dir}")
    print("Make sure this directory is in your PATH to use the command anywhere.")
    print("\nExample usage:")
    print("  senate info")
    print("  senate simulate")
    print("  senate play")

if __name__ == "__main__":
    main()