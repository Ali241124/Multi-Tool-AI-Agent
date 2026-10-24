
import json
import ollama

from agent.tool_registry import AVAILABLE_FUNCTIONS, TOOL_SCHEMAS

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

Never claim a tool succeeded unless its result confirms success.
After receiving tool results, explain the answer clearly.
If a tool fails, explain the limitation honestly.
"""


def validate_tool_arguments(name: str, arguments) -> None:
    """Check tool arguments before executing a tool."""

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


def run_agent(question: str) -> str:
    """Run the agent until it produces a final answer."""

    if not isinstance(question, str) or not question.strip():
        return "Please enter a valid question."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question.strip()},
    ]

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
        messages.append(assistant_message)

        tool_calls = assistant_message.tool_calls or []

        # No tool calls means the model has produced its final answer.
        if not tool_calls:
            return (
                assistant_message.content
                or "The model returned an empty response."
            )

        if len(tool_calls) > MAX_TOOL_CALLS_PER_RESPONSE:
            return (
                "The model requested too many tools at once. "
                "Please try a simpler question."
            )

        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            print(f"\n[Agent selected tool: {name}]")
            print(f"[Arguments: {arguments}]")

            result = execute_tool(name, arguments)

            if "error" in result:
                print(f"[Tool error: {result['error']}]")
            else:
                print("[Tool executed successfully]")

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
        f"I reached the limit of {MAX_ITERATIONS} "
        "agent iterations without completing the answer. "
        "Please try a simpler question."
    )
