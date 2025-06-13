from openai import OpenAI
import pandas as pd

# These will be set by the app
catalog_df = None
raw_csv_text = ""

def set_catalog(df):
    global catalog_df, raw_csv_text
    catalog_df = df.copy()
    catalog_df.columns = catalog_df.columns.str.strip().str.lower()
    raw_csv_text = catalog_df.to_csv(index=False)

client = OpenAI(api_key="key")  # Use your key here

def validate_schedule(possible_schedule):
    valid = []
    for entry in possible_schedule:
        norm_entry = {k.strip().lower(): str(v).strip().lower() for k, v in entry.items()}
        query = catalog_df.copy()
        for col, val in norm_entry.items():
            if col in query.columns:
                query = query[query[col].astype(str).str.lower().str.strip() == val]
            # else: just ignore keys not in catalog
        if not query.empty:
            valid.append(entry)
    return valid

def get_chat_response(conversation_history, csv_mode=False):
    if catalog_df is None or raw_csv_text == "":
        raise ValueError("Catalog not set. Please upload a catalog CSV first.")

    if csv_mode:
        system_content = (
            "You are a helpful university course scheduling assistant. "
            "Only use the official catalog provided. You must ONLY use rows and values exactly as they appear in the official catalog below."
            "Do NOT invent classes, times, or days. Do NOT invent, summarize, or mix up any values. "
            f"Here are the available columns: {', '.join(catalog_df.columns)}. "
            "Return ONLY the schedule as a CSV file (with a header row), "
            "using the exact column names and values as in the catalog. "
            "Do not include any extra text, explanation, or formatting—just the CSV."
        )
    else:
        system_content = (
            "You are a helpful university course scheduling assistant. "
            "Use the official catalog provided. "
            "If the user asks for a subject or area (like 'english'), you may suggest related or relevant courses from the catalog, "
            "even if the course name is not an exact match. "
            "Be creative and helpful in finding courses that fit the user's interests, using course names, types, or descriptions. "
            f"Here are the available columns: {', '.join(catalog_df.columns)}. "
            "Respond conversationally and help the user plan their schedule using only the catalog."
        )

    messages = [
        {
            "role": "system",
            "content": system_content
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
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()
