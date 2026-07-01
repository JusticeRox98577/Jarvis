import pyttsx3

_PREFERRED_VOICE_HINTS = ("david", "mark", "guy", "male")


class TextToSpeech:
    def __init__(self, rate: int = 178, voice_hint: str = "male"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self._pick_voice(voice_hint)

    def _pick_voice(self, hint: str):
        hints = (hint.lower(),) + _PREFERRED_VOICE_HINTS if hint else _PREFERRED_VOICE_HINTS
        voices = self.engine.getProperty("voices")
        for v in voices:
            name = (v.name or "").lower()
            if any(h in name for h in hints):
                self.engine.setProperty("voice", v.id)
                return

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
