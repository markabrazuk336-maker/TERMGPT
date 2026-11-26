import json
import os
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text

ROOT = Path(os.environ["LOCALAPPDATA"]) / "TERMGPT" / "sessions"
ROOT.mkdir(parents=True, exist_ok=True)

ACTIVE = ROOT / "active.txt"

console = Console()


class SessionManager:
    def __init__(self):
        self.current = "default"

        if ACTIVE.exists():
            name = ACTIVE.read_text(encoding="utf-8").strip()

            if re.fullmatch(r"[a-zA-Z0-9_-]{1,60}", name):
                self.current = name

    def path(self, name):
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,60}", name):
            raise ValueError(
                "Use letters, numbers, underscore or hyphen"
            )

        return ROOT / (name + ".json")

    def save(self, agent, engine):
        data = {
            "name": self.current,
            "model": agent.model,
            "workspace": str(engine.workspace),
            "history": agent.history,
            "updated": datetime.now().isoformat()
        }

        target = self.path(self.current)
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        temporary.replace(target)

        ACTIVE.write_text(self.current, encoding="utf-8")

    def restore(self, agent, engine):
        target = self.path(self.current)

        if not target.exists():
            return False

        data = json.loads(target.read_text(encoding="utf-8"))

        workspace = Path(data["workspace"]).resolve()

        if not workspace.is_dir():
            raise ValueError("Session workspace no longer exists")

        if workspace != engine.workspace:
            agent.auto_mode = "off"

        engine.workspace = workspace
        agent.model = data["model"]
        agent.history = data["history"]

        return True

    def new(self, name, agent, engine):
        target = self.path(name)

        if target.exists():
            raise ValueError("Session already exists")

        self.save(agent, engine)

        self.current = name
        agent.reset()
        agent.tasks.tasks.clear()

        self.save(agent, engine)

    def open(self, name, agent, engine):
        target = self.path(name)

        if not target.exists():
            raise ValueError("Session not found")

        self.save(agent, engine)

        previous = self.current
        self.current = name

        try:
            self.restore(agent, engine)
        except Exception:
            self.current = previous
            raise

        agent.tasks.tasks.clear()

        self.save(agent, engine)

    def delete(self, name):
        if name == self.current:
            raise ValueError("Cannot delete active session")

        self.path(name).unlink()

    def show(self):
        table = Table(
            title="TERMGPT Sessions",
            border_style="#334155"
        )

        table.add_column("Session", style="cyan")
        table.add_column("Messages")
        table.add_column("Workspace")
        table.add_column("Updated")
        table.add_column("Status")

        for path in sorted(ROOT.glob("*.json")):
            try:
                data = json.loads(
                    path.read_text(encoding="utf-8")
                )

                table.add_row(
                    Text(path.stem),
                    str(len(data.get("history", []))),
                    Text(data.get("workspace", "")),
                    data.get("updated", "")[:19],
                    "[green]ACTIVE[/green]"
                    if path.stem == self.current else ""
                )

            except (OSError, ValueError):
                continue

        console.print(table)
