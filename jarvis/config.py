import os
import sys
from pathlib import Path

import yaml


def _project_root() -> Path:
    """Where config.yaml / assets live. When running from source this is
    the repo root; when packaged with PyInstaller it's the folder holding
    JARVIS.exe (build_exe.bat copies config.yaml and assets/ there)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = _project_root()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


class AttrDict(dict):
    """Dict that also supports attribute access, recursively."""

    def __getattr__(self, key):
        try:
            val = self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc
        return AttrDict(val) if isinstance(val, dict) else val

    def __setattr__(self, key, value):
        self[key] = value


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AttrDict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return AttrDict(data)


def resolve_data_dir(cfg: AttrDict) -> Path:
    """Where history/memory/personality get written. Installed (frozen)
    builds default to %APPDATA%\\JARVIS so data survives reinstalls/updates
    and doesn't require write access to Program Files. Running from source
    keeps using a project-local folder, unchanged from before."""
    configured = Path(cfg.app.data_dir)
    if configured.is_absolute():
        data_dir = configured
    elif getattr(sys, "frozen", False):
        appdata = os.getenv("APPDATA") or str(PROJECT_ROOT)
        data_dir = Path(appdata) / "JARVIS" / configured.name
    else:
        data_dir = PROJECT_ROOT / configured
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def resolve_asset(name: str) -> Path:
    return PROJECT_ROOT / "assets" / name
