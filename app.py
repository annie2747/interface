# MyAI Voice + Text UI Interface (Streamlit + GPT-4 + Notion Logging)

import streamlit as st
import openai
import requests
import datetime
import os

# ========== SETUP ==========
openai.api_key = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ========== UI ==========
st.title("🧠 MyAI Interface")
st.markdown("Speak or type to MyAI. All input/output is logged to Notion.")

input_method = st.radio("Choose input method:", ("🎤 Voice (coming soon)", "⌨️ Text"))

user_input = ""
if input_method == "⌨️ Text":
    user_input = st.text_area("Your input:")
    submit = st.button("Send")
else:
    st.info("Voice input will be enabled in the next version.")
    submit = False

# ========== FUNCTIONS ==========
def log_to_notion(prompt, response):
    now = datetime.datetime.now().isoformat()
    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "CONTENT": {"title": [{"text": {"content": prompt[:100]}}]},
            "TIMESTAMP": {"date": {"start": now}},
            "TYPE": {"select": {"name": "INPUT+OUTPUT"}},
            "FEED TO MyAi": {"checkbox": True},
        },
        "children": [
            {"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": f"INPUT: {prompt}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": f"OUTPUT: {response}"}}]}}
        ]
    }
    requests.post("https://api.notion.com/v1/pages", headers=headers, json=notion_data)

# ========== GPT CALL ==========
if submit and user_input:
    st.markdown("---")
    st.markdown("**Thinking...**")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are MyAI, a personal cognition engine designed to help the user think clearly."},
            {"role": "user", "content": user_input}
        ]
    )
    reply = response["choices"][0]["message"]["content"]
    
    st.markdown("### 🧠 MyAI says:")
    st.write(reply)
    log_to_notion(user_input, reply)
