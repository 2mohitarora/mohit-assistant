# Claude Agent SDK Hooks: Comprehensive Implementation Guide

## Table of Contents
1. [Introduction](#introduction)
2. [What Are Hooks?](#what-are-hooks)
3. [Hook Types and Events](#hook-types-and-events)
4. [Implementation Patterns](#implementation-patterns)
5. [Configuration Guide](#configuration-guide)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Real-World Use Cases](#real-world-use-cases)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Hooks in the Claude Agent SDK provide deterministic control over agent behavior by executing custom code at specific points in the agent's workflow. Unlike relying on the LLM to initiate actions, hooks ensure certain operations consistently execute at predefined lifecycle events.

**Key Benefits:**
- Automated security validation and permission controls
- Consistent code quality enforcement (formatting, linting, testing)
- Audit trails and logging capabilities
- Custom workflow integrations
- User notification systems

---

## What Are Hooks?

Hooks are functions (Python) or commands (shell scripts) that the Claude Code application invokes at specific points in the agent loop. They enable:

1. **Deterministic Processing**: Actions execute reliably without depending on LLM decisions
2. **Automated Feedback**: Provide context and guidance to Claude based on tool results
3. **Permission Management**: Block, allow, or request user approval for tool execution
4. **Context Injection**: Add information at key workflow moments

**Important Distinction:**
- Hooks are executed by the Claude Code application, not by Claude itself
- They run with your environment's credentials and permissions
- They can modify agent behavior and tool execution

---

## Hook Types and Events

The Claude Agent SDK supports nine distinct hook events that fire at different stages of the agent lifecycle:

### 1. PreToolUse
**Timing**: After Claude creates tool parameters but before processing the tool call

**Purpose**: Validate, block, or modify tool execution before it occurs

**Capabilities**:
- Block dangerous operations
- Request user permission
- Modify tool parameters
- Bypass permission system

**Output Structure**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow" | "deny" | "ask",
    "permissionDecisionReason": "Explanation for decision",
    "updatedInput": {}
  }
}
```

### 2. PostToolUse
**Timing**: Immediately after a tool completes successfully

**Purpose**: Provide feedback to Claude or take automated actions based on tool results

**Capabilities**:
- Add context for Claude's next action
- Block Claude from continuing
- Log tool execution
- Trigger automated workflows (formatting, testing)

**Output Structure**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "decision": "block",
    "reason": "Explanation",
    "additionalContext": "Additional information for Claude"
  }
}
```

### 3. UserPromptSubmit
**Timing**: When user submits a prompt, before Claude processes it

**Purpose**: Validate, enhance, or block user prompts

**Capabilities**:
- Block inappropriate prompts
- Add contextual information
- Log user interactions

**Output Structure**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "decision": "block",
    "reason": "Explanation",
    "additionalContext": "Context to add to prompt"
  }
}
```

### 4. Stop
**Timing**: When the main Claude Code agent finishes responding

**Purpose**: Execute cleanup actions or notifications after agent completion

**Capabilities**:
- Send completion notifications
- Log session summaries
- Block agent from stopping (force continuation)
- Trigger post-completion workflows

**Output Structure**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "block",
    "reason": "Must continue because..."
  }
}
```

### 5. SubagentStop
**Timing**: When a subagent (Task tool call) completes

**Purpose**: Handle subagent completion events

**Capabilities**: Same as Stop event, but for subagent tasks

### 6. Notification
**Timing**: When Claude Code sends notifications

**Purpose**: Customize or extend notification behavior

**Common Uses**:
- Desktop notifications
- Sound alerts
- External integrations (Slack, email)

### 7. SessionStart
**Timing**: When a session begins or resumes

**Purpose**: Initialize session-specific configurations

**Capabilities**:
- Add session context
- Set environment variables via `CLAUDE_ENV_FILE`
- Initialize logging systems

### 8. SessionEnd
**Timing**: When a session terminates

**Purpose**: Cleanup and finalization tasks

### 9. PreCompact
**Timing**: Before context compaction operations

**Purpose**: Prepare for or prevent context compaction

---

## Implementation Patterns

### Python SDK Hooks

Python hooks are async functions that receive structured input and return control dictionaries.

**Function Signature**:
```python
async def hook_function(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Hook function that executes at specific lifecycle events.

    Args:
        input_data: Dictionary containing tool and session information
        tool_use_id: Unique identifier for the tool use
        context: Hook context with additional metadata

    Returns:
        Dictionary with hookSpecificOutput containing decisions
    """
    # Hook logic here
    return {}
```

**Input Data Schema**:
```python
{
    "session_id": str,
    "transcript_path": str,
    "cwd": str,
    "permission_mode": "default" | "plan" | "acceptEdits" | "bypassPermissions",
    "hook_event_name": str,
    "tool_name": str,  # For PreToolUse and PostToolUse
    "tool_input": dict,  # For PreToolUse and PostToolUse
    "tool_response": dict  # For PostToolUse only
}
```

### Command-Based Hooks (Shell Scripts)

Command hooks execute as shell scripts with JSON input via stdin.

**Configuration Structure**:
```json
{
  "type": "command",
  "command": "bash script.sh",
  "timeout": 60
}
```

**Exit Code Meanings**:
- **0**: Success; stdout shown to user (or added as context for certain events)
- **2**: Blocking error; stderr fed back to Claude for processing
- **Other codes**: Non-blocking error; stderr shown to user, execution continues

### Prompt-Based Hooks (LLM Evaluation)

Available for `Stop` and `SubagentStop` events, these use LLM evaluation for intelligent decisions.

**Configuration**:
```json
{
  "type": "prompt",
  "prompt": "Evaluate if the task is complete: $ARGUMENTS",
  "timeout": 30
}
```

---

## Configuration Guide

### Configuration File Locations

Hooks are configured in settings files with the following precedence:

1. **Project-specific**: `.claude/settings.json` (highest priority)
2. **Local overrides**: `.claude/settings.local.json`
3. **User-wide**: `~/.claude/settings.json` (lowest priority)

### Python SDK Configuration

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher

# Define hook function
async def my_hook(input_data, tool_use_id, context):
    # Hook logic
    return {}

# Configure options with hooks
options = ClaudeAgentOptions(
    allowed_tools=["Bash", "Write", "Edit"],
    hooks={
        "PreToolUse": [
            HookMatcher(
                matcher="Bash",  # Tool name or regex pattern
                hooks=[my_hook]
            ),
        ],
        "PostToolUse": [
            HookMatcher(
                matcher="*",  # Match all tools
                hooks=[another_hook]
            ),
        ]
    }
)

# Create client with options
client = ClaudeSDKClient(options=options)
```

### Shell Command Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/validate_bash.py",
            "timeout": 60
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write $CLAUDE_PROJECT_DIR"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Funk.aiff"
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns

Matchers determine which tools trigger hooks:

- **Exact match**: `"Bash"` matches only the Bash tool
- **Regex patterns**: `"Edit|Write"` matches Edit or Write tools
- **Wildcard**: `"*"` or `""` matches all tools
- **Pattern matching**: `"Notebook.*"` matches tools starting with "Notebook"
- **MCP tools**: `"mcp__memory__.*"` matches all tools from memory MCP server

**Examples**:
```python
# Match specific tool
HookMatcher(matcher="Bash", hooks=[validate_bash])

# Match multiple tools with regex
HookMatcher(matcher="Edit|Write", hooks=[format_files])

# Match all tools
HookMatcher(matcher="*", hooks=[log_all_tools])

# Match MCP tools
HookMatcher(matcher="mcp__.*__write.*", hooks=[validate_writes])
```

---

## Code Examples

### Example 1: Block Dangerous Bash Commands

**Purpose**: Prevent execution of dangerous shell commands

```python
async def block_dangerous_bash(input_data, tool_use_id, context):
    """Block dangerous bash commands before execution."""
    tool_name = input_data.get("tool_name")

    # Only check Bash tool
    if tool_name != "Bash":
        return {}

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Define dangerous patterns
    dangerous_patterns = [
        "rm -rf /",
        "rm -rf ~",
        "rm -rf *",
        "mkfs",
        "> /dev/sda",
        "dd if=/dev/zero",
        ":(){ :|:& };:",  # Fork bomb
    ]

    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Command blocked for safety: contains dangerous pattern '{pattern}'. "
                        f"This command could cause system damage or data loss."
                    ),
                }
            }

    # Allow safe commands
    return {}

