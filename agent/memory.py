
import json
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent / "agent_memory.db"
)


def initialize_database() -> None:
    """Create the conversation table and safely update older schemas."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL DEFAULT 'New chat',
                title_custom INTEGER NOT NULL DEFAULT 0
            )
            """
        )

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

        if "title_custom" not in columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN title_custom INTEGER NOT NULL DEFAULT 0
                """
            )


def load_conversation(conversation_id: str):
    """Load and validate the saved messages for one conversation."""

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

    messages = json.loads(row[0])

    if not isinstance(messages, list):
        raise ValueError(
            "Saved conversation history must be a list of messages."
        )

    if not all(isinstance(message, dict) for message in messages):
        raise ValueError(
            "Saved conversation history contains an invalid message."
        )

    return messages


def save_conversation(
    conversation_id: str,
    messages: list,
) -> None:
    """Save messages while preserving a user-defined title."""

    if not conversation_id or not conversation_id.strip():
        raise ValueError("Conversation ID cannot be empty.")

    if not isinstance(messages, list):
        raise ValueError("Messages must be provided as a list.")

    serializable_messages = []

    for message in messages:
        if hasattr(message, "model_dump"):
            message = message.model_dump(exclude_none=True)

        if not isinstance(message, dict):
            raise ValueError("Every message must be a dictionary.")

        serializable_messages.append(message)

    first_user_message = next(
        (
            message.get("content", "").strip()
            for message in serializable_messages
            if message.get("role") == "user"
            and isinstance(message.get("content"), str)
            and message["content"].strip()
        ),
        "New chat",
    )

    # Generate a readable title from the first user message.
    generated_title = " ".join(first_user_message.split())

    if len(generated_title) > 45:
        generated_title = generated_title[:42].rstrip() + "..."

    messages_json = json.dumps(
        serializable_messages,
        ensure_ascii=False,
        default=str,
    )

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        existing = connection.execute(
            """
            SELECT title, title_custom
            FROM conversations
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

        # Keep a renamed title instead of replacing it with the question.
        if existing and existing[1] == 1:
            title = existing[0]
            title_custom = 1
        else:
            title = generated_title
            title_custom = 0

        connection.execute(
            """
            INSERT INTO conversations (
                conversation_id,
                messages,
                updated_at,
                title,
                title_custom
            )
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)

            ON CONFLICT(conversation_id)
            DO UPDATE SET
                messages = excluded.messages,
                updated_at = CURRENT_TIMESTAMP,
                title = excluded.title,
                title_custom = excluded.title_custom
            """,
            (
                conversation_id,
                messages_json,
                title,
                title_custom,
            ),
        )


def rename_conversation(
    conversation_id: str,
    new_title: str,
) -> None:
    """Rename a conversation and preserve that title on future saves."""

    if not isinstance(new_title, str):
        raise ValueError("The title must be text.")

    new_title = " ".join(new_title.split())

    if not new_title:
        raise ValueError("The title cannot be empty.")

    if len(new_title) > 80:
        raise ValueError("The title cannot exceed 80 characters.")

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            UPDATE conversations
            SET title = ?,
                title_custom = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
            """,
            (new_title, conversation_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "This conversation does not exist or has been deleted."
            )


def delete_conversation(conversation_id: str) -> None:
    """Delete a conversation and its saved message history."""

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
    """Return saved conversations, newest activity first."""

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT conversation_id, title, updated_at
            FROM conversations
            ORDER BY updated_at DESC, conversation_id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
