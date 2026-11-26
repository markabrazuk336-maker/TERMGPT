import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from tools.engine import ToolEngine
from agent import Agent
from access import list_drives
from access import list_drives
from sessions import SessionManager
from attachments import expand_attachments
import sys
from backup import undo_last, show_backups
from settings import restore_state, save_state
import atexit
from ui import banner as premium_banner, toolbar
from prompt_toolkit.completion import WordCompleter, DynamicCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

console = Console()
agent = Agent()
base = Path(__file__).resolve().parent
engine = ToolEngine(Path.cwd())

restore_state(agent, engine)

sessions = SessionManager()
sessions.restore(agent, engine)

if "--here" in sys.argv:
    current = Path.cwd().resolve()

    if current != engine.workspace:
        sessions.save(agent, engine)

        engine.workspace = current
        agent.auto_mode = "off"

        import uuid
        name = "workspace-" + uuid.uuid4().hex[:8]
        sessions.current = name
        agent.reset()
        agent.tasks.tasks.clear()
        sessions.save(agent, engine)


def autosave():
    save_state(agent, engine)
    sessions.save(agent, engine)

atexit.register(autosave)

history = FileHistory(str(base / ".history"))



from prompt_toolkit.completion import Completer, Completion
import re

class AttachmentCompleter(Completer):
    def get_completions(self, document, complete_event):
        before = document.text_before_cursor

        match = re.search(
            r'(?<!\\S)@(?:"([^"]*)|([^\\s]*))$',
            before
        )

        if not match:
            return

        prefix = match.group(1) or match.group(2) or ""
        prefix = prefix.replace(chr(92), "/")

        parent, _, fragment = prefix.rpartition("/")

        try:
            directory = engine.resolve(parent or ".")

            for item in sorted(directory.iterdir())[:300]:
                if item.name.startswith("."):
                    continue

                if not item.name.lower().startswith(fragment.lower()):
                    continue

                name = item.relative_to(
                    engine.workspace
                ).as_posix()

                if item.is_dir():
                    name += "/"

                value = (
                    '@"' + name + '"'
                    if " " in name else "@" + name
                )

                yield Completion(
                    value,
                    start_position=-len(match.group(0)),
                    display=name
                )

        except (OSError, ValueError):
            return

def command_completer():
    from prompt_toolkit.application import get_app

    text = get_app().current_buffer.text

    if not text.startswith("/"):
        return AttachmentCompleter()

    return WordCompleter([
        "/help", "/exit", "/clear",
        "/pwd", "/cd", "/ls",
        "/read", "/write", "/run",
        "/status", "/account",
        "/login", "/logout",
        "/models", "/model",
        "/new", "/auto",
        "/auto on", "/auto off", "/auto safe",
        "/fast", "/fast on", "/fast off",
        "/plan", "/chat", "/agent", "/mode", "/tasks", "/undo", "/backups",
        "/sessions", "/session",
        "/session new", "/session open",
        "/session delete", "/session save",
        "/access", "/access full",
        "/access workspace", "/drives",
        "/access", "/access full",
        "/access workspace", "/drives"
    ], ignore_case=True, sentence=True)

def banner():
    premium_banner(agent, engine)

def help_menu():
    table = Table(title="Available commands", border_style="cyan")
    table.add_column("Command", style="cyan")
    table.add_column("Description")

    commands = {
        
        "/login": "Sign in with ChatGPT",
        "/logout": "Disconnect ChatGPT",
        "/models": "List AI models",
        "/model NAME": "Select model",
        "/new": "Clear conversation",
        "/account": "Connection status",
        "/auto on": "Enable full auto approval",
        "/auto safe": "Enable safe auto approval",
        "/auto off": "Disable auto approval",
        "/auto": "Show approval mode",
        "/fast on": "Enable fast mode",
        "/fast off": "Disable fast mode",
        "/chat": "Chat with streaming",
        "/agent": "Coding agent mode",
        "/plan": "Read-only planning mode",
        "/mode": "Show current modes",
        "/tasks": "Show agent tasks",
        "/backups": "Show file backups",
        "/undo": "Undo last agent file change",
        "/sessions": "List saved sessions",
        "/session": "Current session",
        "/session new NAME": "Create session",
        "/session open NAME": "Open session",
        "/session delete NAME": "Delete session",
        "/session save": "Save session",
        "/access": "Show access mode",
        "/access full": "Enable full disk access",
        "/access workspace": "Restrict access to workspace",
        "/drives": "List available drives",
        "/access": "Show access mode",
        "/access full": "Enable full disk access",
        "/access workspace": "Restrict access to workspace",
        "/drives": "List available drives",
        "/help": "Show commands",
    
        "/exit": "Exit terminal",
        "/clear": "Clear screen",
        "/pwd": "Show workspace",
        "/cd PATH": "Change workspace",
        "/ls": "List files",
        "/read FILE": "Read source code",
        "/write FILE": "Create or overwrite file",
        "/run COMMAND": "Execute PowerShell command",
        "/status": "Show system status"
    }

    for cmd, desc in commands.items():
        table.add_row(cmd, desc)

    console.print(table)

