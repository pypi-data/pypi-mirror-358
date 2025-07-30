# repl-chat

A beautiful terminal chat interface for OpenAI agents with rich markdown support and an elegant UI.

## Installation

Install in development mode using uv:

```bash
uv pip install -e .
```

## Usage

```python
from repl_chat import start_chat
from agents import Agent

# Create your agent
agent = Agent(
    name="My Assistant",
    instructions="You are a helpful assistant that provides clear and concise answers.",
    model="gpt-4"
)

# Start the chat interface
start_chat(agent)
```

## Features

- 🎨 Beautiful terminal interface with rich markdown rendering
- 🔄 Conversation continuity with response threading
- ⌨️ Interactive commands:
  - `q`, `quit`, or `exit` - Quit the chat
  - `n` or `new` - Start a new conversation
- 🤖 Works with any OpenAI Agent configuration
- ⚡ Async support for responsive interactions

## Requirements

- Python 3.11+
- openai-agents
- prompt-toolkit
- rich

## Development

The package follows Python packaging best practices with a `src/` layout for clean imports and development workflows. 