
import json
import sqlite3

from pathlib import Path


# Store the database in the main project folder.
DATABASE_PATH = Path(__file__).resolve().parent.parent / "agent_memory.db"


def initialize_database() -> None:
    """Create the conversation table if it does not exist."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
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
    """Save conversation messages as JSON in SQLite."""

    serializable_messages = []

    for message in messages:
        if hasattr(message, "model_dump"):
            message = message.model_dump(exclude_none=True)

        serializable_messages.append(message)

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
                updated_at
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(conversation_id)
            DO UPDATE SET
                messages = excluded.messages,
                updated_at = CURRENT_TIMESTAMP
            """,
            (conversation_id, messages_json),
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
    """Return conversation IDs and their last update times."""

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT conversation_id, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
