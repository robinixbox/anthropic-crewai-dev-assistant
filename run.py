#!/usr/bin/env python3
"""
Launcher script for the Anthropic CrewAI Dev Assistant

This script provides a simple way to start the application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point"""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Set the PYTHONPATH to include the project directory
    os.environ["PYTHONPATH"] = str(script_dir)
    
    # Check if the virtual environment exists
    venv_dir = script_dir / "venv"
    if not venv_dir.exists():
        print("Virtual environment not found. Creating one...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("Virtual environment created.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            return 1
    
    # Determine the python executable in the virtual environment
    if os.name == "nt":  # Windows
        python_executable = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/MacOS
        python_executable = venv_dir / "bin" / "python"
    
    # Check if requirements are installed
    try:
        subprocess.run(
            [str(python_executable), "-c", "import streamlit, anthropic, crewai"],
            check=False,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        print("Some required packages are not installed. Installing...")
        
        try:
            subprocess.run(
                [str(python_executable), "-m", "pip", "install", "-r", "requirements.txt"],
                check=True
            )
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return 1
    
    # Run the application
    try:
        subprocess.run(
            [str(python_executable), "-m", "streamlit", "run", "src/ui/app.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())