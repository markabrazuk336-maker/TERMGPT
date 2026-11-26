from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class TaskManager:
    def __init__(self):
        self.tasks = []

    def set_tasks(self, tasks):
        if not isinstance(tasks, list):
            raise ValueError("Expected task list")

        self.tasks = [
            {
                "title": str(title)[:200],
                "status": "pending"
            }
            for title in tasks[:30]
        ]

        self.show()
        return "Task list created."

    def update(self, index, status):
        if status not in (
            "pending", "running", "done", "failed"
        ):
            raise ValueError("Invalid task status")

        if not 0 <= index < len(self.tasks):
            raise ValueError("Invalid task index")

        self.tasks[index]["status"] = status
        self.show()

        return "Task status updated."

    def show(self):
        if not self.tasks:
            console.print("[dim]No active tasks[/dim]")
            return

        done = sum(
            task["status"] == "done"
            for task in self.tasks
        )

        total = len(self.tasks)
        filled = int(done / total * 24)

        output = Text()

        icons = {
            "done": ("[OK]", "green"),
            "running": (">", "cyan"),
            "pending": ("[ ]", "dim"),
            "failed": ("[X]", "red")
        }

        for task in self.tasks:
            icon, color = icons[task["status"]]

            output.append(
                f"{icon} {task['title']}\n",
                style=color
            )

        output.append("\n")
        output.append("━" * filled, style="bright_cyan")
        output.append("━" * (24 - filled), style="dim")
        output.append(f" {done}/{total}")

        console.print(Panel(
            output,
            title="[bold cyan] TASK PROGRESS [/bold cyan]",
            border_style="#334155"
        ))
