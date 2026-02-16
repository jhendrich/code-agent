import anthropic


def main():
    client = anthropic.Anthropic()
    conversation_history = []

    print("Chat with Claude (type 'quit' to exit)")
    print("-" * 40)

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() == "quit":
            break

        conversation_history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=conversation_history,
        )

        assistant_message = response.content[0].text
        conversation_history.append({"role": "assistant", "content": assistant_message})

        print(f"\nClaude: {assistant_message}")
