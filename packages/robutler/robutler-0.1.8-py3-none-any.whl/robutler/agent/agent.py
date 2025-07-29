"""
RobutlerAgent - Enhanced OpenAI Agent with cost tracking and finalization callbacks

This module provides a RobutlerAgent class that extends the OpenAI Agent with:
- Automatic cost calculation based on token usage
- Finalization callbacks for usage tracking
- Intent classification support
- Credit-based pricing model
"""

from typing import List, Optional, Dict, Any, Callable
from functools import wraps
import time
import logging
from datetime import datetime

# Import OpenAI Agents SDK
from agents import Agent

# Set up logger
logger = logging.getLogger(__name__)

class RobutlerAgent(Agent):
    """
    Enhanced OpenAI Agent with cost tracking and finalization callbacks.
    
    This class extends the OpenAI Agent to add:
    - Automatic cost calculation based on token usage
    - Finalization callbacks that are automatically registered with the Server
    - Intent classification support
    - Credit-based pricing model
    
    Args:
        name: Agent name
        instructions: Agent instructions/system prompt
        model: Model to use (default: gpt-4o-mini)
        tools: List of tools/functions available to the agent
        credits_per_token: Optional cost per token in credits
        credits_per_call: Optional fixed cost per call in credits
        intents: Optional list of intent strings this agent handles
        min_balance: Optional minimum credit balance required to use this agent
        **kwargs: Additional arguments passed to the base Agent class
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-4o-mini",
        tools: Optional[List] = None,
        credits_per_token: Optional[float] = None,
        credits_per_call: Optional[float] = None,
        intents: Optional[List[str]] = None,
        min_balance: int = 0,
        **kwargs
    ):
        # Initialize the base OpenAI Agent
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or [],
            **kwargs
        )
        
        # Store RobutlerAgent-specific attributes
        self.credits_per_token = credits_per_token
        self.credits_per_call = credits_per_call
        self.intents = intents or []
        self.min_balance = min_balance
    

    
    def has_intent(self, intent: str) -> bool:
        """
        Check if this agent handles a specific intent.
        
        Args:
            intent: Intent string to check
            
        Returns:
            True if the agent handles this intent
        """
        return intent in self.intents
    
    def add_intent(self, intent: str) -> None:
        """
        Add an intent to this agent.
        
        Args:
            intent: Intent string to add
        """
        if intent not in self.intents:
            self.intents.append(intent)
    
    def remove_intent(self, intent: str) -> None:
        """
        Remove an intent from this agent.
        
        Args:
            intent: Intent string to remove
        """
        if intent in self.intents:
            self.intents.remove(intent)
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Get pricing information for this agent.
        
        Returns:
            Dictionary containing pricing configuration
        """
        return {
            'credits_per_token': self.credits_per_token,
            'credits_per_call': self.credits_per_call,
            'min_balance': self.min_balance,
            'has_pricing': self.credits_per_token is not None or self.credits_per_call is not None
        }
    
    def __repr__(self) -> str:
        """String representation of the RobutlerAgent."""
        pricing = []
        if self.credits_per_call is not None:
            pricing.append(f"{self.credits_per_call} credits/call")
        if self.credits_per_token is not None:
            pricing.append(f"{self.credits_per_token} credits/token")
        
        pricing_str = f" ({', '.join(pricing)})" if pricing else " (free)"
        intents_str = f" intents={self.intents}" if self.intents else ""
        
        return f"RobutlerAgent(name='{self.name}', model='{self.model}'{pricing_str}{intents_str})"


