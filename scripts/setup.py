#!/usr/bin/env python3
"""
Setup and initialization script for bonsai-penjing-design-automation.

This script handles:
- Initial project setup
- Directory creation
- Configuration validation
- Dependency checks
- Environment preparation
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


def print_step(step: int, total: int, message: str) -> None:
    """Print setup step."""
    print(f"[{step}/{total}] {message}")


def check_python_version() -> bool:
    """Check Python version compatibility."""
    print_step(1, 7, "Checking Python version...")

    version = sys.version_info
    if version < (3, 11):
        print(f"ERROR: Python 3.11+ required, found {version.major}.{version.minor}")
        return False

    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories(project_root: Path) -> bool:
    """Create required directories."""
    print_step(2, 7, "Creating directory structure...")

    directories = [
        "config",
        "scripts",
        "references",
        "assets",
        "logs",
        "bonsai_penjing/services",
        "tests",
        "skills",
        "tools",
    ]

    for dir_name in directories:
        dir_path = project_root / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

    return True


def check_dependencies(project_root: Path) -> Tuple[bool, List[str]]:
    """Check if dependencies are installed."""
    print_step(3, 7, "Checking dependencies...")

    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print("  ✗ requirements.txt not found")
        return False, []

    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    missing = []
    for req in requirements:
        package = req.split(">")[0].split("=")[0].split("<")[0].strip()
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package}")
        except ImportError:
            missing.append(req)
            print(f"  ✗ {package} (missing)")

    return len(missing) == 0, missing


def install_dependencies(project_root: Path) -> bool:
    """Install dependencies from requirements.txt."""
    print_step(4, 7, "Installing dependencies...")

    requirements_file = project_root / "requirements.txt"
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
        )
        print("  ✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install: {e}")
        return False


def validate_config(project_root: Path) -> bool:
    """Validate configuration files."""
    print_step(5, 7, "Validating configuration...")

    config_file = project_root / "config" / "defaults.yaml"
    if not config_file.exists():
        print(f"  ✗ Missing: {config_file}")
        return False

    try:
        import yaml

        with open(config_file) as f:
            yaml.safe_load(f)
        print(f"  ✓ {config_file}")
    except Exception as e:
        print(f"  ✗ Invalid YAML: {e}")
        return False

    return True


def initialize_knowledge_base(project_root: Path) -> bool:
    """Initialize the knowledge base."""
    print_step(6, 7, "Initializing knowledge base...")

    brain_file = project_root / "SECOND-KNOWLEDGE-BRAIN.md"
    if brain_file.exists():
        print(f"  ✓ Knowledge base exists: {brain_file}")
        return True

    print(f"  ⚠ Knowledge base not found, creating placeholder...")
    brain_file.write_text(
        "# SECOND-KNOWLEDGE-BRAIN.md\n\n"
        "> Knowledge base for bonsai-penjing-design-automation\n\n"
        "This file is automatically populated by the knowledge crawl pipeline.\n\n"
        "## Sections\n\n"
        "- Core Methods\n"
        "- Key Papers\n"
        "- State of the Art\n"
        "- Data Sources\n"
        "- Frameworks\n"
        "- Self-Update Protocol\n"
        "- Update Log\n"
    )
    return True


def run_tests(project_root: Path) -> bool:
    """Run test suite to verify installation."""
    print_step(7, 7, "Running test suite...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"  ✗ Test execution failed: {e}")
        return False


def main() -> int:
    """Run setup process."""
    print("=" * 60)
    print("bonsai-penjing-design-automation Setup")
    print("=" * 60)
    print()

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Step 1: Check Python version
    if not check_python_version():
        return 1

    # Step 2: Create directories
    if not create_directories(project_root):
        return 1

    # Step 3: Check dependencies
    deps_ok, missing = check_dependencies(project_root)

    # Step 4: Install if needed
    if not deps_ok:
        print(f"\nMissing {len(missing)} dependencies.")
        response = input("Install missing dependencies? [Y/n] ").strip().lower()
        if response != "n":
            if not install_dependencies(project_root):
                return 1

    # Step 5: Validate config
    if not validate_config(project_root):
        print("\nERROR: Configuration validation failed")
        return 1

    # Step 6: Initialize knowledge base
    if not initialize_knowledge_base(project_root):
        return 1

    # Step 7: Run tests
    response = input("\nRun test suite to verify installation? [Y/n] ").strip().lower()
    if response != "n":
        if not run_tests(project_root):
            print("\nWARNING: Some tests failed, but installation is usable")

    print()
    print("=" * 60)
    print("✓ Setup complete!")
    print()
    print("Next steps:")
    print("  1. Review config/defaults.yaml for customization")
    print("  2. Run: bonsai analyze --help")
    print("  3. Run: bonsai crawl --dry-run to test knowledge pipeline")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
