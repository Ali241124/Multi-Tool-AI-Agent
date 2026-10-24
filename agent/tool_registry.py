
from tools.calculator import calculator
from tools.datetime_tool import get_current_datetime
from tools.web_search import web_search
from tools.weather_tool import get_weather


# Functions the agent is allowed to execute.
AVAILABLE_FUNCTIONS = {
    "calculator": calculator,
    "get_current_datetime": get_current_datetime,
    "web_search": web_search,
    "get_weather": get_weather,
}


# Descriptions that tell the LLM when to use each tool.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Perform arithmetic: add, subtract, "
                "multiply, or divide two numbers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["operation", "a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current local date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet for information, "
                "especially recent information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results, from 1 to 10.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Retrieve current weather conditions for a city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city.",
                    },
                },
                "required": ["city"],
            },
        },
    },
]
