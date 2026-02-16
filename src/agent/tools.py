import json

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
    }
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

    return f"[error] Unknown tool: {name}"
