
import uuid

from agent.core import run_agent, reset_conversation
from agent.memory import list_conversations


def create_conversation_id() -> str:
    """Generate a unique ID for a new conversation."""
    return uuid.uuid4().hex[:8]


def show_recent_chats() -> None:
    """Display saved conversations."""

    conversations = list_conversations()

    if not conversations:
        print("\nNo saved conversations yet.\n")
        return

    print("\nRecent conversations:")

    for index, conversation in enumerate(conversations, start=1):
        print(
            f"{index}. ID: {conversation['conversation_id']} "
            f"| Updated: {conversation['updated_at']}"
        )

    print()


def main() -> None:
    current_id = create_conversation_id()

    print("=" * 45)
    print("       MULTI-TOOL AI AGENT")
    print("=" * 45)
    print(f"Current chat ID: {current_id}")
    print("\nCommands:")
    print("  new chat       - Start a separate conversation")
    print("  chats          - Show saved conversations")
    print("  switch <id>    - Open an existing conversation")
    print("  delete chat    - Delete the current conversation")
    print("  exit           - Quit the program\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye, buddy!")
            break

        if not question:
            continue

        command = question.lower()

        if command in {"exit", "quit"}:
            print("Goodbye, buddy!")
            break

        elif command == "new chat":
            current_id = create_conversation_id()
            print(f"\nStarted a new chat. ID: {current_id}\n")
            continue

        elif command == "chats":
            show_recent_chats()
            continue

        elif command.startswith("switch "):
            requested_id = question[7:].strip()

            if not requested_id:
                print("Please provide a conversation ID.\n")
                continue

            saved_chats = list_conversations()
            known_ids = {
                chat["conversation_id"]
                for chat in saved_chats
            }

            if requested_id not in known_ids:
                print("Conversation not found. Use 'chats' to list saved chats.\n")
                continue

            current_id = requested_id
            print(f"\nSwitched to conversation: {current_id}\n")
            continue

        elif command == "delete chat":
            confirm = input(
                f"Delete conversation {current_id}? Type 'yes' to confirm: "
            ).strip().lower()

            if confirm == "yes":
                reset_conversation(current_id)
                print("Conversation deleted.")

                current_id = create_conversation_id()
                print(f"Started a fresh chat. ID: {current_id}\n")
            else:
                print("Deletion cancelled.\n")

            continue

        try:
            answer = run_agent(
                question,
                conversation_id=current_id,
            )
            print(f"\nAgent: {answer}\n")

        except Exception as error:
            print(f"\nAgent error: {type(error).__name__}: {error}\n")


if __name__ == "__main__":
    main()
