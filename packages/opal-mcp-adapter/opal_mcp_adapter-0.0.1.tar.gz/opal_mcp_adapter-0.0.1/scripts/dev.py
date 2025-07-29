#!/usr/bin/env python3
"""Development helper script for MCP-Opal adapter"""

import sys
import subprocess
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def run_tests():
    """Run the test suite"""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

def run_linter():
    """Run code linting"""
    print("Running linter...")
    subprocess.run([sys.executable, "-m", "flake8", "src/", "tests/"])

def run_app():
    """Run the application"""
    print("Starting MCP-Opal adapter...")
    subprocess.run([sys.executable, "main.py"])

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py [test|lint|run]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        run_tests()
    elif command == "lint":
        run_linter()
    elif command == "run":
        run_app()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: test, lint, run")
        sys.exit(1)

if __name__ == "__main__":
    main() 