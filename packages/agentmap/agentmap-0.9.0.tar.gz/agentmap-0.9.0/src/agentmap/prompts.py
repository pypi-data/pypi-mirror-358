"""
Prompts module for AgentMap.

This module provides convenient access to prompt management functionality.
Re-exports key functions from the prompt manager service for backward compatibility.
"""

from agentmap.services.prompt_manager_service import (
    format_prompt,
    get_formatted_prompt,
    get_prompt_manager,
    resolve_prompt,
)

__all__ = [
    "get_formatted_prompt",
    "resolve_prompt",
    "format_prompt",
    "get_prompt_manager",
]
