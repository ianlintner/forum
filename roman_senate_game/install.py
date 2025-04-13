#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - Installation Script

This script installs the required dependencies for the Roman Senate AI Game.
"""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install all required dependencies."""
    print("\n=== Installing Roman Senate AI Game ===")
    
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"],
                     check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e.stderr}")
        return False

def main():
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        script_dir = Path(__file__).parent
        if Path(script_dir / "requirements.txt").exists():
            print("Changing to correct directory...")
            os.chdir(script_dir)
        else:
            print("Error: Cannot find requirements.txt")
            return 1

    # Install dependencies
    if install_dependencies():
        print("\n=== Installation Complete ===")
        print("\nTo run the game:")
        print("python main.py")
        return 0
    else:
        print("\n=== Installation Failed ===")
        print("Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())