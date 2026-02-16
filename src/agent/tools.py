import json
import os

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
]


def execute_tool(name, input):
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

    return f"[error] Unknown tool: {name}"
