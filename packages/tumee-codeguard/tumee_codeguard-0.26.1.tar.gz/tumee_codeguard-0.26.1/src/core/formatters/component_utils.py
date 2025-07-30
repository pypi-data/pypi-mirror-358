"""
Shared utilities for component rendering across all formatters.
"""

import re
from typing import Any, Dict, List, Union


class ComponentRenderer:
    """Shared component rendering utilities for all formatters."""

    @staticmethod
    def calculate_column_widths(columns: List[Union[str, Dict]], min_width: int = 10) -> List[int]:
        """Calculate column widths based on column specifications."""
        col_widths = []
        for col in columns:
            if isinstance(col, dict):
                # Use specified width or calculate from name
                specified_width = col.get("width", 0)
                name_width = len(col.get("name", "Column"))
                width = max(specified_width, name_width, min_width)
                col_widths.append(width)
            else:
                col_widths.append(max(len(str(col)), min_width))
        return col_widths

    @staticmethod
    def substitute_template(template: str, data: dict) -> str:
        """
        Template substitution for component data.

        Handles:
        - Simple fields: {total_files}
        - Nested fields: {category_counts.critical}
        - Formatting: {average_score:.1f}
        - Expressions: {max(1, total_files * 0.05):.0f}
        """
        if not isinstance(template, str):
            return str(template)

        def replacer(match):
            field_path = match.group(1)

            try:
                # Handle expressions like max(1, total_files * 0.05):.0f
                if "max(" in field_path or "min(" in field_path:
                    # Split on : for format spec
                    if ":" in field_path:
                        expr, format_spec = field_path.rsplit(":", 1)
                        # Evaluate expression with data context and safe builtins
                        safe_builtins = {"max": max, "min": min, "abs": abs, "round": round}
                        result = eval(expr, {"__builtins__": safe_builtins}, data)
                        return f"{result:{format_spec}}"
                    else:
                        safe_builtins = {"max": max, "min": min, "abs": abs, "round": round}
                        result = eval(field_path, {"__builtins__": safe_builtins}, data)
                        return str(result)

                # Handle formatted fields like {average_score:.1f}
                if ":" in field_path:
                    field_name, format_spec = field_path.split(":", 1)
                    value = ComponentRenderer._get_nested_value(data, field_name)
                    try:
                        return f"{value:{format_spec}}"
                    except (ValueError, TypeError):
                        return str(value)

                # Handle nested fields like {category_counts.critical}
                value = ComponentRenderer._get_nested_value(data, field_path)
                return str(value)

            except Exception:
                # Return original placeholder if can't process
                return f"{{{field_path}}}"

        return re.sub(r"\{([^}]+)\}", replacer, template)

    @staticmethod
    def _get_nested_value(data: dict, field_path: str) -> Any:
        """Get nested value from data using dot notation."""
        parts = field_path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, 0)
            else:
                return 0
        return value

    @staticmethod
    def get_column_names(columns: List[Union[str, Dict]]) -> List[str]:
        """Extract column names from column specifications."""
        names = []
        for col in columns:
            if isinstance(col, dict):
                names.append(col.get("name", "Column"))
            else:
                names.append(str(col))
        return names

    @staticmethod
    def process_table_rows(display_spec: dict, data: dict) -> List[List[str]]:
        """Process table rows with template substitution or dynamic mapping."""
        rows = display_spec.get("rows", [])
        row_mapping = display_spec.get("row_mapping", {})
        columns = display_spec.get("columns", [])

        if rows:
            # Static rows with template substitution
            processed_rows = []
            for row in rows:
                processed_row = []
                for cell in row:
                    if cell is None or cell == "":
                        processed_row.append("")
                    else:
                        processed_cell = ComponentRenderer.substitute_template(str(cell), data)
                        processed_row.append(processed_cell)
                processed_rows.append(processed_row)
            return processed_rows

        elif row_mapping:
            # Dynamic rows from array data (like file lists)
            processed_rows = []

            # Find the first array in data
            data_array = None
            for key, value in data.items():
                if isinstance(value, list) and value:
                    data_array = value
                    break

            if data_array:
                for item in data_array:
                    row = []
                    for col in columns:
                        col_name = col.get("name", "") if isinstance(col, dict) else str(col)

                        # Find mapping for this column
                        mapped_value = ""
                        for field, mapping in row_mapping.items():
                            if (isinstance(mapping, str) and mapping == col_name) or (
                                isinstance(mapping, dict) and mapping.get("column") == col_name
                            ):
                                # Get value from item
                                value = item.get(field, "")
                                # TODO: Apply transforms if needed
                                mapped_value = str(value)
                                break
                        row.append(mapped_value)
                    processed_rows.append(row)

            return processed_rows

        return []

    @staticmethod
    def is_component_format(item: Any) -> bool:
        """Check if item follows component format."""
        return (
            isinstance(item, dict) and "component" in item and "data" in item and "display" in item
        )

    @staticmethod
    def extract_component_info(item: dict) -> tuple[str, dict, dict]:
        """Extract component name, data, and display spec from component item."""
        component_name = item.get("component", "Component")
        data = item.get("data", {})
        display = item.get("display", {})
        return component_name, data, display