# Configuration
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_bash]),
        ],
    }
)
```

### Example 2: Validate File Paths

**Purpose**: Prevent modifications to sensitive files and directories

```python
async def validate_file_paths(input_data, tool_use_id, context):
    """Prevent modifications to sensitive files."""
    tool_name = input_data.get("tool_name")

    # Check Write and Edit tools
    if tool_name not in ["Write", "Edit"]:
        return {}

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Define protected paths
    protected_paths = [
        ".env",
        ".git/",
        "node_modules/",
        ".aws/credentials",
        ".ssh/",
        "id_rsa",
    ]

    # Check for path traversal
    if ".." in file_path:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Path traversal detected. File paths cannot contain '..' for security."
                ),
            }
        }

    # Check protected paths
    for protected in protected_paths:
        if protected in file_path:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": (
                        f"Attempting to modify protected path: {file_path}. "
                        f"This may contain sensitive information. Confirm to proceed."
                    ),
                }
            }

    return {}
```

### Example 3: Auto-Format Code After Edits

**Purpose**: Automatically format code files after editing

```python
import subprocess
import os

async def auto_format_code(input_data, tool_use_id, context):
    """Automatically format code files after editing."""
    tool_name = input_data.get("tool_name")

    # Only run on Write and Edit
    if tool_name not in ["Write", "Edit"]:
        return {}

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Skip if no file path
    if not file_path or not os.path.exists(file_path):
        return {}

    # Determine formatter based on file extension
    formatters = {
        ".py": ["black", file_path],
        ".js": ["prettier", "--write", file_path],
        ".ts": ["prettier", "--write", file_path],
        ".tsx": ["prettier", "--write", file_path],
        ".go": ["gofmt", "-w", file_path],
        ".rs": ["rustfmt", file_path],
    }

    # Get file extension
    _, ext = os.path.splitext(file_path)

    # Run formatter if applicable
    if ext in formatters:
        try:
            result = subprocess.run(
                formatters[ext],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"File automatically formatted using {formatters[ext][0]}"
                    }
                }
            else:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": (
                            f"Warning: Formatter {formatters[ext][0]} reported issues: "
                            f"{result.stderr}"
                        )
                    }
                }
        except subprocess.TimeoutExpired:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "Warning: Formatter timed out"
                }
            }
        except FileNotFoundError:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"Warning: Formatter {formatters[ext][0]} not found. "
                        f"Install it to enable automatic formatting."
                    )
                }
            }

    return {}

# Configuration
options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [
            HookMatcher(matcher="Write|Edit", hooks=[auto_format_code]),
        ],
    }
)
```

### Example 4: Run Tests After Code Changes

**Purpose**: Enforce test-driven development by running tests after code changes

```python
import subprocess
import os

