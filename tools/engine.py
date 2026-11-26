import subprocess
from access import protected_path
from pathlib import Path

class ToolEngine:
    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve()
        self.access_mode = "workspace"

    def resolve(self, path):
        target = (self.workspace / path).resolve()

        if self.access_mode == "workspace":
            if not target.is_relative_to(self.workspace):
                raise PermissionError("Path outside workspace")

        if protected_path(target):
            raise PermissionError("Protected path")

        return target

    def read_file(self, path):
        return self.resolve(path).read_text(encoding="utf-8")

    def write_file(self, path, content):
        target = self.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Saved: {target}"

    def list_files(self):
        return "\n".join(
            f"[DIR] {p.name}" if p.is_dir() else p.name
            for p in self.workspace.iterdir()
        )

    def run_command(self, command):
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
                "$OutputEncoding = [Console]::OutputEncoding; "
                "$env:PYTHONIOENCODING = 'utf-8'; " + command
            ],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120
        )
        return (
            result.stdout + result.stderr
            + f"\nExit code: {result.returncode}"
        )
