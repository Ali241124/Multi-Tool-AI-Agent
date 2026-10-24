
import uuid

import streamlit as st

from agent.core import run_agent, reset_conversation
from agent.memory import (
    load_conversation,
    list_conversations,
    rename_conversation,
)


st.set_page_config(
    page_title="Multi-Tool AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------- STYLING --------------------

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


# -------------------- SESSION STATE --------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = uuid.uuid4().hex[:8]


def create_new_chat() -> None:
    """Start a new conversation without deleting saved chats."""

    st.session_state.conversation_id = uuid.uuid4().hex[:8]


def delete_chat(conversation_id: str) -> None:
    """Delete a saved chat and select a fresh chat if necessary."""

    reset_conversation(conversation_id)

    if st.session_state.conversation_id == conversation_id:
        create_new_chat()


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.title("🤖 Agent Desk")
    st.caption("Your personal multi-tool assistant")

    if st.button(
        "＋  New chat",
        use_container_width=True,
    ):
        create_new_chat()
        st.rerun()

    st.divider()
    st.subheader("Recent chats")

    try:
        conversations = list_conversations()

    except Exception as error:
        conversations = []
        st.error(f"Could not load saved chats: {error}")

    if not conversations:
        st.caption("Your saved conversations will appear here.")

    for conversation in conversations:
        chat_id = conversation["conversation_id"]
        title = conversation.get("title") or "New chat"

        is_current = (
            chat_id == st.session_state.conversation_id
        )

        # Select a conversation.
        label = f"●  {title}" if is_current else title

        if st.button(
            label,
            key=f"select_chat_{chat_id}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            st.session_state.conversation_id = chat_id
            st.rerun()

        # Rename and delete controls for this conversation.
        with st.expander(
            "Manage chat",
            expanded=False,
        ):
            st.caption(f"ID: {chat_id}")

            with st.form(
                key=f"rename_form_{chat_id}",
            ):
                new_title = st.text_input(
                    "Conversation title",
                    value=title,
                    max_chars=80,
                    key=f"title_input_{chat_id}",
                )

                rename_submitted = st.form_submit_button(
                    "Save title",
                    use_container_width=True,
                )

            if rename_submitted:
                try:
                    rename_conversation(
                        chat_id,
                        new_title,
                    )

                    st.success("Chat renamed.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not rename chat: {error}")

            st.divider()

            confirm_delete = st.checkbox(
                "I want to delete this conversation",
                key=f"confirm_delete_{chat_id}",
            )

            if st.button(
                "Delete this chat",
                key=f"delete_chat_{chat_id}",
                use_container_width=True,
                disabled=not confirm_delete,
            ):
                try:
                    delete_chat(chat_id)
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not delete chat: {error}")

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


# -------------------- MAIN CHAT --------------------

current_id = st.session_state.conversation_id

st.title("Multi-Tool AI Agent")
st.caption(
    "Ask questions, use tools, and continue conversations "
    "without losing your saved history."
)

st.caption(f"Conversation ID: `{current_id}`")


# Load the currently selected conversation.
try:
    messages = load_conversation(current_id) or []

except Exception as error:
    st.error(
        "I couldn't load this conversation's history. "
        "Your saved database has not been intentionally deleted. "
        f"Details: {type(error).__name__}: {error}"
    )
    messages = []


# Display only user-visible messages.
for message in messages:
    role = message.get("role")
    content = message.get("content", "")

    if role not in {"user", "assistant"}:
        continue

    if not isinstance(content, str) or not content.strip():
        continue

    with st.chat_message(role):
        st.markdown(content)


# -------------------- CHAT INPUT --------------------

question = st.chat_input("Ask me anything...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        status = st.status(
            "Thinking...",
            expanded=True,
        )

        def report_tool_event(
            message: str,
            state: str = "running",
        ) -> None:
            """Display tool activity while the agent is running."""

            status.write(message)

            if state == "error":
                status.update(
                    label="A tool encountered an error",
                    state="error",
                    expanded=True,
                )

            elif state == "complete":
                status.update(
                    label="Tool completed",
                    state="running",
                    expanded=True,
                )

        try:
            answer = run_agent(
                question,
                conversation_id=current_id,
                on_tool_event=report_tool_event,
            )

            status.update(
                label="Response ready",
                state="complete",
                expanded=False,
            )

            st.markdown(answer)

        except Exception as error:
            status.update(
                label="Something went wrong",
                state="error",
                expanded=True,
            )

            st.error(
                f"{type(error).__name__}: {error}"
            )

    st.rerun()
