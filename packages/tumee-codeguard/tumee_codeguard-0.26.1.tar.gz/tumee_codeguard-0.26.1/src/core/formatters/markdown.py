"""
Markdown formatter for CodeGuard reports.
"""

from typing import Any, AsyncGenerator, List

from .base import DataType, FormatterRegistry, UniversalFormatter
from .component_utils import ComponentRenderer


@FormatterRegistry.register
class MarkdownFormatter(UniversalFormatter):
    """Formatter for Markdown output."""

    @property
    def format_name(self) -> str:
        return "markdown"

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format items as streaming Markdown for any data type."""
        if data_type == DataType.VALIDATION_RESULTS:
            async for chunk in self._format_validation_stream(items, **kwargs):
                yield chunk
        elif data_type == DataType.CONTEXT_FILES:
            async for chunk in self._format_context_files_stream(items, **kwargs):
                yield chunk
        elif data_type == DataType.ACL_PERMISSIONS:
            async for chunk in self._format_acl_stream(items, **kwargs):
                yield chunk
        elif data_type == DataType.ANALYSIS_RESULTS:
            async for chunk in self._format_analysis_results_stream(items, **kwargs):
                yield chunk
        else:
            # Debug: show what data type is missing
            yield f"<!-- WARNING: Unknown data_type: {data_type} -->\n"
            async for chunk in self._format_generic_stream(items, **kwargs):
                yield chunk

    async def format_collection(self, items: List[Any], data_type: DataType, **kwargs) -> str:
        """Format a complete collection as Markdown."""
        chunks = []
        async for chunk in self.format_stream(
            self._items_to_async_generator(items), data_type, **kwargs
        ):
            chunks.append(chunk)
        return "".join(chunks)

    async def _format_validation_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as streaming Markdown output.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            **kwargs: Additional formatting options

        Yields:
            Markdown string chunks for streaming output
        """
        include_content = kwargs.get("include_content", True)
        include_diff = kwargs.get("include_diff", True)
        max_content_lines = kwargs.get("max_content_lines", 10)

        yield "# CodeGuard Validation Report\n\n"

        violation_count = 0

        async for item in items:
            # Handle both ValidationResult and individual violations
            if hasattr(item, "violations"):
                # ValidationResult object - show summary first
                yield "## Summary\n\n"
                yield "| Metric | Value |\n"
                yield "|--------|---------|\n"
                yield f"| Files Checked | {item.files_checked} |\n"
                yield f"| Violations Found | {item.violations_found} |\n"
                yield f"| Critical Violations | {item.critical_count} |\n"
                yield f"| Warning Violations | {item.warning_count} |\n"
                yield f"| Info Violations | {item.info_count} |\n"
                yield f"| Status | {item.status} |\n\n"

                yield "## Violations\n\n"

                if item.violations_found > 0:
                    for i, violation in enumerate(item.violations, 1):
                        violation_count = i
                        async for chunk in self._format_violation(
                            violation,
                            violation_count,
                            include_content,
                            include_diff,
                            max_content_lines,
                        ):
                            yield chunk
                else:
                    yield "No violations found.\n\n"
            else:
                # Individual violation object
                violation_count += 1
                async for chunk in self._format_violation(
                    item, violation_count, include_content, include_diff, max_content_lines
                ):
                    yield chunk

    async def _format_violation(
        self, violation, index, include_content, include_diff, max_content_lines
    ):
        """Format a single violation for Markdown output."""
        severity_emoji = {"critical": "❌", "warning": "⚠️", "info": "ℹ️"}.get(violation.severity, "")

        yield f"### {severity_emoji} Violation #{index} - {violation.severity.upper()}\n\n"
        yield f"**File:** {violation.file}:{violation.line}\n"
        yield f"**Guard Type:** {violation.guard_type}\n"
        if hasattr(violation, "violated_by") and violation.violated_by:
            yield f"**Violated By:** {violation.violated_by}\n"
        yield f"**Message:** {violation.message}\n"
        if hasattr(violation, "guard_source") and violation.guard_source:
            yield f"**Guard Source:** {violation.guard_source}\n"
        yield "\n"

        if include_diff and violation.diff_summary:
            yield "#### Diff:\n\n"
            yield "```diff\n"
            yield f"{violation.diff_summary}\n"
            yield "```\n\n"

        if include_content:
            yield "#### Original Content:\n\n"
            yield "```\n"
            orig_lines = violation.original_content.splitlines()[:max_content_lines]
            yield "\n".join(orig_lines) + "\n"
            if len(violation.original_content.splitlines()) > max_content_lines:
                yield f"... ({len(violation.original_content.splitlines()) - max_content_lines} more lines)\n"
            yield "```\n\n"

            yield "#### Modified Content:\n\n"
            yield "```\n"
            mod_lines = violation.modified_content.splitlines()[:max_content_lines]
            yield "\n".join(mod_lines) + "\n"
            if len(violation.modified_content.splitlines()) > max_content_lines:
                yield f"... ({len(violation.modified_content.splitlines()) - max_content_lines} more lines)\n"
            yield "```\n\n"

    async def _format_context_files_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format context files as streaming Markdown."""
        directory = kwargs.get("directory", "")
        tree_format = kwargs.get("tree_format", False)

        yield f"# Context Files in {directory}\n\n"

        total = 0
        async for cf in items:
            level = cf.get("level", -1)
            if not isinstance(level, int):
                level = -1
            level_prefix = f"[L{level}]" if level >= 0 else "[-]"

            if tree_format:
                indent = "  " * level if level >= 0 else ""
                file_display = cf.get("relative_path", cf["path"])
                yield f"- {level_prefix} {indent}`{file_display}`\n"
            else:
                yield f"- {level_prefix} `{cf['path']}`\n"

            metadata = cf.get("metadata", {})
            if metadata:
                if "priority" in metadata:
                    yield f"  - Priority: {metadata['priority']}\n"
                if "for" in metadata:
                    yield f"  - For: {metadata['for']}\n"
                if "inherit" in metadata:
                    yield f"  - Inherit: {metadata['inherit']}\n"
            total += 1

        yield f"\n**Total**: {total} files\n"

    async def _format_acl_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format ACL permissions as streaming Markdown."""
        verbose = kwargs.get("verbose", False)
        recursive = kwargs.get("recursive", False)

        yield "# ACL Permissions\n\n"

        async for perm_info in items:
            if perm_info.get("status") == "error":
                yield f"## ❌ Error\n\n**Error**: {perm_info.get('error')}\n\n"
                continue

            yield f"## `{perm_info['path']}`\n\n"
            yield f"**Type**: {perm_info['type']}\n\n"

            yield "### Permissions\n\n"
            yield "| Target | Permission |\n"
            yield "|--------|------------|\n"
            yield f"| AI | {perm_info['permissions']['ai']} |\n"
            if "human" in perm_info["permissions"]:
                yield f"| Human | {perm_info['permissions']['human']} |\n"
            yield "\n"

            if verbose and "permission_sources" in perm_info:
                yield "### Permission Sources\n\n"
                for source in perm_info["permission_sources"]:
                    yield f"- **Target**: {source.get('target', 'unknown')}\n"
                    yield f"- **Source**: {source['source']}\n"
                    if "line" in source:
                        yield f"- **Line**: {source['line']}\n"
                    yield f"- **Permission**: {source['permission']}\n\n"

            if verbose and "file_level_guards" in perm_info and perm_info["file_level_guards"]:
                yield "### File-Level Guards\n\n"
                for guard in perm_info["file_level_guards"]:
                    yield f"- **Line {guard['line']}**: `{guard['annotation']}`\n"
                    if "description" in guard and guard["description"]:
                        yield f"  - Description: {guard['description']}\n"
                yield "\n"

            if recursive and perm_info["type"] == "directory" and "children" in perm_info:
                yield "### Directory Summary\n\n"
                yield f"- **Total Children**: {perm_info['children']['total']}\n"
                yield f"- **Permissions Consistent**: {perm_info['children']['consistent']}\n"

                if not perm_info["children"]["consistent"]:
                    yield "\n**Inconsistent Paths**:\n\n"
                    for path in perm_info["children"]["inconsistent_paths"]:
                        yield f"- `{path}`\n"

                if verbose and "child_permissions" in perm_info:
                    yield "\n**Child Permissions**:\n\n"
                    for child in perm_info["child_permissions"]:
                        child_perms = child.get("permissions", {})
                        perm_str = ", ".join([f"{k}:{v}" for k, v in child_perms.items()])
                        yield f"- `{child['path']}`: {perm_str}\n"

            yield "\n---\n\n"

    async def _format_analysis_results_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format analysis results (components) as streaming Markdown."""
        async for item in items:
            if isinstance(item, dict):
                # Check if this is a component with display instructions
                if ComponentRenderer.is_component_format(item):
                    for chunk in self._format_component_markdown(item):
                        yield chunk
                else:
                    # Legacy format - process each component in the item
                    for component_name, component_data in item.items():
                        if isinstance(component_data, dict) and "display" in component_data:
                            # Create component format for legacy data
                            legacy_component = {
                                "component": component_name,
                                "data": component_data.get("data", {}),
                                "display": component_data.get("display", {}),
                            }
                            for chunk in self._format_component_markdown(legacy_component):
                                yield chunk
                        else:
                            # Fallback to dict formatting
                            for chunk in self._format_dict_as_markdown(item, level=2):
                                yield chunk
            else:
                yield f"```\n{str(item)}\n```\n\n"

    async def _format_generic_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generic Markdown streaming for unknown data types."""
        yield "# Generic Data\n\n"

        count = 0
        async for item in items:
            count += 1
            yield f"## Item {count}\n\n"
            if hasattr(item, "to_dict"):
                for key, value in item.to_dict().items():
                    yield f"- **{key}**: {value}\n"
            elif isinstance(item, dict):
                # Check if this is a component with display instructions
                if ComponentRenderer.is_component_format(item):
                    for chunk in self._format_component_markdown(item):
                        yield chunk
                else:
                    for chunk in self._format_dict_as_markdown(item, level=3):
                        yield chunk
            else:
                yield f"```\n{str(item)}\n```\n"
            yield "\n"

    def _format_component_markdown(self, component: dict):
        """Format a component with display instructions as proper markdown."""
        component_name, data, display = ComponentRenderer.extract_component_info(component)

        # Add component title
        if display.get("title"):
            yield f"## {display['title']}\n\n"
        else:
            yield f"## {component_name}\n\n"

        display_type = display.get("type", "")

        if display_type == "table":
            # Render as markdown table
            for chunk in self._render_markdown_table(display, data):
                yield chunk
        elif display_type == "list":
            # Render as markdown list
            for chunk in self._render_markdown_list(display, data):
                yield chunk
        else:
            # Fallback to generic dict formatting
            for chunk in self._format_dict_as_markdown(data, level=3):
                yield chunk

    def _render_markdown_table(self, display: dict, data: dict):
        """Render a table display as nested lists for LLM-friendly consumption."""
        columns = display.get("columns", [])

        if not columns:
            yield "No table structure defined.\n\n"
            return

        # Process table rows
        processed_rows = ComponentRenderer.process_table_rows(display, data)

        if not processed_rows:
            yield "No data available.\n\n"
            return

        # Group rows into logical sections based on empty rows
        sections = []
        current_section = []

        for row in processed_rows:
            if not any(row):  # Empty row indicates section break
                if current_section:
                    sections.append(current_section)
                    current_section = []
            else:
                current_section.append(row)

        # Add final section if exists
        if current_section:
            sections.append(current_section)

        # Render sections
        if len(sections) == 1:
            # Single section - just render as list
            for row in sections[0]:
                if len(row) >= 2:
                    metric = row[0]
                    value = row[1]
                    target = row[2] if len(row) > 2 and row[2] else ""
                    if target:
                        yield f"- **{metric}:** {value} (target: {target})\n"
                    else:
                        yield f"- **{metric}:** {value}\n"
        else:
            # Multiple sections - create subsections
            section_names = ["Summary", "Priority Breakdown", "Additional Metrics"]

            for i, section in enumerate(sections):
                if i < len(section_names):
                    yield f"### {section_names[i]}\n"
                else:
                    yield f"### Section {i + 1}\n"

                for row in section:
                    if len(row) >= 2:
                        metric = row[0]
                        value = row[1]
                        target = row[2] if len(row) > 2 and row[2] else ""
                        if target:
                            yield f"- **{metric}:** {value} (target: {target})\n"
                        else:
                            yield f"- **{metric}:** {value}\n"

                yield "\n"

        yield "\n"

    def _render_markdown_list(self, display: dict, data: dict):
        """Render a list display as markdown list."""
        items = display.get("items", [])

        for item in items:
            if isinstance(item, str):
                processed_item = ComponentRenderer.substitute_template(item, data)
                yield f"- {processed_item}\n"
            elif isinstance(item, dict):
                title = item.get("title", "")
                content = item.get("content", "")
                processed_title = ComponentRenderer.substitute_template(title, data)
                processed_content = ComponentRenderer.substitute_template(content, data)
                yield f"- **{processed_title}**: {processed_content}\n"

        yield "\n"

    def _format_dict_as_markdown(self, data: dict, level: int = 3):
        """Format a dictionary as proper markdown with nested structures."""
        for key, value in data.items():
            if isinstance(value, dict):
                # Nested dictionary - create subsection
                header = "#" * level
                yield f"{header} {key.replace('_', ' ').title()}\n\n"
                for chunk in self._format_dict_as_markdown(value, level + 1):
                    yield chunk
                yield "\n"
            elif isinstance(value, list):
                # List - create markdown list
                yield f"**{key.replace('_', ' ').title()}:**\n\n"
                for item in value:
                    if isinstance(item, dict):
                        yield f"- **{list(item.keys())[0] if item else 'Item'}:** {list(item.values())[0] if item else 'N/A'}\n"
                    else:
                        yield f"- {item}\n"
                yield "\n"
            else:
                # Simple key-value pair
                formatted_key = key.replace("_", " ").title()
                yield f"- **{formatted_key}:** {value}\n"

    async def _items_to_async_generator(self, items: List[Any]):
        """Convert list to async generator."""
        for item in items:
            yield item
