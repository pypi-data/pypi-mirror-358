from langchain_core.tools import Tool
from typing import Callable, Dict, Any
import json

# In‐process registry of all dynamic tools
dynamic_registry: Dict[str, Tool] = {}
dynamic_info: Dict[str, str] = {}


def register_tool(name: str, func: Callable, description: str) -> None:
    """Add a new Tool to the in‐memory registry."""
    dynamic_registry[name] = Tool(name=name, func=func, description=description)
    dynamic_info[name] = description


def dynamic_tool_lister(*args) -> str:
    return json.dumps(dynamic_info)


def dynamic_execute(input_str: str) -> Any:
    """
    Expects a JSON string with:
      - "tool_name": name of the registered tool
      - "args": a dict of arguments to pass to that tool
    Returns the tool's output or an error message.
    """
    # Parse the JSON input
    try:
        payload = json.loads(input_str)
        tool_name = payload.get("tool_name")
        args = payload.get("args", {})
    except Exception as e:
        return f"Error parsing input JSON: {e}"

    # Lookup the tool
    if tool_name not in dynamic_registry:
        return f"Tool '{tool_name}' not found."

    tool = dynamic_registry[tool_name]

    # Execute the tool
    try:
        return tool.func(**args)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {e}"


# Single entry-point tool for your supervisor
dynamic_invoker = Tool(
    name="user_generated_tool_invoker",
    func=dynamic_execute,
    description=(
        "Invoke any user created tool by passing a JSON string. "
        "The JSON must contain 'tool_name' (string) and 'args' (object), "
        "for example: "
        "{\"tool_name\": \"my_tool\", \"args\": {\"param1\": \"value1\"}}."
    ),
)

dynamic_lister = Tool(
    name="user_generated_tool_lister",
    func=dynamic_tool_lister,
    description=(
        "This function takes no arguments and returns all the function names and descriptions of the user generated"
        "tools."
    ),
)
