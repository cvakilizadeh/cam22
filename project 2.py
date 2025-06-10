from openai import OpenAI
import pandas as pd

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Use your actual API key

# Load course catalog
csv_path = r'C:/Users/cvakili-zadeh/Desktop/university_classes_expanded.csv'
with open(csv_path, 'r', encoding='utf-8') as file:
    raw_csv_text = file.read()

# Also load with pandas for strict validation
catalog_df = pd.read_csv(csv_path)
catalog_df.columns = catalog_df.columns.str.strip().str.lower()

def validate_schedule(possible_schedule):
    """Validates GPT's proposed schedule against the actual course catalog."""
    valid = []
    for entry in possible_schedule:
        norm_entry = {k.strip().lower(): v for k, v in entry.items()}
        query = catalog_df
        for col in norm_entry:
            if col in query.columns:
                query = query[query[col] == norm_entry[col]]
            else:
                break
        if not query.empty:
            valid.append(entry)
    return valid

def get_chat_response(conversation_history):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful and conversational university scheduling assistant. "
                "Your job is to talk naturally with the student, understand what they're looking for, "
                "and recommend schedules using ONLY data from the course catalog provided. "
                "NEVER invent times, classes, or days. If the user requests something not available, kindly explain why. "
                "Reply in a friendly, helpful tone. Always ask if they’d like to adjust their schedule or need more advice."
            )
        },
        {
            "role": "system",
            "content": f"Here is the official course catalog in CSV format:\n\n{raw_csv_text}"
        }
    ]

    for user_msg, assistant_msg in conversation_history:
        messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

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
    all_valid_schedules = []

    print("What do you want me to do for classes?")

    while True:
        user_input = input(": ")
        if user_input.lower() in ['exit', 'quit', 'bye', 'done']:
            print("Finished. Validating and exporting any schedules...")
            if all_valid_schedules:
                pd.DataFrame(all_valid_schedules).to_csv("validated_schedule.csv", index=False)
                print("✅ Exported valid suggestions to 'validated_schedule.csv'.")
            else:
                print("⚠️ No valid schedule entries were found.")
            break

        conversation.append((user_input, None))
        reply = get_chat_response(conversation)
        print(reply)
        conversation[-1] = (user_input, reply)

        try:
            proposed_schedule = eval(reply.strip(), {"__builtins__": {}})
            if isinstance(proposed_schedule, list) and all(isinstance(x, dict) for x in proposed_schedule):
                valid_entries = validate_schedule(proposed_schedule)
                all_valid_schedules.extend(valid_entries)
        except Exception:
            pass
