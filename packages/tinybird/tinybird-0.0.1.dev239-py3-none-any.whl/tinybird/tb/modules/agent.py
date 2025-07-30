import os
import sys
from typing import Any, Dict, Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from tinybird.tb.client import TinyB
from tinybird.tb.modules.common import _get_tb_client
from tinybird.tb.modules.feedback_manager import FeedbackManager


def agent_banner():
    # Define gradient colors (teal/turquoise range)
    colors = [
        "\033[38;2;0;128;128m",  # Teal
        "\033[38;2;0;150;136m",  # Teal-ish
        "\033[38;2;20;160;145m",  # Turquoise blend
        "\033[38;2;40;170;155m",  # Light turquoise
        "\033[38;2;60;180;165m",  # Lighter turquoise
        "\033[38;2;80;190;175m",  # Very light turquoise
    ]
    reset = "\033[0m"

    # The Tinybird Code ASCII art banner
    banner = [
        "  ████████╗██╗███╗   ██╗██╗   ██╗██████╗ ██╗██████╗ ██████╗     ██████╗ ██████╗ ██████╗ ███████╗",
        "  ╚══██╔══╝██║████╗  ██║╚██╗ ██╔╝██╔══██╗██║██╔══██╗██╔══██╗   ██╔════╝██╔═══██╗██╔══██╗██╔════╝",
        "     ██║   ██║██╔██╗ ██║ ╚████╔╝ ██████╔╝██║██████╔╝██║  ██║   ██║     ██║   ██║██║  ██║█████╗  ",
        "     ██║   ██║██║╚██╗██║  ╚██╔╝  ██╔══██╗██║██╔══██╗██║  ██║   ██║     ██║   ██║██║  ██║██╔══╝  ",
        "     ██║   ██║██║ ╚████║   ██║   ██████╔╝██║██║  ██║██████╔╝   ╚██████╗╚██████╔╝██████╔╝███████╗",
        "     ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝",
    ]

    # Print each line with a smooth horizontal gradient
    for line in banner:
        colored_line = ""
        for j, char in enumerate(line):
            # Skip coloring spaces
            if char == " ":
                colored_line += char
                continue

            # Calculate color index for a smooth gradient
            color_index = min(int(j * len(colors) / len(line)), len(colors) - 1)
            colored_line += f"{colors[color_index]}{char}"

        click.echo(colored_line + reset)


def explore_data(client: TinyB, prompt: str):
    click.echo(FeedbackManager.highlight(message="\nExploring data...\n"))
    result = client.explore_data(prompt)
    click.echo(result)


def run_agent_shell(config: Dict[str, Any]):
    style = Style.from_dict({"prompt": "fg:#34D399 bold"})
    history: Optional[FileHistory] = None
    try:
        history_file = os.path.expanduser("~/.tb_agent_history")
        history = FileHistory(history_file)
    except Exception:
        pass
    workspace_name = config.get("name", "No workspace found")
    session: PromptSession = PromptSession(history=history)
    user_input = session.prompt([("class:prompt", f"\ntb ({workspace_name}) » ")], style=style)
    if user_input == "exit":
        sys.exit(0)
    else:
        client = _get_tb_client(config.get("token", None), config["host"])
        explore_data(client, user_input)
        return run_agent_shell(config)


def run_agent(config: Dict[str, Any]):
    agent_banner()
    run_agent_shell(config)