async def run_tests_after_edit(input_data, tool_use_id, context):
    """Run test suite after code modifications."""
    tool_name = input_data.get("tool_name")

    if tool_name not in ["Write", "Edit"]:
        return {}

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only run tests for source code files
    source_extensions = [".py", ".js", ".ts", ".go", ".rs"]
    if not any(file_path.endswith(ext) for ext in source_extensions):
        return {}

    # Skip test files themselves
    if "test" in file_path.lower() or "spec" in file_path.lower():
        return {}

    cwd = input_data.get("cwd", ".")

    # Determine test command based on project
    test_commands = []
    if os.path.exists(os.path.join(cwd, "pytest.ini")) or os.path.exists(os.path.join(cwd, "setup.py")):
        test_commands = ["pytest", "-v"]
    elif os.path.exists(os.path.join(cwd, "package.json")):
        test_commands = ["npm", "test"]
    elif os.path.exists(os.path.join(cwd, "go.mod")):
        test_commands = ["go", "test", "./..."]

    if not test_commands:
        return {}

    try:
        result = subprocess.run(
            test_commands,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "All tests passed successfully."
                }
            }
        else:
            # Block and provide test output to Claude
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "decision": "block",
                    "reason": (
                        "Tests failed. You must fix the failing tests before proceeding.\n\n"
                        f"Test output:\n{result.stdout}\n\nErrors:\n{result.stderr}"
                    )
                }
            }
    except subprocess.TimeoutExpired:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Warning: Test suite timed out after 60 seconds"
            }
        }
    except Exception as e:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Warning: Could not run tests: {str(e)}"
            }
        }
```

### Example 5: Log All Agent Actions

**Purpose**: Maintain audit trail of all agent actions

```python
import json
import os
from datetime import datetime

async def log_agent_actions(input_data, tool_use_id, context):
    """Log all tool executions to a file."""
    session_id = input_data.get("session_id", "unknown")
    hook_event = input_data.get("hook_event_name")
    tool_name = input_data.get("tool_name", "N/A")

    # Create logs directory
    log_dir = ".claude/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create log file path
    log_file = os.path.join(log_dir, f"session_{session_id}.log")

    # Prepare log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook_event": hook_event,
        "tool_name": tool_name,
        "tool_use_id": tool_use_id,
    }

    # Add tool input and response if available
    if "tool_input" in input_data:
        log_entry["tool_input"] = input_data["tool_input"]
    if "tool_response" in input_data:
        log_entry["tool_response"] = input_data["tool_response"]

    # Append to log file
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"Warning: Could not write to log: {e}")

    return {}

# Configuration to log all PreToolUse and PostToolUse events
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="*", hooks=[log_agent_actions]),
        ],
        "PostToolUse": [
            HookMatcher(matcher="*", hooks=[log_agent_actions]),
        ],
    }
)
```

### Example 6: Inject Context at Session Start

**Purpose**: Add project-specific context when session begins

```python
import os

async def inject_session_context(input_data, tool_use_id, context):
    """Add project context at session start."""
    cwd = input_data.get("cwd", ".")

    # Build context from project files
    context_parts = []

    # Check for README
    readme_path = os.path.join(cwd, "README.md")
    if os.path.exists(readme_path):
        context_parts.append("Project documentation is available in README.md")

    # Check for coding standards
    standards_path = os.path.join(cwd, ".claude/coding-standards.md")
    if os.path.exists(standards_path):
        with open(standards_path, "r") as f:
            standards = f.read()
        context_parts.append(f"Coding standards:\n{standards}")

    # Check for project type
    if os.path.exists(os.path.join(cwd, "package.json")):
        context_parts.append("This is a Node.js project. Use npm/bun for package management.")
    elif os.path.exists(os.path.join(cwd, "requirements.txt")):
        context_parts.append("This is a Python project. Use uv for package management.")

    additional_context = "\n\n".join(context_parts)

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context
        }
    }

# Configuration
options = ClaudeAgentOptions(
    hooks={
        "SessionStart": [
            HookMatcher(matcher="", hooks=[inject_session_context]),
        ],
    }
)
```

### Example 7: Shell Command Hook for Notifications

**Shell script**: `.claude/hooks/notify.sh`
```bash
#!/bin/bash

# Read JSON from stdin
input=$(cat)

# Extract event name
event=$(echo "$input" | jq -r '.hook_event_name')

# Send notification based on event
case "$event" in
    "Stop")
        osascript -e 'display notification "Claude has finished" with title "Claude Code"'
        afplay /System/Library/Sounds/Glass.aiff
        ;;
    "Notification")
        osascript -e 'display notification "Claude needs your input" with title "Claude Code"'
        afplay /System/Library/Sounds/Purr.aiff
        ;;
esac

exit 0
```

**Configuration**: `.claude/settings.json`
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/notify.sh"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/notify.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Best Practices

### 1. Security First

**Always validate and sanitize inputs:**
```python
async def safe_hook(input_data, tool_use_id, context):
    """Example of safe input handling."""
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Validate path is absolute
    if not os.path.isabs(file_path):
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "File path must be absolute"
        }}

    # Check for path traversal
    if ".." in file_path:
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Path traversal detected"
        }}

    # Validate file is within project
    cwd = input_data.get("cwd", "")
    if not file_path.startswith(cwd):
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "File is outside project directory"
        }}

    return {}
```

**Quote shell variables properly:**
```bash
# BAD - vulnerable to injection
command="ls $user_input"

# GOOD - properly quoted
command="ls \"$user_input\""
```

**Skip sensitive files:**
```python
SENSITIVE_FILES = [
    ".env", ".env.local", ".env.production",
    ".aws/credentials",
    ".ssh/id_rsa", ".ssh/id_ed25519",
    ".git/config",
    "secrets.json",
]

