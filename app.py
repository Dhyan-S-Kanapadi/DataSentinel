 
import streamlit as st
from agent import run_agent

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenMetadata Workflow Agent",
    page_icon="🤖",
    layout="centered"
)

# ── Header ─────────────────────────────────────────────────────
st.title("🤖 OpenMetadata Workflow Agent")
st.caption("Powered by Cerebras Llama + LangGraph + OpenMetadata")

# ── Suggested Questions ────────────────────────────────────────
st.markdown("**Try asking:**")
col1, col2 = st.columns(2)
with col1:
    if st.button("Which tables have no owners?"):
        st.session_state.suggested = "Which tables have no owners?"
    if st.button("Show data quality failures"):
        st.session_state.suggested = "Show data quality failures"
with col2:
    if st.button("Which tables are undocumented?"):
        st.session_state.suggested = "Which tables are undocumented?"
    if st.button("Show all pipelines"):
        st.session_state.suggested = "Show all pipelines"

st.divider()

# ── Chat History ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle Suggested Question ──────────────────────────────────
if "suggested" in st.session_state:
    prompt = st.session_state.suggested
    del st.session_state.suggested

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

# ── Chat Input ─────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your data platform..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })