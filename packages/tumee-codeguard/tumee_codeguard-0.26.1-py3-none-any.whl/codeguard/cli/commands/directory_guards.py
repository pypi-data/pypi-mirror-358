"""
Directory guard CLI commands for CodeGuard.
Handles directory-level guard annotations via .ai-attributes files.
"""

import argparse
import json
import os
from pathlib import Path

import yaml

from ...core.validation.directory_guard import DirectoryGuard
from ...core.validation.guard_tag_parser import parse_guard_tag
from ..cli_utils import create_validator_from_args


def cmd_create_aiattributes(args: argparse.Namespace) -> int:
    """
    Execute the 'aiattributes create' command to create or update an .ai-attributes file.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.is_dir():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    # Path to the .ai-attributes file
    attrs_file = directory / DirectoryGuard.AI_ATTRIBUTES_FILE

    # Parse existing file if it exists
    rules = []
    if attrs_file.exists():
        try:
            with open(attrs_file, "r") as f:
                existing_content = f.read()

            # If there's existing content, keep it as a base
            rules.append(existing_content.rstrip())
        except Exception as e:
            print(f"Error reading existing .ai-attributes file: {str(e)}")
            return 1
    else:
        # Add a header if creating a new file
        rules.append("# CodeGuard Directory-Level Guard Annotations")
        rules.append("#")
        rules.append("# Format: <pattern> @GUARD:<WHO>-<PERMISSION> [description]")
        rules.append("#")
        rules.append("# Examples:")
        rules.append("# * @GUARD:AI-RO All files in this directory are AI read-only")
        rules.append("# *.py @GUARD:ALL-FX All Python files are fixed for everyone")
        rules.append("# data/*.json @GUARD:HU-ED JSON files in data dir are human editable")
        rules.append("")

    # Add new rules
    if args.rule:
        for rule_str in args.rule:
            try:
                # Use existing guard tag parser to validate the rule line
                parsed_result = parse_guard_tag(rule_str)

                if not parsed_result:
                    raise ValueError(f"Invalid rule format: {rule_str}")

                # Extract pattern from the rule (everything before the guard tag)
                guard_tag_start = rule_str.find("@guard:")
                if guard_tag_start == -1:
                    raise ValueError(f"No guard tag found in rule: {rule_str}")

                pattern = rule_str[:guard_tag_start].strip()
                if not pattern:
                    raise ValueError(f"No pattern specified in rule: {rule_str}")

                # Add the rule exactly as provided (already validated by parser)
                desc = ""
                if args.description:
                    # Find a matching description for this pattern
                    for desc_str in args.description:
                        if desc_str.startswith(f"{pattern}:"):
                            desc = desc_str.split(":", 1)[1].strip()
                            break

                rule_line = rule_str
                if desc:
                    rule_line += f" {desc}"

                rules.append(rule_line)

            except ValueError as e:
                print(f"Error parsing rule '{rule_str}': {str(e)}")
                return 1

    # Write the file
    try:
        with open(attrs_file, "w") as f:
            f.write("\n".join(rules) + "\n")

        print(f"Created/updated .ai-attributes file at: {attrs_file}")
        return 0
    except Exception as e:
        print(f"Error writing .ai-attributes file: {str(e)}")
        return 1


def cmd_list_aiattributes(args: argparse.Namespace) -> int:
    """
    Execute the 'aiattributes list' command to list rules from .ai-attributes files.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.is_dir():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    # Find .ai-attributes files
    ai_attributes_files = []
    if args.recursive:
        # Find all .ai-attributes files recursively
        for root, _, files in os.walk(directory):
            root_path = Path(root)
            if DirectoryGuard.AI_ATTRIBUTES_FILE in files:
                ai_attributes_files.append(root_path / DirectoryGuard.AI_ATTRIBUTES_FILE)
    else:
        # Just check the specified directory
        attrs_file = directory / DirectoryGuard.AI_ATTRIBUTES_FILE
        if attrs_file.exists():
            ai_attributes_files.append(attrs_file)

    if not ai_attributes_files:
        print(f"No .ai-attributes files found in {directory}")
        return 0

    # Parse each file and collect rules
    results = []

    for attrs_file in ai_attributes_files:
        try:
            # Create validator and DirectoryGuard with filesystem access
            validator = create_validator_from_args(args)
            dg = DirectoryGuard(validator.fs)
            dg._load_rules_from_file(attrs_file)
            rules = dg.list_rules()

            file_result = {"file": str(attrs_file), "rules": []}

            # Convert rules to a serializable format
            for rule in rules:
                rule_data = {
                    "pattern": rule.pattern,
                    "who": rule.target,
                    "permission": rule.permission,
                    "description": rule.description,
                    "source_line": rule.source_line,
                }
                file_result["rules"].append(rule_data)

            results.append(file_result)

        except Exception as e:
            print(f"Error parsing {attrs_file}: {str(e)}")
            continue

    # Format and output results
    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "yaml":
        try:
            print(yaml.dump(results, sort_keys=False))
        except Exception:
            # Fallback to JSON if YAML is not available
            print(json.dumps(results, indent=2))
    else:
        # Text format
        for file_result in results:
            print(f"File: {file_result['file']}")
            print("-" * 60)

            if not file_result["rules"]:
                print("No rules found.")
                print()
                continue

            for rule in file_result["rules"]:
                print(f"Pattern: {rule['pattern']}")
                print(f"Guard: {rule['who']}-{rule['permission']}")
                if rule["description"]:
                    print(f"Description: {rule['description']}")
                print(f"Line: {rule['source_line']}")
                print()

    return 0


def cmd_validate_aiattributes(args: argparse.Namespace) -> int:
    """
    Execute the 'aiattributes validate' command to validate .ai-attributes files.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.is_dir():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    # Find .ai-attributes files
    ai_attributes_files = []
    if args.recursive:
        # Find all .ai-attributes files recursively
        for root, _, files in os.walk(directory):
            root_path = Path(root)
            if DirectoryGuard.AI_ATTRIBUTES_FILE in files:
                ai_attributes_files.append(root_path / DirectoryGuard.AI_ATTRIBUTES_FILE)
    else:
        # Just check the specified directory
        attrs_file = directory / DirectoryGuard.AI_ATTRIBUTES_FILE
        if attrs_file.exists():
            ai_attributes_files.append(attrs_file)

    if not ai_attributes_files:
        print(f"No .ai-attributes files found in {directory}")
        return 0

    # Validate each file
    has_errors = False

    for attrs_file in ai_attributes_files:
        print(f"Validating {attrs_file}...")

        try:
            # Read the file
            with open(attrs_file, "r") as f:
                lines = f.readlines()

            # Track errors for this file
            file_errors = []
            modified_lines = lines.copy()

            # Process each line
            for i, line in enumerate(lines):
                line = line.strip()
                line_num = i + 1

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Try to parse the line
                try:
                    # Check if the line has required components
                    parts = line.split()
                    if len(parts) < 2:
                        file_errors.append(
                            (
                                line_num,
                                f"Line {line_num}: Invalid format. Expected '<pattern> @GUARD:<WHO>-<PERMISSION>'",
                            )
                        )
                        continue

                    pattern = parts[0]

                    # Find guard directive
                    guard_parts = None
                    for part in parts[1:]:
                        if part.startswith("@GUARD:"):
                            guard_parts = part.split("@GUARD:")[1].split("-")
                            break

                    if not guard_parts:
                        file_errors.append((line_num, f"Line {line_num}: Missing @GUARD directive"))
                        continue

                    if len(guard_parts) != 2:
                        file_errors.append(
                            (
                                line_num,
                                f"Line {line_num}: Invalid @GUARD format. Expected '<WHO>-<PERMISSION>'",
                            )
                        )
                        continue

                    # Validate WHO part
                    who = guard_parts[0]
                    if who not in ("AI", "HU", "ALL"):
                        file_errors.append(
                            (
                                line_num,
                                f"Line {line_num}: Invalid WHO value '{who}'. Must be AI, HU, or ALL",
                            )
                        )

                        if args.fix:
                            # Try to fix WHO part
                            if who.upper() in ("AI", "HU", "ALL"):
                                fixed_who = who.upper()
                                modified_lines[i] = line.replace(
                                    f"@GUARD:{who}", f"@GUARD:{fixed_who}"
                                )
                                file_errors[-1] = (
                                    line_num,
                                    f"Line {line_num}: Fixed WHO value from '{who}' to '{fixed_who}'",
                                )

                        continue

                    # Validate PERMISSION part
                    permission = guard_parts[1]
                    if permission not in ("RO", "ED", "FX"):
                        file_errors.append(
                            (
                                line_num,
                                f"Line {line_num}: Invalid PERMISSION value '{permission}'. Must be RO, ED, or FX",
                            )
                        )

                        if args.fix:
                            # Try to fix PERMISSION part
                            if permission.upper() in ("RO", "ED", "FX"):
                                fixed_permission = permission.upper()
                                modified_lines[i] = line.replace(
                                    f"-{permission}", f"-{fixed_permission}"
                                )
                                file_errors[-1] = (
                                    line_num,
                                    f"Line {line_num}: Fixed PERMISSION value from '{permission}' to '{fixed_permission}'",
                                )

                        continue

                except Exception as e:
                    file_errors.append((line_num, f"Line {line_num}: Parsing error: {str(e)}"))

            # Report and fix errors if needed
            if file_errors:
                has_errors = True
                print(f"Found {len(file_errors)} errors in {attrs_file}:")
                for line_num, error in file_errors:
                    print(f"  {error}")

                if args.fix and any(modified_lines[i] != lines[i] for i in range(len(lines))):
                    # Write the fixed file
                    with open(attrs_file, "w") as f:
                        f.writelines(modified_lines)
                    print(f"Fixed {attrs_file}")
            else:
                print(f"No errors found in {attrs_file}")

            print()

        except Exception as e:
            print(f"Error validating {attrs_file}: {str(e)}")
            has_errors = True

    return 1 if has_errors else 0


def cmd_list_guarded_directories(args: argparse.Namespace) -> int:
    """
    Execute the 'list-guarded-directories' command to list directories with guard annotations.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.is_dir():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    # Find all .ai-attributes files recursively
    guarded_dirs = []

    for root, _, files in os.walk(directory):
        root_path = Path(root)
        if DirectoryGuard.AI_ATTRIBUTES_FILE in files:
            try:
                # Create validator and DirectoryGuard with filesystem access
                validator = create_validator_from_args(args)
                dg = DirectoryGuard(validator.fs)
                dg._load_rules_from_file(root_path / DirectoryGuard.AI_ATTRIBUTES_FILE)
                rules = dg.list_rules()

                dir_info = {
                    "path": str(root_path),
                    "rules_count": len(rules),
                    "patterns": [rule.pattern for rule in rules],
                }

                guarded_dirs.append(dir_info)
            except Exception as e:
                print(f"Error parsing {root_path / DirectoryGuard.AI_ATTRIBUTES_FILE}: {str(e)}")
                continue

    # Format and output results
    if args.format == "json":
        print(json.dumps(guarded_dirs, indent=2))
    elif args.format == "yaml":
        try:
            print(yaml.dump(guarded_dirs, sort_keys=False))
        except Exception:
            # Fallback to JSON if YAML is not available
            print(json.dumps(guarded_dirs, indent=2))
    else:
        # Text format
        print(f"Found {len(guarded_dirs)} guarded directories:")
        print()

        for dir_info in guarded_dirs:
            print(f"Directory: {dir_info['path']}")
            print(f"Rules: {dir_info['rules_count']}")
            print("Patterns:")
            for pattern in dir_info["patterns"]:
                print(f"  - {pattern}")
            print()

    return 0
