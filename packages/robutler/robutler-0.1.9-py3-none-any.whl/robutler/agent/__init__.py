"""
RobutlerAgent - AI Agent module with OpenAI Agents SDK integration

Provides simple ways to create AI agents with credit tracking and streaming support.
"""

from .agent import RobutlerAgent

# Temporary import - will be replaced with native implementation
from agents import function_tool as tool  # TODO: Replace with native robutler tool decorator

__all__ = [
    "RobutlerAgent",
    "tool"
] 