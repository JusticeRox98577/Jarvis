import json
from pathlib import Path


class Memory:
    """Persists conversation turns to disk and hands back bounded context."""

    def __init__(self, data_dir: Path, max_turns: int = 20):
        self.file = Path(data_dir) / "history.json"
        self.max_turns = max_turns
        self.messages = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._save()

    def context(self):
        """Last N turns (user+assistant pairs) to send to the LLM."""
        return self.messages[-self.max_turns * 2:]

    def _save(self):
        self.file.write_text(json.dumps(self.messages, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self):
        self.messages = []
        self._save()
