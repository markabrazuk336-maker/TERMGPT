import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ["LOCALAPPDATA"]) / "TERMGPT"
DATA.mkdir(parents=True, exist_ok=True)

SETTINGS = DATA / "settings.json"
CONVERSATION = DATA / "conversation.json"

DEFAULTS = {
    "model": "gpt-6.2-sol",
    "auto_mode": "off",
    "access_mode": "workspace",
    "fast_mode": False,
    "work_mode": "agent",
    "workspace": str(BASE)
}


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path, data):
    temporary = path.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    temporary.replace(path)


def load_settings():
    saved = load_json(SETTINGS, {})

    if not isinstance(saved, dict):
        saved = {}

    return {**DEFAULTS, **saved}


def restore_state(agent, engine):
    settings = load_settings()

    agent.model = settings["model"]

    access = settings.get("access_mode", "workspace")
    engine.access_mode = (
        access if access in ("workspace", "full")
        else "workspace"
    )

    agent.fast_mode = settings.get("fast_mode") is True

    mode = settings.get("work_mode", "agent")

    agent.work_mode = (
        mode if mode in ("agent", "chat", "plan")
        else "agent"
    )

    mode = settings["auto_mode"]
    agent.auto_mode = mode if mode in (
        "off", "safe", "on"
    ) else "off"

    workspace = Path(settings["workspace"])

    if workspace.is_dir():
        engine.workspace = workspace.resolve()
    else:
        agent.auto_mode = "off"

    history = load_json(CONVERSATION, [])

    agent.history = history if isinstance(history, list) else []

    return settings


def save_state(agent, engine):
    save_json(SETTINGS, {
        "model": agent.model,
        "auto_mode": agent.auto_mode,
        "access_mode": engine.access_mode,
        "fast_mode": agent.fast_mode,
        "work_mode": agent.work_mode,
        "workspace": str(engine.workspace)
    })

    save_json(CONVERSATION, agent.history)