def is_sensitive_file(file_path: str) -> bool:
    """Check if file path contains sensitive files."""
    return any(sensitive in file_path for sensitive in SENSITIVE_FILES)
```

### 2. Use Appropriate Hook Events

**Block-at-Submit Strategy** (Recommended):
- Use `PreToolUse` for validation before execution
- Use `PostToolUse` for quality checks after completion
- Avoid blocking `Write` or `Edit` directly; let Claude finish then validate

```python
# RECOMMENDED: Validate after edit is complete
async def check_after_edit(input_data, tool_use_id, context):
    """Run validation after file is written."""
    # Let the edit complete first
    # Then run tests/linters
    # Block if quality checks fail
    pass

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [  # Not PreToolUse
            HookMatcher(matcher="Edit|Write", hooks=[check_after_edit]),
        ],
    }
)
```

**Event Selection Guide**:
- **PreToolUse**: Security validation, permission checks, parameter modification
- **PostToolUse**: Quality enforcement, formatting, testing, logging
- **Stop**: Final validations, notifications, cleanup
- **SessionStart**: Context injection, initialization

### 3. Handle Errors Gracefully

**Don't fail the entire workflow for non-critical hooks:**
```python
async def non_critical_hook(input_data, tool_use_id, context):
    """Hook that shouldn't stop workflow on failure."""
    try:
        # Hook logic here
        result = perform_operation()
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Operation succeeded: {result}"
            }
        }
    except Exception as e:
        # Log error but don't block
        print(f"Warning: Hook failed: {e}", file=sys.stderr)
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Warning: Operation failed but continuing: {e}"
            }
        }
```

**Use appropriate exit codes in shell hooks:**
```bash
#!/bin/bash

# Exit 0 for success
# Exit 2 for blocking error (feeds back to Claude)
# Exit other for non-blocking error (shows to user)

if ! run_tests; then
    echo "Tests failed" >&2
    exit 2  # Block and give feedback to Claude
fi

exit 0
```

### 4. Optimize Performance

**Use timeouts appropriately:**
```python
# For quick validations
{"type": "command", "command": "validate.sh", "timeout": 10}

# For test suites
{"type": "command", "command": "npm test", "timeout": 120}

# For formatting
{"type": "command", "command": "prettier --write .", "timeout": 30}
```

**Run hooks in parallel when possible:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "lint.sh"},
          {"type": "command", "command": "format.sh"}
        ]
      }
    ]
  }
}
```
*Note: Multiple hooks for the same event run in parallel automatically*

**Avoid expensive operations in PreToolUse:**
```python
# BAD: Expensive operation before tool execution
async def slow_validation(input_data, tool_use_id, context):
    # This runs BEFORE every tool call
    run_full_test_suite()  # Too slow!
    return {}

# GOOD: Light validation in PreToolUse
async def quick_validation(input_data, tool_use_id, context):
    # Quick checks only
    if looks_dangerous(input_data):
        return deny_execution()
    return {}

# GOOD: Expensive operation in PostToolUse
async def thorough_check(input_data, tool_use_id, context):
    # This runs AFTER tool completes
    results = run_full_test_suite()
    if not results.passed:
        return block_with_results(results)
    return {}
```

### 5. Make Hooks Maintainable

**Document hook purposes:**
```python
async def validate_database_queries(input_data, tool_use_id, context):
    """
    Validate database queries before execution.

    Purpose:
        Prevent dangerous SQL operations in production environment.

    Blocks:
        - DROP statements
        - TRUNCATE statements
        - DELETE without WHERE clause
        - Operations on production databases

    Related:
        - Database security policy: docs/security.md
        - Safe query patterns: docs/database-guidelines.md
    """
    # Implementation
```

**Use configuration files for patterns:**
```python
# .claude/config/dangerous-patterns.json
{
  "bash_patterns": ["rm -rf", "mkfs", "dd if=/dev/zero"],
  "sql_patterns": ["DROP TABLE", "TRUNCATE", "DELETE FROM .* (?!WHERE)"]
}

async def validate_with_config(input_data, tool_use_id, context):
    """Load patterns from configuration file."""
    with open(".claude/config/dangerous-patterns.json") as f:
        config = json.load(f)

    patterns = config.get("bash_patterns", [])
    # Use patterns for validation
```

**Store hooks in version control:**
```
.claude/
├── hooks/
│   ├── validate_bash.py
│   ├── format_code.py
│   ├── run_tests.py
│   └── notify.sh
├── config/
│   └── dangerous-patterns.json
└── settings.json
```

### 6. Test Hooks Thoroughly

**Test in isolated environment first:**
```python
# Create test settings file
# .claude/settings.test.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "echo 'TEST MODE' && cat"}]
      }
    ]
  }
}
```

**Use debug mode:**
```bash
# Run Claude Code with debug flag
claude --debug

# Or set environment variable
export CLAUDE_DEBUG=1
claude
```

**Test hook behavior:**
```python
import unittest
from your_hooks import validate_file_paths

class TestFileValidation(unittest.TestCase):
    async def test_blocks_path_traversal(self):
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "../../../etc/passwd"}
        }
        result = await validate_file_paths(input_data, None, None)
        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny"
        )

    async def test_allows_safe_paths(self):
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/src/main.py"}
        }
        result = await validate_file_paths(input_data, None, None)
        self.assertEqual(result, {})
```

### 7. Use Environment Variables

