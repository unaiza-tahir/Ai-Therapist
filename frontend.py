# Step1: Setup Streamlit
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="AI Mental Health Therapist", layout="wide")
st.title("🧠 SafeSpace – AI Mental Health Therapist")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Step2: User is able to ask question
# Chat input
user_input = st.chat_input("What's on your mind today?")
if user_input:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # AI Agent exists here
    try:
        response = requests.post(BACKEND_URL, json={"message": user_input})

        if response.status_code == 200:
            result = response.json()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f'{result["response"]} WITH TOOL: [{result["tool_called"]}]'
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"⚠️ Backend error {response.status_code}: {response.text}"
            })
    except requests.exceptions.RequestException as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Could not connect to backend: {e}"
        })

# Step3: Show response from backend
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])