"""
A beautiful terminal chat interface for OpenAI agents.

Usage:
    from repl_chat import start_chat
    from agents import Agent
    
    agent = Agent(name="My Assistant", instructions="You are a helpful assistant.")
    start_chat(agent)
"""

from .chat import start_chat

__all__ = ["start_chat"]
__version__ = "0.1.0" 