import json
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

ROOT = Path(os.environ["LOCALAPPDATA"]) / "TERMGPT" / "backups"
ROOT.mkdir(parents=True, exist_ok=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def create_backup(workspace, target, new_content):
    workspace = Path(workspace).resolve()
    target = Path(target).resolve()
    target.relative_to(workspace)

    backup_id = uuid.uuid4().hex
    folder = ROOT / backup_id
    folder.mkdir()

    existed = target.exists()

    if existed:
        (folder / "original.bin").write_bytes(
            target.read_bytes()
        )

    metadata = {
        "id": backup_id,
        "workspace": str(workspace),
        "path": str(target),
        "existed": existed,
        "new_hash": digest(new_content.encode("utf-8")),
        "created": datetime.now().isoformat(),
        "undone": False
    }

    (folder / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return backup_id


def get_backups(workspace):
    workspace = str(Path(workspace).resolve())
    results = []

    for path in ROOT.glob("*/metadata.json"):
        try:
            item = json.loads(
                path.read_text(encoding="utf-8")
            )

            if item["workspace"] == workspace:
                results.append(item)
        except (OSError, ValueError, KeyError):
            continue

    return sorted(
        results,
        key=lambda item: item["created"],
        reverse=True
    )


def show_backups(workspace):
    table = Table(title="File Backups", border_style="cyan")

    table.add_column("File")
    table.add_column("Created")
    table.add_column("Status")

    for item in get_backups(workspace)[:20]:
        table.add_row(
            Text(Path(item["path"]).name),
            item["created"][:19],
            "Restored" if item["undone"] else "Available"
        )

    console.print(table)


def undo_last(workspace):
    workspace = Path(workspace).resolve()

    items = [
        item for item in get_backups(workspace)
        if not item["undone"]
    ]

    if not items:
        return "No changes to undo."

    item = items[0]
    target = Path(item["path"]).resolve()
    target.relative_to(workspace)

    folder = ROOT / item["id"]

    if not target.is_file():
        return "Undo refused: file is missing."

    if digest(target.read_bytes()) != item["new_hash"]:
        return "Undo refused: file was changed externally."

    if item["existed"]:
        target.write_bytes(
            (folder / "original.bin").read_bytes()
        )
    else:
        target.unlink()

    item["undone"] = True

    (folder / "metadata.json").write_text(
        json.dumps(item, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return f"Restored: {target}"
