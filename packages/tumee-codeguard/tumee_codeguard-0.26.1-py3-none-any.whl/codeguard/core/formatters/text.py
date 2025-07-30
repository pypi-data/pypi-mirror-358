"""
Text formatter for CodeGuard reports.
"""

from typing import Any, AsyncGenerator, List

from .base import DataType, FormatterRegistry, UniversalFormatter
from .component_utils import ComponentRenderer


@FormatterRegistry.register
class TextFormatter(UniversalFormatter):
    """Formatter for plain text output."""

    @property
    def format_name(self) -> str:
        return "text"

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format items as streaming text using universal self-describing format."""
        async for item in items:
            yield await self._format_self_describing_item(item, **kwargs)

    async def format_collection(self, items: List[Any], data_type: DataType, **kwargs) -> str:
        """Format a complete collection as text using universal self-describing format."""
        chunks = []
        for item in items:
            chunks.append(await self._format_self_describing_item(item, **kwargs))
        return "".join(chunks)

    async def _format_self_describing_item(self, item: Any, **kwargs) -> str:
        """Format a single self-describing item as text."""
        if isinstance(item, dict):
            # Check if this is a component format
            if ComponentRenderer.is_component_format(item):
                return self._render_component_as_text(item)
            else:
                # Process each component in the item
                output_chunks = []
                for component_name, component_data in item.items():
                    if isinstance(component_data, dict) and "display" in component_data:
                        output_chunks.append(
                            self._render_self_describing_component(component_name, component_data)
                        )
                    else:
                        raise ValueError(
                            f"Component '{component_name}' must provide 'data' and 'display' structure"
                        )
                return "".join(output_chunks)
        else:
            # Handle generic objects by converting to string
            return str(item)

    def _render_component_as_text(self, component: dict) -> str:
        """Render a component with display instructions as simple text."""
        component_name, data, display = ComponentRenderer.extract_component_info(component)

        lines = []

        # Add component title
        if display.get("title"):
            lines.append(f"=== {display['title']} ===")
        else:
            lines.append(f"=== {component_name} ===")
        lines.append("")

        display_type = display.get("type", "")

        if display_type == "table":
            lines.extend(self._render_table_as_simple_text(display, data))
        elif display_type == "list":
            lines.extend(self._render_list_as_text(display, data))
        else:
            # Fallback to key-value pairs
            for key, value in data.items():
                lines.append(f"{key}: {value}")

        lines.append("")  # Empty line after component
        return "\n".join(lines)

    def _render_table_as_simple_text(self, display: dict, data: dict):
        """Render table as simple key-value or CSV-like text for LLM consumption."""
        columns = display.get("columns", [])

        if not columns:
            return ["No table structure defined."]

        lines = []
        col_names = ComponentRenderer.get_column_names(columns)

        # CSV-like header
        lines.append(" | ".join(col_names))
        lines.append("-" * (len(" | ".join(col_names))))

        # Process and render rows
        processed_rows = ComponentRenderer.process_table_rows(display, data)
        for row in processed_rows:
            if not any(row):  # Empty row
                lines.append("")
                continue

            # Ensure row has same number of cells as columns
            padded_row = row + [""] * (len(col_names) - len(row))
            padded_row = padded_row[: len(col_names)]

            lines.append(" | ".join(str(cell) for cell in padded_row))

        return lines

    def _render_list_as_text(self, display: dict, data: dict):
        """Render list as simple bullet points."""
        items = display.get("items", [])
        lines = []

        for item in items:
            if isinstance(item, str):
                processed_item = ComponentRenderer.substitute_template(item, data)
                lines.append(f"• {processed_item}")
            elif isinstance(item, dict):
                title = item.get("title", "")
                content = item.get("content", "")
                processed_title = ComponentRenderer.substitute_template(title, data)
                processed_content = ComponentRenderer.substitute_template(content, data)
                lines.append(f"• {processed_title}: {processed_content}")

        return lines

    def _render_self_describing_component(self, component_name: str, component_data: dict) -> str:
        """Render a component using its self-describing display instructions as text."""
        display_spec = component_data.get("display", {})
        raw_data = component_data.get("data", {})

        display_type = display_spec.get("type", "")

        if display_type == "table":
            return self._render_table_as_text(raw_data, display_spec)
        elif display_type == "text":
            return self._render_text_from_spec(raw_data, display_spec)
        else:
            raise ValueError(
                f"Unknown display type '{display_type}' for component '{component_name}'"
            )

    def _render_table_as_text(self, raw_data: dict, display_spec: dict) -> str:
        """Render a table as plain text."""
        lines = []

        # Add title
        title = display_spec.get("title", "")
        if title:
            lines.append(title)
            lines.append("=" * len(title))
            lines.append("")

        columns = display_spec.get("columns", [])
        row_mapping = display_spec.get("row_mapping", {})
        transforms = display_spec.get("transforms", {})

        # Static rows with template substitution
        if "rows" in display_spec:
            for row_template in display_spec["rows"]:
                row_values = []
                for cell_template in row_template:
                    cell_value = self._substitute_template(cell_template, raw_data)
                    row_values.append(str(cell_value))
                if any(row_values):  # Skip empty rows
                    lines.append(" | ".join(row_values))

        # Dynamic rows from array data
        elif row_mapping:
            # Find the first array in raw_data
            data_array = None
            for key, value in raw_data.items():
                if isinstance(value, list) and value:
                    data_array = value
                    break

            if data_array:
                # Add header
                header_values = [
                    col.get("name", "") if isinstance(col, dict) else str(col) for col in columns
                ]
                lines.append(" | ".join(header_values))
                lines.append("-" * len(" | ".join(header_values)))

                # Add data rows
                for item in data_array:
                    row_values = []
                    for col in columns:
                        col_name = col.get("name", "") if isinstance(col, dict) else str(col)
                        # Find mapping for this column
                        mapped_value = ""
                        for field, mapping in row_mapping.items():
                            if (isinstance(mapping, str) and mapping == col_name) or (
                                isinstance(mapping, dict) and mapping.get("column") == col_name
                            ):
                                # Get value and apply transform if needed
                                value = item.get(field, "")
                                if isinstance(mapping, dict) and "transform" in mapping:
                                    transform_name = mapping["transform"]
                                    if transform_name in transforms:
                                        value = self._apply_text_transform(
                                            value, transforms[transform_name], item
                                        )
                                mapped_value = str(value)
                                break
                        row_values.append(mapped_value)
                    lines.append(" | ".join(row_values))

        lines.append("\n")
        return "\n".join(lines)

    def _render_text_from_spec(self, raw_data: dict, display_spec: dict) -> str:
        """Render text using display specification."""
        text = display_spec.get("text", "")
        return text + "\n"

    def _substitute_template(self, template: str, data: dict) -> str:
        """Simple template substitution for static rows."""
        if not isinstance(template, str):
            return template

        # Handle simple field substitutions like {total_files}
        import re

        def replacer(match):
            field_path = match.group(1)
            # Handle nested fields like category_counts.critical
            parts = field_path.split(".")
            value = data
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, 0)
                else:
                    value = 0
                    break

            # Handle formatting like {average_score:.1f}
            if ":" in field_path:
                field_name, format_spec = field_path.split(":", 1)
                parts = field_name.split(".")
                value = data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, 0)
                    else:
                        value = 0
                        break
                try:
                    return f"{value:{format_spec}}"
                except:
                    return str(value)

            return str(value)

        return re.sub(r"\{([^}]+)\}", replacer, template)

    def _apply_text_transform(self, value, transform_spec: dict, item: dict) -> str:
        """Apply transformation to a value for text output."""
        transform_type = transform_spec.get("type", "")

        if transform_type == "mapping":
            mapping = transform_spec.get("map", {})
            return mapping.get(value, str(value))
        elif transform_type == "format":
            format_str = transform_spec.get("format", "{}")
            try:
                return format_str.format(**item)
            except:
                return str(value)
        elif transform_type == "truncate_path":
            # Simple truncation for text - no width constraints
            path_str = str(value)
            if len(path_str) > 60:  # Reasonable default for text
                return path_str[:30] + "..." + path_str[-27:]
            return path_str
        elif transform_type == "conditional_format":
            conditions = transform_spec.get("conditions", [])
            for condition in conditions:
                if "if" in condition:
                    condition_str = condition["if"]
                    condition_met = False
                    if "urgency_category == 'critical'" in condition_str:
                        condition_met = item.get("urgency_category") == "critical"

                    if condition_met:
                        format_str = condition["format"]
                        try:
                            if "{total_score/1000:" in format_str:
                                score_k = item.get("total_score", 0) / 1000
                                return f"{score_k:.0f}k (CRITICAL)"
                            else:
                                return format_str.format(**item)
                        except:
                            return str(value)
                elif "default" in condition:
                    format_str = condition["default"]
                    try:
                        if "{total_score/1000:" in format_str:
                            score_k = item.get("total_score", 0) / 1000
                            return f"{score_k:.0f}k"
                        else:
                            return format_str.format(**item)
                    except:
                        return str(value)

        return str(value)
