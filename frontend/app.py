import streamlit as st
import requests

# Backend URL endpoint
BACKEND_URL = "https://aiintern-oze9.onrender.com"

# Page setup
st.set_page_config(page_title="Document Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for styling user and bot messages
st.markdown(
    """
    <style>
    .stChatMessage {background-color: #23272f; border-radius: 10px; padding: 16px; margin-bottom: 10px;}
    .stChatUser {background-color: #1a1d23; border-radius: 10px; padding: 16px; margin-bottom: 10px;}
    .stUploadIcon {font-size: 40px; color: #4F8BF9; margin-bottom: 10px;}
    textarea {min-height: 40px !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# App title
st.markdown("<h1 style='text-align: center;'>🤖FileBot🤖</h1>", unsafe_allow_html=True)

# Initialize chat history & file uploader session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# Sidebar reset control
st.sidebar.header("Session Controls")
if st.sidebar.button("Start New Chat"):
    try:
        # Reset backend state
        resp = requests.post(f"{BACKEND_URL}/reset_backend/")
        if resp.status_code == 200:
            st.success("Backend reset successfully!")
        else:
            st.error("Failed to reset backend.")
    except Exception as e:
        st.error(f"Error resetting backend: {e}")
    # Reset frontend session state
    st.session_state.chat_history = []
    st.session_state.file_uploader_key += 1
    st.rerun()

# --- Document upload section ---
st.header("Upload Documents or Enter Text")

with st.form("upload_form", clear_on_submit=True):
    # Upload PDFs and image files
    uploaded_files = st.file_uploader(
        "Upload PDFs or images (PDF, PNG, JPG, JPEG)", 
        accept_multiple_files=True, 
        type=["pdf", "png", "jpg", "jpeg"],
        key=st.session_state.file_uploader_key
    )

    # Or paste raw text
    user_text = st.text_area("Or paste your text here to upload as a document.", height=150)
    upload_submit = st.form_submit_button("Upload")

# Handle uploads
if upload_submit:
    if uploaded_files:
        for idx, file in enumerate(uploaded_files, 1):
            files = {"file": (file.name, file.getvalue(), file.type)}
            try:
                resp = requests.post(f"{BACKEND_URL}/upload/", files=files)
                resp.raise_for_status()
                if resp.text.strip():
                    result = resp.json()
                    doc_id = result.get("doc_id", f"DOC{idx}")
                    st.success(f"✅ Document {idx}: {file.name} uploaded as {doc_id}")
                else:
                    st.error(f"❌ Document {file.name} uploaded but got empty response.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to upload {file.name}: {e}")
            except ValueError:
                st.error(f"❌ Invalid JSON response for {file.name}: {resp.text}")

    # Upload text input
    if user_text.strip():
        resp = requests.post(f"{BACKEND_URL}/upload_text/", json={"text": user_text})
        if resp.status_code == 200:
            st.success("Text uploaded successfully!")
        else:
            st.error("Failed to upload text.")

# --- Chat Section ---
st.divider()
st.header("💬 Chat with your Documents")

# Display chat history
for entry in st.session_state.chat_history:
    if entry["role"] == "user":
        st.markdown(f'<div class="stChatUser"><b>You:</b> {entry["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stChatMessage"><b>Bot:</b> {entry["content"]}</div>', unsafe_allow_html=True)

# Helper for expanding textarea input
def auto_expand_text_area(label, key, placeholder):
    return st.text_area(
        label,
        key=key,
        placeholder=placeholder,
        height=68,
        help="Type your question here"
    )

# Chat input form
with st.form(key="query_form", clear_on_submit=True):
    question = auto_expand_text_area(
        "Ask a question about your documents",
        key="question_input",
        placeholder="Type your question (multi-line supported)..."
    )
    submit = st.form_submit_button("Send")

# Submit question to backend and get answer
if submit and question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    history = st.session_state.chat_history[:-1]
    with st.spinner("🤔 Thinking..."):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/query/",
                json={"question": question, "history": history}
            )
            resp.raise_for_status()
            if resp.text.strip():
                data = resp.json()
                answer = data.get("answer", "❌ No answer returned.")
                st.session_state.chat_history.append({"role": "bot", "content": answer})
            else:
                st.session_state.chat_history.append({"role": "bot", "content": "❌ Got empty response from backend."})
        except requests.exceptions.RequestException as e:
            st.session_state.chat_history.append({"role": "bot", "content": f"❌ Error: {e}"})
        except ValueError:
            st.session_state.chat_history.append({"role": "bot", "content": f"❌ Invalid JSON response: {resp.text}"})
    st.rerun()
