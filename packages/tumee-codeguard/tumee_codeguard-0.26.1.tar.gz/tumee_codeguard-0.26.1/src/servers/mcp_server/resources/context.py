"""
Context resource functions for MCP server.

This module provides MCP resource endpoints for accessing discovered context files.
"""

import base64
from pathlib import Path
from typing import Dict


def get_all_context(context_data: Dict) -> dict:
    """Return all discovered context files."""
    return context_data


def get_root_context(root_id: str, context_data: Dict) -> dict:
    """Return context files for specific root."""
    return context_data.get("roots", {}).get(root_id, {})


def get_context_file_content(file_path_b64: str) -> dict:
    """Return content of specific context file."""
    try:
        # Decode base64 file path
        file_path = base64.urlsafe_b64decode(file_path_b64.encode()).decode()

        # Check if file exists and is accessible
        path_obj = Path(file_path)
        if not path_obj.exists() or not path_obj.is_file():
            return {"error": "File not found or not accessible", "path": file_path}

        # Read file content
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "path": file_path,
                "content": content,
                "size": len(content),
                "encoding": "utf-8",
            }
        except UnicodeDecodeError:
            # Try binary read for non-text files
            with open(path_obj, "rb") as f:
                content = f.read()

            return {
                "path": file_path,
                "content": base64.b64encode(content).decode(),
                "size": len(content),
                "encoding": "base64",
            }

    except Exception as e:
        return {"error": str(e), "path_b64": file_path_b64}
