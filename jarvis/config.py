from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
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
    data_dir = Path(cfg.app.data_dir)
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
