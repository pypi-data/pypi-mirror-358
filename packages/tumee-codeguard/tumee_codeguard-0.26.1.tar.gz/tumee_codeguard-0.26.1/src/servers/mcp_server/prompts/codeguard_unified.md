🛡️ CodeGuard: Unified code validation and analysis tool

## Auto-Setup Flow (Handles Everything)

**First call (any validation command)**: CodeGuard will detect missing setup and guide you:
```
codeguard(command="validate", ...)  
→ Returns setup instructions automatically
```

**Follow the setup instructions**: 
```
codeguard(command="setup_roots", roots=["/project/path"], session_id="session1")
→ Establishes security boundaries
```

**Retry original command**:
```
codeguard(command="validate", ...)  
→ Now works perfectly
```

## Commands

**setup_roots** - Initialize security boundaries (called automatically when needed)
- `roots`: List of project directory paths  
- `session_id`: Your session identifier

**validate** - Compare original vs modified content
- `original_content`: Original file content
- `modified_content`: Modified file content
- `file_path`: Path to the file being validated

**git_validate** - Validate changes against git revision
- `file_path`: Path to file
- `modified_content`: Your proposed changes
- `revision`: Git revision to compare against (default: "HEAD")

**compare** - Compare file between git revisions  
- `file_path`: Path to file
- `from_revision`: Starting revision
- `to_revision`: Ending revision (default: "HEAD")

**scan** - Find guard tags in directory
- `directory`: Directory path to scan
- `target`: Target to scan for (default: "AI")

## Usage Examples

```python
# Basic validation
codeguard(command="validate", 
         original_content="def old_func():\n    pass", 
         modified_content="def new_func():\n    return True",
         file_path="src/example.py")

# Git validation  
codeguard(command="git_validate",
         file_path="src/app.py", 
         modified_content="updated content here")

# Directory scan
codeguard(command="scan", directory="/project/src")
```

## Key Benefits

✅ **Single tool** - No need to discover multiple tools
✅ **Auto-guidance** - Missing setup? Get exact instructions automatically  
✅ **Smart errors** - Clear next steps, never get stuck
✅ **Consistent API** - Same parameters across all commands