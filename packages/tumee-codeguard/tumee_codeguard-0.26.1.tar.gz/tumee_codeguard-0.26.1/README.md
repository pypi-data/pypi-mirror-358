# TuMee CodeGuard

A powerful file change detection tool that identifies, tracks, and validates code modifications with a focus on respecting designated "guarded" regions across multiple programming languages.

**Package Name:** `tumee-codeguard`  
**Command:** `codeguard`

> **✨ CodeGuard 2.0** features a modern Typer-based CLI with consistent argument patterns, Rich formatting, and logical command grouping for improved usability.

## Installation

### Prerequisites

- Python 3.10 or higher
- Git (for version control integration)

### Setup

#### On macOS/Linux

```bash
# Make the install script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

#### On Windows

```cmd
# Run the installation script
install.bat
```

## Usage

### Running CodeGuard

#### On macOS/Linux

```bash
# Run CodeGuard
./run_codeguard.sh [command] [options]

# For example, to get help
./run_codeguard.sh --help

# To get effective permissions for a file
./run_codeguard.sh acl /path/to/file
```

#### On Windows

```cmd
# Run CodeGuard
run_codeguard.bat [command] [options]

# For example, to get help
run_codeguard.bat --help

# To get effective permissions for a file
run_codeguard.bat acl C:\path\to\file
```

## Commands

CodeGuard 2.0 features a modern, user-friendly CLI with consistent argument patterns and logical command grouping.

### Core Commands
- `verify` - Compare files/directories for guard violations (unified command)
- `scan` - Scan files/directories for violations  
- `validate` - Validate guard compliance with optional fixes
- `show` - Display file with guard permission visualization
- `acl` - Get effective permissions for files/directories

### Grouped Commands  
- `context up/down` - Context file discovery (upward/downward traversal)
- `guards create/list/validate/directories` - Directory guard management

### Integration Commands
- `mcp` - Start MCP server for IDE integration
- `ide` - Start IDE attachment mode (replaces `--worker-mode`)
- `hook` - Manage git pre-commit hooks
- `themes` - Manage visualization themes

### Key Improvements
- **Consistent patterns**: All commands use similar argument structures
- **Rich formatting**: Beautiful help with proper sections and highlighting  
- **Type validation**: Automatic path validation and type conversion
- **Recursive support**: Most commands support `--recursive` for directories

## Examples

### Code Validation (Unified Commands)

```bash
# Compare two files directly (simplified)
./run_codeguard.sh verify ./original.py ./modified.py

# Compare file to current disk version
./run_codeguard.sh verify ./modified.py

# Compare to git revision
./run_codeguard.sh verify ./src/main.py --git-revision HEAD~1

# Scan directory for violations
./run_codeguard.sh scan ./src --recursive --include "*.py"

# Validate and fix guard compliance
./run_codeguard.sh validate ./src --recursive --fix
```

### Directory Guard Management

```bash
# Create guard rules
./run_codeguard.sh guards create --rule "*.py:AI-RO" --description "*.py:Python read-only"

# List guard rules
./run_codeguard.sh guards list --recursive --format json

# Validate guard files
./run_codeguard.sh guards validate --recursive --fix

# List guarded directories
./run_codeguard.sh guards directories --format text
```

### Access Control Information

```bash
# Get effective permissions for a file
./run_codeguard.sh acl ./src/main.py --verbose --format json

# Check directory permissions recursively
./run_codeguard.sh acl ./src --recursive
```

### File Visualization

```bash
# Display file with guard permissions
./run_codeguard.sh show ./src/main.py

# Use specific theme and syntax highlighting
./run_codeguard.sh show ./src/main.py --theme dark --syntax
```

### Context Discovery

```bash
# Find context files walking up
./run_codeguard.sh context up --priority high

# Find context files walking down
./run_codeguard.sh context down --depth-first --format json
```

### Integration

```bash
# Start MCP server for IDE integration
./run_codeguard.sh mcp --port 8080

# Start IDE attachment mode
./run_codeguard.sh ide --min-version 1.2.0

# Install git pre-commit hook
./run_codeguard.sh hook --install
```

## Guard Annotation System

CodeGuard supports a standardized guard notation that works across programming languages:

```
@GUARD:WHO-PERMISSION
```

Where:
- `@GUARD`: The prefix that identifies this as a guard directive
- `WHO`: Indicates who the rule applies to (`AI` for AI systems, `HU` for human developers, `ALL` for both)
- `PERMISSION`: Specifies the permission level (`RO` for read-only, `ED` for editable with reason, `FX` for fixed/unchangeable)

### Examples

```python
# @GUARD:AI-RO This is an AI read-only section
def sensitive_function():
    pass

# @GUARD:HU-ED Humans can edit this section with good reason
def editable_function():
    pass

"""
@GUARD:ALL-FX
This section is fixed for everyone
"""
```

## Directory-Level Guard System

CodeGuard supports directory-level guard annotations through `.ai-attributes` files:

```
# All files in this directory are AI read-only
* @GUARD:AI-RO

# All Python files in this directory and subdirectories are fixed
**/*.py @GUARD:ALL-FX

# Test files in the tests directory can be edited
tests/* @GUARD:ALL-ED
```
