from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from html import escape
from prompt_toolkit.formatted_text import HTML

console = Console()

LOGO = r"""
████████╗███████╗██████╗ ███╗   ███╗ ██████╗ ██████╗ ████████╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝ ██╔══██╗╚══██╔══╝
   ██║   █████╗  ██████╔╝██╔████╔██║██║  ███╗██████╔╝   ██║
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║██╔═══╝    ██║
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║        ██║
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝        ╚═╝
"""

def gradient(text):
    start = (45, 212, 191)
    end = (167, 139, 250)

    result = Text()
    length = max(len(text), 1)

    for i, char in enumerate(text):
        ratio = i / max(length - 1, 1)

        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)

        result.append(
            char,
            style=f"bold #{r:02x}{g:02x}{b:02x}"
        )

    return result


def banner(agent, engine):
    console.clear()

    try:
        session = agent.status()
        connected = session.get("status") == "connected"
    except Exception:
        connected = False

    console.print()

    if console.width >= 65:
        for line in LOGO.strip("\n").splitlines():
            console.print(gradient(line))
    else:
        console.print(gradient("TERMGPT"))

    console.print()

    console.print(
        "  YOUR PERSONAL AI CODING AGENT",
        style="bold #94a3b8"
    )

    console.print(
        "  Version 0.8.3 | Professional Edition\n",
        style="#64748b"
    )

    table = Table.grid(
        expand=True,
        padding=(0, 2)
    )

    table.add_column(style="#64748b", width=16)
    table.add_column(justify="right")

    table.add_row(
        "Provider",
        "[#4ade80]Connected[/]" if connected
        else "[red]Disconnected[/]"
    )

    table.add_row(
        "Authentication",
        "[#38bdf8]ChatGPT OAuth[/]"
    )

    table.add_row(
        "Model",
        Text(agent.model, style="#c4b5fd")
    )

    table.add_row(
        "Workspace",
        Text(str(engine.workspace), style="#e2e8f0")
    )


    table.add_row(
        "Work Mode",
        Text(agent.work_mode.upper(), style="#38bdf8")
    )

    table.add_row(
        "Response Mode",
        "[bold yellow]FAST[/]"
        if agent.fast_mode
        else "[#a78bfa]STANDARD[/]"
    )


    table.add_row(
        "File Access",
        "[bold yellow]FULL ACCESS[/]"
        if engine.access_mode == "full"
        else "[green]WORKSPACE[/]"
    )

    modes = {
        "on": "[bold yellow]AUTO MODE[/]",
        "safe": "[bold cyan]SAFE MODE[/]",
        "off": "[bold green]MANUAL MODE[/]"
    }

    table.add_row(
        "Permissions",
        modes.get(agent.auto_mode, "UNKNOWN")
    )

    console.print(Panel(
        table,
        title="[bold #2dd4bf] SYSTEM OVERVIEW [/]",
        subtitle="[dim] Powered by OpenAI [/]",
        border_style="#334155",
        box=box.ROUNDED,
        padding=(1, 1)
    ))

    console.print(
        "  /help  /models  /sessions  /tasks  /undo  /plan",
        style="#64748b"
    )

    console.print()


def toolbar(agent, engine):
    mode = agent.auto_mode.upper()

    color = {
        "ON": "#fbbf24",
        "SAFE": "#38bdf8",
        "OFF": "#4ade80"
    }.get(mode, "#ffffff")

    model = escape(agent.model)
    workspace = escape(
        engine.workspace.name or str(engine.workspace)
    )


    speed = "FAST" if agent.fast_mode else "STANDARD"
    work = agent.work_mode.upper()

    return HTML(
        ' <style fg="#2dd4bf"><b>TERMGPT</b></style>'
        f'  |  {model}'
        f'  |  {workspace}'
        f'  |  ACCESS: {engine.access_mode.upper()}'
        f'  |  <style fg="#38bdf8">{work}</style>'
        f'  |  <style fg="#a78bfa">{speed}</style>'
        f'  |  <style fg="{color}">AUTO: {mode}</style>'
    )

