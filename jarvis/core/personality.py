import json
import re
from pathlib import Path

DEFAULT_TRAITS = {"verbosity": 0.5, "formality": 0.4, "humor": 0.4}

# Explicit style feedback -> trait nudges. This is deliberately simple and
# inspectable rather than a black-box model: you can see exactly why Jarvis's
# tone shifted by reading this list.
_ADJUSTMENTS = [
    (r"\b(shorter|more concise|too long|less verbose|get to the point)\b", "verbosity", -0.15),
    (r"\b(more detail|elaborate|longer answers|be more thorough)\b", "verbosity", 0.15),
    (r"\b(be more formal|more professional|less casual)\b", "formality", 0.15),
    (r"\b(be more casual|loosen up|relax a bit|less formal|be more chill)\b", "formality", -0.15),
    (r"\b(be funnier|more humor|joke around|lighten up)\b", "humor", 0.15),
    (r"\b(stop joking|be serious|less jokes|too much humor)\b", "humor", -0.15),
]


class Personality:
    """Tracks a small set of tone traits that drift based on explicit
    feedback given in conversation, and persists them across runs."""

    def __init__(self, data_dir: Path, initial: dict = None):
        self.file = Path(data_dir) / "personality.json"
        self.traits = self._load(initial or DEFAULT_TRAITS)

    def _load(self, initial):
        if self.file.exists():
            try:
                saved = json.loads(self.file.read_text(encoding="utf-8"))
                return {**initial, **saved}
            except (json.JSONDecodeError, OSError):
                pass
        return dict(initial)

    def _save(self):
        self.file.write_text(json.dumps(self.traits, indent=2), encoding="utf-8")

    def observe(self, user_text: str) -> bool:
        """Look for style feedback in what the user just said and nudge
        traits accordingly. Returns True if anything changed."""
        t = user_text.lower()
        changed = False
        for pattern, trait, delta in _ADJUSTMENTS:
            if re.search(pattern, t):
                self.traits[trait] = round(max(0.0, min(1.0, self.traits.get(trait, 0.5) + delta)), 3)
                changed = True
        if changed:
            self._save()
        return changed

    def prompt_fragment(self) -> str:
        v, f, h = self.traits["verbosity"], self.traits["formality"], self.traits["humor"]
        verbosity = "very concise, one or two sentences" if v < 0.35 else "detailed and thorough" if v > 0.65 else "moderately detailed"
        formality = "formal and professional" if f > 0.65 else "casual and relaxed" if f < 0.35 else "neutral in tone"
        humor = "witty with frequent humor" if h > 0.65 else "mostly serious, rare jokes" if h < 0.35 else "occasionally playful"
        return f"Current calibrated style: {verbosity}; {formality}; {humor}."
