# agent-repl-chat

A beautiful terminal chat interface for OpenAI agents with rich markdown support and an elegant UI.

## Installation

Install from PyPI:

```bash
pip install agent-repl-chat
```

Or install in development mode using uv:

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
    model="gpt-4.1-mini"
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

### Setup for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agent-repl-chat.git
   cd agent-repl-chat
   ```

2. Install in development mode:
   ```bash
   uv pip install -e .
   ```

3. Run the example:
   ```bash
   uv run example.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (2025-01-XX)
- Initial release
- Beautiful terminal chat interface
- Rich markdown support
- Conversation continuity
- Interactive commands (quit, new chat)
- Async support for responsive interactions 