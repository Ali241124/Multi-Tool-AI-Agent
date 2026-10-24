
import json
import ollama

from agent.tool_registry import AVAILABLE_FUNCTIONS, TOOL_SCHEMAS
from agent.memory import (
    load_conversation,
    save_conversation,
    delete_conversation,
)


# -----------------------------
# Configuration
# -----------------------------

MODEL_NAME = "qwen2.5:7b"

MAX_ITERATIONS = 5
MAX_TOOL_CALLS_PER_RESPONSE = 4


SYSTEM_PROMPT = """
You are a helpful multi-tool AI assistant.

Available tools:
- calculator: perform mathematical calculations
- get_current_datetime: get the current date and time
- web_search: search the internet
- get_weather: get weather for a city

Use the appropriate tool when needed.
Use web search for current information.
Use the calculator for mathematical calculations.
Use the weather tool for weather questions.

Use previous conversation messages to understand follow-up questions.

Never claim a tool succeeded unless its result confirms success.
After receiving tool results, explain the answer clearly.
If a tool fails, explain the limitation honestly.
"""


# -----------------------------
# Argument Validation
# -----------------------------

def validate_tool_arguments(name: str, arguments) -> None:
    """Validate tool arguments before execution."""

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    schema = next(
        (
            item["function"]
            for item in TOOL_SCHEMAS
            if item["function"]["name"] == name
        ),
        None,
    )

    if schema is None:
        raise ValueError(f"Unknown tool: {name}")

    parameters = schema.get("parameters", {})
    properties = parameters.get("properties", {})
    required = parameters.get("required", [])

    unknown_arguments = set(arguments) - set(properties)

    if unknown_arguments:
        raise ValueError(
            f"Unexpected arguments: "
            f"{', '.join(sorted(unknown_arguments))}"
        )

    missing_arguments = set(required) - set(arguments)

    if missing_arguments:
        raise ValueError(
            f"Missing arguments: "
            f"{', '.join(sorted(missing_arguments))}"
        )


# -----------------------------
# Tool Execution
# -----------------------------

def execute_tool(name: str, arguments: dict) -> dict:
    """Validate and execute a registered tool safely."""

    function = AVAILABLE_FUNCTIONS.get(name)

    if function is None:
        return {"error": f"Unknown tool requested: {name}"}

    try:
        validate_tool_arguments(name, arguments)

        output = function(**arguments)

        return {"result": output}

    except Exception as error:
        return {
            "error": f"{type(error).__name__}: {error}"
        }


# -----------------------------
# Conversation Management
# -----------------------------

def reset_conversation(
    conversation_id: str = "default",
) -> None:
    """Delete a conversation from persistent storage."""

    delete_conversation(conversation_id)


# -----------------------------
# Main Agent
# -----------------------------

def run_agent(
    question: str,
    conversation_id: str = "default",
) -> str:
    """Run the AI agent with persistent conversation memory."""

    if not isinstance(question, str) or not question.strip():
        return "Please enter a valid question."

    if not conversation_id or not conversation_id.strip():
        return "Please provide a valid conversation ID."

    conversation_id = conversation_id.strip()

    # Load existing history from SQLite.
    try:
        messages = load_conversation(conversation_id)

    except Exception as error:
        return (
            "I couldn't load the conversation history. "
            f"Details: {type(error).__name__}: {error}"
        )

    # Create a new conversation if no saved history exists.
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

    # Ensure the current system instructions are present.
    elif not messages or messages[0].get("role") != "system":
        messages.insert(
            0,
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
        )

    # Add the user's latest question.
    messages.append(
        {
            "role": "user",
            "content": question.strip(),
        }
    )

    # Save the question immediately.
    try:
        save_conversation(conversation_id, messages)

    except Exception as error:
        return (
            "I couldn't save the conversation. "
            f"Details: {type(error).__name__}: {error}"
        )

    # Ask the model to respond or select tools.
    for iteration in range(MAX_ITERATIONS):

        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOL_SCHEMAS,
            )

        except Exception as error:
            return (
                "I couldn't communicate with Ollama. "
                f"Details: {type(error).__name__}: {error}"
            )

        assistant_message = response.message

        # Convert the SDK message to a dictionary for storage
        # while preserving its tool-call information.
        if hasattr(assistant_message, "model_dump"):
            assistant_dict = assistant_message.model_dump(
                exclude_none=True
            )
        else:
            assistant_dict = assistant_message

        messages.append(assistant_dict)

        # Persist the assistant message and any tool requests.
        try:
            save_conversation(conversation_id, messages)

        except Exception as error:
            return (
                "The assistant responded, but I couldn't save "
                "the conversation. "
                f"Details: {type(error).__name__}: {error}"
            )

        tool_calls = assistant_dict.get("tool_calls") or []

        # If the model did not request tools, return its answer.
        if not tool_calls:
            answer = assistant_dict.get("content") or (
                "The model returned an empty response."
            )
            return answer

        # Prevent too many simultaneous tool requests.
        if len(tool_calls) > MAX_TOOL_CALLS_PER_RESPONSE:
            return (
                "The model requested too many tools at once. "
                "Please try a simpler question."
            )

        # Execute each requested tool.
        for tool_call in tool_calls:

            function_details = tool_call.get("function", {})
            name = function_details.get("name", "")
            arguments = function_details.get("arguments", {})

            print(f"\n[Agent selected tool: {name}]")
            print(f"[Arguments: {arguments}]")

            result = execute_tool(name, arguments)

            if "error" in result:
                print(f"[Tool error: {result['error']}]")
            else:
                print("[Tool executed successfully]")

            # Send the tool result back to the model.
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

            # Persist the tool result immediately.
            try:
                save_conversation(conversation_id, messages)

            except Exception as error:
                return (
                    "The tool ran, but I couldn't save its result. "
                    f"Details: {type(error).__name__}: {error}"
                )

    return (
        f"I reached the limit of {MAX_ITERATIONS} "
        "agent iterations without completing the answer. "
        "Please try a simpler question."
    )
