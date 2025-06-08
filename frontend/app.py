import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Document Chatbot", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stChatMessage {background-color: #23272f; border-radius: 10px; padding: 16px; margin-bottom: 10px;}
    .stChatUser {background-color: #1a1d23; border-radius: 10px; padding: 16px; margin-bottom: 10px;}
    .stUploadIcon {font-size: 40px; color: #4F8BF9; margin-bottom: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 Document Chatbot with Theme Identification")

st.header("Upload Documents")
st.markdown('<div class="stUploadIcon">📄</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload PDFs or images",
    accept_multiple_files=True,
    type=["pdf", "png", "jpg", "jpeg"],
    label_visibility="collapsed"
)
if uploaded_files:
    if st.button("⬆️ Upload to Backend"):
        for idx, file in enumerate(uploaded_files, 1):
            files = {"file": (file.name, file.getvalue(), file.type)}
            resp = requests.post(f"{BACKEND_URL}/upload/", files=files)
            st.success(f"Document {idx}: {file.name} uploaded ({resp.json().get('chunks', 0)} chunks)")

st.divider()

st.header("Chat with your Documents")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def render_chat():
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            st.markdown(f'<div class="stChatUser"><b>You:</b> {entry["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="stChatMessage"><b>Bot:</b> {entry["content"]}</div>', unsafe_allow_html=True)

render_chat()

with st.form(key="query_form", clear_on_submit=True):
    question = st.text_input(
        "Ask a question about your documents",
        key="question_input",
        placeholder="Type your question and press Enter..."
    )
    submit = st.form_submit_button("Send")

if submit and question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    # Prepare chat history for backend (exclude current question)
    history = [
        {"role": entry["role"], "content": entry["content"]}
        for entry in st.session_state.chat_history[:-1]
    ]
    with st.spinner("Thinking..."):
        resp = requests.post(
            f"{BACKEND_URL}/query/",
            json={"question": question, "history": history}
        )
        data = resp.json()
        # ChatGPT-style answer formatting
        if "answer" in data:
            answer = data["answer"]
            st.session_state.chat_history.append({"role": "bot", "content": answer})
        elif "answers" in data and isinstance(data["answers"], list) and len(data["answers"]) > 0:
            answer_lines = []
            for idx, ans in enumerate(data["answers"], 1):
                doc_id = f"Document {idx}"
                page_info = ans.get("citation", "")
                answer_lines.append(f"**{doc_id}** (at {page_info}):\n{ans['answer']}")
            answer = "\n\n".join(answer_lines)
            st.session_state.chat_history.append({"role": "bot", "content": answer})
        elif "themes" in data and isinstance(data["themes"], list) and len(data["themes"]) > 0:
            answer_lines = []
            for theme in data["themes"]:
                answer_lines.append(f"**Theme – {theme['theme']}:**\n{theme['summary']}")
            answer = "\n\n".join(answer_lines)
            st.session_state.chat_history.append({"role": "bot", "content": answer})
        else:
            st.session_state.chat_history.append({"role": "bot", "content": "Sorry, I couldn't find an answer."})
    render_chat()