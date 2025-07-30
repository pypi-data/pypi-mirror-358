"""
Document management for IDE Server.

This module handles document state management, content processing,
and delta update operations for the IDE integration.
"""

from typing import Any, Dict, List, Optional, Tuple

from ...core.infrastructure.processor import process_document
from .models import TextChange, WorkerDocument


class DocumentManager:
    """
    Manages document state and content processing.

    This class handles document lifecycle, content updates via deltas,
    and processing documents for guard tags and line permissions.
    """

    def __init__(self):
        """Initialize the document manager"""
        self.document: Optional[WorkerDocument] = None

    def lines_from_content(self, content: str) -> List[str]:
        """Split content into lines, preserving line endings"""
        if not content:
            return []
        return content.splitlines(keepends=False)

    def apply_text_changes(self, content: str, changes: List[TextChange]) -> str:
        """Apply text changes to content"""
        lines = content.splitlines(keepends=True)

        # Sort changes by position (start from end to avoid offset issues)
        sorted_changes = sorted(changes, key=lambda c: (c.startLine, c.startChar), reverse=True)

        for change in sorted_changes:
            # Convert to 0-based indexing
            start_line = change.startLine
            end_line = change.endLine
            start_char = change.startChar
            end_char = change.endChar

            if start_line >= len(lines):
                continue

            if start_line == end_line:
                # Single line change
                line = lines[start_line].rstrip("\n\r")
                new_line = line[:start_char] + change.newText + line[end_char:]
                lines[start_line] = (
                    new_line + "\n" if lines[start_line].endswith("\n") else new_line
                )
            else:
                # Multi-line change
                start_line_content = lines[start_line][:start_char]
                end_line_content = lines[end_line][end_char:] if end_line < len(lines) else ""

                # Replace the range with new content
                new_content = start_line_content + change.newText + end_line_content
                new_lines = new_content.splitlines(keepends=True)

                # Replace the lines
                lines[start_line : end_line + 1] = new_lines

        return "".join(lines)

    async def process_document_content(
        self, content: str, language_id: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process document content and return guard tags and line permissions"""
        try:
            # Process the document
            guard_tags_list, line_permissions_dict = await process_document(content, language_id)

            # Convert guard tags to serializable format
            guard_tags = []
            for tag in guard_tags_list:
                guard_dict = {
                    "lineNumber": getattr(tag, "lineNumber", 0),
                    "scope": getattr(tag, "scope", "line"),
                }

                # Add optional fields if present
                for field in [
                    "identifier",
                    "lineCount",
                    "addScopes",
                    "removeScopes",
                    "scopeStart",
                    "scopeEnd",
                    "aiPermission",
                    "humanPermission",
                    "aiIsContext",
                    "humanIsContext",
                ]:
                    if hasattr(tag, field):
                        value = getattr(tag, field)
                        if value is not None:
                            guard_dict[field] = value

                guard_tags.append(guard_dict)

            # Convert line permissions to serializable format
            line_permissions = []
            for line_num, perm in line_permissions_dict.items():
                line_perm = {
                    "line": line_num,
                    "permissions": getattr(perm, "permissions", {}),
                    "isContext": getattr(perm, "isContext", {}),
                }

                # Add optional fields
                for field in ["identifier", "isTrailingWhitespace"]:
                    if hasattr(perm, field):
                        value = getattr(perm, field)
                        if value is not None:
                            line_perm[field] = value

                line_permissions.append(line_perm)

            return guard_tags, line_permissions

        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")

    async def set_document(
        self, fileName: str, languageId: str, content: str, version: int
    ) -> WorkerDocument:
        """Set the current document and process it"""
        lines = self.lines_from_content(content)
        guard_tags, line_permissions = await self.process_document_content(content, languageId)

        self.document = WorkerDocument(
            fileName=fileName,
            languageId=languageId,
            content=content,
            version=version,
            lines=lines,
            guardTags=guard_tags,
            linePermissions=line_permissions,
        )

        return self.document

    async def apply_delta_update(
        self, changes: List[Dict[str, Any]], version: int
    ) -> Optional[WorkerDocument]:
        """Apply delta updates to the current document"""
        if not self.document:
            raise Exception("No document set")

        # Convert changes to TextChange objects
        text_changes = []
        for change in changes:
            text_changes.append(
                TextChange(
                    startLine=change["startLine"],
                    startChar=change["startChar"],
                    endLine=change["endLine"],
                    endChar=change["endChar"],
                    newText=change["newText"],
                )
            )

        # Apply changes
        new_content = self.apply_text_changes(self.document.content, text_changes)

        # Update document
        return await self.set_document(
            self.document.fileName, self.document.languageId, new_content, version
        )

    def get_document(self) -> Optional[WorkerDocument]:
        """Get the current document"""
        return self.document
