
import uuid

import streamlit as st

from agent.core import run_agent, reset_conversation
from agent.memory import load_conversation, list_conversations


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Multi-Tool AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Custom styling
# -----------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #101114;
    }

    [data-testid="stSidebar"] {
        background-color: #17181d;
        border-right: 1px solid #292a30;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #292a30;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = uuid.uuid4().hex[:8]


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.title("🤖 Agent Desk")
    st.caption("Your personal multi-tool assistant")

    if st.button("＋  New chat", use_container_width=True):
        st.session_state.conversation_id = uuid.uuid4().hex[:8]
        st.rerun()

    st.divider()

    st.subheader("Recent chats")

    try:
        conversations = list_conversations()
    except Exception as error:
        conversations = []
        st.error(f"Could not load chats: {error}")

    if not conversations:
        st.caption("Your conversations will appear here.")
    else:
        for conversation in conversations:
            chat_id = conversation["conversation_id"]
            is_current = (
                chat_id == st.session_state.conversation_id
            )

            label = (
                f"●  {chat_id}"
                if is_current
                else f"    {chat_id}"
            )

            if st.button(
                label,
                key=f"chat_{chat_id}",
                use_container_width=True,
            ):
                st.session_state.conversation_id = chat_id
                st.rerun()

    st.divider()

    st.caption("Available tools")
    st.markdown(
        """
        - 🧮 Calculator
        - 🕒 Date and time
        - 🌐 Web search
        - 🌦️ Weather
        """
    )

    if st.button(
        "Delete current chat",
        use_container_width=True,
    ):
        chat_id = st.session_state.conversation_id

        try:
            reset_conversation(chat_id)
            st.session_state.conversation_id = uuid.uuid4().hex[:8]
            st.rerun()
        except Exception as error:
            st.error(f"Could not delete conversation: {error}")


# -----------------------------
# Main chat area
# -----------------------------

st.title("Multi-Tool AI Agent")
st.caption(
    "Ask questions, use tools, and continue conversations "
    "without losing your saved history."
)

current_id = st.session_state.conversation_id

st.caption(f"Conversation ID: `{current_id}`")


# Load persisted messages for the active conversation.
try:
    messages = load_conversation(current_id) or []
except Exception as error:
    st.error(f"Could not load conversation: {error}")
    messages = []


# Display user and assistant messages.
for message in messages:
    role = message.get("role")
    content = message.get("content", "")

    if role not in {"user", "assistant"}:
        continue

    if not isinstance(content, str) or not content.strip():
        continue

    with st.chat_message(role):
        st.markdown(content)


# -----------------------------
# User input
# -----------------------------

question = st.chat_input("Ask me anything...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and using tools if needed..."):
            try:
                answer = run_agent(
                    question,
                    conversation_id=current_id,
                )
                st.markdown(answer)

            except Exception as error:
                st.error(
                    f"Something went wrong: "
                    f"{type(error).__name__}: {error}"
                )

    # Reload the database-backed history on the next rerun.
    st.rerun()