banner()

while True:
    try:
        autosave()
        text = prompt(
            HTML('<style fg="#2dd4bf"><b>❯</b></style> '),
            history=history,
            completer=DynamicCompleter(command_completer),
            complete_while_typing=True,
            bottom_toolbar=lambda: toolbar(agent, engine),
            style=Style.from_dict({
                "bottom-toolbar": "bg:#161b22 #dddddd",
                "completion-menu.completion": "bg:#161b22 #dddddd",
                "completion-menu.completion.current": "bg:#008b8b #ffffff"
            })
        ).strip()

        if not text:
            continue

        if text == "/exit":
            console.print("[cyan]Goodbye![/cyan]")
            break

        elif text == "/help":
            help_menu()

        elif text == "/clear":
            banner()

        elif text == "/pwd":
            console.print(str(engine.workspace))

        elif text == "/ls":
            console.print(engine.list_files(), markup=False)

        elif text.startswith("/cd "):
            path = (
                engine.workspace / text[4:].strip()
            ).resolve()

            if path.is_dir():
                previous_access = engine.access_mode
                engine = ToolEngine(path)
                engine.access_mode = previous_access
                agent.auto_mode = "off"
                agent.reset()
                console.print(f"[green]Workspace: {path}[/green]")
            else:
                console.print("[red]Directory not found[/red]")

        elif text.startswith("/read "):
            path = text[6:].strip()
            content = engine.read_file(path)
            lexer = Path(path).suffix.lstrip(".") or "text"

            console.print(Syntax(
                content,
                lexer,
                line_numbers=True,
                theme="monokai"
            ))

        elif text.startswith("/write "):
            path = text[7:].strip()
            console.print(
                "[cyan]Enter file content. Type END to finish.[/cyan]"
            )

            lines = []

            while True:
                line = input()

                if line == "END":
                    break

                lines.append(line)

            target = engine.resolve(path)

            if target.exists():
                console.print("[yellow]File already exists![/yellow]")

            if prompt("Save file? [y/N]: ").lower() == "y":
                console.print(
                    engine.write_file(path, "\n".join(lines)),
                    style="green",
                    markup=False
                )
            else:
                console.print("[yellow]Cancelled[/yellow]")

        elif text.startswith("/run "):
            command = text[5:].strip()

            console.print(
                f"Execute: {command}",
                style="yellow",
                markup=False
            )

            if prompt("Allow execution? [y/N]: ").lower() == "y":
                with console.status("Executing..."):
                    result = engine.run_command(command)

                console.print(result, markup=False)


        elif text == "/auto":
            console.print("Auto mode: " + agent.auto_mode)

        elif text.startswith("/auto "):
            mode = text[6:].strip().lower()

            if mode == "on":
                console.print(
                    "[bold red]WARNING: Full auto mode allows "
                    "commands without confirmation.[/bold red]"
                )

                if prompt("Enable full auto mode? [y/N]: ").lower() == "y":
                    agent.auto_mode = "on"
                    console.print("[green]Auto Approve: ON[/green]")

            elif mode == "safe":
                agent.auto_mode = "safe"
                console.print("[cyan]Auto Approve: SAFE[/cyan]")

            elif mode == "off":
                agent.auto_mode = "off"
                console.print("[yellow]Auto Approve: OFF[/yellow]")

            else:
                console.print("Usage: /auto on | safe | off")

        elif text == "/fast":
            console.print(
                "Fast Mode: " +
                ("ON" if agent.fast_mode else "OFF")
            )

        elif text in ("/fast on", "/fast off"):
            agent.fast_mode = text.endswith("on")

            console.print(
                "[cyan]Fast Mode: " +
                ("ON" if agent.fast_mode else "OFF") +
                "[/cyan]"
            )

        elif text in ("/chat", "/agent", "/plan"):
            mode = text[1:]

            if agent.work_mode != mode:
                agent.reset()
                agent.work_mode = mode

            console.print(
                "[bold cyan]Mode: " +
                agent.work_mode.upper() +
                "[/bold cyan]"
            )

        elif text == "/mode":
            console.print(
                "Work mode: " + agent.work_mode.upper()
            )
            console.print(
                "Fast mode: " +
                ("ON" if agent.fast_mode else "OFF")
            )
            console.print(
                "Auto mode: " + agent.auto_mode.upper()
            )
            console.print("Model: " + agent.model)

        elif text == "/tasks":
            agent.tasks.show()

        elif text == "/backups":
            show_backups(engine.workspace)

        elif text == "/undo":
            console.print(
                "[yellow]Undo last agent file change?[/yellow]"
            )

            if prompt("Confirm [y/N]: ").lower() == "y":
                console.print(
                    undo_last(engine.workspace),
                    markup=False
                )

        elif text == "/sessions":
            sessions.save(agent, engine)
            sessions.show()

        elif text == "/session":
            console.print("Session: " + sessions.current)

        elif text == "/session save":
            sessions.save(agent, engine)
            console.print("[green]Session saved[/green]")

        elif text.startswith("/session new "):
            name = text[len("/session new "):].strip()
            sessions.new(name, agent, engine)
            console.print("New session: " + name, markup=False)

        elif text.startswith("/session open "):
            name = text[len("/session open "):].strip()
            sessions.open(name, agent, engine)
            console.print("Active session: " + name, markup=False)

        elif text.startswith("/session delete "):
            name = text[len("/session delete "):].strip()

            if prompt("Delete session? [y/N]: ").lower() == "y":
                sessions.delete(name)
                console.print("[green]Session deleted[/green]")

        elif text == "/access":
            console.print(
                "Access mode: " + engine.access_mode.upper()
            )

        elif text == "/access full":
            console.print(
                "[bold yellow]FULL ACCESS allows inspection "
                "of files outside the workspace.[/bold yellow]"
            )

            if prompt("Enable full access? [y/N]: ").lower() == "y":
                engine.access_mode = "full"
                console.print("[green]Full Access: ON[/green]")

        elif text == "/access workspace":
            engine.access_mode = "workspace"
            console.print("[cyan]Workspace Access: ON[/cyan]")

        elif text == "/drives":
            table = Table(title="Available Drives")
            table.add_column("Drive", style="cyan")

            for drive in list_drives():
                table.add_row(drive)

            console.print(table)

        elif text == "/access":
            console.print(
                "Access mode: " + engine.access_mode.upper()
            )

        elif text == "/access full":
            console.print(
                "[bold yellow]FULL ACCESS allows inspection "
                "of files outside the workspace.[/bold yellow]"
            )

            if prompt("Enable full access? [y/N]: ").lower() == "y":
                engine.access_mode = "full"
                console.print("[green]Full Access: ON[/green]")

        elif text == "/access workspace":
            engine.access_mode = "workspace"
            console.print("[cyan]Workspace Access: ON[/cyan]")

        elif text == "/drives":
            table = Table(title="Available Drives")
            table.add_column("Drive", style="cyan")

            for drive in list_drives():
                table.add_row(drive)

            console.print(table)

        elif text == "/login":
            console.print(agent.login())

        elif text == "/logout":
            console.print(agent.logout())

        elif text == "/account":
            console.print(agent.status())

        elif text == "/models":
            table = Table(title="Available AI Models")
            table.add_column("Model", style="cyan")
            table.add_column("ID")

            for model in agent.models():
                table.add_row(
                    model["displayName"],
                    model["slug"]
                )

            console.print(table)

        elif text.startswith("/model "):
            selected = text[7:].strip()
            available = [m["slug"] for m in agent.models()]

            if selected in available:
                agent.model = selected
                agent.reset()
                console.print("Model: " + agent.model)
            else:
                console.print("[red]Unknown model[/red]")

        elif text == "/new":
            agent.reset()
            console.print("[green]New conversation[/green]")

        elif text == "/status":
            console.print(Panel(
                f"[green]Tool Engine: ONLINE[/green]\n"
                f"[yellow]AI Backend: READY[/yellow]\n"
                f"Workspace: {engine.workspace}\n"
                f"OS: {os.name}",
                title="System Status",
                border_style="cyan"
            ))

        else:
            text = expand_attachments(text, engine)
            agent.chat(text, engine)

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")

    except EOFError:
        break

    except Exception as e:
        console.print(str(e), style="red", markup=False)
