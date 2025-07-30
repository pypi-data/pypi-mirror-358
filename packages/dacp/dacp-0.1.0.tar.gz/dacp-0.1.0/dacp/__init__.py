"""
DACP - Declarative Agent Communication Protocol

A Python library for managing LLM/agent communications and tool function calls
following the OAS Open Agent Specification.
"""

from .tools import register_tool, run_tool, TOOL_REGISTRY
from .llm import call_llm
from .protocol import (
    parse_agent_response,
    is_tool_request,
    get_tool_request,
    wrap_tool_result,
    is_final_response,
    get_final_response,
)

__version__ = "0.1.0"
__all__ = [
    "register_tool",
    "run_tool",
    "TOOL_REGISTRY",
    "call_llm",
    "parse_agent_response",
    "is_tool_request",
    "get_tool_request",
    "wrap_tool_result",
    "is_final_response",
    "get_final_response",
]
