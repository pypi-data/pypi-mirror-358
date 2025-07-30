import pytest
from dacp.tools import register_tool, run_tool, TOOL_REGISTRY


def test_register_tool():
    """Test registering a tool."""

    def test_tool(param1: str, param2: int) -> dict:
        return {"result": f"Processed {param1} with {param2}"}

    register_tool("test_tool", test_tool)
    assert "test_tool" in TOOL_REGISTRY
    assert TOOL_REGISTRY["test_tool"] == test_tool


def test_run_tool():
    """Test running a registered tool."""

    def test_tool(param1: str, param2: int) -> dict:
        return {"result": f"Processed {param1} with {param2}"}

    register_tool("test_tool", test_tool)
    result = run_tool("test_tool", {"param1": "hello", "param2": 42})
    assert result["result"] == "Processed hello with 42"


def test_run_nonexistent_tool():
    """Test running a tool that doesn't exist."""
    with pytest.raises(ValueError):
        run_tool("nonexistent_tool", {})


def test_tool_with_no_args():
    """Test running a tool with no arguments."""

    def no_args_tool() -> dict:
        return {"result": "success"}

    register_tool("no_args_tool", no_args_tool)
    result = run_tool("no_args_tool", {})
    assert result["result"] == "success"


def test_tool_with_optional_args():
    """Test running a tool with optional arguments."""

    def optional_args_tool(required: str, optional: str = "default") -> dict:
        return {"result": f"{required}:{optional}"}

    register_tool("optional_args_tool", optional_args_tool)

    # Test with both args
    result = run_tool("optional_args_tool", {"required": "test", "optional": "custom"})
    assert result["result"] == "test:custom"

    # Test with only required arg
    result = run_tool("optional_args_tool", {"required": "test"})
    assert result["result"] == "test:default"


def test_clear_tool_registry():
    """Test that we can clear and re-register tools."""

    def test_tool() -> dict:
        return {"result": "test"}

    register_tool("test_tool", test_tool)
    assert "test_tool" in TOOL_REGISTRY

    # Clear registry
    TOOL_REGISTRY.clear()
    assert "test_tool" not in TOOL_REGISTRY
