
import json
import sqlite3

from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent / "agent_memory.db"
)


def initialize_database() -> None:
    """Create the conversation table and migrate older databases."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL DEFAULT 'New chat'
            )
            """
        )

        # Add the title column to databases created by older versions.
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        }

        if "title" not in columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN title TEXT NOT NULL DEFAULT 'New chat'
                """
            )


def load_conversation(conversation_id: str):
    """Load saved messages, or return None for a new conversation."""

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT messages
            FROM conversations
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

    if row is None:
        return None

    return json.loads(row[0])


def save_conversation(conversation_id: str, messages: list) -> None:
    """Save messages and derive a title from the first user message."""

    serializable_messages = []

    for message in messages:
        if hasattr(message, "model_dump"):
            message = message.model_dump(exclude_none=True)

        serializable_messages.append(message)

    # Find the first actual user message for the chat title.
    first_user_message = next(
        (
            message.get("content", "").strip()
            for message in serializable_messages
            if isinstance(message, dict)
            and message.get("role") == "user"
            and isinstance(message.get("content"), str)
            and message.get("content", "").strip()
        ),
        "New chat",
    )

    # Keep titles compact for the sidebar.
    title = " ".join(first_user_message.split())

    if len(title) > 40:
        title = title[:37].rstrip() + "..."

    messages_json = json.dumps(
        serializable_messages,
        ensure_ascii=False,
        default=str,
    )

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO conversations (
                conversation_id,
                messages,
                updated_at,
                title
            )
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(conversation_id)
            DO UPDATE SET
                messages = excluded.messages,
                updated_at = CURRENT_TIMESTAMP,
                title = excluded.title
            """,
            (conversation_id, messages_json, title),
        )


def delete_conversation(conversation_id: str) -> None:
    """Delete one saved conversation."""

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            DELETE FROM conversations
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )


def list_conversations() -> list[dict]:
    """Return saved conversations, newest first."""

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT conversation_id, title, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
