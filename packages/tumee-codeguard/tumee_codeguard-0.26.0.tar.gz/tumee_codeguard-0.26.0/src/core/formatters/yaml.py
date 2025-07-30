"""
YAML formatter for CodeGuard reports.
"""

from typing import Any, AsyncGenerator, Dict, List

from .base import DataType, FormatterRegistry, UniversalFormatter

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@FormatterRegistry.register
class YamlFormatter(UniversalFormatter):
    """Formatter for YAML output."""

    @property
    def format_name(self) -> str:
        return "yaml"

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format items as streaming YAML for any data type."""
        if not YAML_AVAILABLE:
            yield "YAML not available. Install pyyaml package.\n"
            return

        if data_type == DataType.VALIDATION_RESULTS:
            async for chunk in self._format_validation_stream(items, **kwargs):
                yield chunk
        elif data_type == DataType.CONTEXT_FILES:
            async for chunk in self._format_context_files_stream(items, **kwargs):
                yield chunk
        elif data_type == DataType.ACL_PERMISSIONS:
            async for chunk in self._format_acl_stream(items, **kwargs):
                yield chunk
        else:
            async for chunk in self._format_generic_stream(items, **kwargs):
                yield chunk

    async def format_collection(self, items: List[Any], data_type: DataType, **kwargs) -> str:
        """Format a complete collection as YAML."""
        if not YAML_AVAILABLE:
            return "YAML not available. Install pyyaml package.\n"

        if data_type == DataType.VALIDATION_RESULTS:
            return self._format_validation_collection(items, **kwargs)
        elif data_type == DataType.CONTEXT_FILES:
            return self._format_context_files_collection(items, **kwargs)
        elif data_type == DataType.ACL_PERMISSIONS:
            return self._format_acl_collection(items, **kwargs)
        else:
            return self._format_generic_collection(items, **kwargs)

    async def _format_validation_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as streaming YAML output.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            **kwargs: Additional formatting options

        Yields:
            YAML string chunks for streaming output
        """
        if not YAML_AVAILABLE:
            yield "YAML not available. Install pyyaml package.\n"
            return

        include_content = kwargs.get("include_content", True)
        include_diff = kwargs.get("include_diff", True)

        yield "violations:\n"

        async for item in items:
            # Handle both ValidationResult and individual violations
            if hasattr(item, "violations"):
                # ValidationResult object
                for violation in item.violations:
                    violation_dict = violation.to_dict()
                    if not include_content:
                        violation_dict.pop("original_content", None)
                        violation_dict.pop("modified_content", None)
                    if not include_diff:
                        violation_dict.pop("diff_summary", None)

                    # Convert to YAML document
                    yaml_content = yaml.dump(
                        violation_dict, sort_keys=False, default_flow_style=False
                    )
                    # Indent each line for array formatting
                    for line in yaml_content.splitlines():
                        if line.strip():
                            yield (
                                f"  - {line}\n"
                                if line == yaml_content.splitlines()[0]
                                else f"    {line}\n"
                            )
                    yield "\n"
            else:
                # Individual violation object
                violation_dict = item.to_dict()
                if not include_content:
                    violation_dict.pop("original_content", None)
                    violation_dict.pop("modified_content", None)
                if not include_diff:
                    violation_dict.pop("diff_summary", None)

                # Convert to YAML document
                yaml_content = yaml.dump(violation_dict, sort_keys=False, default_flow_style=False)
                # Indent each line for array formatting
                for line in yaml_content.splitlines():
                    if line.strip():
                        yield (
                            f"  - {line}\n"
                            if line == yaml_content.splitlines()[0]
                            else f"    {line}\n"
                        )
                yield "\n"

    def _format_validation_collection(self, items: List[Any], **kwargs) -> str:
        """Format validation results collection as YAML."""
        include_content = kwargs.get("include_content", True)
        include_diff = kwargs.get("include_diff", True)

        violations = []
        for item in items:
            if hasattr(item, "violations"):
                for violation in item.violations:
                    violation_dict = violation.to_dict()
                    if not include_content:
                        violation_dict.pop("original_content", None)
                        violation_dict.pop("modified_content", None)
                    if not include_diff:
                        violation_dict.pop("diff_summary", None)
                    violations.append(violation_dict)
            else:
                violation_dict = item.to_dict()
                if not include_content:
                    violation_dict.pop("original_content", None)
                    violation_dict.pop("modified_content", None)
                if not include_diff:
                    violation_dict.pop("diff_summary", None)
                violations.append(violation_dict)

        return yaml.dump({"violations": violations}, sort_keys=False, default_flow_style=False)

    async def _format_context_files_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format context files as streaming YAML."""
        directory = kwargs.get("directory", "")

        yield "directory: " + yaml.dump(str(directory), default_flow_style=True).strip() + "\n"
        yield "context_files:\n"

        total = 0
        async for context_info in items:
            yaml_content = yaml.dump(context_info, sort_keys=False, default_flow_style=False)
            for line in yaml_content.splitlines():
                if line.strip():
                    yield (
                        f"  - {line}\n" if line == yaml_content.splitlines()[0] else f"    {line}\n"
                    )
            total += 1

        yield f"total: {total}\n"
        yield "status: success\n"

    def _format_context_files_collection(self, items: List[Any], **kwargs) -> str:
        """Format context files collection as YAML."""
        directory = kwargs.get("directory", "")
        priority = kwargs.get("priority")
        for_use = kwargs.get("for_use")

        response = {
            "directory": str(directory),
            "context_files": items,
            "total": len(items),
            "filters": {"priority": priority, "for": for_use},
            "status": "success",
        }

        return yaml.dump(response, sort_keys=False, default_flow_style=False)

    async def _format_acl_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format ACL permissions as streaming YAML."""
        yield "permissions:\n"

        async for perm_info in items:
            yaml_content = yaml.dump(perm_info, sort_keys=False, default_flow_style=False)
            for line in yaml_content.splitlines():
                if line.strip():
                    yield (
                        f"  - {line}\n" if line == yaml_content.splitlines()[0] else f"    {line}\n"
                    )

    def _format_acl_collection(self, items: List[Any], **kwargs) -> str:
        """Format ACL permissions collection as YAML."""
        return yaml.dump({"permissions": items}, sort_keys=False, default_flow_style=False)

    async def _format_generic_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generic YAML streaming for unknown data types."""
        yield "items:\n"

        async for item in items:
            if hasattr(item, "to_dict"):
                item_data = item.to_dict()
            elif isinstance(item, dict):
                item_data = item
            else:
                item_data = str(item)

            yaml_content = yaml.dump(item_data, sort_keys=False, default_flow_style=False)
            for line in yaml_content.splitlines():
                if line.strip():
                    yield (
                        f"  - {line}\n" if line == yaml_content.splitlines()[0] else f"    {line}\n"
                    )

    def _format_generic_collection(self, items: List[Any], **kwargs) -> str:
        """Generic YAML formatting for unknown data types."""
        formatted_items = []
        for item in items:
            if hasattr(item, "to_dict"):
                formatted_items.append(item.to_dict())
            elif isinstance(item, dict):
                formatted_items.append(item)
            else:
                formatted_items.append(str(item))

        return yaml.dump({"items": formatted_items}, sort_keys=False, default_flow_style=False)
