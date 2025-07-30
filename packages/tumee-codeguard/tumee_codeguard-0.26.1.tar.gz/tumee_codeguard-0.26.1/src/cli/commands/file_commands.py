"""
File verification CLI commands for CodeGuard.
Handles file comparison, git integration, and directory scanning.
All commands are async for streaming operations.
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import pathspec

from ...core.decorators.filesystem import with_filesystem_access
from ...core.exit_codes import SECURITY_VIOLATION, get_exit_code_description
from ...core.infrastructure.filtering import create_filter
from ...core.infrastructure.processor import detect_language, process_document
from ...core.interfaces import IFileSystemAccess
from ...core.parsing.tree_sitter_parser import parse_document
from ...vcs.git_integration import GitError, GitIntegration
from ..cli_utils import create_reporter_from_args, create_validator_from_args


async def async_results_generator(results: List[Any]) -> AsyncGenerator[Any, None]:
    """Convert a list of results to an async generator."""
    for result in results:
        yield result


async def cmd_verify(args):
    """Execute the verify command with streaming validation."""
    original_path = Path(args.original)
    modified_path = Path(args.modified)

    if not original_path.is_file():
        if not getattr(args, "quiet", False):
            print(f"Error: Original file does not exist: {original_path}")
        return 1

    if not modified_path.is_file():
        if not getattr(args, "quiet", False):
            print(f"Error: Modified file does not exist: {modified_path}")
        return 1

    # Create validator and reporter
    validator = create_validator_from_args(args)
    reporter = create_reporter_from_args(args)

    # Validate files asynchronously
    result = await validator.validate_files(original_path, modified_path)

    # Generate streaming report
    if not args.output and not getattr(args, "report", None):
        # Stream to stdout
        async for chunk in reporter.generate_stream_report(async_results_generator([result])):
            print(chunk, end="")
    else:
        # Save to file
        if getattr(args, "report", None):
            await reporter.generate_report_to_file(async_results_generator([result]), args.report)
        elif args.output:
            await reporter.generate_report_to_file(async_results_generator([result]), args.output)

    # Return appropriate exit code
    if result.status == "SUCCESS":
        return 0
    else:
        exit_code = 1
        # Check for security violations
        if hasattr(result, "violations") and result.violations:
            for violation in result.violations:
                if violation.violation_type == "security_violation":
                    exit_code = SECURITY_VIOLATION
                    break
        return exit_code


async def cmd_verify_disk(args):
    """Execute verify-disk command with streaming validation."""
    modified_path = Path(args.modified)

    if not modified_path.is_file():
        if not getattr(args, "quiet", False):
            print(f"Error: Modified file does not exist: {modified_path}")
        return 1

    # Create validator and reporter
    validator = create_validator_from_args(args)
    reporter = create_reporter_from_args(args)

    # Validate file against itself (disk comparison)
    result = await validator.validate_file(modified_path)

    # Generate streaming report
    if not args.output and not getattr(args, "report", None):
        # Stream to stdout
        async for chunk in reporter.generate_stream_report(async_results_generator([result])):
            print(chunk, end="")
    else:
        # Save to file
        if getattr(args, "report", None):
            await reporter.generate_report_to_file(async_results_generator([result]), args.report)
        elif args.output:
            await reporter.generate_report_to_file(async_results_generator([result]), args.output)

    return 0 if result.status == "SUCCESS" else 1


async def cmd_verify_git(args):
    """Execute verify-git command with streaming validation."""
    file_path = Path(args.file)
    revision = args.revision

    if not file_path.exists():
        if not getattr(args, "quiet", False):
            print(f"Error: File does not exist: {file_path}")
        return 1

    try:
        # Use git integration to get file contents from revision
        git_integration = GitIntegration(args.repo_path)

        try:
            original_content = await git_integration.get_file_content(file_path, revision)
        except GitError as e:
            # If file doesn't exist in the specified revision, it's a new file
            if "does not exist" in str(e):
                original_content = ""
                if not getattr(args, "quiet", False):
                    print(
                        f"Note: File is new (doesn't exist in {revision}), comparing against empty content"
                    )
            else:
                raise

        # Read current file
        with open(file_path, "r", encoding="utf-8") as f:
            modified_content = f.read()

        # Create validator and reporter
        validator = create_validator_from_args(args)
        reporter = create_reporter_from_args(args)

        # Validate files with git content
        result = await validator.validate_file(
            file_path, original_content=original_content, modified_content=modified_content
        )

        # Generate streaming report
        if not args.output and not getattr(args, "report", None):
            # Stream to stdout
            async for chunk in reporter.generate_stream_report(async_results_generator([result])):
                print(chunk, end="")
        else:
            # Save to file
            if getattr(args, "report", None):
                await reporter.generate_report_to_file(
                    async_results_generator([result]), args.report
                )
            elif args.output:
                await reporter.generate_report_to_file(
                    async_results_generator([result]), args.output
                )

        return 0 if result.status == "SUCCESS" else 1

    except GitError as e:
        if not getattr(args, "quiet", False):
            print(f"Git error: {e}")
        return 1
    except Exception as e:
        if not getattr(args, "quiet", False):
            print(f"Error: {e}")
        return 1


@with_filesystem_access()
async def cmd_tags(
    directory: Path,
    filesystem_access: IFileSystemAccess,
    include: Optional[str] = None,
    exclude: Optional[List[str]] = None,
    recursive: bool = True,
    quiet: bool = False,
    verbose: bool = False,
    count_only: bool = False,
    format: str = "text",
    output: Optional[Path] = None,
):
    """Execute tags command to report guard tag locations and counts."""

    if not directory.exists():
        if not quiet:
            print(f"Error: Path does not exist: {directory}")
        return 1

    # Create filtering (filesystem_access injected by decorator)
    fs = filesystem_access
    filter_engine = create_filter(
        respect_gitignore=True,
        use_ai_attributes=True,
        default_include=False,
    )

    # Default file patterns for code files
    file_patterns = (
        [include] if include else ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.cs"]
    )
    exclude_patterns = exclude or []

    total_files = 0
    total_tags = 0
    files_with_tags = 0
    tag_details = []

    if directory.is_file():
        # Single file
        files_to_check = [directory]
    else:
        # Directory - find matching files using centralized filesystem access
        files_to_check = []
        for pattern in file_patterns:
            try:
                if recursive:
                    # Use centralized filesystem access with gitignore filtering
                    matched_files = await fs.safe_glob(directory, pattern, recursive=True)
                    # Apply additional filtering
                    filtered_matches = await filter_engine.filter_file_list(
                        matched_files, directory
                    )
                    files_to_check.extend([file_path for file_path, _reason in filtered_matches])
                else:
                    # Non-recursive: use safe_glob without filtering since it's shallow
                    matched_files = await fs.safe_glob(directory, pattern, recursive=False)
                    files_to_check.extend(matched_files)
            except Exception as e:
                if not quiet:
                    print(f"Warning: Error scanning pattern {pattern}: {e}")
                continue

        # Filter out excluded files
        if exclude_patterns:
            exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude_patterns)

            filtered_files = []
            for file_path in files_to_check:
                try:
                    relative_path = file_path.relative_to(directory)
                    relative_str = str(relative_path).replace("\\", "/")
                    if not exclude_spec.match_file(relative_str):
                        filtered_files.append(file_path)
                except ValueError:
                    filtered_files.append(file_path)

            files_to_check = filtered_files

    # Process each file
    for file_path in files_to_check:
        if not file_path.is_file():
            continue

        total_files += 1

        try:
            # Read file content
            content = await fs.safe_read_file(file_path)

            # Detect language and process for guard tags
            language_id = detect_language(str(file_path))
            parse_result = parse_document(content, language_id)
            guard_tags, _ = await process_document(content, language_id, parse_result)

            if guard_tags:
                files_with_tags += 1
                file_tag_count = len(guard_tags)
                total_tags += file_tag_count

                if verbose:
                    for tag in guard_tags:
                        tag_details.append(
                            {
                                "file": str(file_path),
                                "line": getattr(tag, "lineNumber", 0),
                                "scope": getattr(tag, "scope", "unknown"),
                                "identifier": getattr(tag, "identifier", ""),
                                "permissions": getattr(tag, "permissions", {}),
                            }
                        )
                elif not count_only:
                    tag_details.append({"file": str(file_path), "tag_count": file_tag_count})

        except Exception as e:
            if verbose:
                print(f"Warning: Could not process {file_path}: {e}")
            continue

    # Output results
    output_text = ""  # Initialize to ensure it's always defined

    if format == "json":
        result: Dict[str, Any] = {
            "summary": {
                "total_files_checked": total_files,
                "files_with_tags": files_with_tags,
                "total_tags": total_tags,
            }
        }

        if not count_only:
            if verbose:
                result["tag_details"] = tag_details
            else:
                result["files"] = tag_details

        output_text = json.dumps(result, indent=2)

    else:  # text format
        output_lines = []
        output_lines.append(f"Guard Tag Summary:")
        output_lines.append(f"  Files checked: {total_files}")
        output_lines.append(f"  Files with tags: {files_with_tags}")
        output_lines.append(f"  Total tags found: {total_tags}")

        if not count_only and tag_details:
            output_lines.append("")
            if verbose:
                output_lines.append("Tag Details:")
                for detail in tag_details:
                    permissions_str = ", ".join(
                        [f"{k}:{v}" for k, v in detail["permissions"].items()]
                    )
                    output_lines.append(
                        f"  {detail['file']}:{detail['line']} [{detail['scope']}] {detail['identifier']} ({permissions_str})"
                    )
            else:
                output_lines.append("Files with tags:")
                for detail in tag_details:
                    output_lines.append(f"  {detail['file']}: {detail['tag_count']} tags")

        output_text = "\n".join(output_lines)

    # Write output
    if output:
        with open(output, "w") as f:
            f.write(output_text)
        print(f"Report saved to {output}")
    else:
        print(output_text)

    return 0
