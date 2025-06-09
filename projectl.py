from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace with your actual API key

# Load the raw CSV as text
csv_path = r'C:/Users/cvakili-zadeh/Desktop/university_classes_expanded.csv'
with open(csv_path, 'r', encoding='utf-8') as file:
    raw_csv_text = file.read()

# ChatGPT conversation handler
def get_chat_response(conversation_history):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful university scheduling assistant. A student will chat with you about their preferences. "
                "Use the following raw CSV course catalog to build and recommend ideal schedules. Do not request preferences formally — have a natural conversation."
            )
        },
        {
            "role": "system",
            "content": f"Here is the course catalog in CSV format:\n\n{raw_csv_text}"
        }
    ]

    # Add conversation history
    for user_msg, assistant_msg in conversation_history:
        messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

    # Call GPT-3.5 Turbo
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content

# Main chatbot loop
if __name__ == "__main__":
    conversation = []
    print("What do you want me to do for classes?")

    while True:
        user_input = input(": ")
        if user_input.lower() in ['exit', 'quit', 'bye', 'done']:
            print("thanks")
            break
        conversation.append((user_input, None))
        reply = get_chat_response(conversation)
        print("Scheduling:", reply)
        conversation[-1] = (user_input, reply)
