
from agent.core import run_agent


print("Multi-Tool AI Agent")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ").strip()

    if question.lower() in {"exit", "quit"}:
        print("Goodbye, buddy!")
        break

    if not question:
        continue

    try:
        answer = run_agent(question)
        print(f"\nAgent: {answer}\n")

    except Exception as error:
        print(f"\nAgent error: {error}\n")
