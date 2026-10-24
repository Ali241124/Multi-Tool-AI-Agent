
import json

import ollama

from agent.tool_registry import (
    AVAILABLE_FUNCTIONS,
    TOOL_SCHEMAS,
)


MODEL_NAME = "qwen2.5:7b"

SYSTEM_PROMPT = """
You are a helpful multi-tool AI assistant.

You can use these tools:
- calculator: mathematical calculations
- get_current_datetime: current local date and time
- web_search: information from the internet
- get_weather: current weather for a city

Use the appropriate tools when needed.
For current information, prefer web search.
For calculations, use the calculator.
For weather questions, use the weather tool.

Never claim that a tool succeeded unless its result
confirms the success.

After receiving tool results, explain the answer clearly.
If a tool fails, explain the limitation honestly.
"""


def run_agent(question: str) -> str:
    """Run the AI agent and return its final answer."""

    if not question.strip():
        return "Please enter a question."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    # Prevent endless tool-calling loops.
    max_iterations = 5

    for _ in range(max_iterations):
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        assistant_message = response.message
        messages.append(assistant_message)

        tool_calls = assistant_message.tool_calls or []

        # No tool requested: the model has produced its answer.
        if not tool_calls:
            return assistant_message.content or (
                "The model returned an empty response."
            )

        # Execute each tool requested by the model.
        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            print(f"\n[Agent selected tool: {name}]")
            print(f"[Arguments: {arguments}]")

            function = AVAILABLE_FUNCTIONS.get(name)

            if function is None:
                result = {"error": "Unknown tool requested."}
            else:
                try:
                    # Validate the tool name through the registry.
                    output = function(**arguments)
                    result = {"result": output}

                except Exception as error:
                    # Report failure to the model instead of crashing.
                    result = {
                        "error": (
                            f"{type(error).__name__}: {error}"
                        )
                    }

            messages.append(
                {
                    "role": "tool",
                    "tool_name": name,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    ),
                }
            )

    return (
        "I reached the tool-call limit. "
        "Please simplify your question and try again."
    )
