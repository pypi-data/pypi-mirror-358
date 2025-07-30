from typing import Dict, Any, Callable

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {}


def register_tool(tool_id: str, func: Callable[..., Dict[str, Any]]) -> None:
    """Register a tool function."""
    TOOL_REGISTRY[tool_id] = func


def run_tool(tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a registered tool with the given arguments."""
    if tool_id not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_id}")
    tool_func = TOOL_REGISTRY[tool_id]
    return tool_func(**args)


# --- Example tool ---
def file_writer(path: str, content: str) -> dict:
    # Only allow paths in /tmp or ./output for now!
    allowed_prefixes = ["./output/", "/tmp/"]
    if not any(path.startswith(prefix) for prefix in allowed_prefixes):
        raise ValueError("Path not allowed")
    with open(path, "w") as f:
        f.write(content)
    return {"result": f"Written to {path}"}


register_tool("file_writer", file_writer)