**Available variables in shell hooks:**
```bash
#!/bin/bash

# Project directory
cd "$CLAUDE_PROJECT_DIR"

# Remote execution indicator
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
    echo "Running in remote environment"
fi

# Session-specific environment file (SessionStart only)
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "MY_VAR=value" >> "$CLAUDE_ENV_FILE"
fi
```

**Use project directory for relative paths:**
```python
async def use_project_paths(input_data, tool_use_id, context):
    """Use project directory for file operations."""
    cwd = input_data.get("cwd", "")
    config_file = os.path.join(cwd, ".claude/config.json")

    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)

    return {}
```

---

## Common Pitfalls

### 1. Blocking Too Aggressively

**Problem**: Blocking every Write operation slows down the workflow

```python
# BAD: Blocks too often
async def overly_strict_hook(input_data, tool_use_id, context):
    if input_data["tool_name"] == "Write":
        return {
            "hookSpecificOutput": {
                "permissionDecision": "ask"  # Asks every time!
            }
        }
```

**Solution**: Use targeted validation

```python
# GOOD: Only blocks problematic operations
async def targeted_validation(input_data, tool_use_id, context):
    if input_data["tool_name"] != "Write":
        return {}

    file_path = input_data["tool_input"].get("file_path", "")

    # Only block truly sensitive files
    if file_path in [".env", ".git/config"]:
        return {
            "hookSpecificOutput": {
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Modifying sensitive file: {file_path}"
            }
        }

    return {}
```

### 2. Ignoring Hook Timeouts

**Problem**: Long-running hooks block the entire workflow

```python
# BAD: No timeout consideration
{"type": "command", "command": "npm test"}  # May run for minutes
```

**Solution**: Set appropriate timeouts and handle them

```python
# GOOD: Reasonable timeout with fallback
{
    "type": "command",
    "command": "timeout 60 npm test || echo 'Tests timed out'",
    "timeout": 65
}
```

### 3. Not Sanitizing Shell Commands

**Problem**: Shell injection vulnerabilities

```bash
# DANGEROUS: Unsanitized user input
command="bash $user_provided_script"
```

**Solution**: Validate and sanitize all inputs

```bash
# SAFE: Validate before using
if [[ "$script_name" =~ ^[a-zA-Z0-9_-]+\.sh$ ]]; then
    bash ".claude/hooks/$script_name"
else
    echo "Invalid script name" >&2
    exit 1
fi
```

### 4. Forgetting to Review Hook Changes

**Problem**: Direct edits to settings.json don't take effect immediately

**Solution**: Always use `/hooks` command to review changes

```bash
# After editing .claude/settings.json
# In Claude Code, run:
/hooks

# Review and approve changes
```

### 5. Returning Wrong Hook Event Names

**Problem**: Mismatched hook event names cause hooks to fail silently

```python
# BAD: Wrong event name for PostToolUse
async def post_hook(input_data, tool_use_id, context):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse"  # Wrong!
        }
    }
```

**Solution**: Always use correct event name

```python
# GOOD: Correct event name
async def post_hook(input_data, tool_use_id, context):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse"  # Correct
        }
    }
```

### 6. Not Handling Missing Data

**Problem**: Assuming all fields exist in input_data

```python
# BAD: May crash if fields are missing
async def unsafe_hook(input_data, tool_use_id, context):
    command = input_data["tool_input"]["command"]  # May not exist!
```

**Solution**: Use safe access patterns

```python
# GOOD: Safe access with defaults
async def safe_hook(input_data, tool_use_id, context):
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        return {}  # Nothing to validate
```

### 7. Creating Circular Dependencies

**Problem**: PostToolUse hook that triggers more tool calls

```python
# BAD: Can cause infinite loop
async def recursive_hook(input_data, tool_use_id, context):
    # This hook runs after Write
    # But then calls Write again, triggering the hook...
    if input_data["tool_name"] == "Write":
        write_to_log()  # This might trigger another Write!
```

**Solution**: Use direct file operations that don't trigger hooks

```python
# GOOD: Direct file operations
async def logging_hook(input_data, tool_use_id, context):
    # Use direct Python file I/O, not tool calls
    with open(".claude/logs/actions.log", "a") as f:
        f.write(f"{input_data}\n")
    return {}
```

### 8. Overusing Wildcards

**Problem**: Hook runs for every tool, creating performance issues

```python
# BAD: Expensive operation for ALL tools
HookMatcher(
    matcher="*",
    hooks=[run_full_test_suite]  # Runs for EVERY tool call!
)
```

**Solution**: Target specific tools

```python
# GOOD: Only for relevant tools
HookMatcher(
    matcher="Write|Edit",  # Only file modifications
    hooks=[run_tests_for_modified_file]
)
```

---

## Real-World Use Cases

### Use Case 1: Automated Code Quality Pipeline

**Scenario**: Ensure all code changes meet quality standards

```python
async def quality_pipeline(input_data, tool_use_id, context):
    """Run complete quality pipeline after code changes."""
    tool_name = input_data.get("tool_name")
    if tool_name not in ["Write", "Edit"]:
        return {}

    file_path = input_data["tool_input"].get("file_path", "")
    if not file_path.endswith((".py", ".js", ".ts")):
        return {}

    issues = []

    # 1. Format code
    try:
        format_result = subprocess.run(
            ["black", file_path] if file_path.endswith(".py")
            else ["prettier", "--write", file_path],
            capture_output=True, timeout=30
        )
        if format_result.returncode != 0:
            issues.append(f"Formatting failed: {format_result.stderr}")
    except Exception as e:
        issues.append(f"Formatting error: {e}")

    # 2. Lint code
    try:
        lint_result = subprocess.run(
            ["ruff", "check", file_path] if file_path.endswith(".py")
            else ["eslint", file_path],
            capture_output=True, timeout=30
        )
        if lint_result.returncode != 0:
            issues.append(f"Linting errors:\n{lint_result.stdout}")
    except Exception as e:
        issues.append(f"Linting error: {e}")

    # 3. Run tests
    try:
        test_result = subprocess.run(
            ["pytest", "-v"],
            capture_output=True, timeout=120
        )
        if test_result.returncode != 0:
            issues.append(f"Tests failed:\n{test_result.stdout}")
    except Exception as e:
        issues.append(f"Test error: {e}")

    # Block if any issues
    if issues:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "decision": "block",
                "reason": (
                    "Code quality checks failed. Fix these issues:\n\n" +
                    "\n\n".join(issues)
                )
            }
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "All quality checks passed (formatting, linting, tests)"
        }
    }
```

