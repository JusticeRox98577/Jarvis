import json
import math
import time
from pathlib import Path

import ollama


class VectorMemory:
    """Local long-term memory. Every remembered exchange or fact is embedded
    with a local Ollama embedding model and stored flat on disk; recall does
    a brute-force cosine search, which is plenty fast for one person's
    conversation history. This only ever stores things said in chat, or
    explicitly given via a "remember that ..." command -- nothing else."""

    def __init__(self, data_dir: Path, host: str, embed_model: str = "nomic-embed-text", top_k: int = 4, keep_alive: str = "5m"):
        self.client = ollama.Client(host=host)
        self.embed_model = embed_model
        self.top_k = top_k
        self.keep_alive = keep_alive
        self.file = Path(data_dir) / "vector_memory.json"
        self.entries = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save(self):
        self.file.write_text(json.dumps(self.entries, ensure_ascii=False), encoding="utf-8")

    def _embed(self, text: str):
        response = self.client.embed(model=self.embed_model, input=text, keep_alive=self.keep_alive)
        vectors = response.embeddings
        return list(vectors[0]) if vectors else None

    def remember(self, text: str, kind: str = "conversation"):
        try:
            vector = self._embed(text)
        except Exception:
            return  # embedding model likely not pulled yet; fail quietly
        if not vector:
            return
        self.entries.append({"text": text, "vector": vector, "kind": kind, "ts": time.time()})
        self._save()

    def recall(self, query: str, k: int = None):
        if not self.entries:
            return []
        try:
            qvec = self._embed(query)
        except Exception:
            return []
        if not qvec:
            return []
        scored = sorted(
            ((self._cosine(qvec, e["vector"]), e["text"]) for e in self.entries),
            key=lambda pair: pair[0],
            reverse=True,
        )
        k = k or self.top_k
        return [text for score, text in scored[:k] if score > 0.5]

    @staticmethod
    def _cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
