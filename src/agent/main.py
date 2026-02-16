import json
import anthropic
from src.agent.loop import agent_loop


def main():
    client = anthropic.Anthropic()
    conversation_history = []

    print("Chat with Claude (type 'quit' to exit)")
    print("-" * 40)

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() == "quit":
            print("\n" + "=" * 40)
            print("CONVERSATION HISTORY")
            print("=" * 40)
            print(json.dumps(conversation_history, indent=2, default=str))
            break

        conversation_history.append({"role": "user", "content": user_input})

        response = agent_loop(client, conversation_history)

        # Print any text blocks from the final response
        for block in response.content:
            if hasattr(block, "text"):
                print(f"\nClaude: {block.text}")
