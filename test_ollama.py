
import ollama


response = ollama.chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": "Explain what an AI agent is in two sentences.",
        }
    ],
)

print(response.message.content)
