import streamlit as st
import pandas as pd
import io
from scheduling_logic import get_chat_response, set_catalog

st.title("University Course Scheduler")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# File uploader for catalog
uploaded_file = st.file_uploader("Upload your course catalog CSV", type=["csv"])
if uploaded_file:
    catalog_df = pd.read_csv(uploaded_file)
    set_catalog(catalog_df)
    st.success("Catalog uploaded and loaded!")
    st.dataframe(catalog_df)
else:
    st.warning("Please upload a course catalog CSV to begin.")
    st.stop()

# --- Display chat history above input ---
st.markdown("## Conversation History")
for user_msg, assistant_msg in st.session_state.conversation:
    st.markdown(f"**You:** {user_msg}")
    if assistant_msg:
        st.markdown(f"**Assistant:** {assistant_msg}")

# Chatbot input line appears below chat history
user_input = st.text_input("What kind of classes or schedule are you looking for?")

col1, col2, col3 = st.columns(3)
with col1:
    send = st.button("Send")
with col2:
    show_schedule = st.button("Show Current Schedule")
with col3:
    done = st.button("Done - Finalize & Export")

def append_user_message(text):
    st.session_state.conversation.append((text, None))

def add_assistant_reply(reply):
    last_user, _ = st.session_state.conversation[-1]
    st.session_state.conversation[-1] = (last_user, reply)

if send and user_input.strip():
    append_user_message(user_input)
    reply = get_chat_response(st.session_state.conversation)
    add_assistant_reply(reply)
    st.rerun()

elif show_schedule:
    append_user_message("Please show me the current schedule you have planned so far.")
    reply = get_chat_response(st.session_state.conversation)
    add_assistant_reply(reply)
    st.rerun()

elif done:
    append_user_message(
        "Please finalize and return the schedule ONLY as a CSV file. "
        "Do NOT return any extra text — only the CSV."
    )
    final_reply = get_chat_response(st.session_state.conversation, csv_mode=True)
    add_assistant_reply(final_reply)
    st.markdown("### Final Schedule (raw GPT output):")
    st.code(final_reply, language='csv')

    try:
        text = final_reply
        # Remove code block markers if present
        if "```" in text:
            text = text.split("```")[1].strip()
        # Try to read as CSV
        df = pd.read_csv(io.StringIO(text))
        csv_bytes = text.encode("utf-8")
        st.success("✅ Schedule ready for download!")
        st.dataframe(df)
        st.download_button(
            label="Download schedule as CSV",
            data=csv_bytes,
            file_name="validated_schedule.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ Error parsing GPT reply as CSV: {e}")
