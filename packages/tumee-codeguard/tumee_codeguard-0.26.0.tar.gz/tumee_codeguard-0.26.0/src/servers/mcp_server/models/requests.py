"""
Pydantic models for MCP server request validation.

This module defines the request models used by various MCP tools
for input validation and documentation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    """Request model for validation endpoint."""

    original_content: str = Field(..., description="Original file content")
    modified_content: str = Field(..., description="Modified file content")
    file_path: str = Field(..., description="Path to the file")
    target: str = Field("AI", description="Target audience (AI, HU, ALL)")
    normalize_whitespace: bool = Field(True, description="Normalize whitespace in comparisons")
    normalize_line_endings: bool = Field(True, description="Normalize line endings in comparisons")
    ignore_blank_lines: bool = Field(True, description="Ignore blank lines in comparisons")
    ignore_indentation: bool = Field(False, description="Ignore indentation changes in comparisons")


class GitValidationRequest(BaseModel):
    """Request model for git validation endpoint."""

    file_path: str = Field(..., description="Path to the file")
    modified_content: str = Field(..., description="Modified file content")
    revision: str = Field("HEAD", description="Git revision to compare against")
    repo_path: Optional[str] = Field(None, description="Path to git repository")
    target: str = Field("AI", description="Target audience (AI, HU, ALL)")
    normalize_whitespace: bool = Field(True, description="Normalize whitespace in comparisons")
    normalize_line_endings: bool = Field(True, description="Normalize line endings in comparisons")
    ignore_blank_lines: bool = Field(True, description="Ignore blank lines in comparisons")
    ignore_indentation: bool = Field(False, description="Ignore indentation changes in comparisons")


class RootsCapabilityRequest(BaseModel):
    """Request model for MCP roots capability."""

    roots: List[str] = Field(..., description="List of allowed root directories")


class RevisionCompareRequest(BaseModel):
    """Request model for revision comparison endpoint."""

    file_path: str = Field(..., description="Path to the file")
    from_revision: str = Field(..., description="Base revision for comparison")
    to_revision: str = Field("HEAD", description="Target revision for comparison")
    repo_path: Optional[str] = Field(None, description="Path to git repository")
    target: str = Field("AI", description="Target audience (AI, HU, ALL)")
    normalize_whitespace: bool = Field(True, description="Normalize whitespace in comparisons")
    normalize_line_endings: bool = Field(True, description="Normalize line endings in comparisons")
    ignore_blank_lines: bool = Field(True, description="Ignore blank lines in comparisons")
    ignore_indentation: bool = Field(False, description="Ignore indentation changes in comparisons")


class ScanRequest(BaseModel):
    """Request model for scan endpoint."""

    directory: str = Field(..., description="Directory to scan")
    include_pattern: Optional[str] = Field(None, description="Glob pattern to include files")
    exclude_pattern: Optional[str] = Field(None, description="Glob pattern to exclude files")
    target: str = Field("AI", description="Target audience (AI, HU, ALL)")
    normalize_whitespace: bool = Field(True, description="Normalize whitespace in comparisons")
    normalize_line_endings: bool = Field(True, description="Normalize line endings in comparisons")
    ignore_blank_lines: bool = Field(True, description="Ignore blank lines in comparisons")
    ignore_indentation: bool = Field(False, description="Ignore indentation changes in comparisons")
