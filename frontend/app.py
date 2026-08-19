"""
Streamlit chat UI for the AI Virtual Assistant.

Talks to the FastAPI backend over HTTP (BACKEND_URL). Keeps the full
conversation in `st.session_state` and re-sends it as `history` on every
turn so the backend/LLM has context.
"""
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

st.set_page_config(page_title="AI Virtual Assistant", page_icon="🤖", layout="centered")
st.title("🤖 AI Virtual Assistant")
st.caption("AI Systems Engineering project — Streamlit frontend · FastAPI backend · Hugging Face LLM")

if "messages" not in st.session_state:
    st.session_state.messages = []  # list[{"role": "user"|"assistant", "content": str}]

with st.sidebar:
    st.subheader("Settings")
    st.text_input("Backend URL", value=BACKEND_URL, key="backend_url_display", disabled=True)
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5).json()
        st.success(f"Backend online — model: {health.get('model', 'unknown')}")
    except requests.RequestException:
        st.error("Backend unreachable. Is it running?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]  # everything except the message just sent
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")
        try:
            resp = requests.post(
                f"{BACKEND_URL}{API_PREFIX}/chat",
                json={"message": user_input, "history": history},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            reply = resp.json()["reply"]
        except requests.RequestException as exc:
            reply = f"⚠️ Error reaching the backend: {exc}"
        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
