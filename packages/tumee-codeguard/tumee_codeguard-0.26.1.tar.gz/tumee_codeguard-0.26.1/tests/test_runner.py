"""
Test runner that discovers and runs tests from various modules.
This orchestrates testing across the entire codebase.
Uses centralized filtering to validate architectural integrity.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest

# Add project root to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.filesystem_access import FileSystemAccess
from src.core.fs_walker import fs_walk
from src.core.roots_security import RootsSecurityManager


async def _discover_test_directories_filtered(project_root: Path) -> List[Path]:
    """Discover test directories using centralized filtering. MUST work or fail."""
    security_manager = RootsSecurityManager([str(project_root)])
    filesystem_access = FileSystemAccess(security_manager)

    test_dirs = []
    async for item in fs_walk(
        filesystem_access=filesystem_access,
        directory=project_root,
        respect_gitignore=True,
        default_include=False,
        traversal_mode="breadth_first",
        max_depth=10,
        yield_type="directories",  # Only yield directories
    ):
        path = Path(item["path"])
        if path.name == "tests":  # item is already a directory
            test_dirs.append(path)

    return test_dirs


def discover_test_modules():
    """Discover all test modules across the codebase."""
    project_root = Path(__file__).parent.parent
    test_modules = []

    # CLI tests
    cli_tests = project_root / "src" / "cli" / "tests"
    if cli_tests.exists():
        test_modules.append(str(cli_tests))

    # Core tests
    core_tests = project_root / "src" / "core" / "tests"
    if core_tests.exists():
        test_modules.append(str(core_tests))

    # IDE tests
    ide_tests = project_root / "src" / "ide" / "tests"
    if ide_tests.exists():
        test_modules.append(str(ide_tests))

    # Utils tests
    utils_tests = project_root / "src" / "utils" / "tests"
    if utils_tests.exists():
        test_modules.append(str(utils_tests))

    # VCS tests
    vcs_tests = project_root / "src" / "vcs" / "tests"
    if vcs_tests.exists():
        test_modules.append(str(vcs_tests))

    # IDE Server tests
    ide_server_tests = project_root / "tests" / "ide_server"
    if ide_server_tests.exists():
        test_modules.append(str(ide_server_tests))

    # Legacy root-level tests that haven't been moved yet
    root_tests = project_root / "tests"
    for test_file in root_tests.glob("test_*.py"):
        test_modules.append(str(test_file))

    return test_modules


def run_all_tests(coverage=True, verbose=False):
    """Run all discovered tests with optional coverage."""
    test_modules = discover_test_modules()

    if not test_modules:
        print("No test modules found!")
        return 1

    print(f"Discovered {len(test_modules)} test modules:")
    for module in test_modules:
        print(f"  - {module}")
    print()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html:htmlcov"])

    if verbose:
        cmd.append("-v")

    # Add all test modules
    cmd.extend(test_modules)

    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)

    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def run_cli_tests_only(coverage=True):
    """Run only CLI tests for focused testing."""
    project_root = Path(__file__).parent.parent
    cli_tests = project_root / "src" / "cli" / "tests"

    if not cli_tests.exists():
        print("CLI tests directory not found!")
        return 1

    cmd = ["python", "-m", "pytest", str(cli_tests)]

    if coverage:
        cmd.extend(["--cov=src.cli", "--cov-report=term-missing"])

    cmd.append("-v")

    print(f"Running CLI tests: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


async def run_e2e_tests_only():
    """Run only end-to-end tests using centralized filtering."""
    project_root = Path(__file__).parent.parent

    # Find all E2E test files using centralized filtering - no fallbacks!
    test_dirs = await _discover_test_directories_filtered(project_root)

    e2e_tests = []
    for test_dir in test_dirs:
        e2e_patterns = list(test_dir.glob("*e2e*.py"))
        e2e_tests.extend(e2e_patterns)

    if not e2e_tests:
        print("No E2E tests found!")
        return 1

    cmd = ["python", "-m", "pytest"] + [str(t) for t in e2e_tests]
    cmd.extend(["--cov=src.cli.commands", "--cov-report=term-missing", "-v"])

    print(f"Running E2E tests: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CodeGuard Test Runner")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--cli-only", action="store_true", help="Run only CLI tests")
    parser.add_argument("--e2e-only", action="store_true", help="Run only E2E tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.cli_only:
        exit_code = run_cli_tests_only(coverage=not args.no_coverage)
    elif args.e2e_only:
        exit_code = asyncio.run(run_e2e_tests_only())
    else:
        exit_code = run_all_tests(coverage=not args.no_coverage, verbose=args.verbose)

    sys.exit(exit_code)