### Use Case 2: Multi-Environment Safety

**Scenario**: Prevent dangerous operations in production

```python
import os
import re

async def environment_safety(input_data, tool_use_id, context):
    """Enforce safety rules based on environment."""

    # Detect environment
    cwd = input_data.get("cwd", "")
    env_file = os.path.join(cwd, ".env")
    is_production = False

    if os.path.exists(env_file):
        with open(env_file) as f:
            content = f.read()
            is_production = "ENVIRONMENT=production" in content

    if not is_production:
        return {}  # Allow all in non-prod

    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Production safety rules
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Block database modifications
        if re.search(r"(DROP|TRUNCATE|DELETE)\s+", command, re.I):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "Database modifications blocked in production. "
                        "Use migration scripts instead."
                    )
                }
            }

        # Block service restarts without approval
        if "systemctl restart" in command or "service restart" in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": (
                        "Service restart in production requires confirmation"
                    )
                }
            }

    elif tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # Block direct config changes
        if any(f in file_path for f in ["nginx.conf", "apache.conf", "prod.config"]):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "Direct configuration changes blocked in production. "
                        "Use configuration management system."
                    )
                }
            }

    return {}
```

### Use Case 3: Compliance and Audit Logging

**Scenario**: Maintain detailed audit trail for compliance

```python
import json
import hashlib
from datetime import datetime

async def compliance_logger(input_data, tool_use_id, context):
    """Log all operations for compliance audit."""

    session_id = input_data.get("session_id")
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})
    hook_event = input_data.get("hook_event_name")

    # Create audit log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "event": hook_event,
        "tool_name": tool_name,
        "user": os.environ.get("USER", "unknown"),
        "cwd": input_data.get("cwd"),
    }

    # Add file hash for Write operations
    if tool_name == "Write" and hook_event == "PostToolUse":
        file_path = tool_input.get("file_path")
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            log_entry["file_hash"] = file_hash
            log_entry["file_path"] = file_path

    # Add command for Bash operations
    if tool_name == "Bash":
        log_entry["command"] = tool_input.get("command")
        if hook_event == "PostToolUse":
            log_entry["exit_code"] = tool_response.get("exit_code")

    # Write to audit log (append-only)
    audit_log = ".claude/logs/audit.jsonl"
    os.makedirs(os.path.dirname(audit_log), exist_ok=True)

    with open(audit_log, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Also send to external logging system (optional)
    try:
        import requests
        requests.post(
            "https://logging.company.com/api/logs",
            json=log_entry,
            timeout=5
        )
    except:
        pass  # Don't fail if external logging unavailable

    return {}

# Configure for both Pre and Post events
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="*", hooks=[compliance_logger]),
        ],
        "PostToolUse": [
            HookMatcher(matcher="*", hooks=[compliance_logger]),
        ],
    }
)
```

### Use Case 4: Intelligent Test Selection

**Scenario**: Run only relevant tests based on changed files

```python
import os
import subprocess
from pathlib import Path

async def smart_test_runner(input_data, tool_use_id, context):
    """Run only tests related to changed files."""

    tool_name = input_data.get("tool_name")
    if tool_name not in ["Write", "Edit"]:
        return {}

    file_path = input_data["tool_input"].get("file_path", "")
    if not file_path:
        return {}

    cwd = input_data.get("cwd", ".")

    # Determine test files based on changed file
    test_files = []

    # Python project
    if file_path.endswith(".py"):
        # Convention: src/module.py -> tests/test_module.py
        path_obj = Path(file_path)
        test_name = f"test_{path_obj.stem}.py"

        # Look in multiple test directories
        for test_dir in ["tests", "test", path_obj.parent / "tests"]:
            test_path = Path(cwd) / test_dir / test_name
            if test_path.exists():
                test_files.append(str(test_path))

    # JavaScript/TypeScript project
    elif file_path.endswith((".js", ".ts", ".tsx")):
        path_obj = Path(file_path)

        # Look for co-located test files
        for pattern in [
            f"{path_obj.stem}.test{path_obj.suffix}",
            f"{path_obj.stem}.spec{path_obj.suffix}",
        ]:
            test_path = path_obj.parent / pattern
            if test_path.exists():
                test_files.append(str(test_path))

    if not test_files:
        # No specific tests found, run all
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "No specific tests found for this file"
            }
        }

    # Run only relevant tests
    failures = []
    for test_file in test_files:
        try:
            if test_file.endswith(".py"):
                result = subprocess.run(
                    ["pytest", "-v", test_file],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                result = subprocess.run(
                    ["npm", "test", "--", test_file],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

            if result.returncode != 0:
                failures.append(f"{test_file}:\n{result.stdout}")

        except subprocess.TimeoutExpired:
            failures.append(f"{test_file}: timed out")

    if failures:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "decision": "block",
                "reason": (
                    f"Tests failed for {file_path}. Fix these failures:\n\n" +
                    "\n\n".join(failures)
                )
            }
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"Tests passed for {file_path} "
                f"({len(test_files)} test file(s) validated)"
            )
        }
    }
```

