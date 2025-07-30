# DACP - Delcarative Agent Communication Protocol

A Python library for managing LLM/agent communications and tool function calls following the OAS Open Agent Specification.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import dacp

# Register a custom tool
def my_custom_tool(param1: str, param2: int) -> dict:
    return {"result": f"Processed {param1} with {param2}"}

dacp.register_tool("my_custom_tool", my_custom_tool)

# Call an LLM
response = dacp.call_llm("What is the weather like today?")

# Parse agent response
parsed = dacp.parse_agent_response(response)

# Check if it's a tool request
if dacp.is_tool_request(parsed):
    tool_name, args = dacp.get_tool_request(parsed)
    result = dacp.run_tool(tool_name, args)
    tool_response = dacp.wrap_tool_result(tool_name, result)
```

## Features

- **Tool Registry**: Register and manage custom tools for LLM agents
- **LLM Integration**: Built-in support for OpenAI models (extensible)
- **Protocol Parsing**: Parse and validate agent responses
- **Tool Execution**: Safe execution of registered tools
- **OAS Compliance**: Follows Open Agent Specification standards

## API Reference

### Tools

- `register_tool(tool_id: str, func)`: Register a new tool
- `run_tool(tool_id: str, args: Dict) -> dict`: Execute a registered tool
- `TOOL_REGISTRY`: Access the current tool registry

### LLM

- `call_llm(prompt: str, model: str = "gpt-4") -> str`: Call an LLM with a prompt

### Protocol

- `parse_agent_response(response: str | dict) -> dict`: Parse agent response
- `is_tool_request(msg: dict) -> bool`: Check if message is a tool request
- `get_tool_request(msg: dict) -> tuple[str, dict]`: Extract tool request details
- `wrap_tool_result(name: str, result: dict) -> dict`: Wrap tool result for agent
- `is_final_response(msg: dict) -> bool`: Check if message is a final response
- `get_final_response(msg: dict) -> dict`: Extract final response

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License
