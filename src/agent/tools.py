import json
import os
import subprocess

# Tool definitions — tells the model what tools are available
TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file at the given path. Creates the file and any parent directories if they don't exist. Overwrites the file if it already exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to write to",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output. Requires user confirmation before executing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default 30)",
                },
            },
            "required": ["command"],
        },
    },
]

DEFAULT_TIMEOUT = 30


def execute_tool(name, input, input_func=input):
    """Execute a tool call and return the result as a string."""
    print(f"\n  [Tool called: {name}]")
    print(f"  [Input: {json.dumps(input)}]")

    if name == "read_file":
        try:
            with open(input["path"], "r") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found: {input['path']}"
        except PermissionError:
            return f"Error: Permission denied: {input['path']}"

    if name == "write_file":
        try:
            parent = os.path.dirname(input["path"])
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(input["path"], "w") as f:
                f.write(input["content"])
            return f"Successfully wrote to {input['path']}"
        except PermissionError:
            return f"Error: Permission denied: {input['path']}"

    if name == "run_command":
        command = input["command"]
        timeout = input.get("timeout", DEFAULT_TIMEOUT)

        # User confirmation
        print(f"\n  Agent wants to run: {command}")
        approval = input_func(f"  Approve? (y/n): ").strip().lower()
        if approval != "y":
            return "Command rejected by user."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"

    return f"[error] Unknown tool: {name}"
