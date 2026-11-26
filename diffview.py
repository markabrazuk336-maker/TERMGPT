import difflib
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_diff(path, new_content):
    path = Path(path)

    old_content = (
        path.read_text(encoding="utf-8")
        if path.exists() else ""
    )

    diff = list(difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile="Before",
        tofile="After",
        lineterm="",
        n=3
    ))

    output = Text()
    added = 0
    removed = 0

    for line in diff:
        if line.startswith(("+++", "---")):
            output.append(line + "\n", style="dim")

        elif line.startswith("+"):
            added += 1
            output.append(line + "\n", style="green")

        elif line.startswith("-"):
            removed += 1
            output.append(line + "\n", style="red")

        elif line.startswith("@@"):
            output.append(line + "\n", style="cyan")

        else:
            output.append(line + "\n", style="white")

    if not diff:
        console.print("[dim]No changes[/dim]")
        return

    console.print(Panel(
        output,
        title=Text(path.name),
        subtitle=f"[green]+{added}[/green] [red]-{removed}[/red]",
        border_style="#334155"
    ))
