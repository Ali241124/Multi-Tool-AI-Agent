
import json
import ollama

from agent.tool_registry import AVAILABLE_FUNCTIONS, TOOL_SCHEMAS
from agent.memory import (
    load_conversation,
    save_conversation,
    delete_conversation,
)


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


def validate_tool_arguments(name: str, arguments) -> None:
    """Validate tool names and arguments against their schemas."""

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
            f"Unexpected arguments: {', '.join(sorted(unknown_arguments))}"
        )

    missing_arguments = set(required) - set(arguments)

    if missing_arguments:
        raise ValueError(
            f"Missing arguments: {', '.join(sorted(missing_arguments))}"
        )


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


def reset_conversation(conversation_id: str = "default") -> None:
    """Delete a conversation and its saved history."""

    delete_conversation(conversation_id)


def run_agent(
    question: str,
    conversation_id: str = "default",
    on_tool_event=None,
) -> str:
    """
    Run the AI agent with conversation memory and tool support.

    on_tool_event is an optional callback used by the UI to report
    tool execution progress. Existing callers do not need to change.
    """

    def notify_tool_event(
        message: str,
        state: str = "running",
    ) -> None:
        """Send a progress event to the UI when a callback is provided."""

        if on_tool_event is None:
            return

        try:
            on_tool_event(message, state)
        except Exception:
            # UI reporting errors should not crash the agent.
            pass

    # 1. Validate user input.
    if not isinstance(question, str) or not question.strip():
        return "Please enter a valid question."

    if (
        not isinstance(conversation_id, str)
        or not conversation_id.strip()
    ):
        return "Please provide a valid conversation ID."

    conversation_id = conversation_id.strip()
    question = question.strip()

    # 2. Load the conversation's saved messages.
    try:
        messages = load_conversation(conversation_id)

    except Exception as error:
        return (
            "I couldn't load the conversation history. "
            f"Details: {type(error).__name__}: {error}"
        )

    if messages is None:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

    elif not messages or messages[0].get("role") != "system":
        messages.insert(
            0,
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
        )

    # 3. Add the user's question.
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        save_conversation(conversation_id, messages)

    except Exception as error:
        return (
            "I couldn't save the conversation. "
            f"Details: {type(error).__name__}: {error}"
        )

    # 4. Let the model decide whether it needs tools.
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

        if hasattr(assistant_message, "model_dump"):
            assistant_dict = assistant_message.model_dump(
                exclude_none=True
            )
        else:
            assistant_dict = assistant_message

        messages.append(assistant_dict)

        try:
            save_conversation(conversation_id, messages)

        except Exception as error:
            return (
                "The assistant responded, but I couldn't save "
                "the conversation. "
                f"Details: {type(error).__name__}: {error}"
            )

        # 5. If the model did not request tools, return its answer.
        tool_calls = assistant_dict.get("tool_calls") or []

        if not tool_calls:
            answer = (
                assistant_dict.get("content")
                or "The model returned an empty response."
            )

            return answer

        # 6. Prevent excessive tool calls in a single response.
        if len(tool_calls) > MAX_TOOL_CALLS_PER_RESPONSE:
            return (
                "The model requested too many tools at once. "
                "Please try a simpler question."
            )

        # 7. Execute each requested tool.
        for tool_call in tool_calls:
            function_details = tool_call.get("function", {})

            name = function_details.get("name", "")
            arguments = function_details.get("arguments", {})

            print(f"\n[Agent selected tool: {name}]")
            print(f"[Arguments: {arguments}]")

            notify_tool_event(
                f"Using tool: {name}",
                "running",
            )

            result = execute_tool(name, arguments)

            if "error" in result:
                print(f"[Tool error: {result['error']}]")

                notify_tool_event(
                    f"{name} failed: {result['error']}",
                    "error",
                )

            else:
                print("[Tool executed successfully]")

                notify_tool_event(
                    f"{name} completed successfully",
                    "complete",
                )

            # 8. Give the tool's result back to the model.
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

            try:
                save_conversation(conversation_id, messages)

            except Exception as error:
                return (
                    "The tool ran, but I couldn't save its result. "
                    f"Details: {type(error).__name__}: {error}"
                )

    # 9. Stop if the model exceeds the iteration limit.
    return (
        f"I reached the limit of {MAX_ITERATIONS} agent iterations "
        "without completing the answer. Please try a simpler question."
    )
