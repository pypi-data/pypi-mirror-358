"""
Example usage of the agent-repl-chat package with different agent configurations.

To run this example:
1. First install the package: pip install agent-repl-chat
2. Then run: python example.py
"""

from repl_chat import start_chat
from agents import Agent

def create_math_tutor():
    """Create a math tutor agent"""
    return Agent(
        name="Math Tutor",
        instructions="You are a helpful math tutor. Explain concepts clearly and provide step-by-step solutions.",
        model="gpt-4"
    )

def create_code_assistant():
    """Create a coding assistant agent"""
    return Agent(
        name="Code Assistant", 
        instructions="You are an expert programming assistant. Help with code, debugging, and best practices.",
        model="gpt-4"
    )

def create_creative_writer():
    """Create a creative writing assistant agent"""
    return Agent(
        name="Creative Writer",
        instructions="You are a creative writing assistant. Help with stories, poetry, and creative expression.",
        model="gpt-4"
    )

if __name__ == "__main__":
    # You can uncomment any of these to try different agents:
    
    # Math tutor example
    agent = create_math_tutor()
    
    # Code assistant example
    # agent = create_code_assistant()
    
    # Creative writer example
    # agent = create_creative_writer()
    
    # Start the chat with your chosen agent
    start_chat(agent) 