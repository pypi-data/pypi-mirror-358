"""
Static Analysis Component

Integrates with existing CodeGuard tree_sitter_parser and document_analyzer
to provide detailed static analysis of code files and modules.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiofiles
from pathspec import PathSpec

from ...core.infrastructure.filtering import create_filter
from ...core.interfaces import IFileSystemAccess, IStaticAnalyzer
from ...core.language.config import (
    get_code_extensions,
    get_language_for_file_path,
    is_other_context_file,
)
from ...core.parsing.unified_parser import get_unified_parser
from ...core.processing.parallel_processor import process_items_parallel
from ..models import ModuleContext
from ..modules import calculate_primary_language

logger = logging.getLogger(__name__)


def _truncate_path(path: str, max_length: int = 100) -> str:
    """
    Truncate a file path to max_length characters using ellipsis in the middle.

    Args:
        path: File path to truncate
        max_length: Maximum length of the result

    Returns:
        Truncated path with ... in the middle if needed
    """
    if len(path) <= max_length:
        return path

    # Reserve 3 chars for "..."
    available_chars = max_length - 3

    # Split available chars between start and end
    start_chars = available_chars // 2
    end_chars = available_chars - start_chars

    return f"{path[:start_chars]}...{path[-end_chars:]}"


class StaticAnalyzer(IStaticAnalyzer):
    """
    Static analysis component that provides detailed code analysis.

    Integrates with existing CodeGuard parsers to extract:
    - Function definitions and signatures
    - Class hierarchies and interfaces
    - Import/export relationships
    - Code complexity metrics
    - Documentation and comments
    """

    def __init__(self, filesystem_access: IFileSystemAccess):
        """
        Initialize static analyzer.

        Args:
            filesystem_access: IFileSystemAccess instance for file operations and security
        """
        self.filesystem_access = filesystem_access
        self.security_manager = filesystem_access.security_manager

        # Initialize filtering for gitignore support
        self.filter_engine = create_filter(
            respect_gitignore=True,
            use_ai_attributes=True,
            default_include=True,  # Include files by default, exclude via gitignore
        )

    async def analyze_module(
        self,
        module_path: str,
        worker_function: Optional[Callable],
        progress_callback: Optional[Callable] = None,
        module_name: Optional[str] = None,
        allow_spawning: bool = True,
    ) -> ModuleContext:
        """
        Perform static analysis on a module.

        Args:
            module_path: Path to the module directory
            progress_callback: Optional callback for progress reporting
            module_name: Optional module name for progress display

        Returns:
            ModuleContext with complete analysis results (always full context)
        """
        try:
            # Validate path
            validated_path = self.security_manager.safe_resolve(module_path)

            logger.info(f"Analyzing module: {validated_path}")

            # Initialize module context
            module_context = ModuleContext(
                path=str(validated_path.relative_to(self.security_manager.get_allowed_roots()[0]))
            )

            # Analyze all files in the module
            file_analyses = {}
            total_complexity = 0.0

            # Get all files first so we know the total
            analyzable_files = await self._get_analyzable_files(validated_path)
            total_files = len(analyzable_files)

            if progress_callback:
                await progress_callback(
                    message=f"Analyzing {total_files} files...",
                    component_event="update",
                    component_id="static_analysis",
                    current=0,
                    total=total_files,
                )

            # Use shared parallel processor for file analysis
            file_analyses = await self._process_files_with_shared_processor(
                analyzable_files,
                validated_path,
                worker_function,
                progress_callback,
                module_name,
                allow_spawning=allow_spawning,
            )

            # Calculate total complexity
            total_complexity = sum(
                analysis.get("complexity_score", 0.0)
                for analysis in file_analyses.values()
                if isinstance(analysis, dict)
            )

            # Final progress report
            if progress_callback:
                await progress_callback(
                    message=f"Completed {len(file_analyses)}/{total_files} files",
                    component_event="update",
                    component_id="static_analysis",
                    current=len(file_analyses),
                    total=total_files,
                )

            # Update module context
            module_context.file_analyses = file_analyses
            module_context.complexity_score = total_complexity / max(len(file_analyses), 1)
            module_context.primary_language = calculate_primary_language(file_analyses)
            module_context.module_summary = self._generate_module_summary(
                validated_path, file_analyses
            )

            # Always extract complete API information
            module_context.api_catalog = self._extract_api_catalog(file_analyses)

            logger.debug(f"Module analysis completed: {len(file_analyses)} files analyzed")
            return module_context

        except Exception as e:
            logger.error(f"Module analysis failed for {module_path}: {e}")
            # Return minimal context on failure
            return ModuleContext(path=module_path, module_summary=f"Analysis failed: {e}")

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with complete file analysis results (always full context)
        """
        try:
            validated_path = self.security_manager.safe_resolve(file_path)
            # For single file analysis, check if it would be included as context
            should_include, reason = self.filter_engine.should_include_file(
                validated_path, validated_path.parent
            )
            inclusion_reason = reason if should_include else "default"
            return await self._analyze_file(validated_path, inclusion_reason)

        except Exception as e:
            logger.error(f"File analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    async def _get_analyzable_files(self, directory: Path) -> List[Tuple[Path, str]]:
        """Get list of files that can be analyzed with their inclusion reasons."""
        analyzable_files = []

        # Get file extensions from centralized config
        analyzable_extensions = get_code_extensions()

        try:
            # Get all files first (within the module directory) using safe_glob
            all_files = await self.filesystem_access.safe_glob(directory, "*", recursive=True)
            all_files = [p for p in all_files if p.is_file()]

            # Also include any files referenced by .ai-attributes files in this directory
            project_root = self.security_manager.get_allowed_roots()[0]
            ai_attributes_files = [p for p in directory.glob(".ai-attributes") if p.is_file()]

            # Time-based yielding for .ai-attributes processing
            last_yield_time = time.time()

            for ai_attributes_file in ai_attributes_files:
                try:
                    # Parse .ai-attributes file to find context patterns with async file reading
                    async with aiofiles.open(
                        ai_attributes_file, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        async for line in f:
                            # Time-based yielding every 50ms
                            current_time = time.time()
                            if (current_time - last_yield_time) >= 0.05:
                                await asyncio.sleep(0)
                                last_yield_time = current_time

                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue

                            # Parse .ai-attributes format: "pattern @guard:target:permission [description]"
                            parts = line.split("@guard:", 1)
                            if len(parts) != 2:
                                continue

                            pattern = parts[0].strip()
                            rule = parts[1].strip()

                            if not pattern or pattern.startswith("!"):
                                continue

                            # Check if this is a context rule
                            if "context" in rule.lower():
                                # Resolve pattern to actual files
                                pattern_spec = PathSpec.from_lines("gitwildmatch", [pattern])

                                # Scan project root for files matching this pattern using safe_glob
                                project_files = await self.filesystem_access.safe_glob(
                                    Path(project_root), "*", recursive=True
                                )

                                # Time-based yielding during project file iteration
                                project_file_last_yield = time.time()
                                for project_file in project_files:
                                    # Time-based yielding every 50ms during pattern matching
                                    current_time = time.time()
                                    if (current_time - project_file_last_yield) >= 0.05:
                                        await asyncio.sleep(0)
                                        project_file_last_yield = current_time

                                    if project_file.is_file():
                                        relative_path = project_file.relative_to(project_root)
                                        if pattern_spec.match_file(str(relative_path)):
                                            all_files.append(project_file)

                except Exception as e:
                    logger.debug(f"Error parsing {ai_attributes_file}: {e}")

            # Filter using hierarchical filter with gitignore support
            filtered_files = await self.filter_engine.filter_file_list(
                all_files, Path(project_root)
            )

            for file_path, reason in filtered_files:
                # Include files that are either:
                # 1. Standard code files, OR
                # 2. Files included as context via .ai-attributes, OR
                # 3. Files detected as context by language config (naming patterns)
                is_code_file = file_path.suffix.lower() in analyzable_extensions
                is_context_file = reason.startswith(".ai-attributes-context:")
                is_language_config_context_file = is_other_context_file(file_path)

                if (
                    is_code_file or is_context_file or is_language_config_context_file
                ) and self.security_manager.is_path_allowed(file_path):

                    # Skip files that are too large
                    try:
                        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                            logger.debug(f"Skipping large file: {file_path}")
                            continue
                    except OSError:
                        continue

                    analyzable_files.append((file_path, reason))

        except Exception as e:
            logger.warning(f"Error scanning directory {directory}: {e}")

        return analyzable_files

    async def _analyze_files_sequential_dict(
        self,
        analyzable_files: List[Tuple[Path, str]],
        validated_path: Path,
        progress_callback: Optional[Callable] = None,
        module_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze files sequentially and return dict (for parallel processor compatibility)."""
        file_analyses = {}
        last_yield_time = time.time()

        for i, (file_path, inclusion_reason) in enumerate(analyzable_files, 1):
            try:
                # Time-based yielding every 50ms during sequential processing
                current_time = time.time()
                if (current_time - last_yield_time) >= 0.05:
                    await asyncio.sleep(0)
                    last_yield_time = current_time

                # Report progress for each file
                if progress_callback:
                    relative_file_path = str(file_path.relative_to(validated_path))
                    # Create proper module/file path format
                    if module_name:
                        full_path = f"({module_name})/{relative_file_path}"
                    else:
                        full_path = relative_file_path

                    # Truncate the path and create a clean progress message
                    truncated_path = _truncate_path(full_path, 70)
                    await progress_callback(
                        message=f"{i}/{len(analyzable_files)} {truncated_path}",
                        current=i,
                        total=len(analyzable_files),
                        component_event="update",
                        component_id="static_analysis",
                    )

                file_analysis = await self._analyze_file(file_path, inclusion_reason)
                if file_analysis:
                    relative_file_path = str(file_path.relative_to(validated_path))
                    file_analyses[relative_file_path] = file_analysis

            except Exception as e:
                logger.warning(f"Failed to analyze file {file_path}: {e}")
                continue

        return file_analyses

    async def _process_files_with_shared_processor(
        self,
        analyzable_files: List[Tuple[Path, str]],
        validated_path: Path,
        worker_function: Optional[Callable],
        progress_callback: Optional[Callable] = None,
        module_name: Optional[str] = None,
        allow_spawning: bool = True,
    ) -> Dict[str, Any]:
        """Process files using the shared parallel processor framework."""

        # Create a prepare function that handles individual files
        def prepare_file_item(file_item):
            if isinstance(file_item, (list, tuple)) and len(file_item) == 2:
                # Individual file item (path, reason)
                return file_item
            else:
                # Single path, default reason
                return (file_item, "default")

        # Create batch prepare function that adds security manager data
        def prepare_batch_data(batch_data):
            # Add security manager information to batch
            batch_data.update(
                {
                    "security_roots": [
                        str(root) for root in self.security_manager.get_allowed_roots()
                    ],
                    "file_paths": batch_data["items"],  # Rename for worker compatibility
                }
            )
            batch_data.pop("items", None)  # Remove original items key
            return batch_data

        # Create sequential fallback function
        async def sequential_fallback(files):
            return await self._analyze_files_sequential_dict(
                files, validated_path, progress_callback, module_name
            )

        # Process the files
        if worker_function is None or not allow_spawning:
            # Fallback to sequential processing when no worker function or spawning disabled
            results = await sequential_fallback(analyzable_files)
        else:
            results = await process_items_parallel(
                items=analyzable_files,
                worker_function=worker_function,
                prepare_data_function=prepare_file_item,
                sequential_function=sequential_fallback,
                context_name="files",
                progress_callback=progress_callback,
                parallel_threshold=10,
                complexity_threshold=50,
                max_workers=4,
                worker_batch_size=20,  # Group files into batches of 20
                allow_spawning=allow_spawning,
                batch_prepare_function=prepare_batch_data,
            )

        # Convert absolute paths to relative paths for module context
        file_analyses = {}
        for abs_file_path, analysis in results.items():
            try:
                abs_path = Path(abs_file_path)
                relative_file_path = str(abs_path.relative_to(validated_path))
                file_analyses[relative_file_path] = analysis
            except ValueError:
                # Path not relative to validated_path, use as-is
                file_analyses[abs_file_path] = analysis

        return file_analyses

    async def _analyze_file(
        self, file_path: Path, inclusion_reason: str = "default"
    ) -> Dict[str, Any]:
        """Analyze a single file using existing parsers (always extracts full context)."""
        try:
            # Read file content
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Try with different encoding
                content = file_path.read_text(encoding="utf-8", errors="ignore")

            analysis = {
                "file_path": str(file_path),
                "size_bytes": len(content.encode("utf-8")),
                "line_count": len(content.splitlines()),
                "language": get_language_for_file_path(str(file_path)),
                "inclusion_reason": inclusion_reason,
                "included_as_ai_context": inclusion_reason == ".ai-attributes inclusion",
            }

            # Always perform comprehensive analysis - filter at query time, not build time
            # Use unified parser for single-pass parsing (eliminates duplicate tree-sitter calls)
            try:
                language_id = get_language_for_file_path(str(file_path))

                # Use unified parser for all extraction in one pass
                unified_parser = get_unified_parser()
                unified_result = await unified_parser.parse_document(content, language_id)

                if unified_result.success:
                    # Extract structured data from unified parsing result
                    analysis["functions"] = unified_result.functions
                    analysis["classes"] = unified_result.classes
                    analysis["imports"] = unified_result.imports
                    analysis["exports"] = unified_result.exports
                    analysis["tree_sitter_metrics"] = {
                        "total_nodes": unified_result.total_nodes,
                        "named_nodes": unified_result.named_nodes,
                        "max_depth": unified_result.max_depth,
                        "function_count": unified_result.function_count,
                        "class_count": unified_result.class_count,
                        "complexity_score": unified_result.complexity_score,
                    }

                    # Store unified result for guard tag extraction below
                    analysis["_unified_result"] = unified_result
                else:
                    logger.debug(f"Unified parsing failed for {file_path}")
                    analysis["_unified_result"] = None
            except Exception as e:
                logger.debug(f"Unified parsing failed for {file_path}: {e}")
                analysis["_unified_result"] = None

            # Use document analyzer for additional insights
            try:
                # Detect if file was included as context via .ai-attributes
                included_as_context = inclusion_reason.startswith(".ai-attributes-context:")

                # Also check if file is a context file based on language config (naming patterns)
                is_language_config_context = is_other_context_file(file_path)

                # File is considered context if either .ai-attributes or language config detects it
                is_any_context_file = included_as_context or is_language_config_context

                # Extract the specific .ai-attributes file path if available
                if included_as_context:
                    ai_attributes_file = (
                        inclusion_reason.split(":", 1)[1] if ":" in inclusion_reason else "unknown"
                    )
                    analysis["included_by_ai_attributes"] = ai_attributes_file
                    analysis["included_as_ai_context"] = True
                elif is_language_config_context:
                    analysis["included_by_language_config"] = True
                    analysis["included_as_ai_context"] = True
                else:
                    analysis["included_as_ai_context"] = False

                # Get guard tags from unified parsing result (no duplicate parsing)
                guard_tags = []
                unified_result = analysis.get("_unified_result")
                if unified_result is not None and unified_result.guard_tags:
                    guard_tags = unified_result.guard_tags

                # Check if any tags are marked as context
                context_tags = []
                for tag in guard_tags:
                    if (
                        getattr(tag, "aiIsContext", False)
                        or getattr(tag, "humanIsContext", False)
                        or getattr(tag, "aiPermission", None) in ["contextRead", "contextWrite"]
                        or getattr(tag, "humanPermission", None) in ["contextRead", "contextWrite"]
                    ):
                        context_tags.append(tag)

                analysis["has_context_tags"] = len(context_tags) > 0

                # Create context regions from guard tags (same as DocumentAnalyzer)
                context_regions = []
                context_line_count = 0
                if analysis["has_context_tags"]:
                    lines = content.split("\n")
                    guard_tag_last_yield = time.time()

                    for tag in context_tags:
                        # Time-based yielding every 50ms during guard tag processing
                        current_time = time.time()
                        if (current_time - guard_tag_last_yield) >= 0.05:
                            await asyncio.sleep(0)
                            guard_tag_last_yield = current_time

                        start_line = getattr(tag, "scopeStart", getattr(tag, "lineNumber", 1))
                        end_line = getattr(tag, "scopeEnd", start_line)

                        # Ensure valid line numbers
                        start_line = max(1, min(start_line, len(lines)))
                        end_line = max(start_line, min(end_line, len(lines)))

                        # Extract content for this region
                        region_lines = lines[
                            start_line - 1 : end_line
                        ]  # Convert to 0-based indexing
                        region_content = "\n".join(region_lines)

                        context_regions.append(
                            {
                                "start_line": start_line,
                                "end_line": end_line,
                                "content": region_content,
                                "encoding": "text",
                                "guard_tags": [
                                    tag.to_dict() if hasattr(tag, "to_dict") else str(tag)
                                ],
                            }
                        )

                        context_line_count += max(0, end_line - start_line + 1)

                analysis["context_regions"] = context_regions
                analysis["context_line_count"] = context_line_count

            except Exception as e:
                logger.error(f"Guard tag analysis failed for {file_path}: {e}", exc_info=True)
                # Set default values if guard tag analysis fails
                analysis["has_context_tags"] = False
                analysis["context_line_count"] = 0

            # Add complexity estimation (use tree-sitter if available, otherwise fallback)
            if "tree_sitter_metrics" in analysis and analysis["tree_sitter_metrics"].get(
                "complexity_score"
            ):
                analysis["complexity_score"] = analysis["tree_sitter_metrics"]["complexity_score"]
            else:
                analysis["complexity_score"] = self._estimate_complexity(
                    content, analysis.get("language", "unknown")
                )

            # Clean up temporary unified result (not needed in final output)
            analysis.pop("_unified_result", None)

            return analysis

        except Exception as e:
            logger.error(f"File analysis failed for {file_path}: {e}")
            return {"file_path": str(file_path), "error": str(e), "complexity_score": 0.0}

    def _estimate_complexity(self, content: str, language: str) -> float:
        """Estimate code complexity based on content analysis."""
        try:
            lines = content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]

            if not non_empty_lines:
                return 0.0

            # Basic complexity metrics
            complexity_indicators = {
                "if": 1.0,
                "else": 0.5,
                "elif": 0.5,
                "while": 1.0,
                "for": 1.0,
                "try": 0.5,
                "except": 0.5,
                "catch": 0.5,
                "switch": 1.0,
                "case": 0.3,
            }

            total_complexity = 0.0
            for line in non_empty_lines:
                line_lower = line.lower().strip()
                for keyword, weight in complexity_indicators.items():
                    if keyword in line_lower:
                        total_complexity += weight

            # Normalize by lines of code
            return min(total_complexity / len(non_empty_lines), 10.0)  # Cap at 10.0

        except Exception:
            return 0.0

    def _extract_functions(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code."""
        functions = []

        try:
            lines = content.splitlines()

            # Simple regex-based extraction (can be enhanced with tree-sitter)
            function_patterns = {
                "python": r"^\s*def\s+(\w+)\s*\(",
                "javascript": r"^\s*(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:function|\([^)]*\)\s*=>))",
                "typescript": r"^\s*(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:function|\([^)]*\)\s*=>))",
                "java": r"^\s*(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
                "go": r"^\s*func\s+(\w+)\s*\(",
            }

            import re

            pattern = function_patterns.get(language)
            if not pattern:
                return functions

            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    function_name = (
                        match.group(1) or match.group(2)
                        if match.lastindex and match.lastindex > 1
                        else match.group(1)
                    )
                    if function_name:
                        functions.append(
                            {
                                "name": function_name,
                                "line_number": i + 1,
                                "definition": line.strip(),
                            }
                        )

        except Exception as e:
            logger.debug(f"Function extraction failed: {e}")

        return functions

    def _extract_classes(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from code."""
        classes = []

        try:
            lines = content.splitlines()

            class_patterns = {
                "python": r"^\s*class\s+(\w+)",
                "javascript": r"^\s*class\s+(\w+)",
                "typescript": r"^\s*(?:export\s+)?class\s+(\w+)",
                "java": r"^\s*(?:public|private|protected)?\s*class\s+(\w+)",
                "go": r"^\s*type\s+(\w+)\s+struct",
            }

            import re

            pattern = class_patterns.get(language)
            if not pattern:
                return classes

            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    class_name = match.group(1)
                    classes.append(
                        {"name": class_name, "line_number": i + 1, "definition": line.strip()}
                    )

        except Exception as e:
            logger.debug(f"Class extraction failed: {e}")

        return classes

    def _extract_imports(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract import statements from code."""
        imports = []

        try:
            lines = content.splitlines()

            import_patterns = {
                "python": r"^\s*(?:from\s+(\S+)\s+)?import\s+(.+)",
                "javascript": r'^\s*import\s+(.+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                "typescript": r'^\s*import\s+(.+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                "java": r"^\s*import\s+([^;]+);",
                "go": r'^\s*import\s+[\'"]([^\'"]+)[\'"]',
            }

            import re

            pattern = import_patterns.get(language)
            if not pattern:
                return imports

            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    if language == "python":
                        from_module = match.group(1)
                        import_items = match.group(2)
                        imports.append(
                            {
                                "type": "import",
                                "from": from_module,
                                "items": import_items,
                                "line_number": i + 1,
                            }
                        )
                    else:
                        imports.append(
                            {"type": "import", "statement": line.strip(), "line_number": i + 1}
                        )

        except Exception as e:
            logger.debug(f"Import extraction failed: {e}")

        return imports

    def _extract_exports(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract export statements from code."""
        exports = []

        try:
            lines = content.splitlines()

            export_patterns = {
                "javascript": r"^\s*export\s+(.+)",
                "typescript": r"^\s*export\s+(.+)",
            }

            import re

            pattern = export_patterns.get(language)
            if not pattern:
                return exports

            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    exports.append(
                        {"type": "export", "statement": line.strip(), "line_number": i + 1}
                    )

        except Exception as e:
            logger.debug(f"Export extraction failed: {e}")

        return exports

    def _generate_module_summary(
        self,
        module_path: Path,
        file_analyses: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate a summary of the module based on analysis (always full summary)."""
        try:
            if not file_analyses:
                return f"Empty module at {module_path.name}"

            total_files = len(file_analyses)
            total_lines = sum(analysis.get("line_count", 0) for analysis in file_analyses.values())
            languages = set(
                analysis.get("language", "unknown") for analysis in file_analyses.values()
            )
            avg_complexity = (
                sum(analysis.get("complexity_score", 0.0) for analysis in file_analyses.values())
                / total_files
            )

            # Count functions and classes
            total_functions = sum(
                len(analysis.get("functions", [])) for analysis in file_analyses.values()
            )
            total_classes = sum(
                len(analysis.get("classes", [])) for analysis in file_analyses.values()
            )

            summary_parts = [
                f"Module '{module_path.name}' with {total_files} files",
                f"{total_lines} lines of code",
                f"Languages: {', '.join(sorted(languages))}",
                f"Average complexity: {avg_complexity:.2f}",
            ]

            # Always include detailed information - filter at query time
            summary_parts.extend([f"{total_functions} functions", f"{total_classes} classes"])

            return ". ".join(summary_parts) + "."

        except Exception as e:
            logger.error(f"Failed to generate module summary: {e}")
            return f"Module summary generation failed: {e}"

    def _extract_api_catalog(self, file_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract API catalog from file analyses."""
        api_catalog = {
            "public_functions": [],
            "public_classes": [],
            "exports": [],
            "main_imports": [],
        }

        try:
            for file_path, analysis in file_analyses.items():
                # Collect functions (assuming public if not starting with _)
                for func in analysis.get("functions", []):
                    if not func["name"].startswith("_"):
                        api_catalog["public_functions"].append(
                            {"name": func["name"], "file": file_path, "line": func["line_number"]}
                        )

                # Collect classes
                for cls in analysis.get("classes", []):
                    if not cls["name"].startswith("_"):
                        api_catalog["public_classes"].append(
                            {"name": cls["name"], "file": file_path, "line": cls["line_number"]}
                        )

                # Collect exports
                api_catalog["exports"].extend(analysis.get("exports", []))

                # Collect major imports (not relative imports)
                for imp in analysis.get("imports", []):
                    import_from = imp.get("from", "")
                    if import_from and not import_from.startswith("."):
                        api_catalog["main_imports"].append(import_from)

            # Deduplicate main imports
            api_catalog["main_imports"] = list(set(api_catalog["main_imports"]))

        except Exception as e:
            logger.error(f"Failed to extract API catalog: {e}")

        return api_catalog
