
from agent.memory import (
    DATABASE_PATH,
    list_conversations,
    load_conversation,
)

print("Database location:", DATABASE_PATH)
print("\nSaved conversations:")

for conversation in list_conversations():
    print(conversation)

messages = load_conversation("default")

if messages:
    print("\nDefault conversation message count:", len(messages))
else:
    print("\nNo default conversation was found.")
