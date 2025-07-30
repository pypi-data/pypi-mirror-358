from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from agents import Agent, Runner, RunResult
import sys
import asyncio

console = Console()
session = PromptSession("User: ")


def display_welcome(agent: Agent):
    """Display a beautiful welcome message using the agent's name"""
    welcome_text = Text()
    welcome_text.append(f"🤖 {agent.name}", style="bold cyan")
    
    console.print(welcome_text)
    
    commands_text = Text()
    commands_text.append("n", style="bold green")
    commands_text.append(" - new chat, ", style="dim")
    commands_text.append("q", style="bold red")
    commands_text.append(" - quit\n", style="dim")
    
    console.print(commands_text)


def clear_previous_line():
    """Clear the previous line"""
    sys.stdout.write("\033[1A\033[0J")
    sys.stdout.flush()


async def async_respond(agent: Agent, input: str, previous_response_id: str = None) -> tuple[str, str]:
    """Async function to get agent response"""
    result: RunResult = await Runner.run(agent, input, previous_response_id=previous_response_id, max_turns=1000)
    response_id = result.last_response_id
    return response_id, result.final_output


def respond(agent: Agent, input: str, previous_response_id: str = None) -> tuple[str, str]:
    """Sync wrapper for async_respond"""
    return asyncio.run(async_respond(agent, input, previous_response_id))


def start_chat(agent: Agent):
    """Start an interactive chat session with the provided agent"""
    previous_response_id: str = None
    
    console.clear()
    display_welcome(agent)
    
    while True:
        try:
            prompt: str = session.prompt()
            console.print("\n")
            if prompt.lower() in {"q", "quit", "exit"}:
                break
            if prompt.lower() in {"n", "new"}:
                previous_response_id = None
                console.clear()
                display_welcome(agent)
                continue
        except (EOFError, KeyboardInterrupt):
            break

        with console.status("[bold yellow]thinking...", spinner="dots"):
            response_id, response_text = respond(agent, prompt, previous_response_id)
        
        console.print(f"[bold blue]Assistant:")
        console.print(Markdown(response_text))
        console.print("\n")
        previous_response_id = response_id 