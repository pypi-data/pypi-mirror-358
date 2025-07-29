import airouter
from airouter.models import LLM


if __name__ == '__main__':
    messages = [{'role': 'system', 'content': "You're very good at mathematics!"}]

    while True:
        user_input = input("\nYou: ")  # Get user input

        # Check if user wants to quit
        if user_input.lower() in ["q", "quit", "exit"]:
            print("Exiting conversation.")
            break

        # Append user's message to the list of messages
        messages.append({"role": "user", "content": user_input})

        # Get assistant's response
        outputs = airouter.StreamedCompletion.create(
            model=LLM.ANTROPHIC_CLAUDE_V35_SONNET_V2,
            temperature=0.0,
            messages=messages,
        )

        assistant_response = outputs.content
        messages.append({"role": "assistant", "content": assistant_response})

        # Print assistant's response
        print("Assistant:", assistant_response)
