import streamlit as st
from agent import run_agent

# ── Page config ──────────────────────────────────────
st.set_page_config(
    page_title="TVM Solver Agent",
    page_icon="📐",
    layout="centered"
)

# ── Header ───────────────────────────────────────────
st.title("📐 TVM Solver Agent")
st.caption(
    "Agentic AI for Aspiring Actuaries · SSSIA · "
    "Module 1: Financial Mathematics"
)

st.markdown("""
Ask any **Time Value of Money** question in plain English.

**Examples you can try:**
- *What is the PV of ₹10,000 due in 5 years at i = 6%?*
- *Find FV of ₹5,000 invested for 10 years at 8%*
- *What is the force of interest if i = 5%?*
- *Convert nominal rate 12% compounded monthly to effective*
- *How many years to double money at i = 7%?*
""")

st.divider()

# ── Chat history ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────
if prompt := st.chat_input("Type your TVM question here..."):

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent and show response
    with st.chat_message("assistant"):
        with st.spinner("Solving..."):
            response = run_agent(prompt)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