### Use Case 5: Dynamic Permission System

**Scenario**: Permission levels based on file sensitivity

```python
import os
import json

async def dynamic_permissions(input_data, tool_use_id, context):
    """Adjust permissions based on file sensitivity levels."""

    tool_name = input_data.get("tool_name")
    if tool_name not in ["Write", "Edit", "Bash"]:
        return {}

    cwd = input_data.get("cwd", ".")

    # Load sensitivity configuration
    config_file = os.path.join(cwd, ".claude/file-sensitivity.json")
    if not os.path.exists(config_file):
        return {}

    with open(config_file) as f:
        sensitivity_config = json.load(f)

    # Get file path
    file_path = ""
    if tool_name in ["Write", "Edit"]:
        file_path = input_data["tool_input"].get("file_path", "")
    elif tool_name == "Bash":
        # Extract file path from command if present
        command = input_data["tool_input"].get("command", "")
        # Simple extraction (would need more robust parsing in production)
        for word in command.split():
            if "/" in word and not word.startswith("-"):
                file_path = word
                break

    if not file_path:
        return {}

    # Check sensitivity level
    sensitivity = "low"
    for pattern, level in sensitivity_config.items():
        if pattern in file_path:
            sensitivity = level
            break

    # Apply permission rules based on sensitivity
    if sensitivity == "critical":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"File {file_path} is marked as CRITICAL. "
                    "Modifications require manual change request."
                )
            }
        }

    elif sensitivity == "high":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    f"File {file_path} is marked as HIGH sensitivity. "
                    "Please review changes carefully."
                )
            }
        }

    elif sensitivity == "medium":
        # Allow but add context
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "additionalContext": (
                    f"Note: {file_path} requires careful testing after modification"
                )
            }
        }

    # Low sensitivity - no restrictions
    return {}
```

**Configuration file**: `.claude/file-sensitivity.json`
```json
{
  ".env": "critical",
  "production": "critical",
  ".git/config": "critical",
  "database/migrations": "high",
  "config/": "high",
  "src/auth": "high",
  "tests/": "low",
  "docs/": "low"
}
```

### Use Case 6: Integration with External Systems

**Scenario**: Notify team via Slack when deployments occur

```python
import requests
import json

async def slack_notifier(input_data, tool_use_id, context):
    """Send Slack notifications for important events."""

    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Only monitor Bash commands
    if tool_name != "Bash":
        return {}

    command = tool_input.get("command", "")

    # Detect deployment commands
    deployment_keywords = ["deploy", "release", "publish", "terraform apply"]

    is_deployment = any(keyword in command.lower() for keyword in deployment_keywords)

    if not is_deployment:
        return {}

    # Get Slack webhook URL from environment
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook:
        return {}

    # Prepare Slack message
    session_id = input_data.get("session_id")
    user = os.environ.get("USER", "unknown")
    cwd = input_data.get("cwd", "")

    message = {
        "text": f"🚀 Deployment initiated by {user}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 Deployment Started"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*User:*\n{user}"},
                    {"type": "mrkdwn", "text": f"*Project:*\n{os.path.basename(cwd)}"},
                    {"type": "mrkdwn", "text": f"*Command:*\n```{command}```"},
                ]
            }
        ]
    }

    # Send to Slack
    try:
        response = requests.post(
            slack_webhook,
            json=message,
            timeout=5
        )

        if response.status_code == 200:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "Team notified via Slack"
                }
            }
    except Exception as e:
        # Don't fail deployment if notification fails
        print(f"Slack notification failed: {e}", file=sys.stderr)

    return {}
```

---

## Troubleshooting

### Issue 1: Hooks Not Triggering

**Symptoms**: Hook configured but not executing

**Possible Causes and Solutions**:

1. **Hook not reviewed after changes**
   ```bash
   # Solution: Review hooks in Claude Code
   /hooks
   # Then approve the changes
   ```

2. **Matcher pattern doesn't match tool name**
   ```python
   # Check exact tool name
   print(input_data.get("tool_name"))

   # Try wildcard first to test
   HookMatcher(matcher="*", hooks=[debug_hook])
   ```

3. **Hook function signature incorrect**
   ```python
   # WRONG
   async def hook(input_data):
       pass

   # CORRECT
   async def hook(input_data, tool_use_id, context):
       pass
   ```

4. **Using hooks with `query()` instead of `ClaudeSDKClient`**
   ```python
   # WRONG - query() doesn't support hooks
   result = await query("Do something", options=options)

   # CORRECT - Use ClaudeSDKClient
   client = ClaudeSDKClient(options=options)
   ```

### Issue 2: Hooks Timing Out

**Symptoms**: Hook execution interrupted, timeout errors

**Solutions**:

1. **Increase timeout**
   ```json
   {
     "type": "command",
     "command": "long-running-script.sh",
     "timeout": 300
   }
   ```

2. **Optimize hook logic**
   ```python
   # Run expensive operations async or in background
   async def optimized_hook(input_data, tool_use_id, context):
       # Quick validation first
       if not should_process(input_data):
           return {}

       # Then expensive operation
       result = await run_with_timeout(expensive_operation(), 30)
       return result
   ```

3. **Move slow operations to PostToolUse**
   ```python
   # PreToolUse should be fast
   # Move slow operations to PostToolUse
   ```

### Issue 3: Permission Decisions Not Working

**Symptoms**: `permissionDecision` not being respected

**Solutions**:

1. **Verify event name matches**
   ```python
   # For PreToolUse
   return {
       "hookSpecificOutput": {
           "hookEventName": "PreToolUse",  # Must match!
           "permissionDecision": "deny"
       }
   }
   ```

2. **Check permission mode**
   ```python
   # Check current permission mode
   permission_mode = input_data.get("permission_mode")

   # "bypassPermissions" mode ignores some decisions
   if permission_mode == "bypassPermissions":
       # Hook runs but some decisions ignored
       pass
   ```

3. **Return correct structure**
   ```python
   # WRONG
   return {"permissionDecision": "deny"}

   # CORRECT
   return {
       "hookSpecificOutput": {
           "hookEventName": "PreToolUse",
           "permissionDecision": "deny",
           "permissionDecisionReason": "Reason here"
       }
   }
   ```

### Issue 4: Shell Hooks Not Receiving Input

**Symptoms**: Shell script can't read JSON input

**Solutions**:

1. **Read from stdin correctly**
   ```bash
   #!/bin/bash

   # Read entire stdin
   input=$(cat)

   # Parse with jq
   tool_name=$(echo "$input" | jq -r '.tool_name')
   ```

2. **Check script permissions**
   ```bash
   chmod +x .claude/hooks/my-hook.sh
   ```

3. **Test script independently**
   ```bash
   # Create test input
   echo '{"tool_name":"Bash","tool_input":{}}' | bash .claude/hooks/my-hook.sh
   ```

### Issue 5: Hooks Creating Infinite Loops

**Symptoms**: Agent gets stuck, repeated hook executions

**Solutions**:

1. **Don't trigger tools from hooks**
   ```python
   # WRONG - triggers another tool call
   async def bad_hook(input_data, tool_use_id, context):
       # This might trigger the hook again!
       client.write_file("log.txt", "...")

   # CORRECT - use direct file I/O
   async def good_hook(input_data, tool_use_id, context):
       with open("log.txt", "a") as f:
           f.write("...")
   ```

2. **Track processed tool IDs**
   ```python
   processed_ids = set()

   async def idempotent_hook(input_data, tool_use_id, context):
       if tool_use_id in processed_ids:
           return {}

       processed_ids.add(tool_use_id)
       # Process...
   ```

### Issue 6: Environment Variables Not Available

**Symptoms**: `$CLAUDE_PROJECT_DIR` or other variables empty

**Solutions**:

1. **Check variable availability by event**
   ```bash
   # CLAUDE_ENV_FILE only available in SessionStart
   if [ "$HOOK_EVENT_NAME" = "SessionStart" ]; then
       echo "VAR=value" >> "$CLAUDE_ENV_FILE"
   fi
   ```

2. **Use input data instead**
   ```bash
   # Get project dir from input data
   cwd=$(echo "$input" | jq -r '.cwd')
   ```

### Issue 7: Debugging Hook Execution

**Enable debug mode to see detailed hook execution logs**:

```bash
# Run with debug flag
claude --debug

# Or set environment variable
export CLAUDE_DEBUG=1
```

**Add logging to hooks**:

```python
import sys

async def debug_hook(input_data, tool_use_id, context):
    """Hook with debug logging."""

    # Log to stderr (shown in debug mode)
    print(f"[DEBUG] Hook triggered", file=sys.stderr)
    print(f"[DEBUG] Tool: {input_data.get('tool_name')}", file=sys.stderr)
    print(f"[DEBUG] Input: {input_data}", file=sys.stderr)

    # Hook logic...
    result = {}

    print(f"[DEBUG] Result: {result}", file=sys.stderr)
    return result
```

**Use `/hooks` command to verify configuration**:

```bash
# In Claude Code
/hooks

# Shows:
# - All registered hooks
# - Matchers and patterns
# - Hook functions/commands
# - Pending approvals
```

---

## Additional Resources

### Official Documentation
- **Claude Agent SDK Overview**: https://docs.claude.com/en/docs/agent-sdk/overview
- **Hooks Reference**: https://code.claude.com/docs/en/hooks
- **Hooks Guide**: https://code.claude.com/docs/en/hooks-guide
- **Python SDK Reference**: https://docs.claude.com/en/docs/agent-sdk/python

### GitHub Repositories
- **Python SDK**: https://github.com/anthropics/claude-agent-sdk-python
- **Examples**: See `examples/hooks.py` in the Python SDK repository

### Community Resources
- **Hook Examples**: https://github.com/disler/claude-code-hooks-mastery
- **Multi-Agent Observability**: https://github.com/disler/claude-code-hooks-multi-agent-observability

### Best Practices Guides
- **Claude Code Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices
- **Building Agents with Claude SDK**: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

---

## Summary

Hooks in the Claude Agent SDK provide powerful capabilities for:

1. **Security and Safety**: Block dangerous operations before they execute
2. **Quality Enforcement**: Ensure code meets standards before continuing
3. **Automation**: Trigger formatters, linters, and tests automatically
4. **Observability**: Log and monitor agent actions
5. **Integration**: Connect with external systems and workflows

**Key Takeaways**:
- Use PreToolUse for validation and blocking
- Use PostToolUse for quality checks and feedback
- Always validate and sanitize inputs
- Set appropriate timeouts
- Test hooks thoroughly before production
- Use targeted matchers, not wildcards for everything
- Handle errors gracefully
- Document hook purposes and behavior

By following this guide and best practices, you can implement robust, secure, and efficient hooks that enhance your Claude Agent SDK applications.

---

*Last updated: 2025*
*Claude Agent SDK version: 0.6.0+*
