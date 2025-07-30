"""
HTML formatter for CodeGuard reports.
"""

from typing import Any, AsyncGenerator, List

from .base import FormatterRegistry, ValidationFormatter


@FormatterRegistry.register
class HtmlFormatter(ValidationFormatter):
    """Formatter for HTML output."""

    @property
    def format_name(self) -> str:
        return "html"

    async def format_validation_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as streaming HTML output.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            **kwargs: Additional formatting options

        Yields:
            HTML string chunks for streaming output
        """
        include_content = kwargs.get("include_content", True)
        include_diff = kwargs.get("include_diff", True)
        max_content_lines = kwargs.get("max_content_lines", 10)

        # Start HTML document
        yield """<!DOCTYPE html>
<html>
<head>
    <title>CodeGuard Validation Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4 {
            margin-top: 0;
        }
        .summary {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .summary table {
            width: 100%;
            border-collapse: collapse;
        }
        .summary table td, .summary table th {
            padding: 8px;
            text-align: left;
        }
        .violation {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .critical {
            background-color: #ffebee;
            border-left: 5px solid #f44336;
        }
        .warning {
            background-color: #fff8e1;
            border-left: 5px solid #ffc107;
        }
        .info {
            background-color: #e3f2fd;
            border-left: 5px solid #2196f3;
        }
        .violation-details {
            margin-left: 10px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .diff pre {
            white-space: pre-wrap;
        }
        .success {
            color: #4caf50;
            font-weight: bold;
        }
        .failed {
            color: #f44336;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>CodeGuard Validation Report</h1>
"""

        violation_count = 0

        async for item in items:
            # Handle both ValidationResult and individual violations
            if hasattr(item, "violations"):
                # ValidationResult object - show summary first
                yield f"""
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <td><strong>Files Checked:</strong></td>
                <td>{item.files_checked}</td>
            </tr>
            <tr>
                <td><strong>Violations Found:</strong></td>
                <td>{item.violations_found}</td>
            </tr>
            <tr>
                <td><strong>Critical Violations:</strong></td>
                <td>{item.critical_count}</td>
            </tr>
            <tr>
                <td><strong>Warning Violations:</strong></td>
                <td>{item.warning_count}</td>
            </tr>
            <tr>
                <td><strong>Info Violations:</strong></td>
                <td>{item.info_count}</td>
            </tr>
            <tr>
                <td><strong>Status:</strong></td>
                <td class="{item.status.lower()}">{item.status}</td>
            </tr>
        </table>
    </div>

    <h2>Violations</h2>
"""

                if item.violations_found > 0:
                    yield '<div class="violations">'
                    for i, violation in enumerate(item.violations, 1):
                        violation_count = i
                        yield await self._format_violation(
                            violation,
                            violation_count,
                            include_content,
                            include_diff,
                            max_content_lines,
                        )
                    yield "</div>"
                else:
                    yield "<p>No violations found.</p>"
            else:
                # Individual violation object
                violation_count += 1
                if violation_count == 1:
                    yield '<div class="violations">'
                yield await self._format_violation(
                    item, violation_count, include_content, include_diff, max_content_lines
                )

        # Close HTML document
        yield """
</body>
</html>
"""

    async def _format_violation(
        self, violation, index, include_content, include_diff, max_content_lines
    ):
        """Format a single violation for HTML output."""
        severity_class = {"critical": "critical", "warning": "warning", "info": "info"}.get(
            violation.severity, ""
        )

        html = f"""
        <div class="violation {severity_class}">
            <h3>Violation #{index} - {violation.severity.upper()}</h3>
            <div class="violation-details">
                <p><strong>File:</strong> {violation.file}:{violation.line}</p>
                <p><strong>Guard Type:</strong> {violation.guard_type}</p>
                {f'<p><strong>Violated By:</strong> {violation.violated_by}</p>' if hasattr(violation, 'violated_by') and violation.violated_by else ''}
                <p><strong>Message:</strong> {violation.message}</p>
                {f'<p><strong>Guard Source:</strong> {violation.guard_source}</p>' if hasattr(violation, 'guard_source') and violation.guard_source else ''}
        """

        if include_diff and violation.diff_summary:
            html += f"""
                <div class="diff">
                    <h4>Diff:</h4>
                    <pre>{violation.diff_summary}</pre>
                </div>
            """

        if include_content:
            orig_lines = violation.original_content.splitlines()[:max_content_lines]
            orig_content = "\n".join(orig_lines)
            if len(violation.original_content.splitlines()) > max_content_lines:
                orig_content += f"\n... ({len(violation.original_content.splitlines()) - max_content_lines} more lines)"

            mod_lines = violation.modified_content.splitlines()[:max_content_lines]
            mod_content = "\n".join(mod_lines)
            if len(violation.modified_content.splitlines()) > max_content_lines:
                mod_content += f"\n... ({len(violation.modified_content.splitlines()) - max_content_lines} more lines)"

            html += f"""
                <div class="content">
                    <h4>Original Content:</h4>
                    <pre>{orig_content}</pre>
                    <h4>Modified Content:</h4>
                    <pre>{mod_content}</pre>
                </div>
            """

        html += """
            </div>
        </div>
        """

        return html

    async def format_validation_collection(self, items: List[Any], **kwargs) -> str:
        """Format a collection of validation results as HTML."""

        async def item_generator():
            for item in items:
                yield item

        result_chunks = []
        async for chunk in self.format_validation_stream(item_generator(), **kwargs):
            result_chunks.append(chunk)

        return "".join(result_chunks)
