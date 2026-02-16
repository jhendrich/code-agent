import json
import anthropic
from src.agent.tools import TOOL_DEFINITIONS, execute_tool


def agent_loop(client, conversation_history):
    """Run the agent loop: call the model, execute tools, repeat until done."""
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=TOOL_DEFINITIONS,
            messages=conversation_history,
        )

        # Add the full assistant response to history
        conversation_history.append({"role": "assistant", "content": response.content})

        # If the model is done (no more tool calls), return the final response
        if response.stop_reason == "end_turn":
            return response

        # Process any tool calls in the response
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        # Send tool results back to the model
        conversation_history.append({"role": "user", "content": tool_results})
