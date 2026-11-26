import ctypes
import string
import os
from pathlib import Path

def list_drives():
    mask = ctypes.windll.kernel32.GetLogicalDrives()

    return [
        letter + ":\\"
        for index, letter in enumerate(string.ascii_uppercase)
        if mask & (1 << index)
    ]


def protected_path(path):
    path = Path(path).resolve()

    protected = {
        ".ssh", ".gnupg", ".git",
        ".env", ".venv", "credentials",
        "cookies", "login data",
        "local.key", "settings.json",
        "conversation.json", ".history"
    }

    for part in path.parts:
        name = part.lower()

        if (
            name in protected
            or name.startswith(".env.")
            or name.endswith(
                (".pem", ".key", ".pfx", ".p12")
            )
        ):
            return True

    local = Path(os.environ["LOCALAPPDATA"])

    roots = [
        local / "TERMGPT",
        local / "GPT-Terminal",
        Path(__file__).resolve().parent / "backend",
        Path(__file__).resolve().parent / "sdk"
    ]

    return any(
        path.is_relative_to(root.resolve())
        for root in roots
    )


def disk_usage():
    import shutil
    import json

    results = []

    for drive in list_drives():
        try:
            usage = shutil.disk_usage(drive)

            results.append({
                "drive": drive,
                "total_gib": round(usage.total / 2**30, 2),
                "used_gib": round(usage.used / 2**30, 2),
                "free_gib": round(usage.free / 2**30, 2),
                "used_percent": round(
                    usage.used / usage.total * 100, 1
                )
            })

        except OSError:
            continue

    return json.dumps(
        results,
        ensure_ascii=False,
        indent=2
    )
